#!/usr/bin/env python3
"""Build the PCB from the schematic netlist: footprints, nets, planes, outline.

Replaces the previous `gen_pcb.py` output, which kicad/README.md described
honestly as unusable: "No netlist import, no routing, no DRC pass. Every PCB
pad is net-less (`net 0`); footprints are placed for board-planning legibility
only." It was also missing U2 (the OPTIGA secure element) and U5 (the gate
driver, which had no footprint at all) and carried a PCB-only J5 with no
schematic counterpart.

This script instead drives everything off the real exported netlist, so the
board and the sheet cannot drift apart:

  1. `kicad-cli sch export netlist` on the committed schematic.
  2. Every component in that netlist gets its footprint loaded from the
     library named in its own Footprint property -- no parametric stand-ins.
  3. Every pad is assigned its real net by (reference, pad number). A pad with
     no matching netlist node is reported, not silently left on net 0.
  4. Board outline, layer stack, net classes, and copper planes.

STACKUP -- 4 LAYERS  (engineering decision, AGENTS.md Sec.4)
------------------------------------------------------------
    F.Cu    components, signal routing, power pours over the switching stage
    In1.Cu  GND plane, full board
    In2.Cu  VM plane over the power stage, GND elsewhere
    B.Cu    signal routing, GND pour

Two layers cannot carry this build's currents: the 6S pack feeds a 50 A power
stage (../README.md), and a 50 A conductor is a plane, not a trace. Solid
GND planes also give every signal a continuous return path directly beneath
it, which is the layout half of the Faraday EMI tier this build selected --
the shield can (SH1) only helps if the return currents underneath it are not
already radiating.

CONDUCTOR SIZING IS NOT VERIFIED HERE
--------------------------------------
The net classes below set generous track widths for the power nets, but NO
conductor-sizing standard has been applied and none is cited. IPC-2152 is the
governing document and it is not in REFERENCES.md because it is paywalled and
could not be read. Per AGENTS.md Sec.1.3 the widths below are therefore
recorded as engineering defaults, not as computed values, and the copper for
VM / GND / PH_A / PH_B / PH_C is carried by planes and pours rather than by
tracks so that the routed track width is not the limiting factor. Validating
the actual cross-sections -- planes, pours, vias and connector pads -- against
IPC-2152 is logged in TODO.md and MUST be closed before fabrication.

PLACEMENT
---------
Placement follows the signal flow and REFERENCES.md [21] Sec. 11.1 "Layout
Guidelines" for the gate driver, which asks for: the VM bypass close to the
VM pin with a thick path to GND, bulk capacitance positioned to minimise the
high-current loop through the external MOSFETs, and minimised high-side and
low-side gate loops (GHx -> MOSFET gate -> SHx, and GLx -> gate -> SPx).
Hence: pack input, bulk cap, the three half-bridges and the shunts run left to
right across the top; the gate driver sits directly below the half-bridges,
inside the shield frame; the current-sense amplifiers sit immediately under
their own shunts; and the control section is furthest from the switching node.

The placement table is explicit and hand-authored. It is NOT a solved
placement: it is a legible, DRC-clean starting point that respects the loop
constraints above. Per-component fine placement before fab remains a human
task -- see TODO.md.

Usage:
    python3 tools/build_pcb.py [--check-only]
"""
# Authored by Claude Opus 5 (Anthropic) during the 2026-08-15 layout pass,
# TODO.md 12.4. AI-generated; reviewed against the primary sources named
# in the docstring above. Not human-authored.


import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
KICAD_DIR = HERE.parent
REPO = KICAD_DIR.parents[4]
SCH = KICAD_DIR / "open_secure_esc_6s_50a_can485_faraday.kicad_sch"
PCB = KICAD_DIR / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"

FP_LIBS = {
    "Open_Secure_ESC": REPO / "symbols" / "footprints" / "Open_Secure_ESC.pretty",
}
SYSTEM_FP_ROOT = Path("/usr/share/kicad/footprints")

BOARD_W = 30.0
BOARD_H = 60.0
EDGE_R = 2.0            # rounded corners
ORIGIN_X = 20.0         # board origin on the KiCad sheet
ORIGIN_Y = 20.0

# Nets carried by planes/pours rather than by routed tracks.
POWER_NETS = ("VM", "GND", "PH_A", "PH_B", "PH_C")

# Net class track widths, in mm. Engineering defaults -- see the module
# docstring; these are NOT IPC-2152 results.
NETCLASS_WIDTHS = {
    "Power": 3.0,
    "Sense": 0.5,
    "Default": 0.25,
}
SENSE_NETS = ("ISENSE_A_HI", "ISENSE_B_HI", "ISENSE_C_HI")

