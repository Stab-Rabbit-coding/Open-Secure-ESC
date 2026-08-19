#!/usr/bin/env python3
"""Move colliding reference designators off pads and off each other.

Governed by AGENTS.md. Closes TODO.md 12.5.u, which the repo owner deferred
until after routing ("silkscreen can wait till after routing", 2026-08-16).
Routing has run, so this is unblocked.

THE VIOLATIONS
--------------
53 warnings, and they are almost entirely one thing:

    35 x silk_over_copper   "Silkscreen clipped by solder mask"
    18 x silk_overlap       "Silkscreen overlap"

Grouped by what is actually colliding, 31 of the 35 are `Reference field of
<ref>` -- a reference designator sitting on a mask aperture. The other 4 are
segments of SH1's own frame outline crossing its pads. None is electrical.
All of them degrade the assembly drawing, which is what silkscreen is for: a
designator printed across a pad is clipped at fab and becomes unreadable
exactly where someone is trying to identify a part.

WHAT THIS DOES
--------------
Reference text only. It does not move a single component, and it does not
touch copper -- CLAUDE.md reserves footprint repositioning for the repo owner,
and this board is tightly packed enough that the rule matters.

The offender list comes from kicad-cli's own DRC report, and ONLY from there.
An earlier version of this script decided for itself which designators
collided, using the same bounding-box test it uses to search for free space.
That test is far coarser than KiCad's shape-level check, so it found 46
"collisions" where DRC saw 15, moved all 46 every run, and never converged --
each pass shuffled forty-odd designators away from their parts without the
violation count changing at all. Churn that does not reduce the number is not
progress, and scattering a designator from its own part is its own
documentation failure.

So the loop is now: ask DRC who is actually violating, move only those, ask
DRC again, and stop as soon as a pass fails to improve the count.

The bounding-box test survives only as the SEARCH heuristic -- a cheap way to
propose a candidate position. DRC remains the judge of whether the move
worked.

For each colliding designator it searches outward from the text's current
position in 0.25 mm steps and takes the nearest position that clears:

  * every mask aperture (pad) on that side of the board,
  * every silk item already placed, including designators moved earlier in
    this same pass,
  * the board outline, inset by the 0.5 mm `min_copper_edge_clearance`.

Nearest-first matters. A designator that has wandered 4 mm from its part is a
different documentation failure from one printed over a pad, so the search
prefers the smallest move that resolves the collision rather than the first
empty space it stumbles into.

WHAT IT DOES NOT DO
-------------------
Designators it cannot place are REPORTED, not hidden and not shrunk below the
`min_text_height = 0.8 mm` floor in `.kicad_pro`. Silkscreen that cannot fit
is a placement fact about a dense board, and quietly making the text invisible
would convert a visible warning into an invisible documentation gap.

SH1's four outline segments are likewise reported rather than deleted. They
are part of a footprint's own graphics, and trimming a shield frame's outline
is a judgement about what the assembly drawing should show -- referred to the
repo owner per CLAUDE.md.

Usage:
    python3 tools/tidy_silkscreen.py [--max-search MM] [--max-rounds N]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.u.
# AI-generated. Collision set is taken from kicad-cli's own DRC report; the
# search is nearest-first and reports its failures. Not human-authored.

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"

STEP_MM = 0.25
EDGE_INSET_MM = 0.5
SILK = (pcbnew.F_SilkS, pcbnew.B_SilkS)


def grow(box, mm):
    """A copy of box expanded by mm on every side."""
    out = pcbnew.BOX2I(box.GetOrigin(), box.GetSize())
    out.Inflate(pcbnew.FromMM(mm))
    return out


def obstacles(board, side_front):
    """Mask apertures on this side, as boxes the text must avoid."""
    layer = pcbnew.F_Mask if side_front else pcbnew.B_Mask
    out = []
    for fp in board.Footprints():
        for pad in fp.Pads():
            if pad.IsOnLayer(layer):
                out.append(pad.GetBoundingBox())
    return out


def silk_items(board, side_front):
    """Every silk graphic and designator on this side, with its box."""
    layer = pcbnew.F_SilkS if side_front else pcbnew.B_SilkS
    out = []
    for fp in board.Footprints():
        for g in fp.GraphicalItems():
            if g.GetLayer() == layer:
                out.append((g, g.GetBoundingBox()))
        ref = fp.Reference()
        if ref.GetLayer() == layer and ref.IsVisible():
            out.append((ref, ref.GetBoundingBox()))
    for d in board.GetDrawings():
        if d.GetLayer() == layer:
            out.append((d, d.GetBoundingBox()))
    return out


def spiral(step_nm, limit_nm):
    """Candidate offsets, nearest first."""
    out = []
    n = int(limit_nm // step_nm)
    for ring in range(1, n + 1):
        for i in range(-ring, ring + 1):
            for j in (-ring, ring):
                out.append((i * step_nm, j * step_nm))
                out.append((j * step_nm, i * step_nm))
    seen, uniq = set(), []
    for d in out:
        if d not in seen:
            seen.add(d)
            uniq.append(d)
    uniq.sort(key=lambda d: d[0] * d[0] + d[1] * d[1])
    return uniq


def drc_silk_offenders(pcb_path):
    """(count, refs) -- silk violations and whose designator is at fault.

    The authority on what is violating is kicad-cli, not this script.
    """
    out = Path(tempfile.gettempdir()) / "tidy_silk_drc.json"
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all",
                    "--format", "json", "-o", str(out), str(pcb_path)],
                   capture_output=True, check=False)
    if not out.is_file():
        return -1, set()
    data = json.loads(out.read_text())
    viol = [v for v in data.get("violations", [])
            if v["type"].startswith("silk")]
    refs = set()
    for v in viol:
        for item in v.get("items", []):
            desc = item.get("description", "")
            if desc.startswith("Reference field of "):
                refs.add(desc[len("Reference field of "):].strip())
    return len(viol), refs


def relocate(board, wanted, offsets, edge):
    """Move each named designator to the nearest position clearing the
    bounding-box model. Returns (moved, stuck)."""
    moved, stuck = [], []
    for side_front in (True, False):
        pads = obstacles(board, side_front)
        others = silk_items(board, side_front)
        layer = pcbnew.F_SilkS if side_front else pcbnew.B_SilkS

        for fp in board.Footprints():
            if fp.GetReference() not in wanted:
                continue
            ref = fp.Reference()
            if ref.GetLayer() != layer or not ref.IsVisible():
                continue

            def clashes(box):
                if not edge.Contains(box):
                    return True
                for p in pads:
                    if box.Intersects(p):
                        return True
                for item, ibox in others:
                    if item is ref:
                        continue
                    if box.Intersects(ibox):
                        return True
                return False

            start = ref.GetPosition()
            placed = None
            for dx, dy in offsets:
                ref.SetPosition(pcbnew.VECTOR2I(start.x + dx, start.y + dy))
                if not clashes(ref.GetBoundingBox()):
                    placed = (dx, dy)
                    break
            if placed is None:
                ref.SetPosition(start)
                stuck.append(fp.GetReference())
            else:
                dist = (placed[0] ** 2 + placed[1] ** 2) ** 0.5
                moved.append((fp.GetReference(), pcbnew.ToMM(dist)))
                others = silk_items(board, side_front)
    return moved, stuck


def main():
    """Relocate colliding designators, reporting what could not be placed."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-search", type=float, default=4.0,
                    help="furthest a designator may be moved, mm "
                         "(default 4.0)")
    ap.add_argument("--max-rounds", type=int, default=6,
                    help="cap on DRC-verified rounds (default 6)")
    args = ap.parse_args()

    offsets = spiral(pcbnew.FromMM(STEP_MM), pcbnew.FromMM(args.max_search))

    count, refs = drc_silk_offenders(PCB)
    print(f"kicad-cli reports {count} silk violations, "
          f"{len(refs)} designators at fault")

    moved, stuck, rounds = [], set(), 0
    while refs and rounds < args.max_rounds:
        rounds += 1
        board = pcbnew.LoadBoard(str(PCB))
        edge = board.GetBoardEdgesBoundingBox()
        edge.Inflate(-pcbnew.FromMM(EDGE_INSET_MM))

        got, could_not = relocate(board, refs, offsets, edge)
        if not got:
            print(f"   round {rounds}: no designator could be moved -- "
                  f"stopping")
            stuck |= set(could_not)
            break
        board.Save(str(PCB))

        new_count, new_refs = drc_silk_offenders(PCB)
        print(f"   round {rounds}: moved {len(got):2d}, "
              f"silk violations {count} -> {new_count}")
        if new_count >= count:
            print("   no improvement -- stopping rather than churning")
            stuck |= set(could_not) | new_refs
            count = new_count
            break
        moved += got
        stuck |= set(could_not)
        count, refs = new_count, new_refs

    print(f"\nfinal silk violations: {count}")
    print(f"designators moved:   {len(moved)}")
    for r, d in sorted(moved, key=lambda x: -x[1]):
        print(f"   {r:5s} {d:5.2f} mm")
    if stuck:
        print(f"\ncould not place ({len(stuck)}) -- REPORTED, not hidden: "
              f"{' '.join(sorted(stuck))}")
    print("\nSH1's 4 outline segments over its own pads are left alone: "
          "trimming a\nfootprint's own graphics is referred to the repo "
          "owner (CLAUDE.md).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
