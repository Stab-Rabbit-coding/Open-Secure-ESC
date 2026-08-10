#!/usr/bin/env python3
"""Inject the OPTIGA(TM) Trust M secure element (U2) into the Open-Secure-ESC
schematic by direct S-expression text edit.

Why a text pass rather than the repo's own generator: builds/.../tools/
gen_schematic.py rebuilds the whole sheet via `kiutils`, which is not installed
on this machine and cannot be installed here. Regenerating is also the wrong
move independently -- the committed .kicad_sch has been opened and saved by
KiCad since it was generated, so a regeneration would discard that. This script
therefore performs a NON-DESTRUCTIVE injection: it only appends new objects and
adds three pins to one embedded lib_symbol. Nothing existing is rewritten.

Reference circuit: REFERENCES.md [45] p.12 Sec.3 Figure 2 -- SCL (pin 8) and
SDA (pin 3) each pulled up 10k to VCC, 100 nF VCC decoupling, GND pin 1,
VCC pin 10. NC contacts 2/4/5/6/7 are left floating per [45] p.17 Table 6
("Shall be left floating"), marked here with explicit no-connect flags.

All new geometry is placed on the 1.27 mm connection grid.
"""

import re
import sys
import uuid
from pathlib import Path

SCH = Path("open_secure_esc_6s_50a_can485_faraday.kicad_sch")
OPTIGA_LIB = Path("../../../../../symbols/OPTIGA_TRUST_M.kicad_sym")

T = "\t"


def uid() -> str:
    return str(uuid.uuid4())


def eff(indent: int, hide: bool = False) -> str:
    """Emit an (effects (font (size 1.27 1.27))) block at the given tab depth."""
    i = T * indent
    out = f"{i}(effects\n{i}{T}(font\n{i}{T}{T}(size 1.27 1.27)\n{i}{T}(font_close)\n"
    out = out.replace(f"{i}{T}(font_close)\n", f"{i}{T})\n")
    if hide:
        out += f"{i}{T}(hide yes)\n"
    out += f"{i})\n"
    return out


def prop(indent: int, key: str, val: str, x: float, y: float, hide: bool = False) -> str:
    i = T * indent
    return (
        f'{i}(property "{key}" "{val}"\n'
        f"{i}{T}(at {x} {y} 0)\n" + eff(indent + 1, hide) + f"{i})\n"
    )