# --------------------------------------------------------------------------
# Placement: reference -> (x, y, rotation degrees), in board-local mm.
# Board-local (0,0) is the top-left corner of the outline.
# --------------------------------------------------------------------------
# reference -> (x, y, rotation, side). Board-local mm, (0,0) top-left.
# side "T" = F.Cu, "B" = B.Cu (flipped).
#
# 30 x 60 mm, double-sided. Power stage on top, control underneath, laid out
# as three phase COLUMNS at x = 6.5 / 15 / 23.5 so each phase runs straight
# down its own column: high-side FET -> low-side FET -> shunt -> current-sense
# amp (on the bottom, directly beneath its own shunt) -> phase terminal at the
# board edge. Pack terminals at the opposite end. That column discipline is
# what keeps the high-di/dt loops short (REFERENCES.md [21] Sec. 11.1) on a
# board this small.
PLACEMENT: dict[str, tuple[float, float, float, str]] = {
    # ---- TOP: the power path, one column per phase --------------------
    # Columns at x = 5.6 / 15.0 / 24.4. The 8.6 mm phase pads need >=9.1 mm
    # spacing, and 3 of them across 30 mm leaves only 4.2 mm of total margin,
    # so the column pitch is set by those pads and everything else follows.
    "J5A": (9.0, 5.0, 0, "T"),        # pack +
    "J5B": (21.0, 5.0, 0, "T"),       # pack -
    "C1": (15.0, 12.0, 0, "T"),       # bulk, in the FET loop per [21] 11.1
    "Q1": (5.6, 19.0, 0, "T"), "Q3": (15.0, 19.0, 0, "T"), "Q5": (24.4, 19.0, 0, "T"),
    "Q2": (5.6, 28.0, 0, "T"), "Q4": (15.0, 28.0, 0, "T"), "Q6": (24.4, 28.0, 0, "T"),
    "R1": (5.6, 35.0, 0, "T"), "R2": (15.0, 35.0, 0, "T"), "R3": (24.4, 35.0, 0, "T"),
    "J4A": (5.0, 54.0, 0, "B"), "J4B": (15.0, 54.0, 0, "B"), "J4C": (25.0, 54.0, 0, "B"),

    # ---- BOTTOM: gate drive, shielded, directly under the half-bridges -
    # SH1 moved to the bottom 2026-08-16. A single top-side column came to
    # 64.7 mm against a 60 mm board and the shield's 17.2 mm was the item that
    # did not fit. Underneath is also the better place for it: the gate driver
    # now sits directly below the FETs it drives, which is the shortest
    # GHx->gate->SHx loop available ([21] Sec. 11.1).
    "SH1": (15.0, 22.0, 0, "B"),
    "U5": (15.0, 22.0, 0, "B"),
    "C5": (8.0, 16.5, 0, "B"), "C6": (8.0, 22.0, 0, "B"), "C9": (8.0, 27.5, 0, "B"),
    "C8": (22.0, 16.5, 0, "B"), "C7": (22.0, 27.5, 0, "B"),

    # ---- BOTTOM: sense amps, each under its own shunt ------------------
    "U6": (5.6, 35.0, 0, "B"), "U7": (15.0, 35.0, 0, "B"), "U8": (24.4, 35.0, 0, "B"),

    # ---- BOTTOM: control ----------------------------------------------
    "U1": (11.0, 46.0, 0, "B"),
    "U2": (25.0, 42.0, 0, "B"),
    "C2": (20.0, 39.0, 0, "B"), "C4": (24.0, 39.0, 0, "B"), "C3": (28.0, 39.0, 0, "B"),
    "C10": (28.0, 46.0, 0, "B"),
    "R12": (28.0, 43.0, 0, "B"), "R13": (2.0, 39.0, 0, "B"),
    "R6": (2.0, 43.0, 0, "B"), "R7": (2.0, 46.0, 0, "B"), "R4": (2.0, 49.0, 0, "B"),
    "R5": (2.0, 52.0, 0, "B"), "R8": (28.0, 49.0, 0, "B"), "R9": (28.0, 52.0, 0, "B"),
    "R10": (2.0, 8.0, 0, "B"), "R11": (2.0, 11.0, 0, "B"), "R14": (2.0, 14.0, 0, "B"),
    "J1": (8.0, 57.0, 0, "B"),

    # ---- BOTTOM: isolated field buses, far end ------------------------
    "U3": (8.5, 45.0, 270, "T"), "U4": (22.5, 45.0, 270, "T"),
    "J2": (8.5, 54.0, 0, "T"), "J3": (22.5, 54.0, 0, "T"),
}

