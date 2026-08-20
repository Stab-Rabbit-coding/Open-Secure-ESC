#!/usr/bin/env python3
"""Stitch the four copper layers together with plane vias.

WHY THIS IS NEEDED
------------------
Checked 2026-08-19: the board carried **zero vias**. Nine zones were filled --
GND on F.Cu/B.Cu/In1.Cu/In2.Cu, VM on F.Cu/In2.Cu, three phase pours on F.Cu
-- and not one of them was connected to any other. In1.Cu (the solid GND
plane) and In2.Cu (the VM plane over the power stage) were floating copper:
poured, DRC-quiet, and carrying nothing.

Nothing in the flow catches this. Zone fills make every same-net pad on a
layer look connected, so the ratsnest goes quiet and the board reads as
"mostly routed" while the inner planes do no work at all. On this board that
is the 50 A pack return: J5B is an F.Cu-only SMD pad and F.Cu carries the VM
pour, not GND, in the top third of the board -- so the pack negative terminal
had no path to the ground plane whatsoever.

WHAT IT PLACES
--------------
1. A stitching grid, GRID_PITCH_MM apart, wherever the same net is poured on
   an outer layer AND on the inner plane it needs to reach:
       GND   F.Cu or B.Cu  <->  In1.Cu  (also In2.Cu below y 60.5)
       VM    F.Cu          <->  In2.Cu
2. A dense array under each pack terminal (J5A = VM, J5B = GND). These are the
   only two conductors on the board that see the full pack current, and a
   terminal that reaches a plane through a single via is a fuse. The array is
   sized by ARRAY_PITCH_MM inside the pad outline.

Vias are placed only where the pour of that net actually exists on BOTH
layers (tested against the filled polygons, not the zone outlines -- the two
differ substantially here because of the rule areas), and only where the via
plus its clearance hits no pad, no existing via, and no board edge.

VIA SIZES
---------
    stitching    0.80 / 0.40 mm     general plane tie
    pack array   1.20 / 0.60 mm     Power net class (tools/set_netclasses.py)

Both clear the project minima in the .kicad_pro (min_via_diameter 0.5,
min_through_hole_diameter 0.3, min_via_annular_width 0.1).

NOT VERIFIED HERE: the number of vias needed to carry 50 A between layers.
IPC-2152 and IPC-2221 Table 6-1 govern that and neither is in REFERENCES.md
(both paywalled, neither read), so per AGENTS.md Sec.1.3 no current rating is
asserted. The array is sized geometrically -- as many vias as fit the pad at
ARRAY_PITCH_MM -- and the count is printed so it can be checked against a
real derating table before fabrication. Logged in TODO.md.

ORDER: run this AFTER tools/autoroute.py, not before.

Stitching first looks tidier but routes worse. 223 vias placed on a 32 x 66 mm
board before routing are 223 obstacles FreeRouting has to solve around, and it
gives up on connections rather than displace copper it was told is fixed.
Placed afterwards, the stitching takes the space the router did not want, and
the `blocked()` test below keeps every via clear of the routed signals.

Usage:
    python3 tools/stitch_planes.py [--dry-run] [--pitch 4.0]
"""
# Authored by Claude Opus 5 (Anthropic), 2026-08-19 routing pass.
# AI-generated. Every geometric premise measured from the board file.

import argparse
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-stitch.bak")

GRID_PITCH_MM = 2.5
SCAN_MM = 0.5
ARRAY_PITCH_MM = 2.0
STITCH_VIA_MM = (0.80, 0.40)
PACK_VIA_MM = (1.20, 0.60)
CLEARANCE_MM = 0.40          # Power net class clearance