# --------------------------------------------------------------------------
# 1. Build the embedded lib_symbol for OPTIGA_TRUST_M from the project library
# --------------------------------------------------------------------------
def build_optiga_lib_symbol() -> str:
    src = OPTIGA_LIB.read_text()
    props = dict(re.findall(r'\(property "([^"]+)" "((?:[^"\\]|\\.)*)"', src))
    pins = re.findall(
        r'\(pin (\w+) line \(at ([-\d.]+) ([-\d.]+) (\d+)\) \(length ([\d.]+)\)\s*'
        r'\(name "([^"]+)"[\s\S]*?\(number "([^"]+)"',
        src,
    )
    if len(pins) != 10:
        sys.exit(f"expected 10 OPTIGA pins, parsed {len(pins)}")

    i2 = T * 2
    out = f'{i2}(symbol "OPTIGA_TRUST_M:OPTIGA_TRUST_M"\n'
    out += f"{i2}{T}(pin_names\n{i2}{T}{T}(offset 1.016)\n{i2}{T})\n"
    out += f"{i2}{T}(exclude_from_sim no)\n{i2}{T}(in_bom yes)\n{i2}{T}(on_board yes)\n"
    out += prop(3, "Reference", "U", 0, 15.24)
    out += prop(3, "Value", "OPTIGA_TRUST_M", 0, 12.7)
    for key, pos in (("Footprint", 0), ("Datasheet", 0), ("Description", 0),
                     ("Citation", 0), ("Verification", 0)):
        out += prop(3, key, props.get(key, ""), pos, pos, hide=True)
    # body outline
    out += (
        f"{i2}{T}(symbol \"OPTIGA_TRUST_M_0_1\"\n"
        f"{i2}{T}{T}(rectangle\n"
        f"{i2}{T}{T}{T}(start -5.08 10.16)\n"
        f"{i2}{T}{T}{T}(end 5.08 -10.16)\n"
        f"{i2}{T}{T}{T}(stroke\n{i2}{T}{T}{T}{T}(width 0)\n{i2}{T}{T}{T}{T}(type default)\n{i2}{T}{T}{T})\n"
        f"{i2}{T}{T}{T}(fill\n{i2}{T}{T}{T}{T}(type none)\n{i2}{T}{T}{T})\n"
        f"{i2}{T}{T})\n"
        f"{i2}{T})\n"
    )
    # pins
    out += f'{i2}{T}(symbol "OPTIGA_TRUST_M_1_1"\n'
    for etype, px, py, rot, length, name, num in pins:
        out += (
            f"{i2}{T}{T}(pin {etype} line\n"
            f"{i2}{T}{T}{T}(at {px} {py} {rot})\n"
            f"{i2}{T}{T}{T}(length {length})\n"
            f'{i2}{T}{T}{T}(name "{name}"\n' + eff(6) + f"{i2}{T}{T}{T})\n"
            f'{i2}{T}{T}{T}(number "{num}"\n' + eff(6) + f"{i2}{T}{T}{T})\n"
            f"{i2}{T}{T})\n"
        )
    out += f"{i2}{T})\n{i2})\n"
    return out


# --------------------------------------------------------------------------
# 2. Placed-instance emitters
# --------------------------------------------------------------------------
def instance(lib_id, x, y, ref, value, footprint, props_extra=None, pin_nums=None,
             ref_dy=-8.89, val_dy=-6.35):
    i1 = T
    out = f"{i1}(symbol\n"
    out += f'{i1}{T}(lib_id "{lib_id}")\n'
    out += f"{i1}{T}(at {x} {y} 0)\n{i1}{T}(unit 1)\n"
    out += f"{i1}{T}(exclude_from_sim no)\n{i1}{T}(in_bom yes)\n{i1}{T}(on_board yes)\n{i1}{T}(dnp no)\n"
    out += f'{i1}{T}(uuid "{uid()}")\n'
    out += prop(2, "Reference", ref, x, round(y + ref_dy, 2))
    out += prop(2, "Value", value, x, round(y + val_dy, 2))
    out += prop(2, "Footprint", footprint, x, y, hide=True)
    out += prop(2, "Datasheet", (props_extra or {}).get("Datasheet", ""), x, y, hide=True)
    out += prop(2, "Description", (props_extra or {}).get("Description", ""), x, y, hide=True)
    for k, v in (props_extra or {}).items():
        if k in ("Datasheet", "Description"):
            continue
        out += prop(2, k, v, x, y, hide=True)
    for n in pin_nums or []:
        out += f'{i1}{T}(pin "{n}"\n{i1}{T}{T}(uuid "{uid()}")\n{i1}{T})\n'
    out += (
        f"{i1}{T}(instances\n"
        f'{i1}{T}{T}(project "open_secure_esc_6s_50a_can485_faraday"\n'
        f'{i1}{T}{T}{T}(path "/{ROOT_UUID}"\n'
        f'{i1}{T}{T}{T}{T}(reference "{ref}")\n{i1}{T}{T}{T}{T}(unit 1)\n'
        f"{i1}{T}{T}{T})\n{i1}{T}{T})\n{i1}{T})\n{i1})\n"
    )
    return out


def wire(x1, y1, x2, y2):
    return (
        f"{T}(wire\n{T}{T}(pts\n{T}{T}{T}(xy {x1} {y1}) (xy {x2} {y2})\n{T}{T})\n"
        f"{T}{T}(stroke\n{T}{T}{T}(width 0)\n{T}{T}{T}(type default)\n{T}{T})\n"
        f'{T}{T}(uuid "{uid()}")\n{T})\n'
    )


