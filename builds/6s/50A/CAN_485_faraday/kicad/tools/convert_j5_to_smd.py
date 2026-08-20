#!/usr/bin/env python3
"""Make the pack terminals SMD on F.Cu so they leave the isolated section's plane.

Governed by AGENTS.md. Closes the pack half of TODO.md 12.5.ac.

WHY THIS WORKS
--------------
Creepage is a SURFACE measure -- the shortest path along insulating material
between two conductors. Every isolated part on this board (U3, U4, J2, J3 and
the C11-C18 / FB1-FB4 support columns) sits on B.Cu. As long as the pack
terminals carry no copper on B.Cu, the two never share a surface, and the only
remaining path runs over the board edge.

That edge path is NOT zero, and it is what makes this a real design rather
than a loophole:

    path = (F.Cu inset from the edge) + board thickness + (B.Cu inset)

C12 sits 0.83 mm in from the outline on B.Cu, so with a 1.6 mm board the F.Cu
copper opposite it must be inset at least 7.5 - 1.6 - 0.83 = 5.07 mm. A
full-width F.Cu pour running past the isolated section would measure 2.93 mm
and fail. The pours are therefore notched.

WHAT THIS CHANGES

1. J5A/J5B become SMD on F.Cu -- the 7.0 x 7.0 mm land stays, the 4.4 mm
   barrel goes. They already sit at x 8.60..15.60 and 17.10..24.10, inside the
   5.12..26.88 mm window, so neither moves.
2. The F.Cu VM and GND pours are notched to that window for the depth of the
   isolated section, then open to full width below it.

WHAT IT COSTS, AND WHAT MUST FOLLOW
------------------------------------
The PTH barrel was doing two jobs this does not:

  * It tied F.Cu VM to the In2 VM plane, and F.Cu GND to In1, for free. Those
    now need via fields, and a through via reaches B.Cu, so it must itself sit
    7.5 mm clear of isolated copper -- i.e. at y >= 31.32. Until those exist,
    the In2 VM plane is an orphan and the unconnected count reflects it.
  * It keyed a 6 mm^2 pack wire mechanically. An SMD pad relies on the solder
    joint alone. On a vibrating airframe carrying the full pack current, that
    is a real reliability change and needs strain relief designed in --
    TODO.md 12.5.k already tracks the same issue for J2/J3, and this is the
    larger version of it.

Usage:
    python3 tools/convert_j5_to_smd.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.ac.
# AI-generated; geometry measured off the board. Not human-authored.

import argparse
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-smd.bak")

ISO_BOTTOM = 23.82  # lowest isolated copper, all of it on B.Cu
NOTCH_TO = 24.50  # notch the F.Cu pours down to here
INSET = 5.12  # 7.5 - 1.6 board - 0.83 (C12's own inset), rounded up
RIGHT = 26.88


def origin(board):
    """Top-left of the board outline."""
    box = board.GetBoardEdgesBoundingBox()
    return box.GetLeft(), box.GetTop()


def main() -> int:
    """Convert the pads, then notch the F.Cu pours clear of the isolated face."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    ox, oy = origin(board)

    print("1. J5A/J5B -> SMD on F.Cu")
    for ref in ("J5A", "J5B"):
        f = next(q for q in board.Footprints() if q.GetReference() == ref)
        for p in f.Pads():
            before = pcbnew.ToMM(p.GetDrillSizeX())
            p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            p.SetDrillSize(pcbnew.VECTOR2I(0, 0))
            ls = pcbnew.LSET()
            ls.AddLayer(pcbnew.F_Cu)
            ls.AddLayer(pcbnew.F_Mask)
            ls.AddLayer(pcbnew.F_Paste)
            p.SetLayerSet(ls)
            print(
                f"   {ref}.{p.GetNumber()} [{p.GetNetname()}] "
                f"{pcbnew.ToMM(p.GetSizeX()):.2f} x {pcbnew.ToMM(p.GetSizeY()):.2f} mm, "
                f"drill {before:.2f} -> none, F.Cu only"
            )

    print(f"\n2. notching the F.Cu pours to x {INSET}..{RIGHT} above y {NOTCH_TO}")
    for z in board.Zones():
        if z.GetIsRuleArea() or not z.IsOnLayer(pcbnew.F_Cu):
            continue
        if z.GetNetname() not in ("VM", "GND"):
            continue
        o = z.Outline()
        bx = o.BBox()
        top = pcbnew.ToMM(bx.GetTop() - oy)
        bot = pcbnew.ToMM(bx.GetBottom() - oy)
        left = pcbnew.ToMM(bx.GetLeft() - ox)
        right = pcbnew.ToMM(bx.GetRight() - ox)
        if top > ISO_BOTTOM:
            print(
                f"   {z.GetNetname():4s} starts below the isolated section, untouched"
            )
            continue
        pts = [
            (INSET, top),
            (RIGHT, top),
            (RIGHT, NOTCH_TO),
            (right, NOTCH_TO),
            (right, bot),
            (left, bot),
            (left, NOTCH_TO),
            (INSET, NOTCH_TO),
        ]
        o.RemoveAllContours()
        o.NewOutline()
        for x, y in pts:
            o.Append(ox + pcbnew.FromMM(x), oy + pcbnew.FromMM(y))
        print(
            f"   {z.GetNetname():4s} notched: full width below y {NOTCH_TO}, "
            f"x {INSET}..{RIGHT} above it"
        )

    if not args.dry_run:
        shutil.copy2(PCB, BACKUP)
        board.Save(str(PCB))

    # Refill from a clean load -- ZONE_FILLER is unreliable after in-memory
    # outline edits (seen twice on this board).
    board = pcbnew.LoadBoard(str(PCB))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    print(
        f"\nunconnected: {board.GetConnectivity().GetUnconnectedCount(False)}"
        "  (In2 VM plane is orphaned until the via fields are added)"
    )
    if args.dry_run:
        print("--dry-run: nothing written")
        return 0
    board.Save(str(PCB))
    print(f"saved (backup: {BACKUP.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
