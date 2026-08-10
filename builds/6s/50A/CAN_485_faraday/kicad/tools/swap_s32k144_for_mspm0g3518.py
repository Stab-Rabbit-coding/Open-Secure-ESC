#!/usr/bin/env python3
"""Swap U1 from the NXP S32K144 to the TI MSPM0G3518-Q1 (PM / LQFP-64).

WHY THIS IS AN INJECTION SCRIPT AND NOT A REGENERATION
------------------------------------------------------
`kiutils` is not installed in this environment and pip is not permitted, so
every generator in this repo (`symbols/tools/gen_kicad_symbol.py`,
`kicad/tools/gen_schematic.py`, `gen_pcb.py`, `genlib.py`) dies at module load.
The committed `.kicad_sch` is also already ahead of `gen_schematic.py`.  The
established pattern here is therefore targeted S-expression injection --
see `inject_optiga_secure_element.py` in this directory, and
`LibreServo_v4/PCB/kicad/tools/swap_slb9672_for_optiga.py`.

PARSER TRAP (documented in docs/HANDOFF-mcu-swap-s32k144-to-mspm0g3518.md SS6):
do NOT find the end of an embedded `lib_symbol` by matching `\\t\\t\\t)\\n\\t\\t)`.
There is an `(embedded_fonts no)` line before the close, so that pattern
silently matches an unrelated node far down the file and yields a file with
balanced parens that KiCad refuses to load.  This script walks parens instead.

WHAT IT DOES
------------
1.  Replaces the embedded `S32K144:S32K144` lib_symbol with
    `MSPM0G3518_Q1_PM:MSPM0G3518_Q1_PM`, rebuilding the pin list from
    `symbols/specs/MSPM0G3518_Q1_PM.json` but reusing the OLD pin
    COORDINATES slot-for-slot so that existing wires still land.
2.  Repoints the U1 instance (lib_id, Value, Datasheet, Description,
    Citation, Verification).
3.  Deletes the `VREFH` and `VREFL_VSSA_VSS` stubs (wire + global label).
    The MSPM0 has no dedicated reference pins -- VREF+/VREF- are IOMUX
    functions on PA23/PA21 and are deliberately left unused; the ADC runs
    supply-referenced off VDDA, which is what the old VREFH->3V3 /
    VREFL->GND wiring was doing anyway.  See the spec JSON `verification`.
4.  Renames the `3V3` global label on the old VDDA stub to `VCORE`.
    [44] p.51 SS7.3 note (2): "The VCORE pin must only be connected to
    CVCORE.  Do not supply any voltage or apply any external load to the
    VCORE pin."  A slot-for-slot VDDA->VCORE remap would have tied VCORE to
    3V3, which the datasheet explicitly forbids.
5.  Repurposes the now-redundant "MCU VDDA decoupling" 100nF cap as
    C_VCORE = 470nF ([44] p.51 SS7.3, +/-20% or better, low-ESR) by
    changing its value/note and moving its top label from 3V3 to VCORE.
6.  Adds C_VDD = 10uF ([44] p.51 SS7.3) and R_NRST = 10k.
    [44] Table 6-20: "NRST is an active-low reset signal; it must be pulled
    high to VCC or the device will not start."  There was no pull-up before.
7.  Labels the previously dangling reset stub `NRST`.
8.  Rewrites the on-sheet text note that described the S32K144's CSEc.

NOT DONE ON PURPOSE: the `J_SWD` connector is present but unwired, and the
SWCLK/SWDIO stubs stay dangling.  That is a pre-existing open item and was
explicitly left in place -- see TODO.md.

Citations: [44] = SLASFA6B (MSPM0G3519-Q1/MSPM0G3518-Q1 datasheet),
[40] = SLAAE29A, [31] = S32K1xx (superseded), [45] = OPTIGA(TM) Trust M.
Written by Claude Opus 5 (`claude-opus-5`) under human direction, 2026-08-10.
"""

import json
import re
import shutil
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCH = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_sch"
SPEC = HERE.parents[5] / "symbols" / "specs" / "MSPM0G3518_Q1_PM.json"

OLD = "S32K144"
NEW = "MSPM0G3518_Q1_PM"