def glabel(name, x, y, rot, shape="passive"):
    return (
        f'{T}(global_label "{name}"\n{T}{T}(shape {shape})\n{T}{T}(at {x} {y} {rot})\n'
        + eff(2)
        + f'{T}{T}(uuid "{uid()}")\n'
        + f'{T}{T}(property "Intersheetrefs" "${{INTERSHEET_REFS}}"\n{T}{T}{T}(at {x} {y} 0)\n'
        + eff(3, hide=True)
        + f"{T}{T})\n{T})\n"
    )


def noconn(x, y):
    return f'{T}(no_connect\n{T}{T}(at {x} {y})\n{T}{T}(uuid "{uid()}")\n{T})\n'


# --------------------------------------------------------------------------
# 3. Apply
# --------------------------------------------------------------------------
text = SCH.read_text()
ROOT_UUID = re.search(r'\n\t\(uuid "([0-9a-f-]+)"\)\n', text).group(1)

# 3a. add the OPTIGA embedded lib_symbol, alphabetically before "S32K144"
anchor = '\t\t(symbol "S32K144:S32K144"\n'
if 'OPTIGA_TRUST_M:OPTIGA_TRUST_M' in text:
    sys.exit("OPTIGA already present in lib_symbols -- refusing to double-inject")
text = text.replace(anchor, build_optiga_lib_symbol() + anchor, 1)

# 3b. add the three SE pins to the embedded S32K144 lib_symbol
se_pins = [
    ("bidirectional", "25.4", "-5.08", "180", "2.54", "SE_I2C_SCL", "28"),
    ("bidirectional", "25.4", "-7.62", "180", "2.54", "SE_I2C_SDA", "29"),
    ("output", "25.4", "-10.16", "180", "2.54", "SE_RST", "30"),
]
i2 = T * 2
se_block = ""
for etype, px, py, rot, length, name, num in se_pins:
    se_block += (
        f"{i2}{T}{T}(pin {etype} line\n"
        f"{i2}{T}{T}{T}(at {px} {py} {rot})\n"
        f"{i2}{T}{T}{T}(length {length})\n"
        f'{i2}{T}{T}{T}(name "{name}"\n' + eff(6) + f"{i2}{T}{T}{T})\n"
        f'{i2}{T}{T}{T}(number "{num}"\n' + eff(6) + f"{i2}{T}{T}{T})\n"
        f"{i2}{T}{T})\n"
    )
def close_paren(s: str, open_idx: int) -> int:
    """Index of the ')' matching the '(' at open_idx, skipping quoted strings."""
    depth, i, instr, esc = 0, open_idx, False, False
    while i < len(s):
        ch = s[i]
        if esc:
            esc = False
        elif ch == "\\" and instr:
            esc = True
        elif ch == '"':
            instr = not instr
        elif not instr:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    sys.exit("unbalanced S-expression")


# The embedded S32K144 symbol ends with an (embedded_fonts no) line, so a naive
# "\t\t\t)\n\t\t)" pattern walks off into an unrelated (text ...) node further
# down the file. Walk the parens instead.
sym_start = text.index('\t\t(symbol "S32K144:S32K144"')
unit_start = text.index('(symbol "S32K144_1_1"', sym_start) - 3
unit_end = close_paren(text, text.index("(", unit_start))
insert_at = text.rindex("\n", 0, unit_end) + 1
text = text[:insert_at] + se_block + text[insert_at:]

