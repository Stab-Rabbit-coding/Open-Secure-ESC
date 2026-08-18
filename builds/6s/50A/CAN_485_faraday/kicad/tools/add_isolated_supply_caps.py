#!/usr/bin/env python3
"""Add the eight isolated-supply capacitors [9]/[10] require, to the sheet.

Governed by AGENTS.md. Completes TODO.md 12.5.af's schematic half; the
companion PCB step parks every new part off-board for the repo owner to
place.

WHY EIGHT
---------
Both isolators specify reservoir and decoupling capacitors by value and by
which pins they bridge. Quoted from the local datasheet copies:

  [10] p.15, pin 19 VISOOUT : "This pin requires 0.22uF and 10uF capacitors
                               to GNDISO."
  [10] p.15, pin 16 VISOIN  : "This pin requires 0.01uF and 0.1uF decoupling
                               capacitors."
  [9]  p.17                 : "The recommended capacitor values are 0.1 uF
                               and 10 uF for VISOOUT at Pin 11 and Pin 12 ...
                               Capacitor values of 0.01 uF and 0.1 uF are
                               recommended for VISOIN at Pin 19 and Pin 20."

Note the grounds differ per capacitor and are NOT interchangeable now that
the isolated grounds are split (TODO.md 12.5.ad): the VISOOUT reservoirs
return to the dc-to-dc converter ground (GNDISO / GND2 pins 11,14), while the
VISOIN decouplers return to the bus-side ground (GND2 pins 11,15 / 20). [9] is
explicit that this ordering is the point: "Ensure that the C1 capacitor
connects between VISOOUT (Pin 12) and GND2 (Pin 11) on the device side of the
L1 and L2 ferrites."

[9] also asks that "the smaller of the two" be a very low inductance ceramic,
and that "the total lead length between both ends of the capacitor and the
input power supply pin should not exceed 10 mm" -- a placement constraint the
repo owner will have to honour, not something this script can.

PACKAGE AND VOLTAGE ARE ENGINEERING DEFAULTS (AGENTS.md Sec.4)
---------------------------------------------------------------
0805 to match every other decoupling capacitor already on this board
(C2..C10). The datasheets specify capacitance, not package or voltage rating;
the isolated rails run at 3.3 V or 5 V, so any common 16 V/25 V X7R part
suits. No specific MPN is claimed here -- none has been selected, and
inventing one would be a fabricated citation.

Usage:
    python3 tools/add_isolated_supply_caps.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-17, TODO.md 12.5.af.
# AI-generated. Every value and pin pairing above is quoted from the local
# copies of [9] and [10] in docs/datasheets/. Not human-authored.

import argparse
import shutil
import uuid
from pathlib import Path

from kiutils.items.common import Effects, Font, Position, Property
from kiutils.items.schitems import (Connection, GlobalLabel, SchematicSymbol,
                                    SymbolProjectInstance, SymbolProjectPath)
from kiutils.schematic import Schematic

HERE = Path(__file__).resolve().parent
SCH = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_sch"
BACKUP = SCH.with_suffix(".kicad_sch.pre-isocaps.bak")

# The generic C symbol is VERTICAL: its pins land at (x, y -/+ 6.35), not at
# (x -/+ 7.62, y) like the two-terminal R and ferrite symbols. Getting this
# wrong produced 16 pin_not_connected on the first attempt. Labels sit a
# further 5.08 mm out with a wire between, matching how C2..C10 are drawn.
PIN_DY = 6.35
LABEL_DY = 11.43
FOOTPRINT = "Capacitor_SMD:C_0805_2012Metric"

# ref, value, net on pin 1, net on pin 2, sheet x, sheet y
CAPS = [
    ("C11", "10uF",  "CAN_VISOOUT",   "CAN_GNDISO",    509.85, 202.54),
    ("C12", "220nF", "CAN_VISOOUT",   "CAN_GNDISO",    509.85, 232.54),
    ("C13", "100nF", "CAN_VISOIN",    "CAN_ISO_GND",   509.85, 262.54),
    ("C14", "10nF",  "CAN_VISOIN",    "CAN_ISO_GND",   509.85, 292.54),
    ("C15", "10uF",  "RS485_VISOOUT", "RS485_GNDISO",  509.85, 422.54),
    ("C16", "100nF", "RS485_VISOOUT", "RS485_GNDISO",  509.85, 452.54),
    ("C17", "100nF", "RS485_VISOIN",  "RS485_ISO_GND", 509.85, 482.54),
    ("C18", "10nF",  "RS485_VISOIN",  "RS485_ISO_GND", 509.85, 512.54),
]


def eff(hide=False):
    """Standard text effects for this sheet."""
    return Effects(font=Font(height=1.27, width=1.27), hide=hide)


def main() -> int:
    """Place the eight capacitors and label both terminals of each."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sch = Schematic.from_file(str(SCH))
    have = {p.value for s in sch.schematicSymbols for p in s.properties
            if p.key == "Reference"}
    if "C11" in have:
        print("isolated-supply capacitors already present -- nothing to do")
        return 0

    proto = next(s for s in sch.schematicSymbols
                 if s.entryName == "C"
                 and any(p.key == "Reference" and p.value == "C2"
                         for p in s.properties))
    proj = proto.instances[0].name
    sheet = proto.instances[0].paths[0].sheetInstancePath

    for ref, val, n1, n2, x, y in CAPS:
        sym = SchematicSymbol(
            libraryNickname=proto.libraryNickname, entryName=proto.entryName,
            position=Position(X=x, Y=y, angle=0),
            unit=1, inBom=True, onBoard=True, uuid=str(uuid.uuid4()),
            instances=[SymbolProjectInstance(name=proj, paths=[
                SymbolProjectPath(sheetInstancePath=sheet,
                                  reference=ref, unit=1)])])
        sym.properties = [
            Property(key="Reference", value=ref,
                     position=Position(X=x, Y=y - 3.81, angle=0),
                     effects=eff()),
            Property(key="Value", value=val,
                     position=Position(X=x, Y=y + 3.81, angle=0),
                     effects=eff()),
            Property(key="Footprint", value=FOOTPRINT,
                     position=Position(X=x, Y=y, angle=0), effects=eff(True)),
        ]
        sch.schematicSymbols.append(sym)
        for net, dy in ((n1, -1), (n2, +1)):
            sch.graphicalItems.append(Connection(
                type="wire", uuid=str(uuid.uuid4()),
                points=[Position(X=x, Y=y + dy * PIN_DY),
                        Position(X=x, Y=y + dy * LABEL_DY)]))
            sch.globalLabels.append(GlobalLabel(
                text=net, shape="input", uuid=str(uuid.uuid4()),
                position=Position(X=x, Y=y + dy * LABEL_DY, angle=90),
                effects=eff()))
        print(f"   {ref:4s} {val:6s} {n1} -- {n2}")

    if args.dry_run:
        print("--dry-run: nothing written")
        return 0
    shutil.copy2(SCH, BACKUP)
    sch.to_file(str(SCH))
    print(f"\nwrote {SCH.name} (backup: {BACKUP.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
