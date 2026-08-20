#!/usr/bin/env python3
"""Decide a board's envelope from its isolation requirement, BEFORE placing it.

Governed by AGENTS.md. Companion to
docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md.

WHY THIS EXISTS
---------------
On the 6S/50A CAN_485_faraday build the creepage requirement was treated as a
DRC-time check. It is not: it is a geometry constraint that decides the board's
aspect ratio, and discovering it during placement cost several full
re-placements, a board-growth attempt, and two reverts.

The governing question is one line of trigonometry, and it can be answered
before a single footprint is placed:

    can the widest non-isolated part sit BETWEEN the two isolated rows?

If yes, control sits alongside comms and the board is short and wide. If no,
control must clear the isolated section in Y, which adds its own height PLUS a
creepage gap to the board length -- on that build, 18.5 mm of length bought
for 6.5 mm of width, at essentially constant area.

WHAT IT DOES NOT DO
-------------------
It does not size copper (see conductor_sizing.py), and it assumes the isolated
rows run along opposite board edges with the non-isolated rows inboard -- the
arrangement that lets planes cross the middle. A single isolated part on one
edge is a different and easier problem.

Usage:
    python3 docs/tools/isolation_envelope.py                 # this build
    python3 docs/tools/isolation_envelope.py --creepage 4.0 --widest 18.0
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-18. AI-generated; the
# arithmetic is plane trigonometry, the defaults are measured off
# builds/6s/50A/CAN_485_faraday. Not human-authored.

import argparse
import math

# Defaults measured off builds/6s/50A/CAN_485_faraday (2026-08-18).
CREEPAGE_MM = 7.5  # ADM2582E [9] Table 6, input terminals to output terminals
PIN_INSET_MM = 1.43  # isolated pin centre to board edge (U3.11 x1.98, edge 0.55)
WIDEST_MM = 12.90  # widest non-isolated part (U1, MSPM0G3507)
EDGE_MARGIN_MM = 0.55
BOARD_W_MM = 25.40


def min_width(widest, creepage, inset, margin):
    """Board width at which `widest` fits between two isolated rows."""
    return widest + 2 * (creepage + inset) + 2 * margin


def clearance_at(board_w, widest, inset, margin):
    """Horizontal gap from an isolated row to the centred part's edge."""
    usable = board_w - 2 * margin
    return (usable - widest) / 2 - inset


def y_offset_needed(creepage, dx):
    """Vertical offset that restores `creepage` when only `dx` exists in x."""
    if dx >= creepage:
        return 0.0
    return math.sqrt(creepage**2 - dx**2)


def main() -> int:
    """Answer the fits-beside question and price the alternative."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--creepage", type=float, default=CREEPAGE_MM)
    ap.add_argument("--inset", type=float, default=PIN_INSET_MM)
    ap.add_argument("--widest", type=float, default=WIDEST_MM)
    ap.add_argument("--margin", type=float, default=EDGE_MARGIN_MM)
    ap.add_argument(
        "--board-width", type=float, default=BOARD_W_MM, help="candidate width to test"
    )
    ap.add_argument(
        "--control-height",
        type=float,
        default=12.90,
        help="height the control band adds if it cannot sit beside",
    )
    a = ap.parse_args()

    need = min_width(a.widest, a.creepage, a.inset, a.margin)
    print(f"creepage required        {a.creepage:6.2f} mm")
    print(f"isolated pin inset       {a.inset:6.2f} mm from the board edge")
    print(f"widest non-isolated part {a.widest:6.2f} mm\n")
    print("MINIMUM BOARD WIDTH for that part to sit BETWEEN the isolated rows:")
    print(
        f"   {a.widest:.2f} + 2 x ({a.creepage} + {a.inset}) + 2 x {a.margin}"
        f" = {need:.2f} mm\n"
    )

    dx = clearance_at(a.board_width, a.widest, a.inset, a.margin)
    ok = dx >= a.creepage
    print(
        f"at the candidate width {a.board_width:.2f} mm -> dx = {dx:.2f} mm  "
        f"{'OK' if ok else 'FAILS'}"
    )
    if ok:
        print("   control sits alongside comms; no creepage band in the stack")
        return 0

    dy = y_offset_needed(a.creepage, max(dx, 0.0))
    cost = dy + a.control_height
    print(f"   the part must instead clear the isolated section in Y by {dy:.2f} mm,")
    print(
        f"   so the stack grows by {dy:.2f} (gap) + {a.control_height:.2f} "
        f"(its own height) = {cost:.2f} mm\n"
    )
    print(f"TRADE: widening to {need:.2f} mm buys back {cost:.2f} mm of length.")
    short = need - a.board_width
    print(
        f"   {short:.2f} mm of width for {cost:.2f} mm of length ({cost / short:.1f}x)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
