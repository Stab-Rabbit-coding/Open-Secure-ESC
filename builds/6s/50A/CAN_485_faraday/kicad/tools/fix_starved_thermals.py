#!/usr/bin/env python3
"""Give the 11 starved GND pads a solid zone connection instead of one spoke.

Governed by AGENTS.md. Part of the clean-build pass, TODO.md 12.5.ao.

THE VIOLATION
-------------
11 x `starved_thermal`, severity ERROR:

    Thermal relief connection to zone incomplete
    (layer F.Cu; zone min spoke count 2; actual 1)

`.kicad_pro` sets `min_resolved_spokes = 2` board-wide. Each of these pads
resolves only one spoke, so each is hanging off the GND pour by a single
0.5 mm neck. Every one of them is a GND pad:

    SH1.1  x4   Faraday shield frame, bars up to 19.20 x 1.50 mm
    U5.25       DRV8353S GND, 0.60 x 0.22 mm
    U6.1/.2     SOIC-8 GND, 1.95 x 0.60 mm
    U7.1/.2     SOIC-8 GND, 1.95 x 0.60 mm
    U8.1/.2     SOIC-8 GND, 1.95 x 0.60 mm

U7 joined the list after the U7/U8 swap (tools/swap_u7_u8.py): the
starvation belongs to the POSITION, not the part -- whichever sense amp
stands in the phase-B column is the one the pour reaches from one side.
All three sense amps are now listed so the set is stable under any
further reshuffling of them.
    C9.2 C10.2  0805 capacitor GND
    R5.2 R10.2  0805 resistor GND

C7.2 joins that list on the second pass: solid-bonding the first ten pads
changed the pour around it enough to drop it from two spokes to one. Zone
fills are coupled, so this class of fix is iterated to a fixed point rather
than applied once.

WHY SOLID RATHER THAN COAXING A SECOND SPOKE
---------------------------------------------
A spoke cannot be conjured where the pour does not reach. Widening spokes or
shrinking the thermal gap only helps when copper is present on another side
of the pad and merely fails to bridge; it does nothing for a pad the pour
approaches from one direction. Solid connection removes the constraint
instead of negotiating with it.

It is also the electrically correct answer on THIS board rather than a
generic one. The design's stated purpose is survival in harsh EMI, which is
why it carries galvanic isolation, redundant control paths, and a Faraday
shield. A shield frame bonded to ground through a single 0.5 mm neck is a
contradiction of that design: shield effectiveness is set by the impedance of
the bond, and one narrow spoke is mostly inductance. The same argument holds
for the IC GND pins, weakly for a 0805 decoupling return.

This repo has already made and documented the same call once, in
`add_vm_top_pour.py`: "Thermal spokes are for solderability on small pads; on
a 50 A drain land they are four necks in series with the conductor."

THE TRADE THIS ACCEPTS -- ASSEMBLY, AND IT IS THE OWNER'S CALL
---------------------------------------------------------------
Thermal relief exists for a reason: a pad tied solidly into a large pour sinks
heat during reflow, which can produce a cold joint, and asymmetric heating
across a two-terminal part can tombston it.

That risk is not uniform across these 11 pads, and this script does not
pretend it is:

  * SH1, U5, U6, U7, U8 -- ICs and a shield frame, reflowed with a proper
    profile and with several pins each. Low risk; take the solid bond.
  * C7, C9, C10, R5, R10 -- two-terminal 0805 passives, where one solid end and
    one relieved end is exactly the asymmetry that tombstones parts. 0805 is
    far more forgiving than the 0402/0201 sizes where this dominates, but the
    risk is not zero.

0805 passives are therefore listed separately below and reported separately,
so reverting just those five is a one-line change if the board is to be hand
-soldered or reworked. See TODO.md 12.5.ao.

Usage:
    python3 tools/fix_starved_thermals.py [--dry-run] [--skip-passives]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.ao.
# AI-generated. The pad list is taken from kicad-cli's own starved_thermal
# report, not chosen by hand. Not human-authored.

import argparse
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"

# ICs and the shield frame: solid bond is both the fix and the better design.
STRUCTURAL = {"SH1": {"1"}, "U5": {"25"},
              "U6": {"1", "2"}, "U7": {"1", "2"}, "U8": {"1", "2"}}

# Two-terminal 0805 passives: solid works, but carries the tombstoning trade
# described above. Separated so they can be reverted independently.
PASSIVES = {"C7": {"2"}, "C9": {"2"}, "C10": {"2"},
            "R5": {"2"}, "R10": {"2"}}


def apply(board, table):
    """Set every listed pad to a solid zone connection. Returns pads changed."""
    done = []
    for fp in board.Footprints():
        want = table.get(fp.GetReference())
        if not want:
            continue
        for pad in fp.Pads():
            if pad.GetNumber() not in want:
                continue
            if pad.GetNetname() != "GND":
                continue
            pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
            done.append(f"{fp.GetReference()}.{pad.GetNumber()}")
    return done


def main():
    """Apply the solid connections and refill, reporting both groups."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report only, write nothing")
    ap.add_argument("--skip-passives", action="store_true",
                    help="leave the four 0805 passives on thermal relief, "
                         "accepting their starved_thermal errors, in exchange "
                         "for keeping their reflow behaviour unchanged")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))

    structural = apply(board, STRUCTURAL)
    print(f"solid GND bond, ICs + shield ({len(structural)} pads):")
    print(f"   {' '.join(structural)}")

    if args.skip_passives:
        print("\n0805 passives: LEFT on thermal relief (--skip-passives); "
              "their starved_thermal errors remain")
    else:
        passives = apply(board, PASSIVES)
        print(f"\nsolid GND bond, 0805 passives ({len(passives)} pads): "
              f"{' '.join(passives)}")
        print("   tombstoning trade accepted -- see this script's docstring "
              "and TODO.md 12.5.ao")

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