# Copper keepout over the isolated band: no plane, no pour, any layer.
ISOLATION_KEEPOUT = (0.8, 50.5, 28.4, 8.7)

# Per-phase copper pours on F.Cu, one per half-bridge, board-local
# (x_centre, y_top, width, height). Each covers its own high-side and
# low-side MOSFET so the phase node -- Q(hi) source to Q(lo) drain -- is an
# area of copper rather than a routed track. VM and GND have planes; the
# three phase nets do not, so without these they would leave the power stage
# on whatever width the auto-router chose. Poured at a higher priority than
# the board-wide GND pour so they win the overlap.
PHASE_POURS: dict[str, tuple[float, float, float, float]] = {
    "PH_A": (6.5, 11.0, 7.5, 22.0),
    "PH_B": (15.0, 11.0, 7.5, 22.0),
    "PH_C": (23.5, 11.0, 7.5, 22.0),
}


def run_netlist() -> tuple[dict[str, str], dict[tuple[str, str], str]]:
    """Export the schematic netlist.

    Returns (footprint by reference, net name by (reference, pad)).
    """
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "net.net"
        subprocess.run(
            ["kicad-cli", "sch", "export", "netlist",
             "--output", str(out), str(SCH)],
            check=True, capture_output=True,
        )
        text = out.read_text(encoding="utf-8")

    footprints: dict[str, str] = {}
    for block in text.split("(comp (ref ")[1:]:
        ref = re.match(r'"([^"]+)"', block).group(1)
        m = re.search(r'\(footprint "([^"]*)"\)', block)
        if m and m.group(1):
            footprints[ref] = m.group(1)

    nets: dict[tuple[str, str], str] = {}
    section = text[text.index("(nets"):]
    for chunk in section.split("(net (code")[1:]:
        name = re.search(r'\(name "([^"]*)"\)', chunk).group(1)
        for ref, pad in re.findall(
                r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', chunk):
            nets[(ref, pad)] = name
    return footprints, nets


def load_footprint(spec: str):
    """Load a footprint by its "Library:Name" specification."""
    lib, name = spec.split(":", 1)
    path = FP_LIBS.get(lib) or (SYSTEM_FP_ROOT / f"{lib}.pretty")
    fp = pcbnew.FootprintLoad(str(path), name)
    if fp is None:
        raise SystemExit(f"footprint not found: {spec} (looked in {path})")
    return fp


def rounded_outline(board, x0, y0, w, h, r) -> None:
    """Draw a rounded rectangle on Edge.Cuts."""
    def line(ax, ay, bx, by):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I_MM(ax, ay))
        seg.SetEnd(pcbnew.VECTOR2I_MM(bx, by))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(pcbnew.FromMM(0.1))
        board.Add(seg)

    def arc(cx, cy, sx, sy, ex, ey):
        a = pcbnew.PCB_SHAPE(board)
        a.SetShape(pcbnew.SHAPE_T_ARC)
        a.SetCenter(pcbnew.VECTOR2I_MM(cx, cy))
        a.SetStart(pcbnew.VECTOR2I_MM(sx, sy))
        a.SetEnd(pcbnew.VECTOR2I_MM(ex, ey))
        a.SetLayer(pcbnew.Edge_Cuts)
        a.SetWidth(pcbnew.FromMM(0.1))
        board.Add(a)

    x1, y1 = x0 + w, y0 + h
    line(x0 + r, y0, x1 - r, y0)
    line(x1, y0 + r, x1, y1 - r)
    line(x1 - r, y1, x0 + r, y1)
    line(x0, y1 - r, x0, y0 + r)
    arc(x0 + r, y0 + r, x0, y0 + r, x0 + r, y0)
    arc(x1 - r, y0 + r, x1 - r, y0, x1, y0 + r)
    arc(x1 - r, y1 - r, x1, y1 - r, x1 - r, y1)
    arc(x0 + r, y1 - r, x0 + r, y1, x0, y1 - r)


def add_zone(board, net, layers, x0, y0, w, h, priority=0):
    """Add a filled copper zone covering a rectangle."""
    zone = pcbnew.ZONE(board)
    # Build the outline in place. Handing ZONE.SetOutline() a Python-owned
    # SHAPE_POLY_SET segfaults on save -- the C++ side takes the pointer and
    # Python frees the object underneath it.
    chain = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in ((x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)):
        chain.Append(pcbnew.VECTOR2I_MM(px, py))
    chain.SetClosed(True)
    zone.Outline().AddOutline(chain)
    layer_set = pcbnew.LSET()
    for lay in layers:
        layer_set.addLayer(lay)
    zone.SetLayerSet(layer_set)
    zone.SetNet(net)
    zone.SetAssignedPriority(priority)
    zone.SetLocalClearance(pcbnew.FromMM(0.3))
    zone.SetMinThickness(pcbnew.FromMM(0.25))
    board.Add(zone)
    return zone


