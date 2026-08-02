"""Shared helpers: pin layout + generic (standard-library-style) symbol specs.

Reuses the exact _layout() algorithm from symbols/tools/gen_kicad_symbol.py so
every symbol on this sheet (sourced BOM parts and the generic Device/Connector
stand-ins) shares one deterministic geometry rule.
"""

import sys
from pathlib import Path

# builds/6s/50A/CAN_485_faraday/kicad/tools/genlib.py -> repo root is 6 parents up
REPO = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPO / "symbols" / "tools"))

from gen_kicad_symbol import GRID, _layout, build_symbol

# Re-exported for gen_schematic.py / gen_pcb.py -- this module is a shared
# import hub, not just a spec table.
__all__ = ["GENERIC_SPECS", "GRID", "REPO", "_layout", "build_symbol"]

# ---------------------------------------------------------------------------
# Generic, unsourced support parts (resistor / capacitor / generic headers).
# Modeled as project-local stand-ins for KiCad's own "Device" / "Connector_Generic"
# system libraries per kicad/README.md Next-steps §3 ("using KiCad's standard
# Device:C / Device:C_Polarized / Device:R library symbols -- not reinvented
# here"). lib_id is deliberately "Device:R" etc. so the part identity matches
# the real system library; the embedded lib_symbols copy below is a simplified
# stand-in geometry (KiCad resyncs it to the real library on next symbol
# update if the system library is present).
# ---------------------------------------------------------------------------

GENERIC_SPECS = {
    "Device:R": {
        "name": "R",
        "reference": "R",
        "footprint": "Resistor_SMD:R_0805_2012Metric",
        "datasheet": "",
        "citation": "",
        "description": "Generic resistor (KiCad standard Device library stand-in).",
        "verification": "Generic passive, not part-specific -- no citation required.",
        "pins": [
            {"num": "1", "name": "~", "etype": "passive", "side": "top"},
            {"num": "2", "name": "~", "etype": "passive", "side": "bottom"},
        ],
    },
    "Device:C": {
        "name": "C",
        "reference": "C",
        "footprint": "Capacitor_SMD:C_0805_2012Metric",
        "datasheet": "",
        "citation": "",
        "description": "Generic capacitor (KiCad standard Device library stand-in).",
        "verification": "Generic passive, not part-specific -- no citation required.",
        "pins": [
            {"num": "1", "name": "~", "etype": "passive", "side": "top"},
            {"num": "2", "name": "~", "etype": "passive", "side": "bottom"},
        ],
    },
    "Device:C_Polarized": {
        "name": "C_Polarized",
        "reference": "C",
        "footprint": "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
        "datasheet": "",
        "citation": "",
        "description": "Generic polarized (electrolytic) capacitor (KiCad standard Device library stand-in).",
        "verification": "Generic passive, not part-specific -- no citation required.",
        "pins": [
            {"num": "1", "name": "+", "etype": "passive", "side": "top"},
            {"num": "2", "name": "-", "etype": "passive", "side": "bottom"},
        ],
    },
    "Connector_Generic:Conn_01x02": {
        "name": "Conn_01x02",
        "reference": "J",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
        "datasheet": "",
        "citation": "",
        "description": "Generic 2-pin connector (KiCad standard Connector_Generic library stand-in).",
        "verification": "Generic connector, not part-specific -- no citation required.",
        "pins": [
            {"num": "1", "name": "Pin_1", "etype": "passive", "side": "left"},
            {"num": "2", "name": "Pin_2", "etype": "passive", "side": "left"},
        ],
    },
    "Connector_Generic:Conn_01x03": {
        "name": "Conn_01x03",
        "reference": "J",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
        "datasheet": "",
        "citation": "",
        "description": "Generic 3-pin connector (KiCad standard Connector_Generic library stand-in).",
        "verification": "Generic connector, not part-specific -- no citation required.",
        "pins": [
            {"num": "1", "name": "Pin_1", "etype": "passive", "side": "left"},
            {"num": "2", "name": "Pin_2", "etype": "passive", "side": "left"},
            {"num": "3", "name": "Pin_3", "etype": "passive", "side": "left"},
        ],
    },
    "Connector_Generic:Conn_01x04": {
        "name": "Conn_01x04",
        "reference": "J",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
        "datasheet": "",
        "citation": "",
        "description": "Generic 4-pin connector (KiCad standard Connector_Generic library stand-in).",
        "verification": "Generic connector, not part-specific -- no citation required.",
        "pins": [
            {"num": "1", "name": "Pin_1", "etype": "passive", "side": "left"},
            {"num": "2", "name": "Pin_2", "etype": "passive", "side": "left"},
            {"num": "3", "name": "Pin_3", "etype": "passive", "side": "left"},
            {"num": "4", "name": "Pin_4", "etype": "passive", "side": "left"},
        ],
    },
    "power:PWR_FLAG": {
        "name": "PWR_FLAG",
        "reference": "#FLG",
        "footprint": "",
        "datasheet": "",
        "citation": "",
        "description": (
            "KiCad standard power-flag marker: asserts a net is driven from "
            "outside this schematic (a rail carried only by same-name labels "
            "here, with no regulator/source symbol on this sheet) so ERC's "
            "power-input-pin-not-driven check doesn't fire. Not itself a "
            "claim about where the power actually comes from -- see "
            "../README.md / kicad/README.md for the open items on 3V3 "
            "regulator and isolated-supply sourcing."
        ),
        "verification": "Generic KiCad mechanism, not part-specific -- no citation required.",
        "pins": [
            {"num": "1", "name": "pwr", "etype": "power_out", "side": "bottom"},
        ],
    },
}
