#!/usr/bin/env python3
"""Give the board a battery input, and size both power connectors for 50 A.

Two problems, both of which make the board unbuildable as it stands.

1. THERE IS NO WAY TO CONNECT THE BATTERY
   ----------------------------------------
   The VM net is C1, C6, R8, U5.3/U5.4 and the drains of Q1/Q3/Q5 -- and
   nothing else. No connector, no pad, no terminal. The 6S pack (BT1..BT6) is
   drawn on the sheet to document the pack composition against REFERENCES.md
   [14], but it is an external assembly and is marked "exclude from board"
   (kicad/README.md, "Battery pack representation"). So the pack's own wires
   have nowhere to land: as drawn, the power stage cannot be energised.

   The previous PCB papered over this with a footprint called J5 "BATT_IN"
   that had no schematic counterpart at all (kicad/README.md admits this:
   "a PCB-only 2-pin terminal footprint J5 ... no schematic counterpart").
   A PCB-only footprint has no net, so it would have been a pair of isolated
   pads. This adds J5 to the SCHEMATIC instead, on VM and GND, so it carries
   real nets into the layout.

2. BOTH POWER CONNECTORS ARE 2.54 mm PIN HEADERS
   -----------------------------------------------
   J4 carries the three motor phases and was drawn as
   `PinHeader_1x03_P2.54mm_Vertical`. This build is the *50 A* tier
   (../README.md). A 2.54 mm header pin is not a 50 A part by any margin, and
   the same would apply to any header used for the pack leads.

   Both connectors are moved to KiCad's heavy solder-wire pads, the largest
   the library offers:

       J4 (phases)  -> Connector_Wire:SolderWire-6sqmm_1x03_P14mm_D3.5mm_OD7mm
       J5 (battery) -> Connector_Wire:SolderWire-6sqmm_1x02_P14mm_D3.5mm_OD7mm

   6 mm^2 is roughly 10 AWG. These are direct wire-solder pads (7 mm pad,
   4.4 mm hole), which is what production ESCs in this class actually use.

   THIS IS AN ENGINEERING DEFAULT, NOT A VERIFIED SELECTION, per AGENTS.md
   Sec.4. No conductor-sizing standard is cited here and none of these parts
   has been checked against one: 6 mm^2 was chosen because it is the largest
   pad in the library and is plainly closer to right than a 2.54 mm header,
   not because a current-capacity calculation was performed. Sizing the pack
   and phase conductors against IPC-2152 -- and choosing real connectors --
   is logged in TODO.md and must be closed before fab.

Both new/changed parts keep the "Note" property convention this sheet already
uses for engineering defaults.

Usage:
    python3 tools/add_power_connectors.py [--dry-run]
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

HERE = Path(__file__).resolve().parent
KICAD_DIR = HERE.parent
SCH = KICAD_DIR / "open_secure_esc_6s_50a_can485_faraday.kicad_sch"

PHASE_FP = "Connector_Wire:SolderWire-6sqmm_1x03_P14mm_D3.5mm_OD7mm"
BATT_FP = "Connector_Wire:SolderWire-6sqmm_1x02_P14mm_D3.5mm_OD7mm"

# J5 sits directly under J4 (the phase connector) so both heavy-gauge
# terminals read as one group on the sheet.
J5_OFFSET_Y = 60.0

NOTE_DEFAULT = (
    "Engineering default, NOT a verified selection (AGENTS.md Sec.4): "
    "6 mm^2 (~10 AWG) solder-wire pad, the largest in KiCad's Connector_Wire "
    "library. Chosen over the previous 2.54 mm pin header because this is the "
    "50A tier; no IPC-2152 conductor-sizing calculation has been performed and "
    "no real connector part has been selected. See TODO.md."
)


def eff(justify: str | None = None) -> Effects:
    """Standard 1.27 mm text effects, optionally justified."""
    return Effects(font=Font(width=1.27, height=1.27),
                   justify=Justify(horizontally=justify))


def prop_of(sym, key: str):
    """Return the named property object on a schematic symbol, or None."""
    for p in sym.properties:
        if p.key == key:
            return p
    return None


def ref_of(sym) -> str:
    """Reference designator of a schematic symbol."""
    return prop_of(sym, "Reference").value


def set_prop(sym, key: str, value: str) -> None:
    """Set a property, creating it if the symbol does not already carry it."""
    p = prop_of(sym, key)
    if p is None:
        sym.properties.append(Property(
            key=key, value=value,
            position=Position(X=sym.position.X, Y=sym.position.Y, angle=0),
            effects=eff(), showName=False,
        ))
    else:
        p.value = value


def add_wire(sch, x1, y1, x2, y2) -> None:
    """Draw a real wire segment between two sheet points."""
    sch.graphicalItems.append(Connection(
        type="wire",
        points=[Position(X=x1, Y=y1), Position(X=x2, Y=y2)],
        stroke=Stroke(width=0, type="default"),
        uuid=str(uuid.uuid4()),
    ))


def add_global_label(sch, text, x, y, angle, justify) -> None:
    """Place a global label at a sheet point."""
    sch.globalLabels.append(GlobalLabel(
        text=text, shape="passive",
        position=Position(X=x, Y=y, angle=angle),
        effects=eff(justify), uuid=str(uuid.uuid4()),
        properties=[Property(
            key="Intersheetrefs", value="${INTERSHEET_REFS}",
            position=Position(X=x, Y=y, angle=0),
            effects=eff(), showName=False,
        )],
    ))


def main() -> int:
    """Retarget J4's footprint and add J5 on VM/GND."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sch = Schematic().from_file(str(SCH))
    by_ref = {ref_of(s): s for s in sch.schematicSymbols}

    # ---- 2. Phase connector: header -> 6 mm^2 wire pads -----------------
    j4 = by_ref["J4"]
    set_prop(j4, "Footprint", PHASE_FP)
    set_prop(j4, "Note", NOTE_DEFAULT)
    print(f"  J4 footprint -> {PHASE_FP}")

    # ---- 1. Battery input ------------------------------------------------
    if "J5" in by_ref:
        print("  J5 already present, leaving it alone")
    else:
        # Cloned from J2/J3, which are the sheet's other 2-pin connectors, so
        # the new part inherits this generator's own symbol conventions.
        template = by_ref["J2"]
        j5 = copy.deepcopy(template)
        j5.uuid = str(uuid.uuid4())
        new_pos = Position(X=j4.position.X, Y=j4.position.Y + J5_OFFSET_Y,
                           angle=j4.position.angle)
        for p in j5.properties:
            p.position = Position(
                X=new_pos.X + (p.position.X - template.position.X),
                Y=new_pos.Y + (p.position.Y - template.position.Y),
                angle=p.position.angle,
            )
        j5.position = new_pos
        for inst in j5.instances:
            for path in inst.paths:
                path.reference = "J5"
        sch.schematicSymbols.append(j5)
        set_prop(j5, "Reference", "J5")
        set_prop(j5, "Value", "J_BATT")
        set_prop(j5, "Footprint", BATT_FP)
        set_prop(j5, "Note", NOTE_DEFAULT)

        # Conn_01x02 pins are symbol-internal (-8.89, 3.81) and (-8.89, 1.27);
        # sheet Y is inverted relative to symbol Y.
        for pin_dy, net in ((3.81, "VM"), (1.27, "GND")):
            px = new_pos.X - 8.89
            py = new_pos.Y - pin_dy
            add_wire(sch, px, py, px - 5.08, py)
            add_global_label(sch, net, px - 5.08, py, 180, "right")
            print(f"  J5 pin @{net}")
        print(f"  added J5 (battery input) at "
              f"({new_pos.X:.2f}, {new_pos.Y:.2f}) -> {BATT_FP}")

    if args.dry_run:
        print("dry run -- nothing written")
        return 0

    sch.to_file(str(SCH))
    print(f"wrote {SCH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
