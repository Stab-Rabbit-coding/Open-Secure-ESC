#!/usr/bin/env python3
"""Wire the isolated supplies of U3/U4 through their required ferrite beads.

Governed by AGENTS.md. Closes TODO.md 12.5.ad, and with it the two
`global_label_dangling` ERC warnings the kicad/README.md has carried since
2026-08-15.

THIS IS NOT AN EMI IMPROVEMENT -- IT IS A BROKEN SUPPLY
--------------------------------------------------------
Before this script, the isolated side of both transceivers was unwired:

    CAN_VISOOUT        U3.19 only        (dangling)
    CAN_VISOIN_OPEN    U3.16 only        (dangling)
    CAN_ISO_GND        U3.11,12,15,18,20 (all merged)
    RS485_VISOOUT      U4.12 only        (dangling)
    RS485_VISOIN_OPEN  U4.19 only        (dangling)
    RS485_ISO_GND      U4.11,14,16,20    (all merged)

Both datasheets require VISOOUT to feed VISOIN. [10] p.15: "Connect this pin
through a ferrite bead and short the PCB trace to VISOIN **for operation**."
[9] p.8: "This pin must be connected externally to VISOIN." That connection
did not exist, so neither transceiver's bus side had a supply at all.

Both also require the isolated grounds to be SPLIT, not merged:
  [10] pins 18,20 GNDISO: "Ground for the Isolated DC-to-DC Converter.
       Connect these pins together through one ferrite bead to PCB ground
       (bus side)."   -- bus-side ground is pins 11,15 (GND2).
  [9]  pins 11,14 GND2:   "Ground for Isolated DC-to-DC Converter. It is
       recommended to connect Pin 11 and Pin 14 together through one ferrite
       bead to PCB ground."
  [9]  pin 16 GND2:       "Ground, Bus Side. **Do not connect this pin to
       Pin 14 and Pin 11.**"
The pre-existing net merged exactly the pins [9] forbids merging.

WHAT THIS SCRIPT DOES
---------------------
Adds four BLM15HD182SN1D beads [53] -- the part [10] Table 12 names by number
for this role, 1800 ohm at 100 MHz / 2700 ohm at 1 GHz, meeting [9] p.17's
"approximately 2 kohm between the 100 MHz and 1 GHz frequency range":

    FB1  CAN_VISOOUT   -> CAN_VISOIN      (U3 supply,  19 -> 16)
    FB2  CAN_GNDISO    -> CAN_ISO_GND     (U3 return,  18/20 -> 11/15)
    FB3  RS485_VISOOUT -> RS485_VISOIN    (U4 supply,  12 -> 19)
    FB4  RS485_GNDISO  -> RS485_ISO_GND   (U4 return,  11/14 -> 16/20)

and re-labels the affected pins so the split actually exists in the netlist.
Pin-to-label mapping was derived from geometry, not assumed: right-side pin 11
sits at y = 198.57 (U3) / 418.57 (U4) on a 2.54 mm pitch, and every resulting
label matched the as-built board netlist pin for pin before any edit was made.

CURRENT RATING CHECKED, NOT ASSUMED
------------------------------------
[53] rates the bead at 200 mA with 2.2 ohm max DCR. The beads carry the
isolated-side transceiver supply, not the pack current. [9] Table 14 shows the
ADM2582E has "no current available externally on VISOOUT", i.e. the whole
isolated budget is the internal RS-485 circuitry, and [9]'s own ICC figures
(150 mA at 120 ohm load, 230 mA at 54 ohm load, 16 Mbps) are INPUT-side
current at VCC, upstream of the isolator. Margin is adequate, but the
isolated-side draw should be confirmed against [9] Figure 21 / [10] Figure 26
before production -- flagged in TODO.md.

WHAT THIS SCRIPT DOES NOT DO
----------------------------
The datasheets also require reservoir/decoupling capacitors that this board
does not have: [10] wants 0.22 uF + 10 uF on VISOOUT to GNDISO and 0.01 uF +
0.1 uF on VISOIN; [9] wants 10 uF + 0.1 uF on VISOOUT and 0.1 uF + 0.01 uF
between pins 19 and 20. That is eight more parts on an already-dense board,
and [9] fixes their position relative to these beads ("the C1 capacitor
connects between VISOOUT (Pin 12) and GND2 (Pin 11) on the device side of the
L1 and L2 ferrites"). Left to the repo owner -- TODO.md 12.5.af.

Usage:
    python3 tools/add_isolated_supply_ferrites.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-17, TODO.md 12.5.ad.
# AI-generated. Every pin function quoted above is read from the local copies
# of [9], [10] and [53] in docs/datasheets/. Not human-authored.

import argparse
import shutil
import uuid
from pathlib import Path

from kiutils.items.common import Effects, Font, Position, Property
from kiutils.items.schitems import (Connection, GlobalLabel,
                                    SchematicSymbol, SymbolProjectInstance,
                                    SymbolProjectPath)
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib

HERE = Path(__file__).resolve().parent
SCH = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_sch"
SYMLIB = HERE.parents[5] / "symbols" / "BLM15HD182SN1D.kicad_sym"
BACKUP = SCH.with_suffix(".kicad_sch.pre-ferrite.bak")

PITCH = 2.54
PIN_REACH = 7.62      # BLM15HD182SN1D symbol pins sit at local (+/-7.62, 0)
FLAG_Y = 782.54       # existing PWR_FLAG row; pin lands 6.35 below, label 11.43
FLAG_PIN_DY = 6.35
FLAG_LABEL_DY = 11.43
PIN11_Y = {"U3": 198.57, "U4": 418.57}      # right-side pin 11, measured
LABEL_X = 385.09                             # right-side label column

# (part, pin) -> new global-label text. Only pins whose NET changes appear.
RELABEL = {
    ("U3", 16): "CAN_VISOIN",       # was CAN_VISOIN_OPEN
    ("U3", 18): "CAN_GNDISO",       # was CAN_ISO_GND  -- [10] GNDISO
    ("U3", 20): "CAN_GNDISO",
    ("U4", 11): "RS485_GNDISO",     # was RS485_ISO_GND -- [9] converter side
    ("U4", 14): "RS485_GNDISO",
    ("U4", 19): "RS485_VISOIN",     # was RS485_VISOIN_OPEN
}
# Stray copies of the renamed nets elsewhere on the sheet (the PWR_FLAG row).
RENAME_ANY = {"CAN_VISOIN_OPEN": "CAN_VISOIN",
              "RS485_VISOIN_OPEN": "RS485_VISOIN"}

# ref -> (net on pin 1, net on pin 2, x, y) in a clear area right of U3/U4.
FERRITES = {
    "FB1": ("CAN_VISOOUT", "CAN_VISOIN", 430.0, 200.0),
    "FB2": ("CAN_GNDISO", "CAN_ISO_GND", 430.0, 215.0),
    "FB3": ("RS485_VISOOUT", "RS485_VISOIN", 430.0, 420.0),
    "FB4": ("RS485_GNDISO", "RS485_ISO_GND", 430.0, 435.0),
}
# New nets that end up with only power_in pins; ERC needs a driver marker.
NEW_FLAGS = {"CAN_GNDISO": 539.85, "RS485_GNDISO": 579.85}


def eff(hide=False):
    """Standard text effects for the sheet."""
    return Effects(font=Font(height=1.27, width=1.27), hide=hide)


def pin_y(part, pin):
    """Y of a right-side pin (11..20) on the 2.54 mm pitch."""
    return PIN11_Y[part] + (pin - 11) * PITCH


def main() -> int:
    """Relabel the split nets, then add the four beads and two flags."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sch = Schematic.from_file(str(SCH))

    # --- 1. relabel the pins whose net membership changes ---
    wanted = {(pin_y(p, n), txt) for (p, n), txt in RELABEL.items()}
    hits = 0
    for lb in sch.globalLabels:
        if abs(lb.position.X - LABEL_X) > 0.01:
            continue
        for y, txt in wanted:
            if abs(lb.position.Y - y) < 0.01:
                print(f"   relabel ({lb.position.X:.2f},{lb.position.Y:.2f}) "
                      f"{lb.text} -> {txt}")
                lb.text = txt
                hits += 1
                break
    if hits != len(RELABEL):
        raise SystemExit(f"expected {len(RELABEL)} relabels, matched {hits} "
                         "-- refusing to write a half-rewired sheet")

    # --- 2. rename the stray copies (PWR_FLAG row) ---
    for lb in sch.globalLabels:
        if lb.text in RENAME_ANY:
            print(f"   rename stray ({lb.position.X:.2f},{lb.position.Y:.2f}) "
                  f"{lb.text} -> {RENAME_ANY[lb.text]}")
            lb.text = RENAME_ANY[lb.text]

    # --- 3. place the beads, each pin carrying its net as a global label ---
    proj = sch.schematicSymbols[0].instances[0].name
    sheet = sch.schematicSymbols[0].instances[0].paths[0].sheetInstancePath

    # The sheet needs the bead's symbol definition, not just a reference to it.
    if not any(s.entryName == "BLM15HD182SN1D" for s in sch.libSymbols):
        lib = SymbolLib.from_file(str(SYMLIB))
        sym_def = lib.symbols[0]
        sym_def.libraryNickname = "BLM15HD182SN1D"
        sch.libSymbols.append(sym_def)
        print("   added BLM15HD182SN1D to lib_symbols")

    def instance(ref):
        return [SymbolProjectInstance(name=proj, paths=[SymbolProjectPath(
            sheetInstancePath=sheet, reference=ref, unit=1)])]

    for ref, (net1, net2, x, y) in FERRITES.items():
        sym = SchematicSymbol(
            libraryNickname="BLM15HD182SN1D", entryName="BLM15HD182SN1D",
            position=Position(X=x, Y=y, angle=0),
            unit=1, inBom=True, onBoard=True,
            uuid=str(uuid.uuid4()), instances=instance(ref))
        sym.properties = [
            Property(key="Reference", value=ref,
                     position=Position(X=x, Y=y - 3.81, angle=0), effects=eff()),
            Property(key="Value", value="BLM15HD182SN1D",
                     position=Position(X=x, Y=y + 3.81, angle=0), effects=eff()),
            Property(key="Footprint", value="Inductor_SMD:L_0402_1005Metric",
                     position=Position(X=x, Y=y, angle=0), effects=eff(True)),
            Property(key="Datasheet", value="docs/datasheets/ENFA0024.pdf",
                     position=Position(X=x, Y=y, angle=0), effects=eff(True)),
        ]
        sch.schematicSymbols.append(sym)
        for net, dx, ang in ((net1, -PIN_REACH, 180), (net2, PIN_REACH, 0)):
            sch.globalLabels.append(GlobalLabel(
                text=net, shape="input", uuid=str(uuid.uuid4()),
                position=Position(X=x + dx, Y=y, angle=ang), effects=eff()))
        print(f"   {ref}: {net1} -- {net2}   at ({x}, {y})")

    # --- 4. drivers for the two new isolated-ground nets ---
    flag = next(s for s in sch.schematicSymbols
                if s.entryName == "PWR_FLAG")
    for net, x in NEW_FLAGS.items():
        sym = SchematicSymbol(
            libraryNickname=flag.libraryNickname, entryName=flag.entryName,
            position=Position(X=x, Y=FLAG_Y, angle=0),
            unit=1, inBom=False, onBoard=False,
            uuid=str(uuid.uuid4()), instances=instance("#FLG0"))
        sym.properties = [
            Property(key="Reference", value="#FLG0",
                     position=Position(X=x, Y=FLAG_Y, angle=0),
                     effects=eff(True)),
            Property(key="Value", value="PWR_FLAG",
                     position=Position(X=x, Y=FLAG_Y - 2.54, angle=0),
                     effects=eff()),
        ]
        sch.schematicSymbols.append(sym)
        # Same shape as every other flag on this sheet: pin -> short wire ->
        # global label, rather than a label dropped straight onto the pin.
        sch.graphicalItems.append(Connection(
            type="wire", uuid=str(uuid.uuid4()),
            points=[Position(X=x, Y=FLAG_Y + FLAG_PIN_DY),
                    Position(X=x, Y=FLAG_Y + FLAG_LABEL_DY)]))
        sch.globalLabels.append(GlobalLabel(
            text=net, shape="input", uuid=str(uuid.uuid4()),
            position=Position(X=x, Y=FLAG_Y + FLAG_LABEL_DY, angle=270),
            effects=eff()))
        print(f"   PWR_FLAG on {net} at ({x}, {FLAG_Y})")

    if args.dry_run:
        print("--dry-run: nothing written")
        return 0
    shutil.copy2(SCH, BACKUP)
    sch.to_file(str(SCH))
    print(f"\nwrote {SCH.name} (backup: {BACKUP.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
