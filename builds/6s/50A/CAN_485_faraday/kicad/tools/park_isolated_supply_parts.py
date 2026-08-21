#!/usr/bin/env python3
"""Put every isolated-supply support part off-board, for hand placement.

Governed by AGENTS.md. TODO.md 12.5.af.

WHAT AND WHY
------------
The isolated sections of U3 (ADM3055E) and U4 (ADM2582E) need twelve support
parts that this board did not have: four ferrite beads [53] and eight
reservoir/decoupling capacitors, all specified by pin pairing in [9] and [10].
The schematic now carries all twelve and is ERC-clean. This script puts their
footprints on the PCB.

It parks them in a staging column OUTSIDE the board outline rather than
guessing positions inside it, because the datasheets constrain where they go
and the board has no room where they belong:

  * [10] p.15: "Connect this pin through a ferrite bead and short the PCB
    trace to VISOIN for operation."
  * [9] p.17: "the total lead length between both ends of the capacitor and
    the input power supply pin should not exceed 10 mm", and the ordering
    "Ensure that the C1 capacitor connects between VISOOUT (Pin 12) and GND2
    (Pin 11) on the device side of the L1 and L2 ferrites."
  * Measured: U3's isolated pin row is at x 11.28 and U4's at x 14.45, facing
    each other across 3.17 mm, with a 0.55 mm channel between their
    courtyards. J2/J3 sit above them, U1/U2 below. Nothing fits.

Parts placed off-board are visible, netted, and DRC-checkable, and they make
the missing space impossible to overlook. The four beads a previous pass had
parked on-board at x 19.4..24.9, y 24.5..28.6 are moved out here too, so the
whole group can be placed together.

NOTE FOR WHOEVER PLACES THESE: the two isolated grounds are NOT
interchangeable. The VISOOUT reservoirs return to the dc-to-dc converter
ground (CAN_GNDISO / RS485_GNDISO), the VISOIN decouplers to the bus-side
ground (CAN_ISO_GND / RS485_ISO_GND), and the beads bridge the two. Swapping
them defeats the split that [9] and [10] require.

Usage:
    python3 tools/park_isolated_supply_parts.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-17, TODO.md 12.5.af.
# AI-generated; every quoted requirement is from the local copies of [9],
# [10] and [53] in docs/datasheets/. Not human-authored.

import argparse
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-isocaps.bak")

CAPLIB = "/usr/share/kicad/footprints/Capacitor_SMD.pretty"
CAPFP = "C_0805_2012Metric"

PARK_X_FB = 32.0  # staging columns, board-local mm (board ends at 25.45)
PARK_X_C = 40.0
PARK_Y0 = 6.0
PARK_DY_FB = 4.0
PARK_DY_C = 5.5

# ref, value, net on pad 1, net on pad 2
CAPS = [
    ("C11", "10uF", "CAN_VISOOUT", "CAN_GNDISO"),
    ("C12", "220nF", "CAN_VISOOUT", "CAN_GNDISO"),
    ("C13", "100nF", "CAN_VISOIN", "CAN_ISO_GND"),
    ("C14", "10nF", "CAN_VISOIN", "CAN_ISO_GND"),
    ("C15", "10uF", "RS485_VISOOUT", "RS485_GNDISO"),
    ("C16", "100nF", "RS485_VISOOUT", "RS485_GNDISO"),
    ("C17", "100nF", "RS485_VISOIN", "RS485_ISO_GND"),
    ("C18", "10nF", "RS485_VISOIN", "RS485_ISO_GND"),
]
FERRITES = ["FB1", "FB2", "FB3", "FB4"]


def origin(board):
    """Top-left of the board outline."""
    box = board.GetBoardEdgesBoundingBox()
    return box.GetLeft(), box.GetTop()


def net(board, name):
    """Existing net by name, or a freshly created one."""
    info = board.GetNetInfo().GetNetItem(name)
    if info is None:
        info = pcbnew.NETINFO_ITEM(board, name)
        board.Add(info)
    return info


def main() -> int:
    """Move the beads out and add the eight capacitors beside them."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    ox, oy = origin(board)

    def put(fp, x, y):
        fp.SetPosition(pcbnew.VECTOR2I(ox + pcbnew.FromMM(x), oy + pcbnew.FromMM(y)))

    print(f"1. moving the four beads out to x = {PARK_X_FB} mm")
    found = {
        f.GetReference(): f for f in board.Footprints() if f.GetReference() in FERRITES
    }
    for i, ref in enumerate(FERRITES):
        if ref not in found:
            print(f"     {ref} not on the board -- skipped")
            continue
        put(found[ref], PARK_X_FB, PARK_Y0 + i * PARK_DY_FB)
        print(f"     {ref} -> ({PARK_X_FB}, {PARK_Y0 + i * PARK_DY_FB})")

    print(f"\n2. adding the eight capacitors at x = {PARK_X_C} mm")
    have = {f.GetReference() for f in board.Footprints()}
    for i, (ref, val, n1, n2) in enumerate(CAPS):
        if ref in have:
            print(f"     {ref} already present -- skipped")
            continue
        fp = pcbnew.FootprintLoad(CAPLIB, CAPFP)
        if fp is None:
            raise SystemExit(f"could not load {CAPLIB}/{CAPFP}")
        fp.SetReference(ref)
        fp.SetValue(val)
        board.Add(fp)
        y = PARK_Y0 + i * PARK_DY_C
        put(fp, PARK_X_C, y)
        fp.Flip(fp.GetPosition(), False)  # isolated section is on B.Cu
        for p in fp.Pads():
            p.SetNet(net(board, n1 if p.GetNumber() == "1" else n2))
        print(f"     {ref:4s} {val:6s} [{n1} | {n2}] -> ({PARK_X_C}, {y})")

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    print(
        f"\nunconnected: {board.GetConnectivity().GetUnconnectedCount(False)}"
        "  (every parked part is unrouted by definition)"
    )

    if args.dry_run:
        print("--dry-run: nothing written")
        return 0
    shutil.copy2(PCB, BACKUP)
    board.Save(str(PCB))
    print(f"saved {PCB.name} (backup: {BACKUP.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
