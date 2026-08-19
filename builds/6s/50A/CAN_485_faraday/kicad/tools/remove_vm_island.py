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

The pocket lies wholly inside the via ring, so no VM copper outside the ring
is affected. Its extent is recomputed from the via positions on every run --
see the note on VIA_OWNER below for why that is not a hardcoded rectangle.

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

# The pocket is DERIVED from U5's thermal-via ring, not hardcoded.
#
# It was hardcoded once, as the measured bbox (13.55, 38.55, 16.65, 40.75),
# and that broke the first time the repo owner moved U5: the board owner
# shifted U5 +1.000 mm to centre it, the via ring went with it, and the rule
# area did not -- letting a 1.117 mm^2 sliver of VM plane escape through
# exactly the millimetre the stale rectangle no longer covered. A constant
# that describes another object's position is a constant that goes stale the
# moment that object moves.
#
# Now the rectangle is computed from the actual via positions every run, so
# it follows U5 wherever it goes. MARGIN_MM pads it past the via copper so
# the pour is excluded rather than trimmed to a hairline.
NAME = "VM island under U5 via ring"
VIA_OWNER = "U5"
VIA_PAD = "41"
MARGIN_MM = 0.15


def existing(board):
    """The rule area this script adds, if it already ran."""
    for zone in board.Zones():
        if zone.GetIsRuleArea() and zone.GetZoneName() == NAME:
            return zone
    return None


def island_box(board):
    """The dead pocket, derived from where U5's via ring actually is now."""
    fp = next((f for f in board.Footprints()
               if f.GetReference() == VIA_OWNER), None)
    if fp is None:
        raise SystemExit(f"{VIA_OWNER} not on board")
    vias = [p for p in fp.Pads()
            if p.GetNumber() == VIA_PAD and p.GetDrillSize().x > 0]
    if not vias:
        raise SystemExit(f"no through-hole {VIA_OWNER}.{VIA_PAD} vias")
    xs, ys, r = [], [], 0
    for v in vias:
        pos = v.GetPosition()
        xs.append(pos.x)
        ys.append(pos.y)
        r = max(r, v.GetSize().x // 2)
    pad = r + pcbnew.FromMM(MARGIN_MM)
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


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
    x1, y1, x2, y2 = island_box(board)

    old = existing(board)
    if old is not None:
        ob = old.GetBoundingBox()
        if (abs(ob.GetLeft() - x1) < 1000 and abs(ob.GetRight() - x2) < 1000
                and abs(ob.GetTop() - y1) < 1000
                and abs(ob.GetBottom() - y2) < 1000):
            print("rule area already present and correctly placed")
            return 0
        print(f"rule area is STALE: it sits at x "
              f"{pcbnew.ToMM(ob.GetLeft()):.2f}..{pcbnew.ToMM(ob.GetRight()):.2f} "
              f"but {VIA_OWNER}'s via ring now needs x "
              f"{pcbnew.ToMM(x1):.2f}..{pcbnew.ToMM(x2):.2f} -- replacing")
        board.Remove(old)

    print(f"In2.Cu VM plane fills as {vm_outlines(board)} polygons")

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

    outline = zone.Outline()
    outline.NewOutline()
    for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        outline.Append(x, y)
    board.Add(zone)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()

    print(f"rule area '{NAME}' on In2.Cu over x "
          f"{pcbnew.ToMM(x1):.2f}..{pcbnew.ToMM(x2):.2f}, y "
          f"{pcbnew.ToMM(y1):.2f}..{pcbnew.ToMM(y2):.2f} (copper pour only), "
          f"derived from {VIA_OWNER}.{VIA_PAD}")
    print(f"In2.Cu VM plane now fills as {vm_outlines(board)} polygons")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    board.Save(str(PCB))
    print(f"\nsaved {PCB.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
