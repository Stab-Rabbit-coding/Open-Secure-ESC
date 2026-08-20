#!/usr/bin/env python3
"""Extend the phase-terminal rule area to the board edge.

Governed by AGENTS.md. Closes the remaining half of TODO.md 12.5.an.

THE VIOLATION
-------------
`isolated_copper` on In2.Cu, for both GND and VM.

The board's authored rule area excludes copper pour over the phase-terminal
band, but it stops at y 85.20 while the board outline runs to y 86.05. In that
0.85 mm gap the pour resumes -- and, cut off from everything above by the rule
area itself, fills as an orphan strip along the bottom edge on every layer:

    PH_A  F.Cu    2.011 mm^2    y 85.20..85.50
    PH_B  F.Cu    4.305 mm^2    y 85.20..85.50
    PH_C  F.Cu    2.101 mm^2    y 85.20..85.50
    GND   In2.Cu  8.747 mm^2    y 85.20..85.50, full board width

The three phase strips are harmless -- each is connected through its own
J4 terminal pad, which spans y 75.50..85.50 and overlaps them. That is why
DRC never flagged those, and why an earlier note in TODO 12.5.an calling them
"stranded" was wrong.

The GND strip on In2.Cu is the real one: 8.747 mm^2 of copper running the full
width of the board with nothing connecting it to anything. A floating
conductor that long is an antenna, and this board exists to survive harsh EMI.

WHY EXTEND THE RULE AREA RATHER THAN STITCH THE STRIP
------------------------------------------------------
The strip has no reason to exist. It is not carrying current, it is not
shielding anything, and it is there only because the rule area's lower edge
was drawn short of the board's. Connecting it would be adding vias to keep
copper nobody asked for; removing it deletes the cause.

Extending the exclusion to past the board edge cannot disconnect the phase
terminals: the J4 pads are pads, not pour, and their connection to their phase
pours is made ABOVE the rule area (pour meets pad over y 75.50..76.50, the
first 1.00 mm of a 10 mm pad -- see TODO 12.5.an). Nothing below y 85.20
contributes to that.

Usage:
    python3 tools/close_edge_orphans.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.an.
# AI-generated. Extent measured from the board outline polygon each run, so it
# survives a board resize. Not human-authored.

import argparse
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"

ISLAND_NAME = "VM island under U5 via ring"
OVERSHOOT_MM = 0.5  # push past the edge so no sliver can survive rounding


def phase_rule_area(board):
    """The authored phase-terminal exclusion, not the U5 island one."""
    for zone in board.Zones():
        if zone.GetIsRuleArea() and zone.GetZoneName() != ISLAND_NAME:
            return zone
    return None


def orphan_count(board):
    """Filled polygons beyond the first, per zone and layer."""
    n = 0
    for zone in board.Zones():
        if zone.GetIsRuleArea():
            continue
        for lid in zone.GetLayerSet().Seq():
            c = zone.GetFilledPolysList(lid).OutlineCount()
            if c > 1:
                n += c - 1
    return n


def main():
    """Extend the exclusion to the board edge and report the effect."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    poly = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(poly)
    edge = poly.BBox().GetBottom()

    zone = phase_rule_area(board)
    if zone is None:
        raise SystemExit("no phase-terminal rule area found")

    bottom = zone.GetBoundingBox().GetBottom()
    target = edge + pcbnew.FromMM(OVERSHOOT_MM)
    gap = pcbnew.ToMM(edge - bottom)
    print(
        f"rule area ends at y {pcbnew.ToMM(bottom):.2f}, "
        f"board edge y {pcbnew.ToMM(edge):.2f}  -> {gap:.2f} mm gap"
    )
    if gap <= 0:
        print("already reaches the edge -- nothing to do")
        return 0

    print(f"orphan polygons before: {orphan_count(board)}")

    outline = zone.Outline().Outline(0)
    moved = 0
    for i in range(outline.PointCount()):
        p = outline.CPoint(i)
        if p.y >= bottom - 1000:
            outline.SetPoint(i, pcbnew.VECTOR2I(p.x, target))
            moved += 1
    print(
        f"extended {moved} outline points to y "
        f"{pcbnew.ToMM(target):.2f} ({OVERSHOOT_MM} mm past the edge)"
    )

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    print(f"orphan polygons after:  {orphan_count(board)}")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    board.Save(str(PCB))
    print(f"\nsaved {PCB.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
