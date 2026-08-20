#!/usr/bin/env python3
"""Centre mirror-image part groups about the board's true centreline.

Governed by AGENTS.md. TODO.md 12.5.aq.

WHAT THE REPO OWNER ASKED FOR
------------------------------
"the middle phase should be centered on the board, and the distance between
the phases should be the same", and "as much as possible, the board should be
symetric left and right ... j5a and j5b should be centered across the
centerline" -- subject to the standing condition that it must not harm the
electrical, thermal, or scripted-build behaviour.

THE CENTRELINE IS x = 16.000, AND GETTING THAT RIGHT MATTERS
-------------------------------------------------------------
`GetBoardEdgesBoundingBox()` reports 32.100 mm, because it measures the OUTER
extent of the 0.05 mm Edge.Cuts stroke -- half a line width proud on each
side. The real outline via `GetBoardPolygonOutlines()` is **32.000 mm**, so the
centreline is exactly 16.000 and lands on the 0.5 mm grid.

Using the bounding box instead would have put the centreline at 16.050 and
pushed every symmetric pair 0.05 mm off-grid, trading one kind of tidiness for
another. This project has already been bitten once by that same 0.05 mm: pads
landed 0.02 mm short of the 0.5 mm edge rule when the stroke box was used for
edge clearance.

HOW A PAIR IS CENTRED
---------------------
For each mirror pair, both sides shift by the SAME delta, so their separation
is preserved exactly and only the midpoint moves onto the centreline. Nothing
is squeezed or stretched -- spacing the repo owner set by hand survives, and
creepage between the two halves of a pair is mathematically unchanged.

For the phase columns that yields the equal pitch directly: centring the A/C
pair and putting B on the centreline makes both gaps (C-A)/2 by construction,
rather than by choosing a pitch number.

WHAT IS DELIBERATELY NOT MIRRORED
----------------------------------
"As much as possible" is doing real work in the request. Left and right are
not the same circuit everywhere on this board, and forcing symmetry on parts
that are not mirror counterparts would be moving hardware to make a picture:

  * the left stack (R7/C4/C3, x 6.050) and right stack (R12/C10/R8/U2,
    x 24.050) are different circuits, not a mirrored pair -- their midpoint is
    15.05, and "fixing" that would drag four parts 1.9 mm for appearance.
  * U5/SH1/U1 are single central parts, already near centre; each is offered
    to the centreline individually and kept only if it costs nothing.
  * R2 rides with its phase column, so it lands 0.5 mm right of centre --
    the same offset R1 and R3 have from their own columns, mirrored. Centring
    R2 alone is offered as a separate move.

EVERY MOVE IS EARNED
--------------------
Same guard as `align_rows_columns.py`: apply -> refill -> score, and revert
unless DRC electrical stays 0, unconnected does not rise, creepage does not
fall (7.83 mm with only 0.33 mm of margin), the isolated lead stays within
10.0 mm, gate and commutation loops do not grow, and both isolation rules
still pass. Symmetry is cosmetic; none of those are.

Usage:
    python3 tools/symmetrize.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.aq.
# AI-generated. Centreline measured from the true board polygon; every pair
# shifts rigidly so no hand-set spacing is altered. Not human-authored.

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
SCORE = HERE / "score_placement.py"
BACKUP = Path("/tmp/claude-1000/sym_revert.kicad_pcb")

MAX_SHIFT_MM = 1.0  # beyond this it is a relayout, not a centring
TOL_MM = 0.05

# (label, left refs, right refs). Both sides shift by the same delta.
PAIRS = [
    (
        "phase A / phase C",
        ["U6", "Q1", "Q2", "J4A", "R1"],
        ["U7", "Q5", "Q6", "J4C", "R3"],
    ),
    ("pack terminals", ["J5A"], ["J5B"]),
    ("isolators", ["U3"], ["U4"]),
    ("comms connectors", ["J2"], ["J3"]),
    ("iso ferrites out", ["FB2"], ["FB4"]),
    ("iso ferrites in", ["FB1"], ["FB3"]),
    ("iso caps upper", ["C11"], ["C15"]),
    ("iso caps lower", ["C12"], ["C16"]),
    ("iso caps outer", ["C14"], ["C18"]),
    ("iso caps inner", ["C13"], ["C17"]),
]

# Groups that should sit ON the centreline.
CENTRED = [
    ("phase B", ["U8", "Q3", "Q4", "J4B", "R2"]),
    ("R2 alone", ["R2"]),
    ("U5 + shield", ["U5", "SH1"]),
    ("U1", ["U1"]),
]


def score():
    """The harness's verdict on the board as it stands."""
    out = subprocess.run(
        [sys.executable, str(SCORE), "--json"],
        capture_output=True,
        check=False,
        text=True,
    )
    return json.loads(out.stdout)


