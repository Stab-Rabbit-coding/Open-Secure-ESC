#!/usr/bin/env python3
"""Push the isolated-supply ferrite change from the schematic into the PCB.

Governed by AGENTS.md. Companion to tools/add_isolated_supply_ferrites.py,
which made the same change on the sheet. Run that one first.

WHAT CHANGES
------------
Four BLM15HD182SN1D beads [53] are added, and the two isolated grounds are
split from one net into two, as [9] and [10] require:

    FB1  CAN_VISOOUT   -> CAN_VISOIN      U3 pin 19 -> pin 16
    FB2  CAN_GNDISO    -> CAN_ISO_GND     U3 pins 18,20 -> pins 11,15
    FB3  RS485_VISOOUT -> RS485_VISOIN    U4 pin 12 -> pin 19
    FB4  RS485_GNDISO  -> RS485_ISO_GND   U4 pins 11,14 -> pins 16,20

Pad-level net reassignment is done explicitly rather than by re-importing a
netlist, because a full netlist import would also rebuild footprint positions
and discard the repo owner's hand placement.

PLACEMENT IS PARKED, NOT SOLVED -- READ THIS
---------------------------------------------
[10] p.15 says of VISOOUT: "Connect this pin through a ferrite bead and short
the PCB trace to VISOIN for operation." There is nowhere short to put them.

Measured on this board: U3's isolated pin row sits at x = 11.28 and U4's at
x = 14.45, facing each other across 3.17 mm, with the two package courtyards
(U3 to x 12.59, U4 from x 13.14) leaving a 0.55 mm channel between them. No
0402 fits there, let alone four of them plus the eight capacitors [9] and [10]
also require. The nearest genuinely free back-side copper is a single
pocket at x 19.4..24.9, y 24.5..28.6 -- right of U2, above J1.

An earlier version of this script parked them at y 2.6/6.6 on the strength of
a free-space scan that only counted BACK-side footprints. That was wrong:
J5A and J5B are FRONT-side through-hole parts whose 7 x 7 mm pads and 4.4 mm
barrels block both sides, and the beads landed straight on top of them -- 8
shorting_items. The repo already documents this trap in
symbols/tools/gen_smd_solder_pad_footprints.py ("a through-hole part costs its
area TWICE"). Any occupancy scan on this board must include through-hole
footprints regardless of which side they are mounted on.

So this script parks the beads in that free space with correct nets, which
makes the design electrically complete and lets ERC/DRC and the router see
them. It does NOT satisfy the datasheets' trace-length guidance. Opening a
channel along the two isolated pin rows is a PLACEMENT change and belongs to
the repo owner -- TODO.md 12.5.af.

Usage:
    python3 tools/add_ferrites_to_pcb.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-17, TODO.md 12.5.ad.
# AI-generated. Pin functions quoted are from the local copies of [9]/[10];
# all coordinates are measured off the board. Not human-authored.

import argparse
import math
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-ferrite.bak")
FPLIB = "/usr/share/kicad/footprints/Inductor_SMD.pretty"
FPNAME = "L_0402_1005Metric"

# (ref, net on pad 1, net on pad 2, park x, park y, rotation)
FERRITES = [
    ("FB1", "CAN_VISOOUT", "CAN_VISOIN", 20.80, 25.30, 0),
    ("FB2", "CAN_GNDISO", "CAN_ISO_GND", 23.30, 25.30, 0),
    ("FB3", "RS485_VISOOUT", "RS485_VISOIN", 20.80, 27.30, 0),
    ("FB4", "RS485_GNDISO", "RS485_ISO_GND", 23.30, 27.30, 0),
]
# Pads whose net membership changes, per the datasheet pin tables.
RENET = {
    ("U3", "16"): "CAN_VISOIN",     # [10] VISOIN, fed from VISOOUT via FB1
    ("U3", "18"): "CAN_GNDISO",     # [10] GNDISO, dc-dc converter ground
    ("U3", "20"): "CAN_GNDISO",
    ("U4", "11"): "RS485_GNDISO",   # [9] GND2 converter side
    ("U4", "14"): "RS485_GNDISO",
    ("U4", "19"): "RS485_VISOIN",   # [9] VISOIN, fed from VISOOUT via FB3
}


def origin(board):
    """Top-left of the board outline."""
    box = board.GetBoardEdgesBoundingBox()
    return box.GetLeft(), box.GetTop()


def net(board, name):
    """Existing net by name, or a freshly created one."""
    info = board.GetNetInfo().GetNetItem(name)
    if info is not None:
        return info
    info = pcbnew.NETINFO_ITEM(board, name)
    board.Add(info)
    print(f"     created net {name}")
    return info


def main() -> int:
    """Add the beads, split the isolated grounds, report trace distances."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    ox, oy = origin(board)

    if any(f.GetReference().startswith("FB") for f in board.Footprints()):
        print("ferrites already present -- nothing to do")
        return 0

    print("1. re-netting U3/U4 pads to split the isolated grounds")
    done = 0
    for f in board.Footprints():
        ref = f.GetReference()
        for p in f.Pads():
            key = (ref, p.GetNumber())
            if key in RENET:
                old = p.GetNetname()
                p.SetNet(net(board, RENET[key]))
                print(f"     {ref}.{p.GetNumber()}: {old} -> {RENET[key]}")
                done += 1
    if done != len(RENET):
        raise SystemExit(f"expected {len(RENET)} pad re-nets, did {done}")

    print("\n2. adding the beads")
    for ref, n1, n2, x, y, rot in FERRITES:
        fp = pcbnew.FootprintLoad(FPLIB, FPNAME)
        if fp is None:
            raise SystemExit(f"could not load {FPLIB}/{FPNAME}")
        fp.SetReference(ref)
        fp.SetValue("BLM15HD182SN1D")
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(ox + pcbnew.FromMM(x),
                                       oy + pcbnew.FromMM(y)))
        fp.Flip(fp.GetPosition(), False)      # isolated section is on B.Cu
        if rot:
            fp.SetOrientationDegrees(rot)
        for p in fp.Pads():
            p.SetNet(net(board, n1 if p.GetNumber() == "1" else n2))
        print(f"     {ref} [{n1} | {n2}] parked at ({x}, {y}) on B.Cu")

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()

    print("\n3. distance from each bead to the pins it must sit near")
    pads = {}
    for f in board.Footprints():
        for p in f.Pads():
            pads.setdefault(p.GetNetname(), []).append(
                (f.GetReference(), p.GetNumber(), p.GetPosition()))
    for ref, n1, n2, x, y, _ in FERRITES:
        here = pcbnew.VECTOR2I(ox + pcbnew.FromMM(x), oy + pcbnew.FromMM(y))
        for n in (n1, n2):
            far = [(math.hypot(pcbnew.ToMM(p.x - here.x),
                               pcbnew.ToMM(p.y - here.y)), r, pn)
                   for r, pn, p in pads.get(n, []) if not r.startswith("FB")]
            if far:
                d, r, pn = min(far)
                print(f"     {ref} -> {r}.{pn} ({n}): {d:5.1f} mm")
    print("\n   These are PARKED positions. [10] p.15 asks for a short trace")
    print("   to VISOIN; see this script's docstring and TODO.md 12.5.af.")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    shutil.copy2(PCB, BACKUP)
    board.Save(str(PCB))
    print(f"\nsaved {PCB.name} (backup: {BACKUP.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