# Pin coordinates lifted verbatim from the embedded S32K144 symbol, keyed by
# the NEW pin name.  Reusing these keeps every existing wire attached.
GEO = {
    "VDD": (-6.35, 13.97, 270), "VSS": (-3.81, 13.97, 270),
    "VCORE": (-1.27, 13.97, 270), "NRST": (6.35, 13.97, 270),
    "SWCLK": (-17.78, 10.16, 0), "SWDIO": (-17.78, 7.62, 0),
    "CAN_TX": (-17.78, 5.08, 0), "CAN_RX": (-17.78, 2.54, 0),
    "RS485_TXD": (-17.78, 0, 0), "RS485_RXD": (-17.78, -2.54, 0),
    "RS485_DE_RE": (-17.78, -5.08, 0),
    "GD_SPI_CS": (17.78, 10.16, 180), "GD_SPI_MISO": (17.78, 7.62, 180),
    "GD_SPI_MOSI": (17.78, 5.08, 180), "GD_SPI_SCK": (17.78, 2.54, 180),
    "SE_I2C_SCL": (25.4, -5.08, 180), "SE_I2C_SDA": (25.4, -7.62, 180),
    "SE_RST": (25.4, -10.16, 180),
    "ADC_IU": (-11.43, -13.97, 90), "ADC_IV": (-8.89, -13.97, 90),
    "ADC_IW": (-6.35, -13.97, 90), "ADC_VBUS": (-3.81, -13.97, 90),
    "PWM_AH": (-1.27, -13.97, 90), "PWM_AL": (1.27, -13.97, 90),
    "PWM_BH": (3.81, -13.97, 90), "PWM_BL": (6.35, -13.97, 90),
    "PWM_CH": (8.89, -13.97, 90), "PWM_CL": (11.43, -13.97, 90),
}

# Stubs to delete outright: (wire endpoint A, wire endpoint B, label coord).
DROP_STUBS = [
    ((531.12, 278.57), (531.12, 273.49), (531.12, 273.49)),   # VREFH  -> 3V3
    ((533.66, 278.57), (533.66, 283.65), (533.66, 283.65)),   # VREFL  -> GND
]

VCORE_LABEL = (528.58, 273.49)     # old VDDA stub label, 3V3 -> VCORE
NRST_STUB = (471.07, 278.66)       # far end of the dangling reset wire
VDDA_CAP = (589.85, 162.54)        # "MCU VDDA decoupling" -> C_VCORE
VDDA_CAP_TOPLABEL = (589.85, 151.11)


def walk(text, i):
    """Return (block, end_index) for the S-expression starting at text[i]."""
    depth = 0
    for q in range(i, len(text)):
        if text[q] == "(":
            depth += 1
        elif text[q] == ")":
            depth -= 1
            if depth == 0:
                return text[i:q + 1], q + 1
    raise ValueError(f"unbalanced S-expression at offset {i}")


def find_block(text, needle):
    i = text.index(needle)
    j = text.rfind("(symbol", 0, i)
    return (j,) + walk(text, j)


def near(a, b, tol=0.02):
    return abs(a - b) < tol


def coord_in(block, x, y):
    """True if block carries an (at x y ...) or (xy x y) at this coordinate."""
    for m in re.finditer(r"\((?:at|xy) (-?[\d.]+) (-?[\d.]+)", block):
        if near(float(m.group(1)), x) and near(float(m.group(2)), y):
            return True
    return False


def esc(t):
    return t.replace("\\", "\\\\").replace('"', '\\"')