def centreline(board):
    """True board centre in x, from the outline polygon, not the stroke box."""
    poly = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(poly)
    bb = poly.BBox()
    return (bb.GetLeft() + bb.GetRight()) // 2


def shift(refs, delta):
    """Move every named footprint by delta in x, then refill."""
    board = pcbnew.LoadBoard(str(PCB))
    for ref in refs:
        fp = next((f for f in board.Footprints() if f.GetReference() == ref), None)
        if fp is None:
            continue
        p = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(p.x + delta, p.y))
    board.Save(str(PCB))
    board = pcbnew.LoadBoard(str(PCB))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    board.Save(str(PCB))


def ok(base, now):
    """Did this centring cost anything that matters?"""
    b, n = base["electrical"], now["electrical"]
    if n["drc_electrical"] != 0:
        return False, f"DRC electrical {n['drc_electrical']}"
    if n["unconnected"] > b["unconnected"]:
        return False, f"unconnected {b['unconnected']} -> {n['unconnected']}"
    if n["creepage_min_mm"] < b["creepage_min_mm"]:
        return False, (f"creepage {b['creepage_min_mm']} -> {n['creepage_min_mm']}")
    if not n["iso_lead_ok"]:
        return False, f"isolated lead {n['iso_lead_max_mm']}"
    if n["gate_loop_max_mm"] > b["gate_loop_max_mm"] + TOL_MM:
        return False, (f"gate loop {b['gate_loop_max_mm']} -> {n['gate_loop_max_mm']}")
    if n["commutation_max_mm"] > b["commutation_max_mm"] + TOL_MM:
        return False, (
            f"commutation {b['commutation_max_mm']} -> {n['commutation_max_mm']}"
        )
    r = now["rules"]
    if not (r["iso_ic_perpendicular"] and r["pack_layer_separated"]):
        return False, "isolation rule regressed"
    return True, ""


def group_x(board, refs):
    """The column a group sits on: the MEDIAN x, not the mean.

    The mean is wrong here, and quietly so. Phase B is U8/Q3/Q4/J4B all on
    x 15.550 plus R2 deliberately offset +0.5 to clear its FETs. The mean of
    those five is 15.650, so centring on the mean would have parked the
    column at 15.900 and called it centred -- 0.1 mm off, with R2's offset
    silently absorbed into the answer.

    The median ignores a minority offset and returns the column the group
    actually shares, which is what "centre this column" means.
    """
    xs = sorted(
        f.GetPosition().x for f in board.Footprints() if f.GetReference() in refs
    )
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) // 2


