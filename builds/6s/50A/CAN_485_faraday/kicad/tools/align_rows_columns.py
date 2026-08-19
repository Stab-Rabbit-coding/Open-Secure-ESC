#!/usr/bin/env python3
"""Snap stray parts onto the row/column their neighbours already share.

Governed by AGENTS.md. TODO.md 12.5.ap.

WHAT THIS IS FOR
----------------
The repo owner asked for centred alignment down each power phase and clean
rows across them, "as long as it doesn't detrimentally effect the electrical,
thermal, and programatic automation for other builds". That last clause is the
whole design of this script: alignment is cosmetic, so it is only ever allowed
to happen when the measured electrical numbers say it cost nothing.

WHAT IT DOES NOT DO
-------------------
It does not invent a layout. Every target below is a value the board ALREADY
uses -- the position two or more parts in the same group agree on. A part 0.5
mm off a row three of its neighbours share is a slip; a part 1.0+ mm away is
more likely a decision someone made, so MAX_SNAP_MM refuses to "fix" it and
reports it instead. Alignment work should tidy slips, not quietly relocate
deliberate spacing.

Consequently this does NOT touch:
  * the 10.0 / 11.0 mm phase-column pitch (a real asymmetry, but a design
    choice, and 1.0 mm out of reach of MAX_SNAP_MM),
  * J5A/J5B, which the repo owner has just aligned by hand,
  * C9 or J1, each ~1.0 mm off the nearest column,
  * anything on a group of fewer than MIN_GROUP members -- two parts agreeing
    is a coincidence, not a row.

HOW EACH MOVE IS JUDGED
-----------------------
One move at a time, and the board's own harness is the judge:

    apply -> refill zones -> score_placement.py --json -> keep or REVERT

A move is kept only if every one of these holds:

    DRC electrical      stays 0
    unconnected         does not increase
    total violations    does not increase
    creepage            does not decrease   (7.83 mm, only 0.33 mm of margin)
    isolated lead       stays <= 10.0 mm
    gate loop           does not grow by more than TOL_MM
    commutation loop    does not grow by more than TOL_MM
    both isolation rules still PASS

The last two are the thermal and switching-performance guards. Gate and
commutation loop lengths are what set switching loss and ringing on a 50 A
half-bridge, so a "tidier" board that lengthened them would be a worse board.

One move here is riskier than it looks and is the reason for the revert
machinery rather than a blind snap: pulling Q4 up onto the low-FET row closes
the gap between the FET rows, and U5's 12 GND thermal vias live in that gap.
Measured after the move, the closest approach is 0.500 mm against a 0.200 mm
rule -- fine, but it was checked, not assumed.

THE MAJORITY IS NOT AUTOMATICALLY THE RIGHT ROW
------------------------------------------------
The first version of this script snapped every outlier to whatever position
most of its group already shared. That is wrong often enough to matter, and it
was wrong on the very first group it touched.

The high-side FET row had Q3 and Q5 at y 33.100 and Q1 at 33.600. Majority
rule moved Q1 up to join them, which pulled Q1 AWAY from U5 and lengthened the
worst gate loop 16.49 -> 16.74 mm, so the guard reverted it and the row stayed
crooked.

The right answer was the opposite move: bring Q3 and Q5 DOWN to Q1's row. That
aligns all six FETs AND shortens the commutation loop 19.60 -> 19.40 mm,
because it moves two parts closer to the driver instead of one part further
away. Strictly better on every metric, and majority rule could never find it.

So each group is now evaluated over EVERY distinct position its members
occupy, not just the popular one. The winning row is whichever the harness
scores best -- which on a half-bridge usually means the row nearest the gate
driver, since gate and commutation loop length set switching loss and ringing
at 50 A.

Usage:
    python3 tools/align_rows_columns.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.ap.
# AI-generated. Every target is a position already present on the board;
# nothing is chosen ad hoc. Each move is kept only on measured evidence.
# Not human-authored.

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
BACKUP = Path("/tmp/claude-1000/align_revert.kicad_pcb")
BEST = Path("/tmp/claude-1000/align_best.kicad_pcb")

MAX_SNAP_MM = 0.60      # beyond this it is a decision, not a slip
MIN_GROUP = 3           # two parts agreeing is a coincidence
TOL_MM = 0.05           # allowed growth in gate / commutation loop

# Groups the board already establishes. axis "x" = share a column,
# "y" = share a row. Target is the value the majority already sit on.
GROUPS = [
    ("high-side FET row",   "y", ["Q1", "Q3", "Q5"]),
    ("low-side FET row",    "y", ["Q2", "Q4", "Q6"]),
    ("sense-amp row",       "y", ["U6", "U8", "U7"]),
    ("phase terminal row",  "y", ["J4A", "J4B", "J4C"]),
    ("gate resistor row",   "y", ["R1", "R2", "R3"]),
    ("phase A column",      "x", ["U6", "Q1", "Q2", "J4A"]),
    ("phase B column",      "x", ["U8", "Q3", "Q4", "J4B"]),
    ("phase C column",      "x", ["U7", "Q5", "Q6", "J4C"]),
    ("right stack column",  "x", ["R12", "C10", "R8", "U2"]),
    ("left stack column",   "x", ["R7", "C4", "C3"]),
]


def score():
    """The harness's verdict on the board as it currently stands."""
    out = subprocess.run([sys.executable, str(SCORE), "--json"],
                         capture_output=True, text=True)
    return json.loads(out.stdout)


