#!/usr/bin/env python3
"""Stop the VM plane filling the dead pocket inside U5's thermal-via ring.

Governed by AGENTS.md. Part of the clean-build pass, TODO.md 12.5.an.

THE VIOLATION
-------------
2 x `isolated_copper`: "Isolated copper fill", Zone [VM] on In2.Cu.

Measured, the In2.Cu VM plane fills as two separate polygons:

    outline 0   1226.921 mm^2   the plane proper
    outline 1      4.313 mm^2   x 13.70..16.50, y 38.70..40.60 (board-local)

The 4.3 mm^2 fragment sits inside the ring of 12 GND thermal vias under U5,
the DRV8353S. Their clearance cutouts sever it from the plane on three sides
and the VM zone's own lower boundary (y = 40.60, where GND takes over In2.Cu)
closes the fourth. Nothing on net VM lies inside it -- checked pads, tracks
and vias -- so it is a floating 4.3 mm^2 plate on the power plane: no current
path, no decoupling value, and a small coupling surface sitting directly under
a switching gate driver.

WHY A RULE AREA AND NOT A ZONE SETTING
---------------------------------------
The obvious lever is the zone's own island removal, and it is already set the
way you would set it: `island_removal_mode = 0` (ALWAYS). It does not remove
this fragment, and a clean reload-fill-save cycle with no in-memory mutation
reproduces both outlines, so this is not the stale-fill trap this project has
hit before -- the filler genuinely keeps it.

Rather than guess at why, or reach for `min_island_area`, which would silently
change how every other island on the board is treated, this adds an explicit
rule area over exactly that pocket, on In2.Cu only. It is visible in the
editor, survives refills deterministically, is scoped to the one place it is
meant to act, and states its own intent.

The pocket lies wholly inside the via ring (vias span x 13.075..17.125,
y 38.075..42.125 at the 0.30 mm copper radius set by
`fix_u5_thermal_vias.py`), so no VM copper outside the ring is affected.

Usage:
    python3 tools/remove_vm_island.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.an.
# AI-generated. The pocket's extent is measured from the filled polygon, not
# assumed; the margin is stated below. Not human-authored.

import argparse
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"

# Measured island bbox, board-local mm, plus a 0.15 mm margin so the pour is
# excluded rather than merely trimmed to a hairline.
ISLAND = (13.55, 38.55, 16.65, 40.75)
NAME = "VM island under U5 via ring"


def existing(board):
    """The rule area this script adds, if it already ran."""
    for zone in board.Zones():
        if zone.GetIsRuleArea() and zone.GetZoneName() == NAME:
            return zone
    return None


def vm_outlines(board):
    """How many separate polygons the In2.Cu VM plane fills as."""
    for zone in board.Zones():
        if (zone.GetNetname() == "VM"
                and zone.IsOnLayer(pcbnew.In2_Cu)
                and not zone.GetIsRuleArea()):
            return zone.GetFilledPolysList(pcbnew.In2_Cu).OutlineCount()
    return -1


def main():
    """Add the rule area, refill, and report the polygon count either side."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report only, write nothing")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    if existing(board) is not None:
        print("rule area already present -- nothing to do")
        return 0

    print(f"In2.Cu VM plane fills as {vm_outlines(board)} polygons")

    box = board.GetBoardEdgesBoundingBox()
    ox, oy = box.GetLeft(), box.GetTop()

    zone = pcbnew.ZONE(board)
    zone.SetIsRuleArea(True)
    zone.SetZoneName(NAME)
    layers = pcbnew.LSET()
    layers.addLayer(pcbnew.In2_Cu)
    zone.SetLayerSet(layers)
    zone.SetDoNotAllowCopperPour(True)
    zone.SetDoNotAllowTracks(False)
    zone.SetDoNotAllowVias(False)
    zone.SetDoNotAllowPads(False)
    zone.SetDoNotAllowFootprints(False)

    x1, y1, x2, y2 = ISLAND
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        outline.Append(ox + pcbnew.FromMM(x), oy + pcbnew.FromMM(y))
    board.Add(zone)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()

    print(f"added rule area '{NAME}' on In2.Cu over "
          f"x {x1}..{x2}, y {y1}..{y2} mm (copper pour only)")
    print(f"In2.Cu VM plane now fills as {vm_outlines(board)} polygons")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    board.Save(str(PCB))
    print(f"\nsaved {PCB.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