def build_lib_symbol(spec):
    """Rebuild the embedded lib_symbol block, 3-tab base indent."""
    T = "\t"
    o = [f'{T*2}(symbol "{NEW}:{NEW}"',
         f"{T*3}(pin_names", f"{T*4}(offset 1.016)", f"{T*3})",
         f"{T*3}(exclude_from_sim no)", f"{T*3}(in_bom yes)",
         f"{T*3}(on_board yes)"]
    props = [("Reference", spec["reference"], "0 16.51 0", False),
             ("Value", NEW, "0 13.97 0", False),
             ("Footprint", spec["footprint"], "0 0 0", True),
             ("Datasheet", spec["datasheet"], "0 0 0", True),
             ("Description", spec["description"], "0 0 0", True),
             ("Citation", spec["citation"], "0 0 0", True),
             ("Verification", spec["verification"], "0 0 0", True)]
    for k, v, at, hide in props:
        o += [f'{T*3}(property "{k}" "{esc(v)}"', f"{T*4}(at {at})",
              f"{T*4}(effects", f"{T*5}(font", f"{T*6}(size 1.27 1.27)",
              f"{T*5})"]
        if hide:
            o.append(f"{T*5}(hide yes)")
        o += [f"{T*4})", f"{T*3})"]
    o += [f'{T*3}(symbol "{NEW}_0_1"', f"{T*4}(rectangle",
          f"{T*5}(start -15.24 11.43)", f"{T*5}(end 15.24 -11.43)",
          f"{T*5}(stroke", f"{T*6}(width 0)", f"{T*6}(type default)",
          f"{T*5})", f"{T*5}(fill", f"{T*6}(type none)", f"{T*5})",
          f"{T*4})", f"{T*3})", f'{T*3}(symbol "{NEW}_1_1"']
    for p in spec["pins"]:
        x, y, r = GEO[p["name"]]
        o += [f'{T*4}(pin {p["etype"]} line', f"{T*5}(at {x:g} {y:g} {r})",
              f"{T*5}(length 2.54)", f'{T*5}(name "{p["name"]}"',
              f"{T*6}(effects", f"{T*7}(font", f"{T*8}(size 1.27 1.27)",
              f"{T*7})", f"{T*6})", f"{T*5})", f'{T*5}(number "{p["num"]}"',
              f"{T*6}(effects", f"{T*7}(font", f"{T*8}(size 1.27 1.27)",
              f"{T*7})", f"{T*6})", f"{T*5})", f"{T*4})"]
    o += [f"{T*3})", f"{T*3}(embedded_fonts no)", f"{T*2})"]
    return "\n".join(o)


def gl(name, x, y, rot=90):
    """A global label in the sheet's existing style (2-tab base indent)."""
    T = "\t"
    return "\n".join([
        f'{T*2}(global_label "{name}"', f"{T*3}(shape passive)",
        f"{T*3}(at {x:g} {y:g} {rot})", f"{T*3}(effects", f"{T*4}(font",
        f"{T*5}(size 1.27 1.27)", f"{T*4})", f"{T*3})",
        f'{T*3}(uuid "{uuid.uuid4()}")',
        f'{T*3}(property "Intersheetrefs" "${{INTERSHEET_REFS}}"',
        f"{T*4}(at {x:g} {y:g} 0)", f"{T*4}(effects", f"{T*5}(font",
        f"{T*6}(size 1.27 1.27)", f"{T*5})", f"{T*5}(hide yes)",
        f"{T*4})", f"{T*3})", f"{T*2})"])


def wire(x1, y1, x2, y2):
    T = "\t"
    return "\n".join([
        f"{T*2}(wire", f"{T*3}(pts", f"{T*4}(xy {x1:g} {y1:g})",
        f"{T*4}(xy {x2:g} {y2:g})", f"{T*3})", f"{T*3}(stroke",
        f"{T*4}(width 0)", f"{T*4}(type default)", f"{T*3})",
        f'{T*3}(uuid "{uuid.uuid4()}")', f"{T*2})"])