# Minimum distance from any stitching via to any isolated-side conductor.
# [9] Table 6 requires 7.5 mm input-terminal to output-terminal.
#
# THIS GUARD WAS MISSING IN THE FIRST VERSION AND THE OMISSION WAS SERIOUS.
# The isolation barrier on this board is held by keeping primary copper on the
# face OPPOSITE the isolated section -- a via defeats that by definition,
# because it punches every layer. Without this check the stitcher placed 26
# vias inside the isolated band, the worst of them **0.340 mm** from
# C13.1 (CAN_VISOIN) against a 7.5 mm requirement, with others landing
# directly over U3/U4's isolated pin rows and the isolated supply capacitors.
#
# Nothing caught it: DRC has no rule for it, and score_placement.py's creepage
# metric compares PADS on a shared layer, so a via is invisible to it. The
# only reason it surfaced was an explicit audit of via positions against the
# isolated nets.
ISOLATION_CLEARANCE_MM = 7.5
ISOLATED_NETS = (
    "CAN_ISO_GND", "CAN_GNDISO", "CAN_VISOIN", "CAN_VISOOUT",
    "RS485_ISO_GND", "RS485_GNDISO", "RS485_VISOIN", "RS485_VISOOUT",
    "RS485_A", "RS485_B", "Net-(J2-Pin_1)", "Net-(J2-Pin_2)",
)
EDGE_CLEARANCE_MM = 0.50     # .kicad_pro min_copper_edge_clearance

# net -> (outer layers it is poured on, inner layers it must reach)
STITCH_PAIRS = {
    "GND": (("F.Cu", "B.Cu"), ("In1.Cu", "In2.Cu")),
    "VM": (("F.Cu",), ("In2.Cu",)),
}
PACK_TERMINALS = {"J5A": "VM", "J5B": "GND"}


def fills_by_layer(board):
    """Filled polygons keyed by (netname, layer id), zones only."""
    out: dict[tuple[str, int], list] = {}
    for zone in board.Zones():
        if zone.GetIsRuleArea():
            continue
        for lid in zone.GetLayerSet().Seq():
            poly = zone.GetFilledPolysList(lid)
            if poly and poly.OutlineCount():
                out.setdefault((zone.GetNetname(), lid), []).append(poly)
    return out


def covered(fills, net, lid, point) -> bool:
    """True if net's pour on layer lid contains point."""
    return any(p.Contains(point) for p in fills.get((net, lid), []))


def blocked(board, point, radius_iu, mm, point_net_hint=None,
            ignore_pads=()) -> bool:
    """True if a via of radius_iu at point would foul something.

    `point_net_hint` names nets the via may legally touch (its own net), so a
    GND stitching via is not rejected for sitting on a GND track.
    `ignore_pads` holds pads the via is deliberately inside (the pack
    terminal it is stitching); every OTHER pad on every layer still counts,
    because a through via punches all four layers regardless of which layer
    its owner pad is on.

    DO NOT CHAIN THE BOUNDING-BOX CALLS HERE. The first version of this
    function read:

        if pad.GetBoundingBox().Inflate(keep).Contains(point):

    which is correct C++ and silently wrong through SWIG. `GetBoundingBox()`
    returns a temporary BOX2I proxy, `Inflate()` returns a reference INTO
    that temporary, and the temporary is free to be collected before
    `Contains()` runs -- so the test reads freed memory and returns False.
    It rejected nothing. The stitcher then placed 60 vias straight through
    Q1/Q3/Q5's VM pads and Q2/Q6's phase pads and took the board from 29 DRC
    violations to 186, including 41 hard shorts. Splitting it across two
    statements, so the box is held by a live name, is the whole fix.
    """
    clr = int(CLEARANCE_MM * mm)
    keep = radius_iu + clr
    iso_keep = radius_iu + int(ISOLATION_CLEARANCE_MM * mm)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() not in ISOLATED_NETS:
                continue
            box = pad.GetBoundingBox()
            box.Inflate(iso_keep)
            if box.Contains(point):
                return True
    # Isolated TRACKS count too, not just isolated pads. Checking pads alone
    # left one VM via at (35.90, 38.90) clearing every isolated pad by more
    # than 7.5 mm while sitting inside that distance of the CAN_VISOIN and
    # CAN_GNDISO tracks running down to y 31.9 -- five DRC violations that the
    # pad-only guard reported as clean.
    for track in board.GetTracks():
        if track.GetClass() != "PCB_TRACK":
            continue
        if track.GetNetname() not in ISOLATED_NETS:
            continue
        seg = pcbnew.SEG(track.GetStart(), track.GetEnd())
        if seg.Distance(point) < iso_keep + track.GetWidth() / 2:
            return True
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad in ignore_pads:
                continue
            # Bounding box first as a cheap reject, then the real pad shape.
            # Box-only rejection is safe but very costly on this board: the
            # FETs' 4.7 x 3.75 mm drain pads and the SOIC/QFN courtyards blank
            # out most of the free copper, and stitching dropped from 125 vias
            # to 21. HitTest() uses the pad's actual polygon, so an L-shaped
            # gap beside a rectangular pad stays usable.
            box = pad.GetBoundingBox()
            box.Inflate(keep)
            if box.Contains(point) and pad.HitTest(point, keep):
                return True
    for track in board.GetTracks():
        if track.GetClass() == "PCB_VIA":
            d = (track.GetPosition() - point).EuclideanNorm()
            if d < keep + track.GetFrontWidth() / 2:
                return True
        elif track.GetClass() == "PCB_TRACK":
            # A stitching via on GND/VM must clear every routed signal. This
            # is why the stitcher runs AFTER the router, not before: 200-odd
            # vias placed first are 200-odd obstacles the router has to solve
            # around, and it will leave connections unrouted rather than
            # displace them. Placed afterwards, the vias take the space the
            # router did not want.
            if track.GetNetname() in (point_net_hint or ()):
                continue
            seg = pcbnew.SEG(track.GetStart(), track.GetEnd())
            if (seg.Distance(point)
                    < keep + track.GetWidth() / 2):
                return True
    edge = board.GetBoardEdgesBoundingBox()
    edge.Inflate(-int(EDGE_CLEARANCE_MM * mm) - radius_iu)
    return not edge.Contains(point)


