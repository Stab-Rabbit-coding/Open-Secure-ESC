#!/usr/bin/env python3
"""Swap the schematic onto the 30 x 70 mm respin BOM.

Four changes, all decided by the repo owner 2026-08-15/16:

  1. Q1..Q6  IRFB4110PBF (TO-220AB, THT)  ->  TPHR8504PL (2-5W1A SOP Advance(N))
  2. R1..R3  shunt value 1 mOhm -> 0.5 mOhm
  3. C1      bulk cap 10 mm radial THT -> SMD
  4. SH1/SH2 WE-SHC 3670375/3671375 -> the compact 3670209/3671209 pair

THE FET SWAP IS NOT A SYMBOL SUBSTITUTION
------------------------------------------
The two parts have incompatible pin geometry AND incompatible pin numbering:

    IRFB4110PBF          TPHR8504PL
    pin 1  G  left       pin 4      G  left
    pin 2  D  top        pins 5-8   D  top
    pin 3  S  bottom     pins 1-3   S  RIGHT

Source moves from the bottom of the symbol to the right, and drain goes from
one pin to four. Only the gate survives as a single left-side pin.

**The gate wiring is preserved by placement, not by rewiring.** Symbol-internal
gate positions are (-7.62, +2.54) on the old part and (-10.16, 0) on the new
one, so placing the new symbol at (px + 2.54, py - 2.54) puts its gate pin on
the exact sheet coordinate the old gate pin occupied. All six DRV8353S
GHx/GLx connections then survive untouched. That is worth doing deliberately:
re-deriving six gate nets by hand is the kind of edit that silently swaps a
high-side and a low-side gate.

Drain and source ARE rewired, via short stubs and global labels naming the net
each pin belongs to. Every one of those nets already exists on the sheet as a
global label (VM, PH_A/B/C, ISENSE_A/B/C_HI), so this adds no new net names --
it re-attaches the new pins to rails the sheet already carries. Labels are used
rather than drawn routes because this sheet's generator separates parallel runs
by 0.01-0.02 mm lane offsets, and hand-routing into that is how shorts get
made (see tools/snap_to_grid.py).

Net assignments, read from the pre-swap netlist rather than assumed:

    Q1 G=GHA D=VM     S=PH_A          Q2 G=GLA D=PH_A S=ISENSE_A_HI
    Q3 G=GHB D=VM     S=PH_B          Q4 G=GLB D=PH_B S=ISENSE_B_HI
    Q5 G=GHC D=VM     S=PH_C          Q6 G=GLC D=PH_C S=ISENSE_C_HI

Requires: pip install kiutils

Usage:
    python3 tools/respin_30x70_schematic.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-16, TODO.md 12.5.
# AI-generated; part selections are the repo owner's. Not human-authored.

import argparse
import copy
import uuid
from pathlib import Path

from kiutils.items.common import (
    Effects, Font, Justify, Position, Property, Stroke,
)
from kiutils.items.schitems import Connection, GlobalLabel
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib

HERE = Path(__file__).resolve().parent
KICAD_DIR = HERE.parent
REPO = KICAD_DIR.parents[4]
SCH = KICAD_DIR / "open_secure_esc_6s_50a_can485_faraday.kicad_sch"

NEW_FET = "TPHR8504PL"
NEW_FET_FP = ("Open_Secure_ESC:"
              "Toshiba_2-5W1A_SOP-Advance-N_5.15x6.1mm_P1.27mm")

# Gate-pin positions, symbol-internal. The delta between them is the whole
# trick that preserves the gate wiring.
OLD_GATE_XY = (-7.62, 2.54)
NEW_GATE_XY = (-10.16, 0.0)
PLACE_DX = OLD_GATE_XY[0] - NEW_GATE_XY[0]        # +2.54
PLACE_DY = -(OLD_GATE_XY[1] - NEW_GATE_XY[1])     # -2.54  (sheet Y is inverted)

# Per-FET drain and source nets, from the pre-swap netlist.
FET_NETS = {
    "Q1": {"D": "VM",   "S": "PH_A"},
    "Q2": {"D": "PH_A", "S": "ISENSE_A_HI"},
    "Q3": {"D": "VM",   "S": "PH_B"},
    "Q4": {"D": "PH_B", "S": "ISENSE_B_HI"},
    "Q5": {"D": "VM",   "S": "PH_C"},
    "Q6": {"D": "PH_C", "S": "ISENSE_C_HI"},
}

SHUNT_VALUE = "0.5mOhm"
SHUNT_NOTE = (
    "Halved from 1 mOhm 2026-08-16. At the build's 50 A rating a 1 mOhm shunt "
    "dissipates I^2R = 2.5 W into a WSLP2512 rated 3.0 W [23] -- 83% of "
    "rating, continuous, before derating, on a board the reference design [47] "
    "measured at 103 C. 0.5 mOhm halves it to 1.25 W and matches the shunt "
    "value [47] ships. 0.5 mOhm is inside the WSLP2512 range ([23] lists "
    "0.0005 to 0.01 ohm). Sense voltage halves too -- confirm the DRV8353S CSA "
    "gain setting and the INA240 range still resolve the trip threshold."
)

C1_FP = "Capacitor_SMD:C_1210_3225Metric"
C1_NOTE = (
    "Package changed from a 10 mm radial THT can to 1210 SMD 2026-08-16 for "
    "the 30 x 70 mm envelope and double-sided assembly. ENGINEERING DEFAULT, "
    "not a selected part: capacitance/voltage/ESR are unchanged on paper but "
    "no 1210 part has been sourced, and a 1210 will hold far less bulk than "
    "the radial it replaces. The reference design [47] carries 470 uF 63 V "
    "EXTERNAL to the board for exactly this reason. Size the on-board bulk "
    "against the final layout and decide whether external bulk is required."
)

SHIELDS = {
    "SH1": ("WE_SHC_3670209", "WE-SHC 3670209 (frame)",
            "Open_Secure_ESC:Wurth_WE-SHC_3670209_Frame_15.3x20.9mm"),
    "SH2": ("WE_SHC_3671209", "WE-SHC 3671209 (cover)", ""),
}


def eff(justify=None):
    """Standard 1.27 mm text effects."""
    return Effects(font=Font(width=1.27, height=1.27),
                   justify=Justify(horizontally=justify))


def prop_of(sym, key):
    """Named property object on a symbol, or None."""
    return next((p for p in sym.properties if p.key == key), None)


def ref_of(sym):
    """Reference designator of a schematic symbol."""
    return prop_of(sym, "Reference").value


def set_prop(sym, key, value):
    """Set a property, creating it if absent."""
    p = prop_of(sym, key)
    if p is None:
        sym.properties.append(Property(
            key=key, value=value,
            position=Position(X=sym.position.X, Y=sym.position.Y, angle=0),
            effects=eff(), showName=False))
    else:
        p.value = value


def add_wire(sch, x1, y1, x2, y2):
    """Draw a wire segment."""
    sch.graphicalItems.append(Connection(
        type="wire",
        points=[Position(X=x1, Y=y1), Position(X=x2, Y=y2)],
        stroke=Stroke(width=0, type="default"), uuid=str(uuid.uuid4())))


def add_label(sch, text, x, y, angle, justify):
    """Place a global label."""
    sch.globalLabels.append(GlobalLabel(
        text=text, shape="passive",
        position=Position(X=x, Y=y, angle=angle),
        effects=eff(justify), uuid=str(uuid.uuid4()),
        properties=[Property(key="Intersheetrefs", value="${INTERSHEET_REFS}",
                             position=Position(X=x, Y=y, angle=0),
                             effects=eff(), showName=False)]))


def lib_symbol(entry_name):
    """Load one symbol from the shared library, ready to embed in the sheet."""
    lib = SymbolLib().from_file(str(REPO / "symbols" / f"{entry_name}.kicad_sym"))
    sym = next(s for s in lib.symbols if s.entryName == entry_name)
    # Match the sheet's existing convention exactly: libId is "NAME:NAME" and
    # entryName is the derived bare "NAME" -- kiutils computes entryName FROM
    # libId, so setting entryName directly is a no-op. Unit entryNames stay
    # bare too (verified against the embedded DRV8353S and IRFB4110PBF).
    sym.libId = f"{entry_name}:{entry_name}"
    return sym


def pin_sheet_xy(sym_pos, internal_xy):
    """Symbol-internal coordinates -> sheet coordinates (rotation 0)."""
    return (sym_pos.X + internal_xy[0], sym_pos.Y - internal_xy[1])


def main() -> int:
    """Apply all four respin changes to the schematic."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sch = Schematic().from_file(str(SCH))
    by_ref = {ref_of(s): s for s in sch.schematicSymbols}

    # ---- new library symbols into the sheet's cache ---------------------
    cached = {ls.entryName for ls in sch.libSymbols}
    for entry in (NEW_FET, "WE_SHC_3670209", "WE_SHC_3671209"):
        if entry not in cached:
            sch.libSymbols.append(lib_symbol(entry))
            print(f"  cached lib symbol {entry}")

    new_fet_pins = {
        p.number: (p.position.X, p.position.Y)
        for ls in sch.libSymbols if ls.entryName == NEW_FET
        for u in ls.units for p in u.pins
    }

    # ---- 1. the six FETs -------------------------------------------------
    removed = 0
    for ref, nets in FET_NETS.items():
        old = by_ref[ref]
        old_pos = old.position
        old_drain = pin_sheet_xy(old_pos, (0.0, 6.35))
        old_source = pin_sheet_xy(old_pos, (0.0, -6.35))

        # Drop the wire stubs on the old drain/source pins. The gate stub is
        # deliberately left alone -- the new gate pin lands on top of it.
        keep = []
        for item in sch.graphicalItems:
            pts = getattr(item, "points", None)
            if pts and len(pts) == 2 and any(
                    abs(p.X - t[0]) < 0.01 and abs(p.Y - t[1]) < 0.01
                    for p in pts for t in (old_drain, old_source)):
                removed += 1
                continue
            keep.append(item)
        sch.graphicalItems = keep
        # And any label sitting on those points.
        sch.globalLabels = [
            g for g in sch.globalLabels
            if not any(abs(g.position.X - t[0]) < 0.01
                       and abs(g.position.Y - t[1]) < 0.01
                       for t in (old_drain, old_source))
        ]

        old.libId = f"{NEW_FET}:{NEW_FET}"
        old.position = Position(X=old_pos.X + PLACE_DX,
                                Y=old_pos.Y + PLACE_DY, angle=0)
        set_prop(old, "Value", NEW_FET)
        set_prop(old, "Footprint", NEW_FET_FP)
        set_prop(old, "Note",
                 "Toshiba TPHR8504PL, 40 V / 0.7 mOhm / 150 A, 2-5W1A SOP "
                 "Advance(N) [49]. Replaces IRFB4110PBF [20]. 40 V against a "
                 "25.2 V pack is 1.59x, down from 3.97x -- accepted for the "
                 "5.7x conduction-loss improvement; drain overshoot MUST be "
                 "bounded via the DRV8353S IDRIVE setting and bench-measured "
                 "before fab (TODO.md).")

        # Drain: one stub off the outermost drain pin, plus its rail label.
        dx, dy = pin_sheet_xy(old.position, new_fet_pins["8"])
        add_wire(sch, dx, dy, dx, dy - 5.08)
        add_label(sch, nets["D"], dx, dy - 5.08, 90, "left")
        # The other three drain pins are the same node; tie them to pin 8.
        for num in ("7", "6", "5"):
            px, py = pin_sheet_xy(old.position, new_fet_pins[num])
            add_wire(sch, px, py, px, dy - 2.54)
            add_wire(sch, px, dy - 2.54, dx, dy - 2.54)
        add_wire(sch, dx, dy - 2.54, dx, dy)

        # Source: stub off pin 2 (the middle source), tie 1 and 3 to it.
        sx, sy = pin_sheet_xy(old.position, new_fet_pins["2"])
        add_wire(sch, sx, sy, sx + 5.08, sy)
        add_label(sch, nets["S"], sx + 5.08, sy, 0, "left")
        for num in ("1", "3"):
            px, py = pin_sheet_xy(old.position, new_fet_pins[num])
            add_wire(sch, px, py, px + 2.54, py)
            add_wire(sch, px + 2.54, py, px + 2.54, sy)
            add_wire(sch, px + 2.54, sy, sx, sy)

        print(f"  {ref}: -> {NEW_FET}, D={nets['D']}, S={nets['S']}, "
              f"gate preserved")

    print(f"  removed {removed} old drain/source stubs")

    # ---- 2. shunts -------------------------------------------------------
    for ref in ("R1", "R2", "R3"):
        set_prop(by_ref[ref], "Value", SHUNT_VALUE)
        set_prop(by_ref[ref], "Note", SHUNT_NOTE)
    print(f"  R1-R3 -> {SHUNT_VALUE}")

    # ---- 3. bulk capacitor ----------------------------------------------
    set_prop(by_ref["C1"], "Footprint", C1_FP)
    set_prop(by_ref["C1"], "Note", C1_NOTE)
    print(f"  C1 -> {C1_FP}")

    # ---- 4. shields ------------------------------------------------------
    for ref, (entry, value, fp) in SHIELDS.items():
        sym = by_ref[ref]
        sym.libId = f"{entry}:{entry}"
        set_prop(sym, "Value", value)
        set_prop(sym, "Footprint", fp)
        print(f"  {ref} -> {entry}")

    if args.dry_run:
        print("dry run -- nothing written")
        return 0

    sch.to_file(str(SCH))
    print(f"wrote {SCH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
