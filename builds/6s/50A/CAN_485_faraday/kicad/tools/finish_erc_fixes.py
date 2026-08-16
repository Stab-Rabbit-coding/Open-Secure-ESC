#!/usr/bin/env python3
"""Close the remaining real electrical defects on the build schematic.

Three separate problems, all of which survive into the PCB if left alone.
Every change below is traceable to a primary datasheet or to the sheet's own
stated intent; nothing here silently resolves one of the open design questions
listed in ../README.md.

1. MISSING PULL-UP ON THE GATE-DRIVER SPI READ PATH  (a real bug)
   ---------------------------------------------------------------
   ERC error: "Input pin not driven by any Output pins" at U1 pin 2
   (GD_SPI_MISO). The net is U1.2 (MCU, input) <-> U5.27 (DRV8353S, SDO) and
   nothing else.

   This is NOT a symbol-typing artefact. REFERENCES.md [21] (TI SLVSDY6A),
   "Pin Functions -- 40-Pin DRV8353 Devices", lists SDO on pin 27 with type
   **OD** and the text: "Serial data output. Data is shifted out on the rising
   edge of the SCLK pin. **This pin requires an external pullup resistor.**"
   The same table gives its open-drain ratings (VOD 0-5.5 V, IOD 0-5 mA), and
   the datasheet's "OPEN DRAIN OUTPUTS (nFAULT, SDO)" section groups SDO with
   nFAULT.

   nFAULT already has its pull-up on this sheet (R11, 10k to 3V3). SDO does
   not. As drawn, every SPI register read from the gate driver would fail:
   there is nothing to pull the line high. This script adds R14, 10k to 3V3,
   mirroring R11 exactly -- same rail, same value, same datasheet requirement,
   same open-drain pin group. The 10k VALUE is an engineering default (the
   datasheet specifies no value, only that a pullup is required), consistent
   with how kicad/README.md already treats the generic support passives.

2. THE GATE DRIVER'S EXPOSED THERMAL PAD HAD NO ELECTRICAL EXISTENCE
   ------------------------------------------------------------------
   The new footprint (symbols/tools/gen_drv8353s_rta0040b_footprint.py) has
   pad 41, the exposed thermal pad, because [21]'s RTA0040B drawing note 3
   requires it to be soldered. The DRV8353S SYMBOL had no pin 41, so the pad
   would have been imported with no net -- an isolated copper island directly
   under a part dissipating gate-drive power.

   This adds pin 41 ("PAD", passive) to the symbol and ties it to GND.

   Tying it to GND is an ENGINEERING DEFAULT recorded per AGENTS.md Sec.4, not
   a datasheet assignment: [21] mandates soldering the pad and Sec. 11.1
   requires a ground-plane connection at the GND pin, but it does not state in
   so many words that the exposed pad is internally common with GND. This also
   deliberately diverges from how the OPTIGA Trust M's exposed pad is modelled
   in this repo (unnumbered, netless) -- that part is a low-power secure
   element, this one is the power stage's gate driver.

3. FOUR POWER FLAGS THAT NEVER REACHED THEIR RAILS
   -------------------------------------------------
   ERC errors: 4x "power_pin_not_driven" on the two transceivers' isolated
   sides, plus 4x "pin_not_connected" on #FLG04..#FLG07, plus 4x
   "unconnected_wire_endpoint".

   The generator's intent is unambiguous -- four flags sitting in a row at the
   bottom of the sheet, and four very long vertical wires (350-588 mm) aimed
   up at exactly the four isolated-side pins. They miss: the wires sit at
   x = 381.51..381.54 while the flag pins are at x = 339.85 / 379.85 / 419.85 /
   459.85, and one wire's top end is 2.54 mm short of its pin.

   The long wires are deleted and each flag is instead given a short stub and
   a global label naming its rail. That is standard KiCad practice for a
   multi-drop rail, it is what the rest of this sheet already does, and it
   removes 588 mm wires that cross the whole drawing.

   This does NOT decide the open transceiver-variant question from
   ../README.md. A PWR_FLAG asserts only "this rail is driven from somewhere
   off-sheet", which is exactly true: whether the isolated side is fed by the
   ADM3057E's integrated DC-DC or by an external isolated supply for the
   ADM3055E is still open, and the nets keep their "_OPEN" names.

Usage:
    python3 tools/finish_erc_fixes.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) during the 2026-08-15 layout pass,
# TODO.md 12.4. AI-generated; reviewed against the primary sources named
# in the docstring above. Not human-authored.


import argparse
import copy
import uuid
from pathlib import Path

from kiutils.items.common import (
    Effects, Font, Justify, Position, Property, Stroke,
)
from kiutils.items.schitems import Connection, GlobalLabel
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib, SymbolPin

HERE = Path(__file__).resolve().parent
KICAD_DIR = HERE.parent
REPO = KICAD_DIR.parents[4]
SCH = KICAD_DIR / "open_secure_esc_6s_50a_can485_faraday.kicad_sch"
DRV_LIB = REPO / "symbols" / "DRV8353S.kicad_sym"

GRID = 1.27

# --- 1. SDO pull-up -------------------------------------------------------
# Placed in the same column as R11 (the nFAULT pull-up, at y=472.54) and one
# 40 mm row below it, matching the spacing already used between R9 and R11.
R14_POS = (629.85, 512.54)
R14_VALUE = "10k"
MISO_NET = "GD_SPI_MISO"

# --- 2. Gate-driver thermal pad -------------------------------------------
# Symbol-internal slot: the left side already runs from y=-11.43 up to 16.51,
# so -13.97 is the next free 2.54 mm slot below the lowest existing pin.
PAD_PIN_NUMBER = "41"
PAD_PIN_NAME = "PAD"
PAD_PIN_XY = (-17.78, -13.97)

# --- 3. Isolated-side power flags -----------------------------------------
# Flag reference -> the rail it declares as externally driven.
# The mapping is read off the broken routes' own geometry rather than guessed:
# each flag's long vertical leg stops at the Y of exactly one isolated-side
# pin, which identifies the rail the generator was aiming at.
#
#   flag      leg top Y     pin at that Y                     rail
#   #FLG04    201.11        U3.11 GND2   @ (380.01, 198.57)   CAN_ISO_GND
#   #FLG05    418.57        U4.11 GND2   @ (380.01, 418.57)   RS485_ISO_GND
#   #FLG06    211.27        U3.16 VISOIN @ (380.01, 211.27)   CAN_VISOIN_OPEN
#   #FLG07    438.89        U4.19 VISOIN @ (380.01, 438.89)   RS485_VISOIN_OPEN
#
# Every leg lands on the right Y and the wrong X -- they sit in a collector
# column at x = 381.51..381.54 while the pins are at x = 380.01, so not one of
# the four ever touched its pin.
FLAG_RAILS: dict[str, str] = {
    "#FLG04": "CAN_ISO_GND",
    "#FLG05": "RS485_ISO_GND",
    "#FLG06": "CAN_VISOIN_OPEN",
    "#FLG07": "RS485_VISOIN_OPEN",
}
# Each broken route has three segments: a short drop off the flag pin, a
# horizontal run into the collector column, and the long vertical leg. All
# four routes -- and only those four -- pass through this column, so it is
# what identifies them. The other four flags on the same row are correctly
# wired to VM / 3V3 / GND through different columns and must not be touched.
COLLECTOR_COLUMN = (381.4, 381.7)
FLAG_DROP_Y_BAND = (788.8, 789.4)


def eff(justify: str | None = None) -> Effects:
    """Standard 1.27 mm text effects, optionally justified."""
    return Effects(
        font=Font(width=1.27, height=1.27),
        justify=Justify(horizontally=justify),
    )


def prop_of(sym, key: str):
    """Return the named property object on a schematic symbol, or None."""
    for p in sym.properties:
        if p.key == key:
            return p
    return None


def ref_of(sym) -> str:
    """Reference designator of a schematic symbol."""
    return prop_of(sym, "Reference").value


def add_wire(sch: Schematic, x1: float, y1: float, x2: float, y2: float) -> None:
    """Draw a real wire segment between two sheet points."""
    sch.graphicalItems.append(Connection(
        type="wire",
        points=[Position(X=x1, Y=y1), Position(X=x2, Y=y2)],
        stroke=Stroke(width=0, type="default"),
        uuid=str(uuid.uuid4()),
    ))


def add_global_label(sch: Schematic, text: str, x: float, y: float,
                     angle: float, justify: str) -> None:
    """Place a global label at a sheet point."""
    # Mirrors the shape/effects/Intersheetrefs pattern of the 139 global
    # labels the generator already placed on this sheet.
    sch.globalLabels.append(GlobalLabel(
        text=text,
        shape="passive",
        position=Position(X=x, Y=y, angle=angle),
        effects=eff(justify),
        uuid=str(uuid.uuid4()),
        properties=[Property(
            key="Intersheetrefs",
            value="${INTERSHEET_REFS}",
            position=Position(X=x, Y=y, angle=0),
            effects=eff(),
            showName=False,
        )],
    ))


def make_pad_pin() -> SymbolPin:
    """The exposed-thermal-pad pin, identical for library and sheet cache."""
    return SymbolPin(
        electricalType="passive",
        graphicalStyle="line",
        position=Position(X=PAD_PIN_XY[0], Y=PAD_PIN_XY[1], angle=0),
        length=2.54,
        name=PAD_PIN_NAME,
        nameEffects=eff(),
        number=PAD_PIN_NUMBER,
        numberEffects=eff(),
    )


def add_pad_pin(sym) -> bool:
    """Append the thermal-pad pin to a DRV8353S symbol. False if already there."""
    if any(p.number == PAD_PIN_NUMBER for u in sym.units for p in u.pins):
        return False
    next(u for u in sym.units if u.pins).pins.append(make_pad_pin())
    return True


def add_pad_pin_to_library() -> bool:
    """Add pin 41 (exposed thermal pad) to symbols/DRV8353S.kicad_sym."""
    lib = SymbolLib().from_file(str(DRV_LIB))
    for sym in lib.symbols:
        if sym.entryName != "DRV8353S":
            continue
        if not add_pad_pin(sym):
            return False            # already present, nothing to do
        lib.to_file(str(DRV_LIB))
        return True
    raise SystemExit("DRV8353S not found in its own library")


def main() -> int:
    """Apply all three fixes to the schematic (and to the DRV8353S library)."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sch = Schematic().from_file(str(SCH))
    by_ref = {ref_of(s): s for s in sch.schematicSymbols}

    # ---- 3a. Delete the four stray long wires ---------------------------
    col_lo, col_hi = COLLECTOR_COLUMN
    drop_lo, drop_hi = FLAG_DROP_Y_BAND
    broken_x = {round(by_ref[r].position.X, 2) for r in FLAG_RAILS}

    def is_broken_route(item) -> bool:
        """True for the 12 segments making up the four failed flag routes."""
        pts = getattr(item, "points", None)
        if not pts or len(pts) != 2:
            return False
        # The vertical legs and the horizontal runs both terminate in the
        # collector column.
        if any(col_lo <= p.X <= col_hi for p in pts):
            return True
        # The short drop segment off each broken flag's own pin.
        return (all(round(p.X, 2) in broken_x for p in pts)
                and all(drop_lo <= p.Y <= drop_hi for p in pts))

    before = len(sch.graphicalItems)
    kept = [g for g in sch.graphicalItems if not is_broken_route(g)]
    sch.graphicalItems = kept
    removed = before - len(kept)
    print(f"  removed {removed} segments of the four failed flag routes")
    if removed != 12:
        raise SystemExit(
            f"expected to remove exactly 12 segments (4 routes x 3), got "
            f"{removed} -- refusing to write a sheet with unverified deletions"
        )

    # ---- 3b. Give each flag a stub and a rail label ----------------------
    for ref, rail in FLAG_RAILS.items():
        flag = by_ref[ref]
        # PWR_FLAG's pin sits at symbol-internal (0, -6.35); sheet Y is
        # inverted relative to symbol Y, so the pin is 6.35 mm BELOW the body.
        px, py = flag.position.X, flag.position.Y + 6.35
        add_wire(sch, px, py, px, py + 5.08)
        add_global_label(sch, rail, px, py + 5.08, 270, "left")
        print(f"  {ref} -> {rail}")

    # ---- 1. R14, the SDO pull-up ----------------------------------------
    if "R14" not in by_ref:
        template = by_ref["R11"]            # the nFAULT pull-up: same part
        r14 = copy.deepcopy(template)
        r14.uuid = str(uuid.uuid4())
        r14.position = Position(X=R14_POS[0], Y=R14_POS[1], angle=0)
        for p in r14.properties:
            if p.key == "Reference":
                p.value = "R14"
            elif p.key == "Value":
                p.value = R14_VALUE
            elif p.key == "Note":
                p.value = (
                    "Pull-up required by REFERENCES.md [21] Pin Functions: "
                    "DRV8353S SDO (pin 27) is an open-drain output and "
                    "'requires an external pullup resistor'. Value 10k is an "
                    "engineering default matched to R11 (nFAULT), not a "
                    "datasheet value."
                )
            # Property positions are relative to the symbol origin in kiutils'
            # model only for display; re-seat them onto the new location.
            p.position = Position(
                X=R14_POS[0] + (p.position.X - template.position.X),
                Y=R14_POS[1] + (p.position.Y - template.position.Y),
                angle=p.position.angle,
            )
        for inst in r14.instances:
            for path in inst.paths:
                path.reference = "R14"
        sch.schematicSymbols.append(r14)

        # Pin 1 (symbol-internal y=+6.35) is the upper pin on the sheet.
        top = (R14_POS[0], R14_POS[1] - 6.35)
        bot = (R14_POS[0], R14_POS[1] + 6.35)
        add_wire(sch, top[0], top[1], top[0], top[1] - 5.08)
        add_global_label(sch, "3V3", top[0], top[1] - 5.08, 90, "left")
        add_wire(sch, bot[0], bot[1], bot[0], bot[1] + 5.08)
        add_global_label(sch, MISO_NET, bot[0], bot[1] + 5.08, 270, "left")
        print(f"  added R14 {R14_VALUE} pull-up on {MISO_NET} (see [21])")

        # Name the existing MISO net so the pull-up joins it. U5's SDO pin is
        # symbol-internal (-17.78, 11.43); sheet Y is inverted.
        u5 = by_ref["U5"]
        add_global_label(sch, MISO_NET,
                         u5.position.X - 17.78, u5.position.Y - 11.43,
                         180, "right")

    # ---- 2. Thermal pad pin, and its tie to GND -------------------------
    u5 = by_ref["U5"]
    pad_x = u5.position.X + PAD_PIN_XY[0]
    pad_y = u5.position.Y - PAD_PIN_XY[1]
    add_wire(sch, pad_x, pad_y, pad_x - 5.08, pad_y)
    add_global_label(sch, "GND", pad_x - 5.08, pad_y, 180, "right")
    print(f"  U5 pin {PAD_PIN_NUMBER} ({PAD_PIN_NAME}) tied to GND "
          f"at ({pad_x:.2f}, {pad_y:.2f})")

    if args.dry_run:
        print("dry run -- nothing written")
        return 0

    if add_pad_pin_to_library():
        print(f"  added pin {PAD_PIN_NUMBER} to {DRV_LIB.name}")

    # The sheet caches its own copy of every library symbol. It must gain the
    # same pin, or KiCad raises lib_symbol_mismatch on U5 and the pad still
    # never reaches the netlist.
    for cached in sch.libSymbols:
        if cached.entryName.endswith("DRV8353S") and add_pad_pin(cached):
            print(f"  added pin {PAD_PIN_NUMBER} to the sheet's cached DRV8353S")

    sch.to_file(str(SCH))
    print(f"wrote {SCH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
