#!/usr/bin/env python3
"""Bring U5's 12 GND thermal vias up to this board's own via spec.

Governed by AGENTS.md. Closes TODO.md 12.5.x.

THE VIOLATION
-------------
12 x `drill_out_of_range`, severity ERROR:

    Hole size out of range (board setup constraints min hole 0.3000 mm;
    actual 0.2000 mm)

All twelve are instances of pad 41 (the GND thermal pad) inside U5, the
DRV8353S gate driver on the back side. They are 0.400 mm pads on 0.200 mm
drills, on a 1.15 mm grid under the exposed pad.

Note this violation is real even though the .kicad_pcb's own cached copy of
the rule says 0.2: `.kicad_pro` sets `min_through_hole_diameter = 0.3`, and
kicad-cli enforces the project file, not the board's cache. That discrepancy
has reversed this call twice before in this project's history.

WHY 0.60 / 0.30 AND NOT SOMETHING CHOSEN FOR THE OCCASION
----------------------------------------------------------
No new number is invented here. `.kicad_pro`'s Default net class already
specifies `via_diameter = 0.6`, `via_drill = 0.3` -- every other via on this
board is 0.6/0.3. U5's thermal vias are the only ones that are not. So the
fix is to make them match the board's existing standard, and the resulting
geometry satisfies all three governing constraints by construction:

    min_through_hole_diameter  0.30    ->  drill 0.30      OK (equal)
    min_via_annular_width      0.10    ->  (0.60-0.30)/2 = 0.15   OK
    min_hole_to_hole           0.25    ->  1.15 pitch - 0.30 = 0.85   OK

THE HAZARD THIS WAS CHECKED AGAINST
------------------------------------
U5 sits on the back directly under the FET bank, and this project has already
had one verified GND-to-VM short from exactly that stack-up. Growing a GND
via from 0.40 to 0.60 mm of copper on every layer is precisely the change
that could recreate it, so the FET drain lands were measured first rather
than assumed:

    via array   y 58.275 .. 61.725 mm
    Q3 pads     y 49.250 .. 56.750 mm   -> 1.525 mm clear above
    Q4 pads     y 62.750 .. 70.250 mm   -> 1.025 mm clear below

The array sits in the ~6 mm gap between the two FET rows, not under either.
At the new 0.30 mm copper radius the closest approach is 0.725 mm, against a
0.20 mm net-class clearance. The vias also pass through the F.Cu VM pour,
which retreats around them automatically at fill time.

Outer extent grows from 3.85 mm to 4.05 mm across, still inside the
RTA0040B's 4.15 mm exposed pad.

Usage:
    python3 tools/fix_u5_thermal_vias.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.x.
# AI-generated. Every dimension is read from .kicad_pro's Default net class or
# measured off the board; none is chosen ad hoc. Not human-authored.

import argparse
import json
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
PRO = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pro"

TARGET_REF = "U5"
TARGET_PAD = "41"


def board_via_spec():
    """The Default net class via geometry, as the board itself defines it."""
    data = json.loads(PRO.read_text())
    for cls in data["net_settings"]["classes"]:
        if cls["name"] == "Default":
            return float(cls["via_diameter"]), float(cls["via_drill"])
    raise SystemExit("no Default net class in .kicad_pro")


def main():
    """Resize the thermal vias, reporting the before/after geometry."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report only, write nothing")
    args = ap.parse_args()

    dia, drill = board_via_spec()
    print(f"board Default net class via: {dia} mm pad / {drill} mm drill")

    board = pcbnew.LoadBoard(str(PCB))
    fp = next((f for f in board.Footprints()
               if f.GetReference() == TARGET_REF), None)
    if fp is None:
        raise SystemExit(f"{TARGET_REF} not on board")

    changed = 0
    for pad in fp.Pads():
        if pad.GetNumber() != TARGET_PAD or pad.GetDrillSize().x <= 0:
            continue
        old_sz = pcbnew.ToMM(pad.GetSize().x)
        old_dr = pcbnew.ToMM(pad.GetDrillSize().x)
        if abs(old_dr - drill) < 1e-6 and abs(old_sz - dia) < 1e-6:
            continue
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(dia), pcbnew.FromMM(dia)))
        pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(drill),
                                         pcbnew.FromMM(drill)))
        changed += 1

    print(f"resized {changed} thermal vias on {TARGET_REF}.{TARGET_PAD}: "
          f"0.400/0.200 -> {dia}/{drill} mm")
    print(f"annular ring {(dia - drill) / 2:.3f} mm "
          f"(board minimum 0.100 mm)")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    board.Save(str(PCB))
    print(f"\nsaved {PCB.name} (zones refilled)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