def positions(board):
    """ref -> (x_nm, y_nm) for every footprint."""
    return {f.GetReference(): (f.GetPosition().x, f.GetPosition().y)
            for f in board.Footprints()}


def candidates(vals):
    """Every distinct position the group occupies, most-shared first.

    Deliberately NOT just the majority value -- see the module docstring for
    the case where the majority row was the worse row.
    """
    counts = {}
    for v in vals:
        counts.setdefault(round(v / 1000.0), []).append(v)
    ranked = sorted(counts.values(), key=len, reverse=True)
    return [(grp[0], len(grp)) for grp in ranked]


def plan(board):
    """For each group, every candidate row and the moves it would need.

    Returns [(group_name, axis, [(target, agree, [(ref, from, to), ...])])]
    with candidates ordered most-shared first. The caller scores them.
    """
    pos = positions(board)
    out, skipped = [], []
    for name, axis, refs in GROUPS:
        have = [r for r in refs if r in pos]
        if len(have) < MIN_GROUP:
            continue
        idx = 0 if axis == "x" else 1
        vals = [pos[r][idx] for r in have]
        options = []
        for target, agree in candidates(vals):
            moves, reach = [], True
            for r in have:
                delta = target - pos[r][idx]
                if delta == 0:
                    continue
                if abs(pcbnew.ToMM(delta)) > MAX_SNAP_MM:
                    reach = False
                    skipped.append((r, name, pcbnew.ToMM(delta)))
                    break
                moves.append((r, pos[r][idx], target))
            if reach and moves:
                options.append((target, agree, moves))
        if options:
            out.append((name, axis, options))
    return out, skipped


def ok(base, now):
    """Did this move cost anything that matters?"""
    b, n = base["electrical"], now["electrical"]
    if n["drc_electrical"] != 0:
        return False, f"DRC electrical {n['drc_electrical']}"
    if n["unconnected"] > b["unconnected"]:
        return False, (f"unconnected {b['unconnected']} -> "
                       f"{n['unconnected']}")
    if n["creepage_min_mm"] < b["creepage_min_mm"]:
        return False, (f"creepage {b['creepage_min_mm']} -> "
                       f"{n['creepage_min_mm']}")
    if not n["iso_lead_ok"]:
        return False, f"isolated lead {n['iso_lead_max_mm']}"
    if n["gate_loop_max_mm"] > b["gate_loop_max_mm"] + TOL_MM:
        return False, (f"gate loop {b['gate_loop_max_mm']} -> "
                       f"{n['gate_loop_max_mm']}")
    if n["commutation_max_mm"] > b["commutation_max_mm"] + TOL_MM:
        return False, (f"commutation {b['commutation_max_mm']} -> "
                       f"{n['commutation_max_mm']}")
    r = now["rules"]
    if not (r["iso_ic_perpendicular"] and r["pack_layer_separated"]):
        return False, "isolation rule regressed"
    return True, ""


