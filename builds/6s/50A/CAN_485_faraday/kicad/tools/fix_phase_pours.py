#!/usr/bin/env python3
"""Extend the three phase pours up to the high-side FET source pads.

WHY THIS IS NEEDED
------------------
The PH_A/PH_B/PH_C pours on F.Cu were drawn (tools/build_pcb.py, later
rebuilt per TODO.md 12.5.y) from the pad positions of an earlier placement.
The 2026-08-19 alignment pass (tools/align_rows_columns.py,
tools/symmetrize.py) moved the FET columns; the pours did not follow.
Measured 2026-08-19 on the current board:

    PH_A pour outline   y 60.02 .. 85.50
    Q1 source pads 1-3  y 55.52 .. 56.98   <- 3.04 mm ABOVE the pour

So each phase pour reaches its LOW-side FET drain (Q2/Q4/Q6, y 62.52..67.33)
but stops short of its HIGH-side FET source (Q1/Q3/Q5). The phase node -- the
conductor carrying the full 50 A between the two FETs of a half-bridge -- was
split in two with no copper joining the halves.

This is fixed as a POUR change, not a routed track, and deliberately so: the
half-bridge switch node is the highest di/dt conductor on the board, and
substituting a track for plane copper there adds both resistance and loop
area.

WHAT IT CHANGES
---------------
Only the TOP EDGE (minimum y) of the three phase zone outlines. The x extents,
the bottom edge, priorities, layers, and every other zone are untouched.

    new top y = 55.25 mm

chosen so the pour clears the high-side FETs' VM drain pads (bottom edge
y 54.83) by 0.42 mm, against the 0.40 mm clearance of the Power net class
(tools/set_netclasses.py). It sits 0.27 mm above the source pads it has to
reach, so the fill covers them.

The phase zones are priority 3 and the F.Cu VM pour is priority 2, so the
extended phase copper correctly takes precedence over VM in the band it now
occupies -- which is the intent: that band is the switch node, not the rail.

RUN THIS BEFORE THE AUTO-ROUTER. Growing a pour after routing invalidates the
router's picture of the board: the gate traces from U5 up to Q1.4/Q3.4/Q5.4
cross exactly the band the pour grows into.

Usage:
    python3 tools/fix_phase_pours.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic), 2026-08-19 routing pass.
# AI-generated. Geometry measured from the board file, not assumed.

import argparse
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-phasepour.bak")

PHASES = ("PH_A", "PH_B", "PH_C")
HIGH_SIDE = ("Q1", "Q3", "Q5")
NEW_TOP_MM = 55.25


def main() -> int:
    """Grow each phase pour's top edge and re-fill."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report the change without writing the board")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    mm = pcbnew.pcbIUScale.IU_PER_MM
    new_top = int(NEW_TOP_MM * mm)

    # Confirm the premise before acting on it: the high-side source pads must
    # really sit above the pour. If a later placement pass fixes this, the
    # script should say so rather than move copper for no reason.
    src_bottom: dict[str, int] = {}
    for fp in board.GetFootprints():
        if fp.GetReference() not in HIGH_SIDE:
            continue
        for pad in fp.Pads():
            net = pad.GetNetname()
            if net in PHASES:
                bottom = pad.GetBoundingBox().GetBottom()
                src_bottom[net] = max(src_bottom.get(net, -(1 << 40)), bottom)

    changed = 0
    for zone in board.Zones():
        if zone.GetIsRuleArea() or zone.GetNetname() not in PHASES:
            continue
        name = zone.GetNetname()
        outline = zone.Outline()
        ys = [outline.Outline(i).CPoint(k).y
              for i in range(outline.OutlineCount())
              for k in range(outline.Outline(i).PointCount())]
        top = min(ys)
        if top <= new_top:
            print(f"  {name}: already at y {top / mm:.2f} mm -- no change")
            continue
        if name in src_bottom and src_bottom[name] <= new_top:
            print(f"  {name}: source pads no longer above the pour -- skipped")
            continue
        for i in range(outline.OutlineCount()):
            chain = outline.Outline(i)
            for k in range(chain.PointCount()):
                pt = chain.CPoint(k)
                if pt.y == top:
                    chain.SetPoint(k, pcbnew.VECTOR2I(pt.x, new_top))
        reach = src_bottom.get(name)
        print(f"  {name}: top edge y {top / mm:.2f} -> {NEW_TOP_MM:.2f} mm"
              + (f" (source pads end at y {reach / mm:.2f})" if reach else ""))
        changed += 1

    if not changed:
        print("nothing to do")
        return 0
    if args.dry_run:
        print("dry run -- not written")
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