def passive(lib, ref, value, footprint, note, x, y):
    """A Device:C / Device:R instance in the sheet's existing style."""
    T = "\t"
    o = [f"{T*1}(symbol", f'{T*2}(lib_id "{lib}")', f"{T*2}(at {x:g} {y:g} 0)",
         f"{T*2}(unit 1)", f"{T*2}(exclude_from_sim no)", f"{T*2}(in_bom yes)",
         f"{T*2}(on_board yes)", f"{T*2}(dnp no)",
         f'{T*2}(uuid "{uuid.uuid4()}")']
    for k, v, dy, hide in [("Reference", ref, -8.89, False),
                           ("Value", value, -6.35, False),
                           ("Footprint", footprint, 0, True),
                           ("Datasheet", "", 0, True),
                           ("Description", "", 0, True),
                           ("Note", note, 0, True)]:
        o += [f'{T*2}(property "{k}" "{esc(v)}"',
              f"{T*3}(at {x:g} {y + dy:g} 0)", f"{T*3}(effects",
              f"{T*4}(font", f"{T*5}(size 1.27 1.27)", f"{T*4})"]
        if hide:
            o.append(f"{T*4}(hide yes)")
        o += [f"{T*3})", f"{T*2})"]
    for n in ("1", "2"):
        o += [f'{T*2}(pin "{n}"', f'{T*3}(uuid "{uuid.uuid4()}")', f"{T*2})"]
    o += [f"{T*2}(instances", f'{T*3}(project "{SCH.stem}"',
          f'{T*4}(path "/b6909b5a-de2d-4466-bb5d-8520126b59da"',
          f'{T*5}(reference "{ref}")', f"{T*5}(unit 1)", f"{T*4})", f"{T*3})",
          f"{T*2})", f"{T*1})"]
    return "\n".join(o)