# 3c. placed instances -------------------------------------------------------
# The block sits below the existing "nFAULT: pulled up only..." text note at
# y=502.54; DY keeps the 3V3 rail labels clear of it. 22.86 = 18 x 1.27, so the
# whole block stays on the connection grid.
DY = 22.86
U2X, U2Y = 660.4, 520.7 + DY
RSDA_X, RSDA_Y = 627.38, 511.81 + DY
RSCL_X, RSCL_Y = 615.95, 514.35 + DY
CSE_X, CSE_Y = 679.45, 514.35 + DY
V3, GNDY = 502.92 + DY, 538.48 + DY

optiga_src = OPTIGA_LIB.read_text()
oprops = dict(re.findall(r'\(property "([^"]+)" "((?:[^"\\]|\\.)*)"', optiga_src))

add = ""
add += instance(
    "OPTIGA_TRUST_M:OPTIGA_TRUST_M", U2X, U2Y, "U?", "OPTIGA_TRUST_M",
    oprops.get("Footprint", ""),
    props_extra={"Datasheet": oprops.get("Datasheet", ""),
                 "Description": oprops.get("Description", ""),
                 "Citation": oprops.get("Citation", ""),
                 "Verification": oprops.get("Verification", "")},
    pin_nums=[str(n) for n in range(1, 11)], ref_dy=-15.24, val_dy=-12.7,
)
add += instance("Device:R", RSDA_X, RSDA_Y, "R?", "10k",
                "Resistor_SMD:R_0805_2012Metric", pin_nums=["1", "2"])
add += instance("Device:R", RSCL_X, RSCL_Y, "R?", "10k",
                "Resistor_SMD:R_0805_2012Metric", pin_nums=["1", "2"])
add += instance("Device:C", CSE_X, CSE_Y, "C?", "100n",
                "Capacitor_SMD:C_0805_2012Metric", pin_nums=["1", "2"])

# 3d. wires + labels ---------------------------------------------------------
SDA_Y, SCL_Y, RST_Y = 518.16 + DY, 520.7 + DY, 523.24 + DY
PINX = 652.78

add += wire(PINX, SDA_Y, RSDA_X, SDA_Y)          # SDA pin -> pull-up
add += wire(PINX, SCL_Y, RSCL_X, SCL_Y)          # SCL pin -> pull-up
add += wire(PINX, RST_Y, 641.35, RST_Y)          # RST pin -> label
add += glabel("SE_I2C_SDA", 641.35, SDA_Y, 180)
add += glabel("SE_I2C_SCL", 641.35, SCL_Y, 180)
add += glabel("SE_RST", 641.35, RST_Y, 180)

add += wire(RSDA_X, 505.46 + DY, RSDA_X, V3)          # pull-up tops -> 3V3
add += glabel("3V3", RSDA_X, V3, 90)
add += wire(RSCL_X, 508.0 + DY, RSCL_X, V3)
add += glabel("3V3", RSCL_X, V3, 90)

add += wire(U2X, 508.0 + DY, U2X, V3)                 # VCC -> 3V3
add += glabel("3V3", U2X, V3, 90)
add += wire(U2X, 533.4 + DY, U2X, GNDY)               # GND
add += glabel("GND", U2X, GNDY, 270)

add += wire(CSE_X, 508.0 + DY, CSE_X, V3)             # decoupling cap
add += glabel("3V3", CSE_X, V3, 90)
add += wire(CSE_X, 520.7 + DY, CSE_X, 527.05 + DY)
add += glabel("GND", CSE_X, 527.05 + DY, 270)

for ny in (n + DY for n in (515.62, 518.16, 520.7, 523.24, 525.78)):   # NC pins 2,4,5,6,7
    add += noconn(668.02, ny)

# 3e. splice in before the closing paren of the sheet ------------------------
assert text.rstrip().endswith(")")
cut = text.rstrip().rfind("\n)")
text = text[:cut] + "\n" + add.rstrip("\n") + text[cut:]

SCH.write_text(text)
print("injected: U2 OPTIGA_TRUST_M + 2x 10k pull-up + 100n decoupling")
print(f"root uuid {ROOT_UUID}")
