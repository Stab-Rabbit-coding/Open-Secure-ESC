#!/usr/bin/env python3
"""Make the board safe to hand to an SMT assembler.

Governed by AGENTS.md. TODO.md 12.5.au. Written after the repo owner
specified professional reflow assembly at JLCPCB or an equivalent house.

WHAT REFLOW ASSEMBLY SETTLES, AND WHAT IT DOES NOT
---------------------------------------------------
It settles TODO 12.5.ao: the five 0805 GND pads (C7 C9 C10 R5 R10) keep their
SOLID zone connections. Thermal relief on those was only ever worth it to
protect hand-soldering and rework; a controlled reflow profile handles a solid
0805 GND bond. `--skip-passives` on `fix_starved_thermals.py` is therefore NOT
to be used on this build. No change was needed -- the board is already in that
state -- and this note exists so nobody reverts it later.

It does not settle anything else. Three real defects below.

1. THREE BARE SOLDER PADS WOULD REACH THE PLACEMENT MACHINE
------------------------------------------------------------
J4A/J4B/J4C and J5A/J5B are wire-attach pads and are correctly flagged
`exclude from BOM` and `exclude from position files`. J1, J2 and J3 are the
same kind of thing -- a 4-pad probe landing and two 2-pad wire pads -- and
were NOT flagged. They would appear in the BOM as parts to buy and in the
pick-and-place file as parts to place, for components that do not exist.

That is the sort of thing an assembler queries at best and mis-builds at
worst, so this flags them to match J4/J5.

2. J5A/J5B CARRY NO SMD/THT ATTRIBUTE
--------------------------------------
Both read "unspecified" -- a leftover from `convert_j5_to_smd.py`, which
changed the pads but not the footprint attribute. Harmless today because both
are excluded from the position file anyway, but an unspecified attribute is a
question waiting to be asked. Set to SMD, which is what they now are.

3. NO FIDUCIALS
---------------
The board has none, on either side, and it is a DOUBLE-SIDED assembly:
18 footprints on F.Cu, 41 on B.Cu. Fiducials are the standard optical
reference an SMT machine uses to correct for board offset, rotation and
scaling; without them the placement system falls back on board edges or
tooling holes, which is coarser on fine-pitch parts. This board carries a
0.5 mm pitch WQFN-40 (U5) and a 0.5 mm pitch LQFP-64 (U1), which is exactly
where that accuracy is spent.

Three per side, deliberately non-collinear so the machine can resolve
rotation as well as translation, placed at the corner-most sites with a
2.2 mm clear radius. Excluded from BOM and position files -- a fiducial is
board artwork, not a part to place.

**Unverified, and flagged as such per AGENTS.md Sec.3:** the specific
fiducial policy of JLCPCB (whether they are required, and at what size and
count) has NOT been read from a JLCPCB capability document. Three 1 mm
fiducials with 2 mm mask openings is ordinary industry practice, and is what
this places, but before the order goes out that policy should be checked and
recorded in REFERENCES.md with a validated URL. Do not treat this script's
choice as a sourced requirement.

WHAT THIS SCRIPT DOES NOT TOUCH -- AND THE REAL BLOCKER
--------------------------------------------------------
None of the above matters yet, because **the board is not routed**. It carries
0 track segments and 2 vias, with 157 unconnected items. Routing was present
once -- commit 15eeaa4 had 352 segments and 49 vias -- and was removed
wholesale by the front/back re-placement repair in 8f4791a. TODO 12.5.w still
describes the pre-repair state and overstates it.

An unrouted board cannot be fabricated or assembled. Everything in this
script is necessary and none of it is sufficient. See TODO.md 12.5.w.

Usage:
    python3 tools/prep_for_assembly.py [--dry-run] [--no-fiducials]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19, TODO.md 12.5.au.
# AI-generated. Fiducial count/size is ordinary practice, NOT a sourced
# JLCPCB requirement -- see the docstring. Not human-authored.

import argparse
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
FID_LIB = "/usr/share/kicad/footprints/Fiducial.pretty"
FID_FP = "Fiducial_1mm_Mask2mm"

# Bare pads that are wire/probe landings, not placed components.
NOT_PLACED = ("J1", "J2", "J3")

# Corner-most sites with a 2.2 mm clear radius, measured off this board.
# Non-collinear on each side so rotation is resolvable.
FIDUCIALS = {
    pcbnew.F_Cu: [(2.2, 2.2), (29.7, 2.2), (10.7, 63.7)],
    pcbnew.B_Cu: [(2.2, 23.2), (29.7, 23.2), (29.7, 63.7)],
}

EXCLUDE = (pcbnew.FP_EXCLUDE_FROM_BOM
           | pcbnew.FP_EXCLUDE_FROM_POS_FILES)


def main():
    """Flag the non-parts, fix the attributes, add the fiducials."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report only, write nothing")
    ap.add_argument("--no-fiducials", action="store_true",
                    help="do the attribute fixes only")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))

    print("1. bare pads excluded from BOM and position files:")
    for ref in NOT_PLACED:
        fp = next((f for f in board.Footprints()
                   if f.GetReference() == ref), None)
        if fp is None:
            print(f"   {ref}: not on board")
            continue
        fp.SetAttributes(fp.GetAttributes() | EXCLUDE | pcbnew.FP_SMD)
        print(f"   {ref}  {fp.GetFPID().GetLibItemName().wx_str()}")

    print("\n2. unspecified footprint attributes set to SMD:")
    for fp in board.Footprints():
        a = fp.GetAttributes()
        if not (a & pcbnew.FP_SMD) and not (a & pcbnew.FP_THROUGH_HOLE):
            fp.SetAttributes(a | pcbnew.FP_SMD)
            print(f"   {fp.GetReference()}")

    existing = [f for f in board.Footprints()
                if f.GetReference().startswith("FID")]
    if args.no_fiducials:
        print("\n3. fiducials: skipped (--no-fiducials)")
    elif existing:
        print(f"\n3. fiducials: {len(existing)} already present, "
              f"leaving alone")
    else:
        poly = pcbnew.SHAPE_POLY_SET()
        board.GetBoardPolygonOutlines(poly)
        bb = poly.BBox()
        ox, oy = bb.GetLeft(), bb.GetTop()
        print("\n3. fiducials added (1 mm copper, 2 mm mask opening):")
        n = 0
        for layer, sites in FIDUCIALS.items():
            for x, y in sites:
                fp = pcbnew.FootprintLoad(FID_LIB, FID_FP)
                if fp is None:
                    raise SystemExit(f"cannot load {FID_FP} from {FID_LIB}")
                n += 1
                fp.SetReference(f"FID{n}")
                board.Add(fp)
                fp.SetPosition(pcbnew.VECTOR2I(ox + pcbnew.FromMM(x),
                                               oy + pcbnew.FromMM(y)))
                if layer == pcbnew.B_Cu:
                    fp.Flip(fp.GetPosition(), False)
                fp.SetAttributes(fp.GetAttributes() | EXCLUDE)
                fp.Reference().SetVisible(False)
                print(f"   FID{n}  {board.GetLayerName(layer):5s} "
                      f"({x:5.1f}, {y:5.1f}) mm")

    print("\nREMINDER: the board is NOT ROUTED -- 0 segments, 157 unconnected."
          "\nNone of the above makes it fabricable. See TODO.md 12.5.w.")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    board.Save(str(PCB))
    print(f"\nsaved {PCB.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