def add_via(board, point, net, size_mm, layer_top, layer_bot):
    """Create a through via on net at point."""
    mm = pcbnew.pcbIUScale.IU_PER_MM
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point)
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    # KiCad 9 gave vias a per-layer padstack, so PCB_VIA::SetWidth() now
    # requires a layer argument and asserts loudly (thousands of lines of
    # "SetWidth called without a layer argument") if called the KiCad 8 way.
    # SetFrontWidth() sets the whole stack while the padstack is in normal
    # mode, which is what a plain through via wants.
    via.SetFrontWidth(int(size_mm[0] * mm))
    via.SetDrill(int(size_mm[1] * mm))
    via.SetLayerPair(layer_top, layer_bot)
    via.SetNet(net)
    board.Add(via)
    return via


def main() -> int:
    """Place the stitching grid and the two pack-terminal arrays."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pitch", type=float, default=GRID_PITCH_MM,
                    help=f"minimum via-to-via spacing in mm (default {GRID_PITCH_MM})".format(GRID_PITCH_MM=GRID_PITCH_MM))
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    mm = pcbnew.pcbIUScale.IU_PER_MM
    fills = fills_by_layer(board)
    lay = {n: board.GetLayerID(n) for n in
           ("F.Cu", "B.Cu", "In1.Cu", "In2.Cu")}

    existing = sum(1 for t in board.GetTracks() if t.GetClass() == "PCB_VIA")
    print(f"vias on the board before this run: {existing}")

    bbox = board.GetBoardEdgesBoundingBox()
    placed = {"GND": 0, "VM": 0}

    # --- 1. stitching pattern ------------------------------------------
    # A rigid lattice is the obvious way to stitch and it fails on a board
    # this dense. At 2.5 mm pitch it placed 32 GND vias and ZERO VM vias --
    # not because the VM plane had nowhere to tie, but because none of the
    # lattice points happened to land on free copper. A 0.5 mm scan of the
    # same board found 116 legal VM sites. So: scan finely, take any legal
    # site, and enforce the pitch as a MINIMUM SPACING between placed vias
    # rather than as a grid. Same density where the board is open, and it
    # still finds the gaps where it is not.
    scan = int(SCAN_MM * mm)
    spacing = int(args.pitch * mm)
    r = int(STITCH_VIA_MM[0] / 2 * mm)
    done: dict[str, list] = {"GND": [], "VM": []}
    y = bbox.GetTop() + scan
    while y < bbox.GetBottom():
        x = bbox.GetLeft() + scan
        while x < bbox.GetRight():
            pt = pcbnew.VECTOR2I(x, y)
            for net_name, (outers, inners) in STITCH_PAIRS.items():
                if any((p - pt).EuclideanNorm() < spacing
                       for p in done[net_name]):
                    continue
                if not any(covered(fills, net_name, lay[o], pt)
                           for o in outers):
                    continue
                if not any(covered(fills, net_name, lay[i], pt)
                           for i in inners):
                    continue
                if blocked(board, pt, r, mm, (net_name,)):
                    continue
                add_via(board, pt, board.FindNet(net_name), STITCH_VIA_MM,
                        lay["F.Cu"], lay["B.Cu"])
                done[net_name].append(pt)
                placed[net_name] += 1
                break
            x += scan
        y += scan

    # --- 2. pack terminal arrays -------------------------------------------
    r2 = int(PACK_VIA_MM[0] / 2 * mm)
    apitch = int(ARRAY_PITCH_MM * mm)
    array = {"J5A": 0, "J5B": 0}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref not in PACK_TERMINALS:
            continue
        net_name = PACK_TERMINALS[ref]
        net = board.FindNet(net_name)
        for pad in fp.Pads():
            pb = pad.GetBoundingBox()
            yy = pb.GetTop() + apitch // 2
            while yy < pb.GetBottom():
                xx = pb.GetLeft() + apitch // 2
                while xx < pb.GetRight():
                    pt = pcbnew.VECTOR2I(xx, yy)
                    if not pad.HitTest(pt):
                        xx += apitch
                        continue
                    inner = lay["In2.Cu"] if net_name == "VM" else lay["In1.Cu"]
                    if not covered(fills, net_name, inner, pt):
                        xx += apitch
                        continue
                    # The pad this via sits in is its own conductor, but the
                    # via still punches every layer -- so everything ELSE is
                    # checked. This matters on this board specifically: J5A
                    # and J5B overlap U3's and U4's isolated pin rows in plan
                    # view (TODO.md 12.5.ac), so an unchecked array drills VM
                    # and GND straight through the isolated CAN and RS-485
                    # conductors.
                    if blocked(board, pt, r2, mm, (net_name,),
                               ignore_pads=(pad,)):
                        xx += apitch
                        continue
                    add_via(board, pt, net, PACK_VIA_MM,
                            lay["F.Cu"], lay["B.Cu"])
                    array[ref] += 1
                    xx += apitch
                yy += apitch

    total = placed["GND"] + placed["VM"] + array["J5A"] + array["J5B"]
    print(f"  GND stitching      : {placed['GND']:4} vias "
          f"({STITCH_VIA_MM[0]}/{STITCH_VIA_MM[1]} mm, "
          f"{args.pitch} mm min spacing)")
    print(f"  VM  stitching      : {placed['VM']:4} vias")
    print(f"  J5A (VM  pack +)   : {array['J5A']:4} vias "
          f"({PACK_VIA_MM[0]}/{PACK_VIA_MM[1]} mm)  <- CHECK AGAINST A "
          f"CURRENT DERATING TABLE")
    print(f"  J5B (GND pack -)   : {array['J5B']:4} vias "
          f"({PACK_VIA_MM[0]}/{PACK_VIA_MM[1]} mm)  <- CHECK AGAINST A "
          f"CURRENT DERATING TABLE")
    print(f"  total placed       : {total}")

    if args.dry_run:
        print("dry run -- not written")
        return 0
    if not total:
        print("nothing placed")
        return 0

    shutil.copy2(PCB, BACKUP)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.BuildConnectivity()
    board.Save(str(PCB))
    print(f"backed up -> {BACKUP.name}; re-poured and saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