def main():
    """Centre each pair and group, keeping only what the numbers allow."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--dry-run", action="store_true", help="list the plan, change nothing"
    )
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    cx = centreline(board)
    print(
        f"true board centreline x = {pcbnew.ToMM(cx):.3f} mm "
        f"(outline polygon, not the stroke bbox)\n"
    )

    specs = [("pair", label, left, right) for label, left, right in PAIRS] + [
        ("centre", label, refs, None) for label, refs in CENTRED
    ]

    def delta_now(kind, left, right):
        """Recompute the shift against the board AS IT IS NOW.

        Deltas must not be snapshotted up front: these moves are applied in
        sequence, and centring phase B changes where R2 is before the "R2
        alone" job is reached. A stale delta would move R2 by the wrong
        amount and quietly leave it off centre.
        """
        b = pcbnew.LoadBoard(str(PCB))
        c = centreline(b)
        if kind == "pair":
            lx, rx = group_x(b, left), group_x(b, right)
            if lx is None or rx is None:
                return None, ""
            mid = (lx + rx) // 2
            return c - mid, f"midpoint {pcbnew.ToMM(mid):.3f}"
        gx = group_x(b, left)
        if gx is None:
            return None, ""
        return c - gx, f"at {pcbnew.ToMM(gx):.3f}"

    jobs = []
    for kind, label, left, right in specs:
        d, note = delta_now(kind, left, right)
        if d is None:
            continue
        jobs.append(
            (
                label,
                (left + right) if kind == "pair" else left,
                d,
                note,
                kind,
                left,
                right,
            )
        )

    plan = []
    for label, refs, delta, note, kind, left, right in jobs:
        mm = pcbnew.ToMM(delta)
        if abs(mm) < 0.0005:
            print(f"   {label:20s} already centred")
        elif abs(mm) > MAX_SHIFT_MM:
            print(
                f"   {label:20s} {note}, off by {mm:+.3f} mm -- "
                f"beyond {MAX_SHIFT_MM} mm, left alone"
            )
        else:
            plan.append((label, refs, mm, note, kind, left, right))

    print(f"\n{len(plan)} groups to centre:")
    for label, refs, mm, note, kind, left, right in plan:
        print(f"   {label:20s} {note}, shift {mm:+.3f} mm  ({len(refs)} parts)")

    if args.dry_run or not plan:
        if args.dry_run:
            print("\n--dry-run: nothing written")
        return 0

    base = score()
    e = base["electrical"]
    print(
        f"\nbaseline: creepage {e['creepage_min_mm']} "
        f"unconn {e['unconnected']} gate {e['gate_loop_max_mm']} "
        f"comm {e['commutation_max_mm']}"
    )

    kept, dropped = [], []
    for label, refs, _mm, _note, kind, left, right in plan:
        delta, _ = delta_now(kind, left, right)
        if delta is None or delta == 0:
            print(f"   SKIP   {label:20s} already centred")
            continue
        mm = pcbnew.ToMM(delta)
        if abs(mm) > MAX_SHIFT_MM:
            print(f"   SKIP   {label:20s} now {mm:+.3f} mm, out of range")
            continue
        shutil.copy2(PCB, BACKUP)
        shift(refs, delta)
        now = score()
        good, why = ok(base, now)
        if good:
            base = now
            kept.append((label, mm))
            print(f"   KEEP   {label:20s} {mm:+.3f} mm")
        else:
            shutil.copy2(BACKUP, PCB)
            dropped.append((label, mm, why))
            print(f"   REVERT {label:20s} {mm:+.3f} mm: {why}")

    f = score()["electrical"]
    print(f"\ncentred {len(kept)}, reverted {len(dropped)}")
    print(
        f"final: creepage {f['creepage_min_mm']} unconn {f['unconnected']} "
        f"gate {f['gate_loop_max_mm']} comm {f['commutation_max_mm']} "
        f"DRC-el {f['drc_electrical']}"
    )
    if dropped:
        print("\nleft off-centre on purpose -- the number said no:")
        for label, mm, why in dropped:
            print(f"   {label:20s} {mm:+.3f} mm: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


def grid_report():
    """Which mirror pairs have a half-separation off the 0.5 mm grid.

    Symmetry and grid alignment only coexist when a pair's separation is a
    whole number of millimetres: centring a pair splits its separation in
    half, so 8.500 mm apart becomes +/-4.250 -- symmetric, and off a 0.5 mm
    grid. Centring this board's pairs is what dropped grid adherence from
    83.1% to 44.1%.

    Rounding each half-separation to the nearest 0.5 mm restores both, at a
    cost of at most 0.25 mm per part, moving both sides equally so symmetry
    is preserved exactly.
    """
    board = pcbnew.LoadBoard(str(PCB))
    out = []
    for label, left, right in PAIRS:
        lx, rx = group_x(board, left), group_x(board, right)
        if lx is None or rx is None:
            continue
        half = pcbnew.ToMM((rx - lx) / 2.0)
        snapped = round(half * 2) / 2.0
        if abs(half - snapped) > 0.0005:
            out.append((label, left, right, half, snapped))
    return out