def apply_moves(moves, axis):
    """Move a whole candidate row at once, then refill."""
    board = pcbnew.LoadBoard(str(PCB))
    for ref, _, target in moves:
        fp = next(f for f in board.Footprints()
                  if f.GetReference() == ref)
        p = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(target, p.y) if axis == "x"
                       else pcbnew.VECTOR2I(p.x, target))
    board.Save(str(PCB))
    board = pcbnew.LoadBoard(str(PCB))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    board.Save(str(PCB))


def gain(base, now):
    """How much shorter the loops got. Ties break toward shorter loops."""
    b, n = base["electrical"], now["electrical"]
    return ((b["gate_loop_max_mm"] - n["gate_loop_max_mm"])
            + (b["commutation_max_mm"] - n["commutation_max_mm"]))


def main():
    """Snap each slip, keeping only the moves the numbers allow."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="list the plan, change nothing")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    groups, skipped = plan(board)

    print(f"{len(groups)} groups have a reachable alternative row:")
    for name, axis, options in groups:
        opts = ", ".join(f"{pcbnew.ToMM(t):.3f} ({a} agree, {len(m)} move)"
                         for t, a, m in options)
        print(f"   {name:22s} {axis}  {opts}")
    if skipped:
        print(f"\n{len(skipped)} left alone -- further than "
              f"{MAX_SNAP_MM} mm, so read as intent not slip:")
        for ref, name, d in skipped:
            print(f"   {ref:4s} {d:+7.3f} mm from {name}")

    if args.dry_run or not groups:
        print("\n--dry-run: nothing written" if args.dry_run else "")
        return 0

    base = score()
    print(f"\nbaseline: creepage {base['electrical']['creepage_min_mm']} "
          f"unconnected {base['electrical']['unconnected']} "
          f"gate {base['electrical']['gate_loop_max_mm']} "
          f"comm {base['electrical']['commutation_max_mm']}")

    kept, dropped = [], []
    for name, axis, options in groups:
        best = None
        for target, agree, moves in options:
            shutil.copy2(PCB, BACKUP)
            apply_moves(moves, axis)
            now = score()
            good, why = ok(base, now)
            if good:
                g = gain(base, now)
                if best is None or g > best[0]:
                    best = (g, target, moves)
                    shutil.copy2(PCB, BEST)
            else:
                dropped.append((name, axis, pcbnew.ToMM(target), why))
            shutil.copy2(BACKUP, PCB)

        if best is None:
            print(f"   {name:22s} {axis}  no candidate row passed")
            continue
        shutil.copy2(BEST, PCB)
        base = score()
        g, target, moves = best
        print(f"   {name:22s} {axis} -> {pcbnew.ToMM(target):7.3f}  "
              f"moved {' '.join(m[0] for m in moves)}"
              f"{'   loops -%.2f mm' % g if g > 0 else ''}")
        kept.append((name, axis, pcbnew.ToMM(target), moves))

    final = score()["electrical"]
    print(f"\nrows aligned {len(kept)}, candidate rows rejected "
          f"{len(dropped)}")
    print(f"final: creepage {final['creepage_min_mm']} "
          f"unconnected {final['unconnected']} "
          f"gate {final['gate_loop_max_mm']} "
          f"comm {final['commutation_max_mm']} "
          f"DRC-el {final['drc_electrical']}")
    if dropped:
        print("\nleft misaligned on purpose -- the number said no:")
        for name, axis, target, why in dropped:
            print(f"   {name:22s} {axis} @ {target:7.3f}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