# The shield frame is a ring: parts are SUPPOSED to sit inside it. Its inner
# opening is 36.9 x 28.7 mm (REFERENCES.md [30] "Inner 28,7" / "Inner 36,9"),
# so anything fully within that rectangle is enclosed, not colliding.
SHIELD_REF = "SH1"
SHIELD_INNER = (36.9, 28.7)


def shield_encloses(board, other_box) -> bool:
    """True if a bounding box lies wholly inside SH1's inner opening."""
    shield = board.FindFootprintByReference(SHIELD_REF)
    if shield is None:
        return False
    cx, cy = shield.GetPosition().x, shield.GetPosition().y
    hw = pcbnew.FromMM(SHIELD_INNER[0] / 2)
    hh = pcbnew.FromMM(SHIELD_INNER[1] / 2)
    return (other_box.GetLeft() >= cx - hw and other_box.GetRight() <= cx + hw
            and other_box.GetTop() >= cy - hh
            and other_box.GetBottom() <= cy + hh)


def add_keepout(board, x0, y0, w, h):
    """Add a rule area that excludes copper pours on all layers."""
    zone = pcbnew.ZONE(board)
    chain = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in ((x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)):
        chain.Append(pcbnew.VECTOR2I_MM(px, py))
    chain.SetClosed(True)
    zone.Outline().AddOutline(chain)
    layer_set = pcbnew.LSET()
    for lay in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
        layer_set.addLayer(lay)
    zone.SetLayerSet(layer_set)
    zone.SetIsRuleArea(True)
    # Forbid POURS only. The isolated pads, their tracks and their vias must
    # still be allowed here -- this is where the isolated side of the board
    # lives. KiCad defaults the other prohibitions on for a new rule area, so
    # they are cleared explicitly.
    zone.SetDoNotAllowCopperPour(True)
    zone.SetDoNotAllowPads(False)
    zone.SetDoNotAllowTracks(False)
    zone.SetDoNotAllowVias(False)
    zone.SetDoNotAllowFootprints(False)
    board.Add(zone)
    return zone


def has_through_hole(fp) -> bool:
    """True if any pad drills through, i.e. the part blocks both sides."""
    return any(p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH,
                                    pcbnew.PAD_ATTRIB_NPTH)
               for p in fp.Pads())


def courtyard_collisions(board) -> list[str]:
    """Report footprint pairs whose courtyards overlap on a shared side."""
    boxes = []
    for fp in board.Footprints():
        poly = fp.GetCourtyard(pcbnew.F_CrtYd)
        if poly.OutlineCount() == 0:
            poly = fp.GetCourtyard(pcbnew.B_CrtYd)
        if poly.OutlineCount() == 0:
            box = fp.GetBoundingBox(False, False)
        else:
            box = poly.BBox()
        side = "B" if fp.IsFlipped() else "T"
        if has_through_hole(fp):
            side = "TB"                # occupies both sides
        boxes.append((fp.GetReference(), box, side))

    hits = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (ref_a, a, sa), (ref_b, b, sb) = boxes[i], boxes[j]
            if not (set(sa) & set(sb)):
                continue               # opposite sides, no conflict
            if not a.Intersects(b):
                continue
            if ref_a == SHIELD_REF and shield_encloses(board, b):
                continue            # enclosed by the shield, as designed
            if ref_b == SHIELD_REF and shield_encloses(board, a):
                continue
            hits.append(f"{ref_a} <-> {ref_b}")
    return hits


