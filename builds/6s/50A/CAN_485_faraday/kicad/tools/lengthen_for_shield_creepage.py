#!/usr/bin/env python3
"""Lengthen the board so the shield clears the isolated section's creepage.

Governed by AGENTS.md. Closes the SH1 half of TODO.md 12.5.ac.

THE CONSTRAINT
--------------
SH1, the WE-SHC 3670209 frame [51], is a GND conductor with a 22.2 x 16.6 mm
land -- 77.6 mm of non-isolated perimeter. [9] Table 6 requires 7.5 mm of
creepage between it and any isolated conductor. Measured before this change:

    lowest isolated copper   y 23.82  (C14.1 / C18.1, the owner's symmetric pair)
    SH1 top edge             y 25.80
    gap                        1.98 mm   against 7.5 required

A smaller can does not fix it. The can's contents measure 16.90 x 12.45 mm and
need a 13.45 mm cavity, so a ~15.2 mm-tall can would fit -- but shrinking with
the bottom fixed lifts the top edge only 1.40 mm. Lifting C14/C18 buys 2.40 mm
more, and FB4 another 0.81, after which the next isolated conductors are
U3.11 / U4.20 at y 20.61 -- the transceivers' own pins, which cannot move
without pushing the ICs into J2/J3 and the board edge. Every available move
totals 4.61 mm against a 5.52 mm requirement. The length is the only lever.

WHAT MOVES, AND WHY BY FUNCTION RATHER THAN BY COORDINATE
----------------------------------------------------------
A y-threshold cannot express this split. At any cut between the isolated
section's bottom (23.82) and SH1's top (25.80), Q1/Q3/Q5 land on the stationary
side (their courtyards start at 23.62/24.12) while Q2/Q4/Q6 move -- tearing
each half-bridge in two and destroying the commutation loop. So the set is
named explicitly: the isolated block and the pack terminals hold station, and
everything else translates.

Zones are handled per zone, translate versus extend, rather than by moving
every point below a line. An earlier attempt at this shape moved all zone
points below a midline, which STRETCHED the phase pours instead of translating
them and produced 28 clearance and 17 solder-mask-bridge violations. A pour
tied to parts that move must move with them; a plane that spans the board only
grows at the new edge.

Usage:
    python3 tools/lengthen_for_shield_creepage.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.ac.
# AI-generated; every coordinate measured off the board. Not human-authored.

import argparse
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-lengthen.bak")

SHIFT = 6.00  # 5.52 required; 6.00 keeps the 0.5 mm grid and adds margin
SPLIT = 24.50  # between the isolated bottom (23.82) and SH1's top (25.80)

# Hold station: the isolated block plus the pack terminals.
STATIONARY = (
    {"J2", "J3", "U3", "U4", "J5A", "J5B"}
    | {f"C{n}" for n in range(11, 19)}
    | {f"FB{n}" for n in range(1, 5)}
)
# Assert these actually translate -- they are what the change is about.
MUST_MOVE = {"SH1", "U5", "U1", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "J4A", "J4B", "J4C"}


def origin(board):
    """Top-left of the board outline."""
    box = board.GetBoardEdgesBoundingBox()
    return box.GetLeft(), box.GetTop()


def main() -> int:
    """Extend the outline, translate the power/control block, fix the zones."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    _, oy = origin(board)
    d = pcbnew.FromMM(SHIFT)
    split = oy + pcbnew.FromMM(SPLIT)
    mid = oy + pcbnew.FromMM(30.0)

    print(f"1. extending Edge.Cuts downward by {SHIFT} mm")
    n = 0
    for g in board.GetDrawings():
        if g.GetLayer() != pcbnew.Edge_Cuts:
            continue
        touched = False
        for get, set_ in ((g.GetStart, g.SetStart), (g.GetEnd, g.SetEnd)):
            p = get()
            if p.y > mid:
                set_(pcbnew.VECTOR2I(p.x, p.y + d))
                touched = True
        if g.GetShape() == pcbnew.SHAPE_T_ARC:
            c = g.GetCenter()
            if c.y > mid:
                g.SetCenter(pcbnew.VECTOR2I(c.x, c.y + d))
                touched = True
        n += touched
    print(f"   {n} outline elements moved")

    print(f"\n2. translating the power/control block by {SHIFT} mm")
    moved, held = [], []
    for f in board.Footprints():
        ref = f.GetReference()
        if ref in STATIONARY:
            held.append(ref)
            continue
        p = f.GetPosition()
        f.SetPosition(pcbnew.VECTOR2I(p.x, p.y + d))
        moved.append(ref)
    print(f"   moved {len(moved)}, held {len(held)}")
    missing = MUST_MOVE - set(moved)
    if missing:
        raise SystemExit(f"these had to move and did not: {sorted(missing)}")
    print(f"   verified: {', '.join(sorted(MUST_MOVE))} all translated")

    print("\n3. zones -- translate those tied to moved parts, extend the planes")
    for z in board.Zones():
        o = z.Outline()
        top = o.BBox().GetTop()
        whole = top >= split  # sits entirely in the moving region
        label = "translate" if whole else "extend"
        for i in range(o.OutlineCount()):
            ol = o.Outline(i)
            for k in range(ol.PointCount()):
                pt = ol.CPoint(k)
                if whole or pt.y > split:
                    ol.SetPoint(k, pcbnew.VECTOR2I(pt.x, pt.y + d))
        name = z.GetNetname() or "(keepout)"
        print(f"   {name:10s} {label}")

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    nb = board.GetBoardEdgesBoundingBox()
    print(
        f"\nboard now {pcbnew.ToMM(nb.GetWidth()) - 0.1:.2f} x "
        f"{pcbnew.ToMM(nb.GetHeight()) - 0.1:.2f} mm"
    )

    if args.dry_run:
        print("--dry-run: nothing written")
        return 0
    shutil.copy2(PCB, BACKUP)
    board.Save(str(PCB))
    print(f"saved (backup: {BACKUP.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
