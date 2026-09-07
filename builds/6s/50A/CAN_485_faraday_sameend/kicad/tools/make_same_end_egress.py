#!/usr/bin/env python3
"""Convert the CAN_485_faraday board to same-end, opposite-face wire egress.

Governed by AGENTS.md. Implements
docs/design-single-end-wire-egress-variant.md for the
`Wire Egress = Same-end, opposite faces` row of docs/decision-matrix.xlsx.

WHY THE BOARD GETS LONGER INSTEAD OF RE-PARTITIONED
----------------------------------------------------
The design document's first partition moved U1/U2/J1 to the logic end to free
the terminal end. **That partition is dead**, and this script does not
implement it. U1's courtyard measures 13.45 mm, not the 12.90 mm the envelope
calculation assumed, so with U1 at the logic end
docs/tools/isolation_envelope.py returns:

    13.45 + 2 x (7.5 + 1.43) + 2 x 0.55 = 32.41 mm minimum board width

against an actual 32.00 mm. It fails by 0.41 mm, and the 7.5 mm creepage it
is built on is REFERENCES.md [9] Table 6 -- a verified primary-source value
that is not negotiable. The design document's own instruction for this case
is explicit: "this variant needs a different partition, NOT a wider board."

The different partition is to leave the logic cluster alone and buy length at
the terminal end instead. isolation_envelope.py prices width against length
at 2.7x on this geometry, so length is the cheap dimension. This also drops
the two regressions the original partition carried: the MCU-to-gate-driver
run and the current-sense returns both stay exactly as built.

WHAT THIS SCRIPT DOES
---------------------
  1. Extends the rounded-rectangle board outline by EXTEND_MM at the
     terminal end (every Edge.Cuts point below Y_SPLIT_MM moves).
  2. Extends every copper zone that reached the old board end.
  3. Moves the phase terminals J4A/J4B/J4C down by EXTEND_MM. They stay on
     F.Cu, on their own pours -- conductor_sizing.py's standing conclusion.
  4. Moves the pack terminals J5A/J5B to B.Cu in the new terminal band,
     directly opposite the phase pads, so the two inner GND planes lie
     between them.
  5. Moves the outer-layer rule area with the terminal band.
  6. Refills and reports.

WHAT THIS SCRIPT DOES NOT DO
-----------------------------
**VM distribution to the relocated pack pad is NOT solved here.** The VM pour
stops at y 60.3 mm (F.Cu) and y 60.5 mm (In2.Cu); B.Cu from y 60.5 mm to the
board end is GND. Carrying VM to a B.Cu pad in the new terminal band means
re-partitioning a plane, which depends on the stackup -- and this board has
NO stackup block at all (TODO.md 15.2). That decision is not this script's to
make, so J5's VM pad is left unconnected and shows in the DRC unconnected
count. It is reported explicitly rather than bridged with a track: a track
across that span would cost more power than all six FETs' conduction loss
combined (docs/tools/conductor_sizing.py).

It also does not delete or re-scope the outer-layer (F.Cu/B.Cu) extent of the
rule area. That moves 50 A current paths and is reserved for sign-off under
TODO.md 12.5.ae; this build inherits that open decision from its parent.

Requires: pcbnew (KiCad 9.x bindings). Do NOT run this under KiCad 10 -- it
would advance the board file format away from `version 20241229`.

Usage:
    python3 tools/make_same_end_egress.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-31. AI-generated. Geometry is
# derived from measurements of the parent board; the creepage figure is
# REFERENCES.md [9] Table 6. Not human-authored. Not yet human-reviewed.

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
BOARD = HERE.parent / "open_secure_esc_6s_50a_can485_faraday_sameend.kicad_pcb"

EXTEND_MM = 10.00       # new length added at the terminal end
Y_SPLIT_MM = 80.00      # Edge.Cuts points below this belong to the moving end
ZONE_SPLIT_MM = 84.00   # zone vertices below this belong to the moving end
TERMINAL_Y_MM = 90.50   # new centre-line for both terminal groups

PHASE_REFS = ("J4A", "J4B", "J4C")
# Pack pads, moved to B.Cu and spread symmetrically about the board centre
# line (x = 35.95 mm) with room for a 10 AWG joint and its fillet.
PACK_TARGETS = {"J5A": 30.95, "J5B": 40.95}
# Fiducials sitting inside the old rule-area band; see step 6.
FIDUCIAL_REFS = ("FID3", "FID6")


def mm(value):
    return pcbnew.ToMM(value)


def shift_edge_cuts(board, dy_nm):
    """Move the terminal end of the rounded-rectangle outline."""
    moved = 0
    for drawing in board.GetDrawings():
        if board.GetLayerName(drawing.GetLayer()) != "Edge.Cuts":
            continue

        # An arc has to be rewritten as a whole via SetArcGeometry -- there is
        # no SetArcMid in the 9.x bindings. The corner arcs lie entirely
        # within the moving end, so start/mid/end all translate together.
        if drawing.GetShapeStr() == "Arc":
            start, end = drawing.GetStart(), drawing.GetEnd()
            if mm(start.y) > Y_SPLIT_MM or mm(end.y) > Y_SPLIT_MM:
                midpoint = drawing.GetArcMid()
                drawing.SetArcGeometry(
                    pcbnew.VECTOR2I(start.x, start.y + dy_nm),
                    pcbnew.VECTOR2I(midpoint.x, midpoint.y + dy_nm),
                    pcbnew.VECTOR2I(end.x, end.y + dy_nm),
                )
                moved += 3
            continue

        for getter, setter in (
            (drawing.GetStart, drawing.SetStart),
            (drawing.GetEnd, drawing.SetEnd),
        ):
            point = getter()
            if mm(point.y) > Y_SPLIT_MM:
                setter(pcbnew.VECTOR2I(point.x, point.y + dy_nm))
                moved += 1
    return moved


def stretch_zone(zone, dy_nm, threshold_mm):
    """Push a zone's lower vertices down by dy. Returns vertices moved."""
    outline = zone.Outline()
    moved = 0
    for index in range(outline.VertexCount()):
        vertex = outline.CVertex(index)
        if mm(vertex.y) > threshold_mm:
            outline.SetVertex(
                index, pcbnew.VECTOR2I(vertex.x, vertex.y + dy_nm)
            )
            moved += 1
    return moved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(BOARD))
    dy = pcbnew.FromMM(EXTEND_MM)

    box = board.GetBoardEdgesBoundingBox()
    print(
        f"before: outline x {mm(box.GetLeft()):.2f}..{mm(box.GetRight()):.2f} "
        f"y {mm(box.GetTop()):.2f}..{mm(box.GetBottom()):.2f} "
        f"({mm(box.GetWidth()):.2f} x {mm(box.GetHeight()):.2f} mm)"
    )

    print(f"\n=== 1. outline +{EXTEND_MM:.2f} mm at the terminal end ===")
    print(f"  Edge.Cuts points moved: {shift_edge_cuts(board, dy)}")

    print("\n=== 2. copper zones stretched to the new end ===")
    for zone in board.Zones():
        if zone.GetIsRuleArea():
            continue
        bbox = zone.GetBoundingBox()
        if mm(bbox.GetBottom()) <= ZONE_SPLIT_MM:
            continue
        layer = board.GetLayerName(zone.GetLayerSet().Seq()[0])
        moved = stretch_zone(zone, dy, ZONE_SPLIT_MM)
        print(f"  {layer:8s}/{zone.GetNetname():6s} vertices moved: {moved}")

    print("\n=== 3. phase terminals move with the end (stay on F.Cu) ===")
    for footprint in board.GetFootprints():
        if footprint.GetReference() not in PHASE_REFS:
            continue
        pos = footprint.GetPosition()
        footprint.SetPosition(pcbnew.VECTOR2I(pos.x, pos.y + dy))
        new = footprint.GetPosition()
        print(
            f"  {footprint.GetReference()}: y {mm(pos.y):.2f} -> "
            f"{mm(new.y):.2f}  layer={board.GetLayerName(footprint.GetLayer())}"
        )

    print("\n=== 4. pack terminals -> B.Cu, opposite the phase pads ===")
    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        if ref not in PACK_TARGETS:
            continue
        old = footprint.GetPosition()
        old_layer = board.GetLayerName(footprint.GetLayer())
        if old_layer != "B.Cu":
            footprint.Flip(footprint.GetPosition(), False)
        footprint.SetPosition(
            pcbnew.VECTOR2I(
                pcbnew.FromMM(PACK_TARGETS[ref]),
                pcbnew.FromMM(TERMINAL_Y_MM),
            )
        )
        nets = sorted({p.GetNetname() for p in footprint.Pads()})
        print(
            f"  {ref}: ({mm(old.x):.2f},{mm(old.y):.2f}) {old_layer} -> "
            f"({PACK_TARGETS[ref]:.2f},{TERMINAL_Y_MM:.2f}) "
            f"{board.GetLayerName(footprint.GetLayer())}  nets={nets}"
        )

    print("\n=== 5. outer-layer rule area follows the terminal band ===")
    for zone in board.Zones():
        if not zone.GetIsRuleArea():
            continue
        layers = [board.GetLayerName(l) for l in zone.GetLayerSet().Seq()]
        bbox = zone.GetBoundingBox()
        if mm(bbox.GetBottom()) < 70:
            print(f"  left in place: {layers} (VM island, TODO.md 12.5.an)")
            continue
        outline = zone.Outline()
        for index in range(outline.VertexCount()):
            vertex = outline.CVertex(index)
            outline.SetVertex(index, pcbnew.VECTOR2I(vertex.x, vertex.y + dy))
        # Read the vertices back rather than GetBoundingBox(): the zone's
        # bounding box is cached and still reports the pre-move extent, which
        # would make a correct edit look like a no-op.
        outline = zone.Outline()
        ys = [mm(outline.CVertex(i).y) for i in range(outline.VertexCount())]
        print(f"  moved {layers}: y {min(ys):.2f}..{max(ys):.2f}")

    print("\n=== 6. terminal-end fiducials follow the band ===")
    # FID3/FID6 sat at y 83.65, inside the old rule area -- a band that was
    # copper-free only because the rule area forbade pour there. Once that
    # area moves with the terminals the band floods, and a 2 mm fiducial mask
    # aperture opening onto a live pour is a solder_mask_bridge error against
    # PH_B (front) and GND (rear). They move with the band that protects them.
    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        if ref not in FIDUCIAL_REFS:
            continue
        pos = footprint.GetPosition()
        footprint.SetPosition(pcbnew.VECTOR2I(pos.x, pos.y + dy))
        new = footprint.GetPosition()
        print(
            f"  {ref}: y {mm(pos.y):.2f} -> {mm(new.y):.2f} "
            f"({board.GetLayerName(footprint.GetLayer())})"
        )

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    print("\nzones refilled")

    box = board.GetBoardEdgesBoundingBox()
    print(
        f"\nafter:  outline x {mm(box.GetLeft()):.2f}..{mm(box.GetRight()):.2f} "
        f"y {mm(box.GetTop()):.2f}..{mm(box.GetBottom()):.2f} "
        f"({mm(box.GetWidth()):.2f} x {mm(box.GetHeight()):.2f} mm)"
    )

    print("\n=== terminal stack check (phase F.Cu vs pack B.Cu) ===")
    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        if ref in PHASE_REFS or ref in PACK_TARGETS:
            pos = footprint.GetPosition()
            print(
                f"  {ref:4s} ({mm(pos.x):6.2f},{mm(pos.y):6.2f}) "
                f"{board.GetLayerName(footprint.GetLayer())}"
            )

    if args.dry_run:
        print("\ndry run -- nothing written")
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = BOARD.with_suffix(f".kicad_pcb.{stamp}.bak")
    shutil.copy2(BOARD, backup)
    board.Save(str(BOARD))
    print(f"\nbacked up  {backup.name}")
    print(f"wrote      {BOARD.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
