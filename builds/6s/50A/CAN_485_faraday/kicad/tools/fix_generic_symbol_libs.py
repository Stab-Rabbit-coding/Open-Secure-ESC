#!/usr/bin/env python3
"""Give this repo ownership of the generic R/C/connector/flag symbols.

Clears the 32 `lib_symbol_mismatch` ERC warnings on the build schematic.

THE PROBLEM
-----------
kicad/README.md states that the generic support parts are "KiCad's own
standard `Device:R` / `Device:C` / `Device:C_Polarized` /
`Connector_Generic:Conn_01x0N` parts". They are not. `tools/genlib.py`
authored its own stand-ins and stored them under KiCad's library names, and
their pin geometry differs from the real KiCad 9.0 symbols:

    symbol                pin 1 (embedded)   pin 1 (KiCad 9.0)
    Device:R              (0,  6.35)         (0,  3.81)
    Device:C              (0,  6.35)         (0,  3.81)
    Device:C_Polarized    (0,  6.35) "+"     (0,  3.81) "~"
    Connector_Generic:Conn_01x02   (-8.89, 3.81)   (-5.08, 0)
    power:PWR_FLAG        (0, -6.35)         (0,  0)

KiCad therefore compares each placed symbol against the real library, finds
a difference, and raises `lib_symbol_mismatch` -- 32 of them.

WHY NOT JUST PULL IN THE REAL KICAD SYMBOLS
--------------------------------------------
Because every pin would move 2.54 mm (and 3.81 mm on the connectors), and
every wire already drawn to those pins would come loose. The committed sheet's
wiring is verified work; silently re-seating 32 symbols to chase a cosmetic
warning is a far larger risk than the warning itself.

WHAT THIS DOES INSTEAD
----------------------
Writes the definitions that are actually in use into a repo-owned library,
`symbols/Open_Secure_ESC_Generic.kicad_sym`, and repoints the schematic's
lib_ids at it. Nothing moves, no net changes, and the schematic now matches
the library it names -- which is the honest description of what these parts
have been all along. `sym-lib-table` gains the new nickname.

PWR_FLAG is included in the move. That is checked rather than assumed: KiCad
recognises a power flag by its symbol's `power` marker and its `power_out`
pin type, not by the library it came from, so the four flags that already
drive VM / 3V3 / GND must keep working afterwards. Re-run ERC and confirm the
`power_pin_not_driven` count does not rise -- if it does, this rename is wrong
and must be reverted.

Usage:
    python3 tools/fix_generic_symbol_libs.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) during the 2026-08-15 layout pass,
# TODO.md 12.4. AI-generated; reviewed against the primary sources named
# in the docstring above. Not human-authored.


import argparse
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
KICAD_DIR = HERE.parent
REPO = KICAD_DIR.parents[4]
SCH = KICAD_DIR / "open_secure_esc_6s_50a_can485_faraday.kicad_sch"
SYM_LIB_TABLE = KICAD_DIR / "sym-lib-table"
NEW_LIB_NAME = "Open_Secure_ESC_Generic"
NEW_LIB = REPO / "symbols" / f"{NEW_LIB_NAME}.kicad_sym"

# lib_id -> entry name. Every one of these is a genlib.py stand-in, not the
# KiCad system part whose name it currently borrows.
MOVE: dict[str, str] = {
    "Device:R": "R",
    "Device:C": "C",
    "Device:C_Polarized": "C_Polarized",
    "Connector_Generic:Conn_01x02": "Conn_01x02",
    "Connector_Generic:Conn_01x03": "Conn_01x03",
    "Connector_Generic:Conn_01x04": "Conn_01x04",
    "power:PWR_FLAG": "PWR_FLAG",
}

# KiCad's S-expression reader rejects Lisp-style ";;" comments in a
# .kicad_sym file (it reports every symbol as missing), so the provenance note
# lives in each symbol's Description property and in this script instead.
HEADER = "(kicad_symbol_lib (version 20211014) (generator open_secure_esc_symgen)\n"


def span(text: str, start: int) -> int:
    """Index just past the S-expression that opens at or after `start`."""
    depth, i = 0, text.index("(", start)
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced S-expression")


def extract_symbols(text: str) -> dict[str, str]:
    """Pull each direct child (symbol "NAME" ...) out of a lib_symbols body.

    Indentation-agnostic: the sheet is written with tabs by KiCad itself but
    with spaces by kiutils, so nesting is found by paren depth, not layout.
    """
    out: dict[str, str] = {}
    # `text` starts at the "(lib_symbols" paren itself, so its direct children
    # -- the symbol entries -- sit at depth 2.
    depth = 0
    i = text.index("(")
    while i < len(text):
        ch = text[i]
        if ch == "(":
            depth += 1
            if depth == 2:
                m = re.match(r'\(symbol\s+"([^"]+)"', text[i:])
                if m:
                    end = span(text, i)
                    out[m.group(1)] = text[i:end]
                    i = end
                    depth -= 1
                    continue
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return out


def reindent(block: str) -> str:
    """Re-indent a lib_symbols entry for a standalone library (2 spaces)."""
    lines = []
    for line in block.split("\n"):
        stripped = line.lstrip(" \t")
        pad = line[: len(line) - len(stripped)]
        depth = pad.count("\t") + len(pad.replace("\t", "")) // 2
        lines.append("  " * max(depth - 1, 0) + stripped)
    return "\n".join(lines)


def main() -> int:
    """Write the repo-owned library and repoint the schematic at it."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    text = SCH.read_text(encoding="utf-8")
    lib_start = text.index("(", text.index("(lib_symbols") - 1)
    lib_block = text[lib_start:span(text, lib_start)]

    blocks = extract_symbols(lib_block)
    # lib_symbols entries are keyed by full lib_id ("Device:R"); a standalone
    # .kicad_sym uses the bare name ("R"), including for its unit sub-symbols
    # ("Device:R_0_1" -> "R_0_1"), so both are rewritten on the way out.
    wanted = {}
    for lib_id, entry in MOVE.items():
        if lib_id not in blocks:
            print(f"  note: {lib_id} not embedded in this sheet, skipping")
            continue
        wanted[entry] = blocks[lib_id].replace(f'"{lib_id}', f'"{entry}')

    lib_text = HEADER + "\n".join(reindent(b) for b in wanted.values()) + "\n)\n"

    # Repoint every lib_id, in both the lib_symbols cache and the instances.
    new_text = text
    for lib_id, entry in MOVE.items():
        if entry not in wanted:
            continue
        new_text = new_text.replace(f'"{lib_id}"', f'"{NEW_LIB_NAME}:{entry}"')
        print(f"  repointed {lib_id:32} -> {NEW_LIB_NAME}:{entry}")

    # sym-lib-table entry.
    table = SYM_LIB_TABLE.read_text(encoding="utf-8")
    if NEW_LIB_NAME not in table:
        entry = (
            f'  (lib (name "{NEW_LIB_NAME}")(type "KiCad")'
            f'(uri "${{KIPRJMOD}}/../../../../../symbols/{NEW_LIB_NAME}.kicad_sym")'
            f'(options "")(descr "Generic support symbols (R, C, C_Polarized, '
            f'Conn_01x02/03/04, PWR_FLAG) authored by tools/genlib.py. These are '
            f'this repo\'s own parts, NOT KiCad\'s Device:/Connector_Generic:/power: '
            f'symbols -- their pin geometry differs. See '
            f'tools/fix_generic_symbol_libs.py."))\n'
        )
        table = table.rstrip()[:-1].rstrip() + "\n" + entry + ")\n"

    if args.dry_run:
        print(f"dry run -- would write {len(wanted)} symbols to {NEW_LIB}")
        return 0

    NEW_LIB.write_text(lib_text, encoding="utf-8")
    SCH.write_text(new_text, encoding="utf-8")
    SYM_LIB_TABLE.write_text(table, encoding="utf-8")
    print(f"wrote {NEW_LIB} ({len(wanted)} symbols)")
    print(f"wrote {SCH}")
    print(f"wrote {SYM_LIB_TABLE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
