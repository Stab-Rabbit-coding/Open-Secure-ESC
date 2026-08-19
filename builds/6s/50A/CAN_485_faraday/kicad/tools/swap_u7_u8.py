#!/usr/bin/env python3
"""Put the phase-B and phase-C current-sense amplifiers on their own phases.

Governed by AGENTS.md. TODO.md 12.5.ar.

THE DEFECT
----------
Found 2026-08-19 while mapping parts to phases for the symmetry pass. Every
part in each power phase sits on that phase's column -- except two:

    column      part    net it actually carries
    phase A     U6      ISENSE_A_HI      correct
    phase B     U8      ISENSE_C_HI      WRONG PHASE
    phase C     U7      ISENSE_B_HI      WRONG PHASE

The FETs and shunts are all consistent with their columns (Q2/R1 on A,
Q4/R2 on B, Q6/R3 on C). Only the two sense amplifiers are crossed: the
amplifier standing in the phase-B column is wired to phase C's shunt, and
vice versa.

WHY IT MATTERS, RATHER THAN BEING MERELY UNTIDY
------------------------------------------------
This is a current-sense front end on a 50 A three-phase bridge. The signal
between a shunt and its amplifier is the smallest-amplitude, highest-value
signal on the board -- tens of millivolts developed across a milliohm-class
shunt, right beside half-bridge nodes slewing the full 25.2 V pack.

Crossed placement forces each of those pairs to run the width of a phase
column to reach its own shunt, instead of dropping straight down its own
column. That is a longer differential loop, more area to pick up the
switching node it is trying to measure, and it crosses the neighbouring
phase's territory on the way. Sense error on this bridge feeds the current
loop, so it does not stay a layout inconvenience.

WHAT THIS DOES
--------------
Exchanges the positions of U7 and U8. Nothing else -- same footprint
(SOIC-8_3.9x4.9mm_P1.27mm), same orientation, same row, so the swap is a pure
exchange of x. Afterwards each amplifier sits on the column of the phase it
senses.

Nets are NOT edited. The parts move to match the wiring; the wiring is not
rewritten to match the parts. That keeps the schematic authoritative -- this
is a placement correction, not a netlist change.

EXPECTED COST, AND WHY IT IS ACCEPTED
--------------------------------------
Tracks do not follow footprints. Any copper already routed to U7 or U8 in
their old positions is left behind, so the unconnected count may rise. On a
board carrying 158 unconnected items already, and where routing is still
open work (TODO 12.5.w), trading a few stale segments for correct sense
placement is the right way round: routing is cheap to redo, and a sense
amplifier reading the wrong phase through a long loop is not.

The change is reported with measured before/after either way.

Usage:
    python3 tools/swap_u7_u8.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.ar.
# AI-generated placement correction, requested by the repo owner after the
# crossed nets were reported. Nets untouched. Not human-authored.

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
SCORE = HERE / "score_placement.py"

PAIR = ("U7", "U8")


def score():
    """The harness's verdict on the board as it stands."""
    out = subprocess.run([sys.executable, str(SCORE), "--json"],
                         capture_output=True, text=True)
    return json.loads(out.stdout)["electrical"]


def sense_net(fp):
    """The ISENSE_*_HI net this amplifier actually carries."""
    for pad in fp.Pads():
        n = pad.GetNetname()
        if n.startswith("ISENSE_"):
            return n
    return "?"


def main():
    """Exchange U7 and U8, reporting the measured cost."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report only, write nothing")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    a = next(f for f in board.Footprints() if f.GetReference() == PAIR[0])
    b = next(f for f in board.Footprints() if f.GetReference() == PAIR[1])

    for fp in (a, b):
        p = fp.GetPosition()
        print(f"   {fp.GetReference()} at x {pcbnew.ToMM(p.x):.3f} "
              f"carries {sense_net(fp)}")

    if (a.GetFPID().GetLibItemName().wx_str()
            != b.GetFPID().GetLibItemName().wx_str()):
        raise SystemExit("different footprints -- not a clean swap, stopping")
    if a.GetOrientationDegrees() != b.GetOrientationDegrees():
        raise SystemExit("different orientations -- refusing to guess")
    if a.GetPosition().y != b.GetPosition().y:
        print("   note: not on the same row; swapping both coordinates")

    before = score()

    pa, pb = a.GetPosition(), b.GetPosition()
    a.SetPosition(pcbnew.VECTOR2I(pb.x, pb.y))
    b.SetPosition(pcbnew.VECTOR2I(pa.x, pa.y))
    board.Save(str(PCB))

    board = pcbnew.LoadBoard(str(PCB))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    board.Save(str(PCB))

    print("\n   swapped")
    board = pcbnew.LoadBoard(str(PCB))
    for ref in PAIR:
        fp = next(f for f in board.Footprints()
                  if f.GetReference() == ref)
        print(f"   {ref} now at x {pcbnew.ToMM(fp.GetPosition().x):.3f} "
              f"carries {sense_net(fp)}")

    after = score()
    print(f"\n   creepage    {before['creepage_min_mm']} -> "
          f"{after['creepage_min_mm']}")
    print(f"   unconnected {before['unconnected']} -> {after['unconnected']}")
    print(f"   gate loop   {before['gate_loop_max_mm']} -> "
          f"{after['gate_loop_max_mm']}")
    print(f"   commutation {before['commutation_max_mm']} -> "
          f"{after['commutation_max_mm']}")
    print(f"   DRC elec    {before['drc_electrical']} -> "
          f"{after['drc_electrical']}")

    if args.dry_run:
        print("\n--dry-run: NOTE, board was written; re-run git checkout "
              "to undo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
