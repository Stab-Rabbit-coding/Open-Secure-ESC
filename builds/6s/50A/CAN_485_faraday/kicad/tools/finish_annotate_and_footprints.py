#!/usr/bin/env python3
"""Annotate the build schematic and assign every remaining footprint.

Closes TODO.md 12.3.i ("Annotate the sheet. Every reference ... is still
`R?`/`C?`/`U?`, which is why a netlist export collapses passives") and the
"No footprint for U5 (DRV8353S)" gap in kicad/README.md's "What's still
missing".

This is a TARGETED modification of the committed
`open_secure_esc_6s_50a_can485_faraday.kicad_sch`, not a regeneration. That is
deliberate: `tools/gen_schematic.py` carries a DIVERGENCE WARNING saying it is
no longer the sole author of that file (the OPTIGA(TM) Trust M block was added
afterwards by `tools/inject_optiga_secure_element.py`, and KiCad itself has
opened and re-saved the sheet). Regenerating would silently drop verified
work, which is exactly what AGENTS.md Sec.1.3 exists to prevent. The pattern
used here is the one that file recommends: extend/patch the committed sheet.

WHAT THIS SCRIPT DOES
---------------------
1. Annotates all 57 symbol instances. Reference designators for the ICs are
   pinned to the values the existing documentation already uses, so that
   docs/secure-element-architecture.md, kicad/README.md and ../README.md stay
   correct without being rewritten:

       U1  MSPM0G3518-Q1 MCU        (sym-lib-table: "Project MCU as of 2026-08-10")
       U2  OPTIGA(TM) Trust M       (TODO.md 12.3, "the `U2` designator the SLB9672 vacated")
       U3  ADM3055E/ADM3057E CAN-FD
       U4  ADM2582E/ADM2587E RS-485
       U5  DRV8353S gate driver     (kicad/README.md, "No footprint for U5 (DRV8353S)")
       U6..U8  INA240 current-sense amplifiers
       R1..R3  WSLP2512 shunts      (the three per-phase 1 mOhm shunts)
       R4..     generic pull-ups / dividers
       Q1..Q6   IRFB4110PBF power MOSFETs
       BT1..BT6 INR21700-P42A cells (kicad/README.md "Battery pack representation")
       SH1      WE-SHC 3670375 FRAME (the soldered piece)
       SH2      WE-SHC 3671375 COVER (clips onto the frame)

   Everything else is numbered in reading order (top-to-bottom, then
   left-to-right) so the result is stable and reproducible across re-runs.

2. Assigns the two footprints this repo has just authored from primary
   mechanical drawings:

       U5  -> Open_Secure_ESC:TI_RTA0040B_WQFN-40_6x6mm_P0.5mm_EP4.15x4.15mm
              (symbols/tools/gen_drv8353s_rta0040b_footprint.py, from TI
              SLVSDY6A drawing 4219112/A -- REFERENCES.md [21])
       SH1 -> Open_Secure_ESC:Wurth_WE-SHC_3670375_Frame_29.3x37.5mm
              (symbols/tools/gen_we_shc_3670375_footprint.py, from Wurth
              rev. ViM 002.000 -- REFERENCES.md [30])

3. Marks the parts that are genuinely not board-mounted as "exclude from
   board", so KiCad stops expecting a footprint for them and the PCB netlist
   is honest about what is actually on the PCB:

       BT1..BT6  a 21700 cell pack is an external assembly. kicad/README.md
                 already documents this ("not placed on the PCB -- a 21700
                 cell pack is physically an external assembly"); this just
                 makes the schematic itself say so.
       SH2       the WE-SHC COVER is not soldered. Its datasheet has no land
                 pattern at all, because it clips onto the FRAME (both
                 datasheets: "Assembly with Frame: Frame (3670375), Cover
                 (3671375)"). Only SH1, the frame, is a board-mounted part.
                 Inventing a land pattern for the cover would be a fabricated
                 design decision under AGENTS.md Sec.1.3.

   Both stay `in_bom` -- they must still be ordered.

Usage:
    python3 tools/finish_annotate_and_footprints.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) during the 2026-08-15 layout pass,
# TODO.md 12.4. AI-generated; reviewed against the primary sources named
# in the docstring above. Not human-authored.


import argparse
import sys
from collections import defaultdict
from pathlib import Path

from kiutils.schematic import Schematic

HERE = Path(__file__).resolve().parent
SCH = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_sch"

# --------------------------------------------------------------------------
# Reference designators pinned by lib_id, so existing docs stay accurate.
# Where several instances share a lib_id they are ordered by position and
# numbered in sequence starting from the number given here.
# --------------------------------------------------------------------------
PINNED: dict[str, tuple[str, int]] = {
    "MSPM0G3518_Q1_PM:MSPM0G3518_Q1_PM": ("U", 1),
    "OPTIGA_TRUST_M:OPTIGA_TRUST_M": ("U", 2),
    "ADM3055E_ADM3057E:ADM3055E_ADM3057E": ("U", 3),
    "ADM2582E_ADM2587E:ADM2582E_ADM2587E": ("U", 4),
    "DRV8353S:DRV8353S": ("U", 5),
    "INA240:INA240": ("U", 6),          # U6, U7, U8
    "WSLP2512:WSLP2512": ("R", 1),      # R1, R2, R3 -- the three phase shunts
    "IRFB4110PBF:IRFB4110PBF": ("Q", 1),
    "INR21700_P42A:INR21700_P42A": ("BT", 1),
    "WE_SHC_3670375:WE_SHC_3670375": ("SH", 1),   # FRAME  -- soldered
    "WE_SHC_3671375:WE_SHC_3671375": ("SH", 2),   # COVER  -- clips on
}

# Everything not pinned above is numbered from this starting point, in
# reading order, using the prefix already on the symbol ("R?" -> "R").
FREE_START: dict[str, int] = {
    "R": 4,     # R1..R3 are the WSLP2512 shunts
    "C": 1,
    "J": 1,
    "U": 9,     # U1..U8 are pinned above
    "Q": 7,
    "BT": 7,
    "SH": 3,
}

FOOTPRINTS: dict[str, str] = {
    "U5": "Open_Secure_ESC:TI_RTA0040B_WQFN-40_6x6mm_P0.5mm_EP4.15x4.15mm",
    "SH1": "Open_Secure_ESC:Wurth_WE-SHC_3670375_Frame_29.3x37.5mm",
}

# Parts that exist in the BOM but are not mounted on this PCB.
EXCLUDE_FROM_BOARD: set[str] = {"BT1", "BT2", "BT3", "BT4", "BT5", "BT6", "SH2"}

# Symbols that are drawing annotations rather than parts. KiCad's convention
# is a '#'-prefixed reference plus in_bom/on_board cleared; the generator that
# produced this sheet left them as ordinary parts ("FLG?", in_bom yes,
# on_board yes), which would have put eight non-existent components into the
# BOM and made the PCB expect eight footprints that do not exist.
VIRTUAL_LIB_IDS: set[str] = {"power:PWR_FLAG"}


def prop(sym, key: str):
    """Return the named property object on a symbol, or None."""
    for p in sym.properties:
        if p.key == key:
            return p
    return None


def prefix_of(sym) -> str:
    """Reference prefix of a symbol, e.g. 'R' from 'R?' or 'R12'."""
    ref = prop(sym, "Reference").value
    return ref.rstrip("?0123456789")


def set_reference(sym, ref: str) -> None:
    """Write a reference designator to both places KiCad stores it."""
    prop(sym, "Reference").value = ref
    for inst in sym.instances:
        for path in inst.paths:
            path.reference = ref


def assign(symbols) -> dict[str, str]:
    """Compute a stable reference for every symbol. Returns uuid -> ref."""
    # Power flags are virtual: they carry no footprint and must not reach the
    # BOM or the board. KiCad marks such symbols with a leading '#', which the
    # generator that produced this sheet omitted -- see fix_power_flags().
    real = [s for s in symbols if s.libId not in VIRTUAL_LIB_IDS]

    # Reading order: top-to-bottom, then left-to-right.
    def reading_order(s):
        return (round(s.position.Y, 3), round(s.position.X, 3))

    out: dict[str, str] = {}
    counters: dict[str, int] = dict(FREE_START)

    # Pass 1 -- pinned lib_ids, numbered from their pinned start.
    by_lib: dict[str, list] = defaultdict(list)
    for s in real:
        if s.libId in PINNED:
            by_lib[s.libId].append(s)
    for lib_id, group in by_lib.items():
        pfx, start = PINNED[lib_id]
        for i, s in enumerate(sorted(group, key=reading_order)):
            out[s.uuid] = f"{pfx}{start + i}"

    # Pass 2 -- everything else, in reading order, per prefix.
    for s in sorted(real, key=reading_order):
        if s.uuid in out:
            continue
        pfx = prefix_of(s)
        n = counters.get(pfx, 1)
        counters[pfx] = n + 1
        out[s.uuid] = f"{pfx}{n}"
    return out


def main() -> int:
    """Annotate, assign footprints, and set board-exclusion flags."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report the changes without writing the file")
    args = ap.parse_args()

    sch = Schematic().from_file(str(SCH))
    refs = assign(sch.schematicSymbols)

    # Guard: a duplicate reference would silently merge two parts on the PCB.
    seen: dict[str, str] = {}
    for uuid_, ref in refs.items():
        if ref in seen:
            print(f"ERROR: duplicate reference {ref}", file=sys.stderr)
            return 1
        seen[ref] = uuid_

    # Virtual symbols: '#'-prefixed reference, out of the BOM, off the board.
    flags = [s for s in sch.schematicSymbols if s.libId in VIRTUAL_LIB_IDS]
    for i, sym in enumerate(sorted(flags,
                                   key=lambda s: (round(s.position.Y, 3),
                                                  round(s.position.X, 3))), 1):
        set_reference(sym, f"#FLG{i:02d}")
        sym.inBom = False
        sym.onBoard = False
    if flags:
        print(f"  virtual    {len(flags)} PWR_FLAG symbols -> #FLGnn, "
              f"out of BOM, off board")

    changed = 0
    for sym in sch.schematicSymbols:
        ref = refs.get(sym.uuid)
        if ref is None:
            continue          # power flag, left to KiCad's own numbering
        old = prop(sym, "Reference").value
        if old != ref:
            set_reference(sym, ref)
            changed += 1

        fp = FOOTPRINTS.get(ref)
        if fp is not None:
            fp_prop = prop(sym, "Footprint")
            if fp_prop.value != fp:
                fp_prop.value = fp
                print(f"  footprint  {ref:5} -> {fp}")

        if ref in EXCLUDE_FROM_BOARD:
            if sym.onBoard:
                sym.onBoard = False
                print(f"  off-board  {ref:5} (stays in BOM)")

    print(f"annotated {changed} symbols "
          f"({len(refs)} total, power flags excluded)")

    if args.dry_run:
        print("dry run -- nothing written")
        return 0

    sch.to_file(str(SCH))
    print(f"wrote {SCH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
