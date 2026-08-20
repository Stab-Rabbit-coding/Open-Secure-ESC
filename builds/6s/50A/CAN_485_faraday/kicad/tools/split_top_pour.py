#!/usr/bin/env python3
"""Give the pack return an F.Cu path, so it does not need vias it cannot have.

TODO.md 12.5.ax option (4). Repo owner's decision, 2026-08-19.

THE PROBLEM THIS SOLVES
-----------------------
J5B is the 50 A pack negative terminal: a 7.00 x 7.00 mm SMD pad on **F.Cu
only**. Across the top of the board F.Cu carries the VM pour (priority 2), so
there is no F.Cu GND copper anywhere near J5B, and its only route to the
ground system is a via down to In1.Cu/B.Cu.

It cannot have one. The isolation barrier on this board is held geometrically
by keeping the pack terminals as single-layer islands on the face OPPOSITE the
isolated section -- `tools/score_placement.py`'s `pack_layer_separated` rule,
worth 2.80 -> 4.64 mm of creepage when it was adopted. A via under J5B punches
GND through to B.Cu a fraction of a millimetre from U4's isolated pin row and
destroys exactly that separation. `tools/stitch_planes.py` placed 0 of 18
pack-terminal vias, and that refusal was correct.

So the connection the pack return needs is the connection the isolation
forbids, and no via count fixes it: `tools/via_current_budget.py` puts the
requirement at 50-100 vias against a pad that holds at most 36 at 0.60 mm
drill.

WHAT THIS DOES
--------------
**Cuts the F.Cu VM zone back** so it stops at the board centreline in the top
stem, letting the existing whole-board GND zone (priority 0) fill the J5B side
by itself. No zone is added.

    VM F.Cu outline, top-stem right edge:  x 46.78  ->  x 35.95

FIRST ATTEMPT, AND WHY IT WAS REPLACED. The obvious implementation was to ADD
a high-priority F.Cu GND region over the J5B side and let it out-rank the VM
pour. Electrically that worked -- J5B joined the main 66-pad GND island and
unrouted went 66 -> 63. But it left **two overlapping GND planes on F.Cu**,
and KiCad exports each zone as its own `(plane GND (polygon F.Cu ...))`. Two
overlapping same-net planes are pathological input for FreeRouting: with them
present the router **failed to complete a single pass in 53 minutes**, having
routed the same board in 23-34 minutes before. Cutting the VM zone instead
produces the same copper with one plane per net per layer.
The pack return then leaves J5B **in plane, on F.Cu**, runs south clear of the
isolated section, and meets the rest of the ground system at y 41..47 -- a band
chosen because it sits below U4's primary pin row (ends y 40.18) and above the
high-side FET drains (start y 50.02), which is where stitching vias are legal
and harmless.

WHY THE GEOMETRY IS WHERE IT IS
-------------------------------
x 35.95 is the board centreline and the axis the layout is already symmetric
about. It leaves J5A (ends x 34.95) and J5B (starts x 36.95) each 1.00 mm
clear of the split, against the Power class's 0.20 mm clearance.

y 48.00 is the southern limit because VM has to reach all three high-side FET
drains (Q1/Q3/Q5, y 50.02..54.83) across the full board width. Above y 48 VM
is confined to x < 35.95; below it VM has the whole width again.

ISOLATION IMPACT: none. The area this hands to GND was already covered by the
F.Cu VM pour, and VM and GND are both primary-side nets -- the copper over the
isolated section changes net, not layer or extent. The around-edge creepage
path is untouched. **This is only true as long as no via is placed in the new
region above y ~34**, which is why the stitching band is bounded below U4.

NOT VERIFIED HERE: whether the resulting F.Cu GND corridor is wide enough to
carry 50 A. It is ~15.5 mm wide, but IPC-2152 is not in REFERENCES.md and no
current rating is asserted per AGENTS.md Sec.1.3. Run
`tools/via_current_budget.py` and the conductor arithmetic against a primary
source before fabrication. Logged in TODO.md 12.5.ax.

Usage:
    python3 tools/split_top_pour.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic), 2026-08-19, implementing the repo
# owner's choice of option (4). AI-generated; geometry measured off the board.

import argparse
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-poursplit.bak")

SPLIT_X = 35.95            # board centreline; J5A ends 34.95, J5B starts 36.95
ZONE_NAME = "GND return corridor for J5B (TODO 12.5.ax option 4)"


def main() -> int:
    """Add the F.Cu GND region over the J5B half of the top pour."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    mm = pcbnew.pcbIUScale.IU_PER_MM
    fcu = board.GetLayerID("F.Cu")

    # Remove the overlapping-zone implementation if a previous run added it.
    stale = [z for z in board.Zones() if z.GetZoneName() == ZONE_NAME]
    for z in stale:
        board.Remove(z)
    if stale:
        print(f"removed {len(stale)} zone(s) from the superseded "
              f"overlapping-region implementation")

    # Cut the VM top stem back to the centreline. The outline is asserted
    # rather than pattern-matched: if the pour is re-drawn this must be
    # re-derived, not silently applied to a shape it no longer fits.
    target = None
    for z in board.Zones():
        if (not z.GetIsRuleArea() and z.GetNetname() == "VM"
                and z.GetLayerSet().Contains(fcu)):
            target = z
    if target is None:
        raise SystemExit("F.Cu VM zone not found")

    chain = target.Outline().Outline(0)
    pts = [(round(chain.CPoint(k).x / mm, 2), round(chain.CPoint(k).y / mm, 2))
           for k in range(chain.PointCount())]
    expected = [(25.02, 20.5), (46.78, 20.5), (46.78, 44.4), (51.45, 44.4),
                (51.45, 60.33), (20.45, 60.33), (20.45, 44.4), (25.02, 44.4)]
    if pts == [(SPLIT_X, 20.5) if q == (46.78, 20.5) else
               (SPLIT_X, 44.4) if q == (46.78, 44.4) else q
               for q in expected]:
        print("VM stem already cut back -- nothing to do")
        return 0
    if pts != expected:
        raise SystemExit(f"F.Cu VM outline is not the shape this tool was "
                         f"written for.\n  found:    {pts}\n"
                         f"  expected: {expected}\nRe-derive before running.")

    moved = 0
    for k in range(chain.PointCount()):
        q = chain.CPoint(k)
        if round(q.x / mm, 2) == 46.78:
            chain.SetPoint(k, pcbnew.VECTOR2I(int(SPLIT_X * mm), q.y))
            moved += 1
    print(f"cut the VM top stem: {moved} vertices x 46.78 -> {SPLIT_X}; "
          f"GND now fills x {SPLIT_X}..51.45 above y 44.40")
    if args.dry_run:
        print("dry run -- not written")
        return 0

    shutil.copy2(PCB, BACKUP)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.BuildConnectivity()

    # Post-condition, not a pre-condition: the whole point of the change is
    # that J5B ends up sitting on F.Cu GND copper. Verify it before saving
    # rather than assuming the pour did what was intended.
    j5b = next((p for f in board.GetFootprints()
                if f.GetReference() == "J5B" for p in f.Pads()), None)
    reached = False
    for z in board.Zones():
        if (z.GetIsRuleArea() or z.GetNetname() != "GND"
                or not z.GetLayerSet().Contains(fcu)):
            continue
        poly = z.GetFilledPolysList(fcu)
        if poly and poly.OutlineCount() and poly.Collide(
                j5b.GetEffectivePolygon(fcu), 0):
            reached = True
    if not reached:
        raise SystemExit("J5B did NOT end up on F.Cu GND copper -- not saving")
    print("verified: J5B sits on F.Cu GND copper")

    board.Save(str(PCB))
    print(f"backed up -> {BACKUP.name}; re-poured and saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
