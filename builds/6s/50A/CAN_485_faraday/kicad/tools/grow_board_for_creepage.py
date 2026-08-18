#!/usr/bin/env python3
"""Lengthen the board so the isolation barrier can meet its rated creepage.

Governed by AGENTS.md. Closes the geometry half of TODO.md 12.5.ac.

WHY THE BOARD GROWS
-------------------
[9] Table 6 requires **7.5 mm external clearance and 7.5 mm creepage, input
terminals to output terminals**, with the explicit footnote that "Consideration
must be given to pad layout to ensure the minimum required distance for
clearance is maintained." The board was undercutting it at 3.49 mm.

The repo owner rotated U3 and U4 so both isolated rows now face the board
edges (U3 at x 1.98, U4 at x 23.75) with the non-isolated rows inboard. That
is the right structure, but it leaves no legal home for U1:

    isolated conductors at x 1.98 and x 23.75
    7.5 mm exclusion each side leaves x 9.48..16.25 = 6.77 mm
    U1 is 13.45 mm wide                            -> cannot fit between them

So U1 has to clear the isolated section in Y rather than beside it. Centred,
U1 spans x 6.02..19.47; the binding pad is then U3.11 at (1.98, 21.32) with
dx = 4.04 mm, so U1's top must sit at y >= 27.63 -- a 4.76 mm move down from
22.88. Everything below it follows, and SH1 cannot absorb that because it is
locked directly under the FETs for the shortest gate loop.

Rounded up to a 4.80 mm shift, the board goes 60.20 -> 65.00 mm.

WHY NOT JUST RELAX THE CREEPAGE
--------------------------------
7.5 mm is the ADM2582E's rating for full 5 kV reinforced isolation, and a
lower system working voltage would permit far less under IEC 60664-1. That
option was put to the repo owner and **rejected, with reason**: this board
exists to survive harsh EMI environments -- which is also why it carries the
Faraday shield and two redundant control paths (CAN-FD and RS-485
concurrently). Weakening the isolation to save 3 mm would defeat the design
intent. Recorded here so the trade is not silently revisited later.

WHAT THIS SCRIPT DOES
---------------------
1. Extends Edge.Cuts: every outline point below the board's midline moves
   down 4.80 mm, preserving the 2 mm corner arcs.
2. Centres U1 horizontally (its own move is what the 4.76 mm figure assumes).
3. Shifts every footprint at or below U1's old top down 4.80 mm, so the whole
   control/power stack keeps its relative geometry.
4. Extends every zone that reached the old bottom edge.
5. Parks the twelve isolated-supply parts (FB1-FB4, C11-C18) off-board. They
   were already 0-of-12 outside [9]'s 10 mm lead-length limit, and this move
   redefines the space they are meant to occupy, so carrying their current
   positions forward would be carrying forward a wrong answer.

Usage:
    python3 tools/grow_board_for_creepage.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-18, TODO.md 12.5.ac.
# AI-generated; every coordinate is measured off the board. Not human-authored.

import argparse
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-grow.bak")

SHIFT = 4.80              # mm, from the creepage arithmetic above
MIDLINE = 30.0            # anything below this on Edge.Cuts moves
# Everything at or below this shifts with U1. Deliberately set 0.9 mm ABOVE
# U1's actual bounding-box top (22.88) rather than equal to it: the first run
# used 22.88 exactly, and U1's own top compares as 22879999 nm against
# FromMM(22.88) = 22880000 nm, so U1 failed its own test and stayed put while
# everything below it moved 4.8 mm down. Never put a shift threshold on a
# part's exact edge.
U1_OLD_TOP = 22.00
USABLE_L, USABLE_W = 0.55, 24.40
PARK = ["FB1", "FB2", "FB3", "FB4"] + [f"C{n}" for n in range(11, 19)]
PARK_X, PARK_Y0, PARK_DY = 32.0, 6.0, 4.0


def origin(board):
    """Top-left of the board outline."""
    box = board.GetBoardEdgesBoundingBox()
    return box.GetLeft(), box.GetTop()


def courtyard_top(f):
    """Y of a footprint's courtyard top, board-local."""
    p = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd)
    box = p.BBox() if p.OutlineCount() else f.GetBoundingBox(False, False)
    return box.GetTop()