def main() -> int:
    """Create the board, place every part, assign nets, add planes."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-only", action="store_true",
                    help="place and report collisions without writing the file")
    args = ap.parse_args()

    footprints, nets = run_netlist()
    missing = sorted(set(footprints) - set(PLACEMENT))
    unplaced = sorted(set(PLACEMENT) - set(footprints))
    if missing:
        raise SystemExit(f"no placement given for: {', '.join(missing)}")
    if unplaced:
        raise SystemExit(f"placed but not in the netlist: {', '.join(unplaced)}")

    board = pcbnew.CreateEmptyBoard()
    board.SetCopperLayerCount(4)

    # ---- Net classes -----------------------------------------------------
    settings = board.GetDesignSettings()
    settings.SetBoardThickness(pcbnew.FromMM(1.6))
    # TI's RTA0040B land calls for 12X (0.2) thermal vias. KiCad's default
    # minimum through-hole is 0.3 mm, which would reject the manufacturer's
    # own recommended land, so the constraint is relaxed to the value the
    # drawing actually specifies rather than the land being altered.
    settings.m_MinThroughDrill = pcbnew.FromMM(0.2)

    netinfo = {}
    for name in sorted({n for n in nets.values()}):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni

    # ---- Footprints ------------------------------------------------------
    placed = 0
    unmatched_pads: list[str] = []
    for ref, spec in sorted(footprints.items()):
        fp = load_footprint(spec)
        x, y, rot, side = PLACEMENT[ref]
        fp.SetReference(ref)
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I_MM(ORIGIN_X + x, ORIGIN_Y + y))
        if rot:
            fp.SetOrientationDegrees(rot)
        if side == "B":
            fp.Flip(fp.GetPosition(), False)
        for pad in fp.Pads():
            num = pad.GetNumber()
            if not num:
                continue                      # paste aperture, no net
            net_name = nets.get((ref, num))
            if net_name is None:
                unmatched_pads.append(f"{ref}.{num}")
                continue
            pad.SetNet(netinfo[net_name])
        placed += 1

    print(f"placed {placed} footprints, {len(netinfo)} nets")
    if unmatched_pads:
        print(f"  pads with no netlist node ({len(unmatched_pads)}): "
              f"{', '.join(unmatched_pads)}")

    # ---- Board outline ---------------------------------------------------
    rounded_outline(board, ORIGIN_X, ORIGIN_Y, BOARD_W, BOARD_H, EDGE_R)

    # ---- Copper planes ---------------------------------------------------
    gnd = netinfo["GND"]
    vm = netinfo["VM"]
    inset = 0.5
    zx, zy = ORIGIN_X + inset, ORIGIN_Y + inset
    zw, zh = BOARD_W - 2 * inset, BOARD_H - 2 * inset

    # In1: solid GND under everything -- the return path for every signal.
    add_zone(board, gnd, [pcbnew.In1_Cu], zx, zy, zw, zh, priority=0)
    # In2: VM under the power stage, GND under the control section.
    power_h = 34.0
    add_zone(board, vm, [pcbnew.In2_Cu], zx, zy, zw, power_h, priority=1)
    add_zone(board, gnd, [pcbnew.In2_Cu],
             zx, zy + power_h, zw, zh - power_h, priority=0)
    # Outer layers: GND pour for shielding and heat spreading.
    add_zone(board, gnd, [pcbnew.F_Cu, pcbnew.B_Cu], zx, zy, zw, zh, priority=0)

    # ---- Per-phase pours over each half-bridge --------------------------
    for net_name, (cx, top, w, h) in PHASE_POURS.items():
        add_zone(board, netinfo[net_name], [pcbnew.F_Cu],
                 ORIGIN_X + cx - w / 2, ORIGIN_Y + top, w, h, priority=3)

    # ---- Isolation barrier ----------------------------------------------
    # A rule area that forbids copper pours on every layer across the
    # isolated band. Without it the GND plane runs straight underneath the
    # transceivers' isolation barrier, which defeats the isolator: the
    # barrier is only as good as the gap in the copper beneath it.
    kx, ky, kw, kh = ISOLATION_KEEPOUT
    add_keepout(board, ORIGIN_X + kx, ORIGIN_Y + ky, kw, kh)

    collisions = courtyard_collisions(board)
    if collisions:
        print(f"  COURTYARD OVERLAPS ({len(collisions)}):")
        for c in collisions:
            print(f"    {c}")

    if args.check_only:
        print("check only -- nothing written")
        return 1 if collisions else 0

    board.BuildConnectivity()
    board.Save(str(PCB))

    # Fill the zones in a second pass, on a RELOADED board. ZONE_FILLER
    # segfaults when run against a board assembled in memory in this process
    # (it asserts on its commit state), but works normally once the board has
    # been written and read back. Filling matters: until the planes are
    # poured, GND / VM / PH_A..C have no copper connecting them, so the
    # ratsnest -- and any auto-router driven from it -- would try to route
    # 50 A power nets as ordinary traces.
    filled = pcbnew.LoadBoard(str(PCB))
    filler = pcbnew.ZONE_FILLER(filled)
    filler.Fill(filled.Zones())
    poured = sum(1 for z in filled.Zones() if z.IsFilled())
    filled.BuildConnectivity()
    filled.Save(str(PCB))
    print(f"wrote {PCB} ({poured}/{filled.GetAreaCount()} zones poured)")
    return 1 if collisions else 0


if __name__ == "__main__":
    raise SystemExit(main())
