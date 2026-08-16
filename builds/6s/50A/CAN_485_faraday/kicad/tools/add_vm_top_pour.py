#!/usr/bin/env python3
"""Pour VM on F.Cu across the power-stage band, and measure the result.

Governed by AGENTS.md. Closes the top-side half of TODO.md 12.5.s.

THE PROBLEM
-----------
The VM plane is on In2.Cu only. Every part that actually carries pack current
sits on F.Cu -- J5A (pack +), C1 (bulk), and the high-side drains Q1/Q3/Q5 --
and nothing joined them. KiCad reported 8 unconnected VM items including
"PTH pad 1 [VM] of J5A <-> Pad 6 [VM] of Q1 on F.Cu".

Left to `tools/autoroute.py`, FreeRouting closes them with 3.0 mm track from
its "power" net class: measured 5.2 W across the J5A-to-far-drain span at
2 oz, against 0.7 W for the same span as pour
(`docs/tools/conductor_sizing.py`). Hence a pour.

WHAT THIS SCRIPT DOES
---------------------
Adds one F.Cu zone on VM over the band y 0.60..15.50 mm, full board width.
Priority 2: **below** the three phase pours (priority 3), so they keep every
square they already own, and **above** the F.Cu GND pour (priority 0), which
had nothing to do in this band anyway.

Pad connection is FULL (solid, no thermal relief). Thermal spokes are for
solderability on small pads; on a 50 A drain land they are four necks in
series with the conductor.

WHAT IT DOES NOT DO, AND WHY -- READ BEFORE FABRICATING
--------------------------------------------------------
It does **not** stitch the F.Cu pour down to the In2.Cu VM plane, and the
pour alone is therefore NOT the finished conductor.

Measured on the filled result, the pour necks to **2.38 mm** of copper height
at x = 17..18 mm. That neck is the sole F.Cu path from J5A to Q5's drain: it
is pinched between J5B (the GND pack terminal, y 1.10..8.10) above and the
PH_C pour (y >= 11.10) below. It is short -- about 2.2 mm long, so roughly
0.9 squares, 0.28 mOhm, 0.7 W at 50 A -- but that is 0.7 W concentrated in
about 5 mm^2, which is a hot spot, not a comfortable margin.

The fix is via stitching to the In2 VM plane, which is unobstructed and would
carry the lateral current in parallel so the neck stops being the sole path.
That is deliberately NOT done here because it needs two decisions this script
must not make alone:

  1. **Via count and placement.** Matching a 2 oz pour takes ~23 x 0.3 mm
     vias (2.2 A each). Free pour area exists either side of the neck, but
     placing vias inside the drain lands instead would be via-in-pad.
  2. **Via-in-pad is a fab option with a cost.** Filled-and-capped plating is
     an upcharge; unfilled vias in a solder pad wick paste and starve the
     joint. On flight hardware that is the repo owner's call, not a default.

Also note: U5 sits on the bottom directly beneath these FETs with its own 12
GND thermal vias. Any new via here must be checked against them -- that pair
has already produced one verified GND-to-VM short on this board.

Usage:
    python3 tools/add_vm_top_pour.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-16, TODO.md 12.5.s.
# AI-generated. Dissipation figures come from docs/tools/conductor_sizing.py,
# an AGENTS.md Sec.4 derivation from copper's resistivity -- watts, not
# degrees. Geometry is measured off the board, not assumed. Not human-authored.

import argparse
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"

# Band covering J5A, C1 and all three high-side drain lands. The lowest VM
# copper is Q5's drain land at y = 14.93 mm; 15.50 clears it.
BAND = (0.55, 0.60, 24.95, 15.50)          # x1, y1, x2, y2 in board-local mm
PRIORITY = 2                                # phase pours are 3, GND is 0
CLEARANCE_MM = 0.3                          # matches every other zone here


def board_origin(board) -> tuple[int, int]:
    """Top-left of the board outline, so the constants above read in mm."""
    box = board.GetBoardEdgesBoundingBox()
    return box.GetLeft(), box.GetTop()


def existing_pour(board):
    """The F.Cu VM zone, if this script already ran."""
    for zone in board.Zones():
        if zone.GetNetname() == "VM" and zone.IsOnLayer(pcbnew.F_Cu):
            return zone
    return None


def measure_neck(board) -> tuple[float, float]:
    """Narrowest copper height of the F.Cu VM fill, and where it occurs.

    Sampled as vertical scan lines across the band. The number that matters
    is the narrowest point on the only path to the far drain, because that
    is where the current density peaks.
    """
    zone = existing_pour(board)
    poly = zone.GetFilledPolysList(pcbnew.F_Cu)
    ox, oy = board_origin(board)
    worst, worst_x = 999.0, 0.0
    x = BAND[0]
    while x <= BAND[2]:
        px = ox + pcbnew.FromMM(x)
        runs, run, prev = [], 0.0, False
        y = BAND[1]
        while y <= BAND[3]:
            here = poly.Collide(pcbnew.VECTOR2I(px, oy + pcbnew.FromMM(y)))
            if here:
                run += 0.01
            elif prev:
                runs.append(run)
                run = 0.0
            prev = here
            y += 0.01
        if run:
            runs.append(run)
        if runs and max(runs) < worst:
            worst, worst_x = max(runs), x
        x += 0.25
    return worst, worst_x


def main() -> int:
    """Add the pour, refill, and report what it connected and where it necks."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report only, write nothing")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    if existing_pour(board) is not None:
        print("an F.Cu VM zone already exists -- nothing to do")
        return 0

    board.BuildConnectivity()
    before = board.GetConnectivity().GetUnconnectedCount(False)

    ox, oy = board_origin(board)
    zone = pcbnew.ZONE(board)
    zone.SetNet(board.GetNetInfo().GetNetItem("VM"))
    zone.SetLayer(pcbnew.F_Cu)
    zone.SetAssignedPriority(PRIORITY)
    zone.SetLocalClearance(pcbnew.FromMM(CLEARANCE_MM))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    outline = zone.Outline()
    outline.NewOutline()
    x1, y1, x2, y2 = BAND
    for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        outline.Append(ox + pcbnew.FromMM(x), oy + pcbnew.FromMM(y))
    board.Add(zone)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    after = board.GetConnectivity().GetUnconnectedCount(False)

    area = zone.GetFilledPolysList(pcbnew.F_Cu).Area() / 1e12
    neck, neck_x = measure_neck(board)

    print(f"F.Cu VM pour: {area:.1f} mm^2 over "
          f"x {x1}..{x2}, y {y1}..{y2} mm, priority {PRIORITY}")
    print(f"unconnected: {before} -> {after}")
    print(f"narrowest copper height: {neck:.2f} mm at x = {neck_x:.1f} mm")
    print("\nThe neck is pinched between J5B (GND pack terminal) above and "
          "the PH_C pour below,\nand is the only F.Cu path to Q5's drain. "
          "It still needs via stitching to the\nIn2 VM plane -- see this "
          "script's docstring and TODO.md 12.5.s.")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    board.Save(str(PCB))
    print(f"\nsaved {PCB.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
