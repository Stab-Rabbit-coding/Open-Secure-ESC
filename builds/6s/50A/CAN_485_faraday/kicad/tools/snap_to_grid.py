#!/usr/bin/env python3
"""Re-seat the whole schematic onto KiCad's 1.27 mm connection grid.

Clears the 347 `endpoint_off_grid` ERC warnings -- the single largest category
of violation left on this sheet.

THE CAUSE
---------
`tools/genlib.py` lays the drawing out on a 10 mm metric grid and then offsets
the whole thing to centre it on the sheet, giving every symbol a position of
the form (n*10 + 9.85, m*10 + 2.54). KiCad's schematic connection grid is
1.27 mm (50 mil), and 10 mm is not a multiple of it, so almost every pin and
wire endpoint lands between grid points.

Nothing is electrically wrong -- KiCad connects by exact coordinate match, and
the wires do meet the pins -- which is why every one of these is a warning
rather than an error. What it costs is editability: a human opening this sheet
in Eeschema cannot draw a wire that lands on an existing pin without turning
the grid off, so any hand edit risks silently detaching something.

RESULT: A GLOBAL SNAP IS **NOT** SAFE ON THIS SHEET -- DO NOT RE-ATTEMPT
-------------------------------------------------------------------------
This was tried, verified, and reverted on 2026-08-15. It silently shorted the
design. `--verify-netlist` is what caught it, and it is now mandatory.

The reason is that `genlib.py` separates parallel routes by offsets of
0.01-0.02 mm rather than by whole grid steps -- the four isolated-supply legs,
for instance, sit in adjacent "lanes" at x = 381.51, 381.52, 381.53, 381.54.
`tools/check_shorts.py` exists precisely because collinear overlapping
segments read as one net, and these hair-thin offsets are how the generator
avoids that. Snapping to 1.27 mm collapses every such lane onto a single grid
line, which merges them.

Measured damage from the attempt (73 nets -> 63):

    VM shorted to GND ......... U5.3/U5.4, Q1/Q3/Q5 drains onto GND
    all six PWM lines merged ... PWM_AH/AL/BH/BL/CH/CL into one net
    CPH shorted to CPL ......... across the charge-pump capacitor C5
    NRST merged into 3V3
    GD_SPI_MISO merged into 3V3

Clearing the 347 `endpoint_off_grid` warnings therefore requires re-laying out
the sheet on a real 1.27 mm grid with >= 1.27 mm lane spacing -- a full
re-route of the drawing, not a coordinate transform. That is tracked in
TODO.md. The warnings are cosmetic: KiCad connects by exact coordinate match,
the netlist is correct, and ERC reports zero errors.

The original reasoning is kept below because it is exactly right about symbol
pins and exactly wrong about lane spacing -- the failure was in what it did
not check.

WHY THE SNAP *LOOKED* SAFE
---------------------------
Each coordinate is rounded independently to the nearest multiple of 1.27 mm.
That is a pure function of the coordinate, so two points that were coincident
before are still coincident after -- which is the property connectivity
depends on.

The one thing that could break it is a symbol whose pins are NOT on a 1.27 mm
grid relative to its own origin: the origin and the pin would then snap by
different deltas and the pin would come off its wire. This script therefore
CHECKS that condition on every library symbol before touching anything, and
refuses to run if any symbol fails. (At the time of writing all of them pass.)

Rotation and mirroring are safe for the same reason: 90 degree rotation maps
(x, y) -> (-y, x), which preserves "is a multiple of 1.27".

Maximum movement is +/-0.635 mm against a 10 mm placement pitch, so no symbol
can be pushed into its neighbour. The caller should still diff the exported
netlist across the change -- `--verify-netlist` does exactly that.

Usage:
    python3 tools/snap_to_grid.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) during the 2026-08-15 layout pass,
# TODO.md 12.4. AI-generated; reviewed against the primary sources named
# in the docstring above. Not human-authored.


import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from kiutils.schematic import Schematic

HERE = Path(__file__).resolve().parent
KICAD_DIR = HERE.parent
SCH = KICAD_DIR / "open_secure_esc_6s_50a_can485_faraday.kicad_sch"

GRID = 1.27
EPS = 1e-6


def on_grid(v: float) -> bool:
    """True if a coordinate already sits on the 1.27 mm grid."""
    return abs(v / GRID - round(v / GRID)) < EPS


def snap(v: float) -> float:
    """Round a coordinate to the nearest 1.27 mm grid point."""
    return round(round(v / GRID) * GRID, 4)


def check_symbol_pins(sch: Schematic) -> list[str]:
    """Return library symbols whose pins are off-grid relative to their origin.

    If this is non-empty a global snap would detach those pins from their
    wires, because origin and pin would move by different amounts.
    """
    bad = []
    for lib in sch.libSymbols:
        for unit in lib.units:
            for pin in unit.pins:
                if not (on_grid(pin.position.X) and on_grid(pin.position.Y)):
                    bad.append(f"{lib.entryName} pin {pin.number} "
                               f"@({pin.position.X}, {pin.position.Y})")
    return bad


def walk_positions(sch: Schematic):
    """Yield every Position object on the sheet that carries sheet coordinates."""
    for sym in sch.schematicSymbols:
        yield sym.position
        for p in sym.properties:
            yield p.position
    for group in (sch.graphicalItems, sch.junctions, sch.noConnects,
                  sch.busEntries, sch.texts, sch.labels, sch.globalLabels,
                  sch.hierarchicalLabels):
        for item in group:
            pts = getattr(item, "points", None)
            if pts:
                yield from pts
            pos = getattr(item, "position", None)
            if pos is not None:
                yield pos
            for p in getattr(item, "properties", []) or []:
                yield p.position


def export_netlist(path: Path, out: Path) -> str:
    """Export a netlist and return just its (nets ...) section."""
    subprocess.run(
        ["kicad-cli", "sch", "export", "netlist", "--output", str(out), str(path)],
        check=True, capture_output=True,
    )
    text = out.read_text(encoding="utf-8")
    return text[text.index("(nets"):]


def main() -> int:
    """Snap every sheet coordinate to the 1.27 mm grid."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify-netlist", action="store_true",
                    help="export the netlist before and after and require "
                         "them to be identical (always on; kept for clarity)")
    ap.add_argument("--force", action="store_true",
                    help="actually attempt the snap. Without this the script "
                         "only reports, because the snap is known to short "
                         "this sheet -- see the module docstring.")
    args = ap.parse_args()
    args.verify_netlist = True      # never write this file unverified

    sch = Schematic().from_file(str(SCH))

    bad = check_symbol_pins(sch)
    if bad:
        print("REFUSING TO SNAP -- these library symbols have off-grid pins, "
              "so a global snap would detach them from their wires:",
              file=sys.stderr)
        for b in bad:
            print(f"  {b}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as td:
        before = (export_netlist(SCH, Path(td) / "before.net")
                  if args.verify_netlist else None)

        moved = 0
        for pos in walk_positions(sch):
            nx, ny = snap(pos.X), snap(pos.Y)
            if nx != pos.X or ny != pos.Y:
                moved += 1
            pos.X, pos.Y = nx, ny
        print(f"snapped {moved} coordinates to the {GRID} mm grid")

        if args.dry_run or not args.force:
            print("not written -- a global snap shorts this sheet "
                  "(VM/GND, the six PWM lines, CPH/CPL). See the module "
                  "docstring; pass --force only if the lane spacing has been "
                  "fixed first.")
            return 0

        sch.to_file(str(SCH))
        print(f"wrote {SCH}")

        if before is not None:
            after = export_netlist(SCH, Path(td) / "after.net")
            if before != after:
                print("NETLIST CHANGED -- the snap altered connectivity. "
                      "Restore from backup and investigate.", file=sys.stderr)
                return 1
            print("netlist verified identical before and after")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
