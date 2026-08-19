#!/usr/bin/env python3
"""Widen the board to 32 mm so the isolation barrier can meet its creepage.

Governed by AGENTS.md. Implements the decision recorded in TODO.md 12.5.ac.

WHY WIDTH RATHER THAN LENGTH
-----------------------------
`docs/tools/isolation_envelope.py` prices the trade. With U3/U4 rotated so
both isolated rows face the board edges, the widest non-isolated part (U1,
13.45 mm) cannot fit between them on a 25.4 mm board:

    12.90 + 2 x (7.5 + 1.43) + 2 x 0.55 = 31.86 mm minimum
    at 25.40 mm -> dx = 4.27 mm  FAILS
    at 32.00 mm -> dx = 7.57 mm  OK

Below the minimum, U1 must instead clear the isolated section in Y, costing
the creepage offset plus its own height -- 19.07 mm of length. So 6.6 mm of
width buys back ~19 mm of length at essentially constant area, and the
nacelle annulus (4.00-11.65 mm radial around a 55 mm EDF casing, 185.2 mm
long) accepts either width with 7-9 mm to spare, so nothing mechanical forces
the narrow option.

WHY THE POWER STAGE DOES NOT MOVE
----------------------------------
SH1 is a Wurth WE-SHC 3670209 frame [51] with a fixed 22.2 mm land, and it
must sit directly under the FETs for the shortest gate loop. The FET columns
are therefore capped at the shield's width no matter how wide the board gets.
Every added millimetre goes to the isolated section and to U1 -- which is
exactly what needed the room. Q1-Q6, SH1, U5, R1-R3 and J4A/B/C keep their x.

WHAT THIS SCRIPT DOES
---------------------
1. Extends Edge.Cuts: every outline point right of the midline moves +6.60 mm,
   preserving the 2 mm corner arcs.
2. Extends every zone the same way.
3. Moves U4 and its connector J3 right by the same amount, so U4's isolated
   row re-anchors to the new right edge.
4. Centres U1 in the widened board.

It does NOT re-place the isolated support components (FB1-FB4, C11-C18) --
they were already outside [9]'s 10 mm lead-length limit before this change and
their target space is what this widening creates. That is TODO.md 12.5.af, and
it belongs to the repo owner.

Usage:
    python3 tools/widen_board_to_32mm.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.ac.
# AI-generated; every coordinate is measured off the board. Not human-authored.

import argparse
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-widen.bak")

WIDEN = 6.60          # 25.40 -> 32.00 mm
MIDLINE = 12.70       # outline points right of this move
# J3 must NOT follow U4 rightward: J5B (the pack GND terminal, x 17.60..24.60)
# already occupies the space U4 vacates. Moving J3 there put it 1.20 mm from
# J5B.1, worse than the 4.83 mm it started at. Where J3 belongs is part of the
# unresolved pack-versus-comms question in TODO.md 12.5.ac.
MOVE_RIGHT = ["U4"]           # re-anchor to the new right edge
CENTRE = ["U1"]               # re-centre in the widened board
USABLE_L = 0.55


def origin(board):
    """Top-left of the board outline."""
    box = board.GetBoardEdgesBoundingBox()
    return box.GetLeft(), box.GetTop()


def pad_span_x(f, ox):
    """Left and right pad extent of a footprint, board-local mm."""
    xs = []
    for p in f.Pads():
        pb = p.GetBoundingBox()
        xs += [pcbnew.ToMM(pb.GetLeft() - ox), pcbnew.ToMM(pb.GetRight() - ox)]
    return (min(xs), max(xs)) if xs else None


def main() -> int:
    """Widen the outline and zones, re-anchor U4/J3, centre U1."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    ox, oy = origin(board)
    d = pcbnew.FromMM(WIDEN)
    mid = ox + pcbnew.FromMM(MIDLINE)

    print(f"1. extending Edge.Cuts by {WIDEN} mm on the right")
    n = 0
    for g in board.GetDrawings():
        if g.GetLayer() != pcbnew.Edge_Cuts:
            continue
        moved = False
        for get, set_ in ((g.GetStart, g.SetStart), (g.GetEnd, g.SetEnd)):
            p = get()
            if p.x > mid:
                set_(pcbnew.VECTOR2I(p.x + d, p.y))
                moved = True
        if g.GetShape() == pcbnew.SHAPE_T_ARC:
            c = g.GetCenter()
            if c.x > mid:
                g.SetCenter(pcbnew.VECTOR2I(c.x + d, c.y))
                moved = True
        n += moved
    print(f"   {n} outline elements moved")

    print("\n2. extending zones")
    z = 0
    for zone in board.Zones():
        o = zone.Outline()
        touched = False
        for i in range(o.OutlineCount()):
            ol = o.Outline(i)
            for k in range(ol.PointCount()):
                p = ol.CPoint(k)
                if p.x > mid:
                    ol.SetPoint(k, pcbnew.VECTOR2I(p.x + d, p.y))
                    touched = True
        z += touched
    print(f"   {z} zones extended")

    print(f"\n3. re-anchoring {', '.join(MOVE_RIGHT)} to the new right edge")
    for ref in MOVE_RIGHT:
        f = next(x for x in board.Footprints() if x.GetReference() == ref)
        before = pad_span_x(f, ox)
        p = f.GetPosition()
        f.SetPosition(pcbnew.VECTOR2I(p.x + d, p.y))
        after = pad_span_x(f, ox)
        print(f"   {ref}: x {before[0]:.2f}..{before[1]:.2f} -> "
              f"{after[0]:.2f}..{after[1]:.2f}")

    box = board.GetBoardEdgesBoundingBox()
    usable_w = pcbnew.ToMM(box.GetWidth()) - 2 * USABLE_L - 0.10
    print(f"\n4. centring {', '.join(CENTRE)} (usable width {usable_w:.2f} mm)")
    for ref in CENTRE:
        f = next(x for x in board.Footprints() if x.GetReference() == ref)
        span = pad_span_x(f, ox)
        w = span[1] - span[0]
        target_left = USABLE_L + (usable_w - w) / 2
        dx = pcbnew.FromMM(target_left - span[0])
        p = f.GetPosition()
        f.SetPosition(pcbnew.VECTOR2I(p.x + dx, p.y))
        after = pad_span_x(f, ox)
        print(f"   {ref}: {w:.2f} mm wide, x {span[0]:.2f}..{span[1]:.2f} -> "
              f"{after[0]:.2f}..{after[1]:.2f}  ({pcbnew.ToMM(dx):+.2f} mm)")

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    nb = board.GetBoardEdgesBoundingBox()
    print(f"\nboard now {pcbnew.ToMM(nb.GetWidth()) - 0.1:.2f} x "
          f"{pcbnew.ToMM(nb.GetHeight()) - 0.1:.2f} mm")

    if args.dry_run:
        print("--dry-run: nothing written")
        return 0
    shutil.copy2(PCB, BACKUP)
    board.Save(str(PCB))
    print(f"saved {PCB.name} (backup: {BACKUP.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