def main() -> int:
    """Grow the outline, centre U1, shift the stack, extend the zones."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    ox, oy = origin(board)
    d = pcbnew.FromMM(SHIFT)
    mid = oy + pcbnew.FromMM(MIDLINE)
    old_top = oy + pcbnew.FromMM(U1_OLD_TOP)

    def drop(pt):
        return pcbnew.VECTOR2I(pt.x, pt.y + d) if pt.y > mid else pt

    print(f"1. extending Edge.Cuts by {SHIFT} mm")
    n = 0
    for g in board.GetDrawings():
        if g.GetLayer() != pcbnew.Edge_Cuts:
            continue
        moved = False
        for get, set_ in ((g.GetStart, g.SetStart), (g.GetEnd, g.SetEnd)):
            p = get()
            if p.y > mid:
                set_(drop(p))
                moved = True
        if g.GetShape() == pcbnew.SHAPE_T_ARC:
            c = g.GetCenter()
            if c.y > mid:
                g.SetCenter(drop(c))
                moved = True
        n += moved
    print(f"   {n} outline elements moved")

    print(f"\n2. centring U1 and shifting the stack down {SHIFT} mm")
    u1 = next(f for f in board.Footprints() if f.GetReference() == "U1")
    cy = u1.GetCourtyard(pcbnew.B_CrtYd if u1.IsFlipped() else pcbnew.F_CrtYd)
    bx = cy.BBox() if cy.OutlineCount() else u1.GetBoundingBox(False, False)
    w = pcbnew.ToMM(bx.GetWidth())
    dx = pcbnew.FromMM(USABLE_L + (USABLE_W - w) / 2) - (bx.GetLeft() - ox)
    u1_y0 = pcbnew.ToMM(u1.GetPosition().y - oy)
    print(f"   U1 is {w:.2f} mm wide; centring moves it {pcbnew.ToMM(dx):+.2f} mm in x")

    parked, shifted = 0, 0
    for f in board.Footprints():
        ref = f.GetReference()
        if ref in PARK:
            i = PARK.index(ref)
            f.SetPosition(pcbnew.VECTOR2I(
                ox + pcbnew.FromMM(PARK_X),
                oy + pcbnew.FromMM(PARK_Y0 + i * PARK_DY)))
            parked += 1
            continue
        if courtyard_top(f) >= old_top:
            p = f.GetPosition()
            f.SetPosition(pcbnew.VECTOR2I(p.x + (dx if ref == "U1" else 0),
                                          p.y + d))
            shifted += 1
    print(f"   {shifted} footprints shifted, {parked} isolated-group parts parked off-board")
    # Assert the part the whole calculation is about actually moved.
    u1_now = pcbnew.ToMM(u1.GetPosition().y - oy)
    if abs(u1_now - (u1_y0 + SHIFT)) > 0.001:
        raise SystemExit(f"U1 did not shift: y {u1_y0:.2f} -> {u1_now:.2f}, "
                         f"expected {u1_y0 + SHIFT:.2f}")
    print(f"   U1 verified: y {u1_y0:.2f} -> {u1_now:.2f}")

    print("\n3. extending zones that reached the old bottom")
    z = 0
    for zone in board.Zones():
        o = zone.Outline()
        touched = False
        for i in range(o.OutlineCount()):
            ol = o.Outline(i)
            for k in range(ol.PointCount()):
                p = ol.CPoint(k)
                if p.y > mid:
                    ol.SetPoint(k, pcbnew.VECTOR2I(p.x, p.y + d))
                    touched = True
        z += touched
    print(f"   {z} zones extended")

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