def main():
    spec = json.loads(SPEC.read_text())
    missing = {p["name"] for p in spec["pins"]} - set(GEO)
    if missing:
        sys.exit(f"spec has pins with no geometry: {sorted(missing)}")

    s = SCH.read_text()
    shutil.copy2(SCH, SCH.with_suffix(".kicad_sch.bak"))
    changes = []

    # --- 1. embedded lib_symbol -------------------------------------------
    i = s.index(f'(symbol "{OLD}:{OLD}"')
    old_blk, end = walk(s, i)
    s = s[:i] + build_lib_symbol(spec).lstrip("\t") + s[end:]
    changes.append(f"lib_symbol {OLD} -> {NEW} ({len(spec['pins'])} pins)")

    # --- 2. U1 instance ----------------------------------------------------
    j, inst, iend = find_block(s, f'(lib_id "{OLD}:{OLD}")')
    new_inst = inst.replace(f'(lib_id "{OLD}:{OLD}")', f'(lib_id "{NEW}:{NEW}")')
    new_inst = re.sub(r'(\(property "Value" ")[^"]*(")',
                      lambda m: m.group(1) + NEW + m.group(2), new_inst, count=1)
    for key, val in (("Datasheet", spec["datasheet"]),
                     ("Description", spec["description"]),
                     ("Citation", spec["citation"]),
                     ("Verification", spec["verification"])):
        pat = re.compile(r'(\(property "%s" ")(?:[^"\\]|\\.)*(")' % key)
        if pat.search(new_inst):
            new_inst = pat.sub(lambda m: m.group(1) + esc(val) + m.group(2),
                               new_inst, count=1)
    s = s[:j] + new_inst + s[iend:]
    changes.append("U1 instance repointed")

    # --- 3. drop VREFH / VREFL stubs --------------------------------------
    for a, b, lab in DROP_STUBS:
        for tag in ("wire", "global_label"):
            for m in list(re.finditer(r"\(%s\b" % tag, s)):
                blk, e = walk(s, m.start())
                hit = (coord_in(blk, *a) and coord_in(blk, *b)) if tag == "wire" \
                    else coord_in(blk, *lab)
                if hit:
                    line0 = s.rfind("\n", 0, m.start()) + 1
                    s = s[:line0] + s[e:].lstrip("\n")
                    changes.append(f"dropped {tag} at {lab}")
                    break

    # --- 4. VDDA stub label 3V3 -> VCORE ----------------------------------
    for m in list(re.finditer(r'\(global_label "3V3"', s)):
        blk, e = walk(s, m.start())
        if coord_in(blk, *VCORE_LABEL):
            s = s[:m.start()] + blk.replace('"3V3"', '"VCORE"', 1) + s[e:]
            changes.append("VDDA stub label 3V3 -> VCORE")
            break

    # --- 5. repurpose the VDDA decoupling cap as C_VCORE -------------------
    for m in list(re.finditer(r'\(property "Note" "MCU VDDA decoupling', s)):
        j = s.rfind("(symbol", 0, m.start())
        blk, e = walk(s, j)
        nb = re.sub(r'(\(property "Value" ")[^"]*(")', r"\g<1>470nF\g<2>", blk, count=1)
        nb = re.sub(r'(\(property "Note" ")(?:[^"\\]|\\.)*(")',
                    r"\g<1>C_VCORE for U1 (MSPM0G3518-Q1). REQUIRED value: "
                    r"470nF nominal between VCORE and VSS per [44] p.51 SS7.3, "
                    r"low-ESR, tolerance +/-20% or better, placed as close to "
                    r"the VCORE pin as possible. This net carries the cap and "
                    r"nothing else -- [44] p.51 note (2) forbids supplying any "
                    r"voltage or applying any external load to VCORE. "
                    r"Repurposed 2026-08-10 from the S32K144 VDDA decoupling "
                    r"cap; the MSPM0 has no VDDA pin.\g<2>", nb, 1)
        s = s[:j] + nb + s[e:]
        changes.append("VDDA decoupling cap -> C_VCORE 470nF")
        break
    for m in list(re.finditer(r'\(global_label "3V3"', s)):
        blk, e = walk(s, m.start())
        if coord_in(blk, *VDDA_CAP_TOPLABEL):
            s = s[:m.start()] + blk.replace('"3V3"', '"VCORE"', 1) + s[e:]
            changes.append("C_VCORE top label 3V3 -> VCORE")
            break

    # --- 6/7. new passives + NRST label -----------------------------------
    add = [gl("NRST", *NRST_STUB, rot=180)]
    for x, lib, ref, val, fp, top, note in [
        (629.85, "Device:C", "C?", "10uF", "Capacitor_SMD:C_0805_2012Metric",
         "3V3", "C_VDD bulk for U1 (MSPM0G3518-Q1). REQUIRED value: 10uF "
         "nominal between VDD and VSS per [44] p.51 SS7.3, low-ESR, tolerance "
         "+/-20% or better, as close to the VDD pin as possible. Added "
         "2026-08-10 with the S32K144 -> MSPM0G3518-Q1 swap; the sheet "
         "previously carried only a 100nF MCU VDD decoupling cap."),
        (669.85, "Device:R", "R?", "10k", "Resistor_SMD:R_0805_2012Metric",
         "3V3", "NRST pull-up for U1 (MSPM0G3518-Q1). MANDATORY, not optional: "
         "[44] Table 6-20 states NRST 'must be pulled high to VCC or the "
         "device will not start'. Added 2026-08-10 -- the superseded S32K144 "
         "design had no pull-up on its reset pin."),
    ]:
        bot = "GND" if lib == "Device:C" else "NRST"
        add += [passive(lib, ref, val, fp, note, x, 162.54),
                wire(x, 156.19, x, 151.11), gl(top, x, 151.11),
                wire(x, 168.89, x, 173.97), gl(bot, x, 173.97, rot=270)]
        changes.append(f"added {val} at ({x}, 162.54): {top}/{bot}")

    k = s.rfind("\n\t(sheet_instances")
    if k < 0:
        k = s.rfind("\n)")
    s = s[:k] + "\n" + "\n".join(add) + s[k:]

    # --- 8. on-sheet text note --------------------------------------------
    s = re.sub(
        r'\(text "No external TPM:(?:[^"\\]|\\.)*"',
        '(text "MCU U1 = TI MSPM0G3518-Q1 (PM/LQFP-64). Per-frame message '
        'authentication runs on its on-chip AES-128/256 accelerator with GCM '
        'and a 4-slot hardware keystore (REFERENCES.md [44]) -- this replaced '
        'the S32K144 CSEc, which was SHE-compliant and therefore AES-128 only. '
        'Asymmetric identity and session-key agreement remain on the OPTIGA(TM) '
        'Trust M secure element U2 (REFERENCES.md [45]); the MCU AES engine is '
        'symmetric-only, so U2 is still required. VCORE carries a dedicated '
        '470nF cap and nothing else per [44] p.51 SS7.3. See ../README.md and '
        'docs/secure-element-architecture.md"', s, count=1)
    changes.append("on-sheet CSEc text note rewritten")

    if s.count("(") != s.count(")"):
        sys.exit(f"ABORT: unbalanced parens ({s.count('(')} vs {s.count(')')})")
    SCH.write_text(s)
    print(f"wrote {SCH}")
    for c in changes:
        print("  -", c)


if __name__ == "__main__":
    main()
