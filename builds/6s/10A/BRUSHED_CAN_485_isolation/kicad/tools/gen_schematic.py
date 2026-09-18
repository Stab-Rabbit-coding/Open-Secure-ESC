#!/usr/bin/env python3
"""Generate the 6S / 10A / BRUSHED / CAN-FD+RS-485 / Isolation schematic.

Build: builds/6s/10A/BRUSHED_CAN_485_isolation/ -- the Serenity-UAV nacelle-tilt
controller (plan: Serenity-UAV docs/plans/2026-09-17-001-feat-tilt-controller-
open-secure-esc-build-plan.md, U4). Governed by AGENTS.md.

HOW THIS GENERATOR WORKS (and why it is not the 50A build's gen_schematic.py)
------------------------------------------------------------------------------
The 50A build's generator needs `kiutils`, which is not installable on every
machine this repo is worked on, and it draws wires between pin endpoints --
the trap documented in docs/solutions/architecture-patterns/
schematic-pin-y-sign-when-hand-wiring.md. This generator avoids both:

  * It writes the .kicad_sch S-expression directly (KiCad 9 format,
    version 20250114) with no third-party library.
  * It never draws a wire. Every pin that carries a net gets a GLOBAL LABEL
    placed exactly on the pin's connection point; every unused pin gets a
    no-connect flag there. Connectivity is therefore a function of one
    formula -- sheet_point = instance + (pin_x, -pin_y) for an unrotated
    instance -- and is PROVED by `kicad-cli sch export netlist`, not
    inferred from a drawing.
  * Symbol definitions are copied verbatim from `symbols/*.kicad_sym` (and
    the KiCad 9 stock libraries for Device:L / Device:D_Schottky /
    Connector_Generic:Conn_01x06) into `lib_symbols`, so the sheet stays
    self-contained and each part's Citation/Verification properties travel
    with it.

The pin geometry used for the label placement is read from the same
library files at generation time, so a regenerated symbol cannot drift from
the sheet.

NET DESIGN (every rule below cites its owner; see ../README.md)
-----------------------------------------------------------------
  VBAT      6S branch in (22.2-25.2 V) through the Serenity harness fuse.
  VMOT      6.5 V motor/solenoid rail, TPS54560B U6 [65] (KTD2).
  3V3       logic rail, TPS54560B U8 [65] (BOM-commonality judgment call).
  DRV8874-Q1 U5 [63]: PH/EN mode (PMODE strapped to GND, Table 7-2),
            IMODE level 3 = 62 kOhm to GND (Table 7-6, KTD15), nFAULT
            pulled up to 3V3 and read on PA26 (TIMA_FAL0), IPROPI into
            RIPROPI + RC into ADC A0_3, VREF from a 3V3 divider (Eq. 3).
  TPL7407L  U7 [66]: IN1+IN2 paralleled on BRAKE_EN, OUT1+OUT2 sink the
            solenoid, COM = VBAT so the clamp sits above VMOT (Sec. 6.3
            8.5-40 V), inputs carry the internal 1 MOhm pull-down (KTD9).
  Sensing   VMOT and VBAT dividers into the ADC (KTD9 rail-droop rule),
            BRAKE_SENSE divider on the solenoid low-side node.
  Bus       ADM3057E U3 [10] and ADM2587E U4 [9] with the ferrite +
            reservoir topology of the 6S/50A build (its kicad/README.md).
  Encoder   6-pin keyed header J7 to the off-board AEAT-8800-Q24 [64].

Component VALUES are engineering defaults where the datasheet gives a
formula rather than a number (dividers, RT, compensation); each such part
carries a "Note" property saying so. Values the datasheet fixes (CVCP,
CFLY, RIMODE, VCORE tank) are cited.

Usage:
    python3 gen_schematic.py            # writes ../<PROJECT>.kicad_sch
    python3 gen_schematic.py --check    # regenerate to a temp file and diff
"""
# Authored by Claude Opus 5 (Anthropic) 2026-09-17 under the direction of
# Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. AI-generated; not yet
# human-reviewed.

from __future__ import annotations

import argparse
import re
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
KICAD_DIR = HERE.parent
REPO = KICAD_DIR.parents[4]
SYMBOLS = REPO / "symbols"
STOCK = Path("/usr/share/kicad/symbols")
PROJECT = "open_secure_esc_6s_10a_brushed_can485_iso"

GRID = 1.27  # KiCad connection grid; every instance sits on it so pin ends do too
NS = uuid.UUID("6b2f2c1e-3a8d-4b1e-9d5c-1b6a7f4e2c10")


def uid(*parts: str) -> str:
    """Deterministic UUID so regeneration is diffable."""
    return str(uuid.uuid5(NS, "/".join(parts)))


# --------------------------------------------------------------- symbols --
def load_symbol(
    lib: str, name: str
) -> tuple[str, list[tuple[str, float, float, int, str]]]:
    """Return (lib_symbols entry text, pins) for LIB:NAME.

    Pins are (number, x, y, angle, etype) in symbol coordinates (Y up).
    """
    path = SYMBOLS / f"{lib}.kicad_sym"
    if not path.exists():
        path = STOCK / f"{lib}.kicad_sym"
    text = path.read_text()
    start = text.find(f'(symbol "{name}"')
    if start < 0:
        raise SystemExit(f"{lib}:{name} not found in {path}")
    # Walk parentheses to the end of this top-level symbol.
    depth = 0
    i = start
    while True:
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = text[start : i + 1]
    pins = []
    for m in re.finditer(
        r"\(pin (\w+) line\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\)[\s\S]*?\(number \"([^\"]+)\"",
        body,
    ):
        pins.append(
            (
                m.group(5),
                float(m.group(2)),
                float(m.group(3)),
                int(m.group(4)),
                m.group(1),
            )
        )
    # Normalise to the KiCad 9 in-sheet dialect.
    body = body.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)
    body = re.sub(r"\(id \d+\) ", "", body)
    body = body.replace("(stroke (width 0.0))", "(stroke (width 0) (type default))")
    body = "\n".join("    " + ln if ln.strip() else ln for ln in body.split("\n"))
    return body, pins


# ---------------------------------------------------------------- design --
# (ref, lib, name, value, footprint, (x, y) in 1.27 mm grid units, {pin_number: net or None}, note)
# A pin mapped to None gets a no-connect flag. Every pin must be listed.
GEN = "Open_Secure_ESC_Generic"
R_FP = "Resistor_SMD:R_0603_1608Metric"
C_FP = "Capacitor_SMD:C_0603_1608Metric"
C_FP_BIG = "Capacitor_SMD:C_1210_3225Metric"
CP_FP = "Capacitor_SMD:CP_Elec_6.3x5.8"

PARTS: list[tuple] = []


def part(ref, lib, name, value, fp, pos, nets, note=""):
    PARTS.append((ref, lib, name, value, fp, pos, nets, note))


def passive2(ref, lib, name, value, fp, pos, n1, n2, note=""):
    part(ref, lib, name, value, fp, pos, {"1": n1, "2": n2}, note)


# --- power entry -----------------------------------------------------------
part(
    "J1",
    GEN,
    "Conn_01x02",
    "VBAT_IN",
    "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    (40, 40),
    {"1": "VBAT", "2": "GND"},
    "6S branch from the Serenity harness (F_TILT_P/S 3 A mini blade is off-board). Connector class is a placeholder pending the harness spec.",
)
passive2(
    "C1",
    GEN,
    "C",
    "10uF 50V",
    C_FP_BIG,
    (60, 40),
    "VBAT",
    "GND",
    "Input bulk, engineering default; [65] Sec. 8.2 input capacitor guidance applies.",
)
passive2("C2", GEN, "C", "100nF 50V", C_FP, (70, 40), "VBAT", "GND", "Input HF bypass.")

# --- U6: VMOT buck (TPS54560B) --------------------------------------------
part(
    "U6",
    "TPS54560B",
    "TPS54560B",
    "TPS54560B",
    "Open_Secure_ESC:TI_DDA0008B_HSOIC-8_3.9x4.9mm_P1.27mm_EP2.71x3.4mm",
    (110, 60),
    {
        "2": "VBAT",
        "3": "U6_EN",
        "4": "U6_RT",
        "5": "U6_FB",
        "6": "U6_COMP",
        "1": "U6_BOOT",
        "8": "U6_SW",
        "7": "GND",
    },
    "Motor/solenoid rail buck, 6.5 V set by R4/R5 (KTD2). [65] Sec. 8.2 design procedure; exposed pad to GND copper.",
)
passive2(
    "R1",
    GEN,
    "R",
    "R_UVLO_HI",
    R_FP,
    (90, 80),
    "VBAT",
    "U6_EN",
    "UVLO divider upper ([65] Sec. 7.3.7) -- value from the design procedure, engineering default pending.",
)
passive2(
    "R2", GEN, "R", "R_UVLO_LO", R_FP, (90, 95), "U6_EN", "GND", "UVLO divider lower."
)
passive2(
    "R3",
    GEN,
    "R",
    "RT_500kHz",
    R_FP,
    (90, 110),
    "U6_RT",
    "GND",
    "RT/CLK timing resistor ([65] Sec. 7.3.9); 500 kHz engineering default.",
)
passive2(
    "R4",
    GEN,
    "R",
    "R_FB_HI",
    R_FP,
    (130, 95),
    "VMOT",
    "U6_FB",
    "Feedback divider upper, VOUT = 0.8 V x (1 + R4/R5) ([65] Sec. 7.3.6).",
)
passive2(
    "R5",
    GEN,
    "R",
    "R_FB_LO",
    R_FP,
    (130, 110),
    "U6_FB",
    "GND",
    "Feedback divider lower.",
)
passive2(
    "R6",
    GEN,
    "R",
    "R_COMP",
    R_FP,
    (90, 125),
    "U6_COMP",
    "U6_CZ",
    "Type-II compensation ([65] Sec. 8.2.2.7), engineering default pending.",
)
passive2(
    "C3",
    GEN,
    "C",
    "C_COMP",
    C_FP,
    (90, 140),
    "U6_CZ",
    "GND",
    "Compensation zero capacitor.",
)
passive2(
    "C4",
    GEN,
    "C",
    "100nF",
    C_FP,
    (140, 60),
    "U6_BOOT",
    "U6_SW",
    "Bootstrap capacitor ([65] Sec. 7.3.4).",
)
part(
    "L1",
    "Device",
    "L",
    "L_VMOT",
    "Inductor_SMD:L_Wuerth_HCI-5040",
    (150, 75),
    {"1": "U6_SW", "2": "VMOT"},
    "Buck inductor -- part NOT selected; height <= 4 mm on the web-facing side is a hard constraint (README host constraints). UNVERIFIED -- needs primary source (see TODO.md 18.3).",
)
part(
    "D1",
    "Device",
    "D_Schottky",
    "D_CATCH_60V",
    "Diode_SMD:D_SMA",
    (150, 95),
    {"1": "U6_SW", "2": "GND"},
    "Catch diode, >= 60 V, >= 5 A avg -- part NOT selected. UNVERIFIED -- needs primary source (see TODO.md 18.3).",
)
passive2(
    "C5",
    GEN,
    "C",
    "22uF 16V",
    C_FP_BIG,
    (165, 95),
    "VMOT",
    "GND",
    "VMOT bulk; also the DRV8874 CVM2 ([63] Table 7-1, Sec. 9.1) sized in U4's follow-up.",
)
passive2(
    "C6",
    GEN,
    "C",
    "22uF 16V",
    C_FP_BIG,
    (175, 95),
    "VMOT",
    "GND",
    "VMOT bulk (second).",
)

# --- U8: 3V3 buck (TPS54560B) ---------------------------------------------
part(
    "U8",
    "TPS54560B",
    "TPS54560B",
    "TPS54560B",
    "Open_Secure_ESC:TI_DDA0008B_HSOIC-8_3.9x4.9mm_P1.27mm_EP2.71x3.4mm",
    (110, 190),
    {
        "2": "VBAT",
        "3": "U8_EN",
        "4": "U8_RT",
        "5": "U8_FB",
        "6": "U8_COMP",
        "1": "U8_BOOT",
        "8": "U8_SW",
        "7": "GND",
    },
    "3.3 V logic rail. Same part as U6 for BOM commonality (judgment call, AGENTS.md Sec. 4); a smaller buck may replace it once the inductor height budget is known.",
)
passive2(
    "R7", GEN, "R", "R_UVLO_HI", R_FP, (90, 210), "VBAT", "U8_EN", "UVLO divider upper."
)
passive2(
    "R8", GEN, "R", "R_UVLO_LO", R_FP, (90, 225), "U8_EN", "GND", "UVLO divider lower."
)
passive2(
    "R9",
    GEN,
    "R",
    "RT_500kHz",
    R_FP,
    (90, 240),
    "U8_RT",
    "GND",
    "RT/CLK timing resistor.",
)
passive2(
    "R10",
    GEN,
    "R",
    "R_FB_HI",
    R_FP,
    (130, 225),
    "3V3",
    "U8_FB",
    "Feedback divider upper, 3.3 V.",
)
passive2(
    "R11",
    GEN,
    "R",
    "R_FB_LO",
    R_FP,
    (130, 240),
    "U8_FB",
    "GND",
    "Feedback divider lower.",
)
passive2(
    "R12", GEN, "R", "R_COMP", R_FP, (90, 255), "U8_COMP", "U8_CZ", "Compensation."
)
passive2(
    "C7",
    GEN,
    "C",
    "C_COMP",
    C_FP,
    (90, 270),
    "U8_CZ",
    "GND",
    "Compensation zero capacitor.",
)
passive2(
    "C8",
    GEN,
    "C",
    "100nF",
    C_FP,
    (140, 190),
    "U8_BOOT",
    "U8_SW",
    "Bootstrap capacitor.",
)
part(
    "L2",
    "Device",
    "L",
    "L_3V3",
    "Inductor_SMD:L_Wuerth_HCI-5040",
    (150, 205),
    {"1": "U8_SW", "2": "3V3"},
    "Buck inductor -- part NOT selected, same height constraint as L1. UNVERIFIED -- needs primary source (see TODO.md 18.3).",
)
part(
    "D2",
    "Device",
    "D_Schottky",
    "D_CATCH_60V",
    "Diode_SMD:D_SMA",
    (150, 225),
    {"1": "U8_SW", "2": "GND"},
    "Catch diode -- part NOT selected. UNVERIFIED -- needs primary source (see TODO.md 18.3).",
)
passive2("C9", GEN, "C", "22uF 10V", C_FP_BIG, (165, 225), "3V3", "GND", "3V3 bulk.")
passive2("C10", GEN, "C", "100nF", C_FP, (175, 225), "3V3", "GND", "3V3 HF bypass.")

# --- U5: DRV8874-Q1 bridge --------------------------------------------------
part(
    "U5",
    "DRV8874_Q1",
    "DRV8874_Q1",
    "DRV8874-Q1",
    "Open_Secure_ESC:TI_PWP0016J_HTSSOP-16_4.4x5mm_P0.65mm_EP2.46x3.55mm",
    (260, 70),
    {
        "1": "MOT_EN",
        "2": "MOT_PH",
        "3": "MOT_nSLEEP",
        "16": "GND",
        "7": "U5_IMODE",
        "5": "U5_VREF",
        "4": "MOT_nFAULT",
        "6": "U5_IPROPI",
        "8": "MOT_OUT1",
        "10": "MOT_OUT2",
        "12": "U5_VCP",
        "13": "U5_CPH",
        "14": "U5_CPL",
        "11": "VMOT",
        "9": "GND",
        "15": "GND",
    },
    "PH/EN mode: PMODE (16) strapped to GND ([63] Table 7-2). Exposed pad to GND copper. Every fault coasts the bridge ([63] Table 7-7) -- firmware engages the brake on nFAULT (KTD9).",
)
passive2(
    "C11",
    GEN,
    "C",
    "100nF 50V",
    C_FP,
    (285, 40),
    "VMOT",
    "GND",
    "CVM1 ([63] Table 7-1): 0.1 uF low-ESR ceramic at VM.",
)
passive2(
    "C12",
    GEN,
    "C",
    "100nF 16V",
    C_FP,
    (300, 40),
    "U5_VCP",
    "VMOT",
    "CVCP ([63] Table 7-1): 100 nF 16 V X5R/X7R, VCP to VM.",
)
passive2(
    "C13",
    GEN,
    "C",
    "22nF 50V",
    C_FP,
    (300, 60),
    "U5_CPH",
    "U5_CPL",
    "CFLY ([63] Table 7-1): 22 nF VM-rated X5R/X7R, CPH to CPL.",
)
passive2(
    "R13",
    GEN,
    "R",
    "10k",
    R_FP,
    (300, 85),
    "3V3",
    "MOT_nFAULT",
    "RnFAULT ([63] Table 7-1): pull-up, IOD <= 5 mA.",
)
passive2(
    "R14",
    GEN,
    "R",
    "R_VREF_HI",
    R_FP,
    (230, 100),
    "3V3",
    "U5_VREF",
    "VREF divider: ITRIP = VVREF / (AIPROPI x RIPROPI) ([63] Eq. 3). Set ITRIP just above the 20D's 2.9 A stall so ITRIP is a stall backstop, not a working limit (KTD6). Value pending.",
)
passive2(
    "R15",
    GEN,
    "R",
    "R_VREF_LO",
    R_FP,
    (230, 115),
    "U5_VREF",
    "GND",
    "VREF divider lower.",
)
passive2(
    "R16",
    GEN,
    "R",
    "RIPROPI",
    R_FP,
    (300, 105),
    "U5_IPROPI",
    "GND",
    "RIPROPI ([63] Sec. 7.3.3.1): VIPROPI = IPROPI x RIPROPI with AIPROPI 450 uA/A; choose for ~2.5 V at ITRIP.",
)
passive2(
    "R17",
    GEN,
    "R",
    "1k",
    R_FP,
    (315, 105),
    "U5_IPROPI",
    "ADC_IPROPI",
    "IPROPI RC filter series element into the ADC.",
)
passive2(
    "C14",
    GEN,
    "C",
    "10nF",
    C_FP,
    (330, 105),
    "ADC_IPROPI",
    "GND",
    "IPROPI RC filter capacitor.",
)
passive2(
    "R18",
    GEN,
    "R",
    "62k",
    R_FP,
    (230, 130),
    "U5_IMODE",
    "GND",
    "RIMODE = 62 kOhm to GND = quad-level 3: cycle-by-cycle chopping, outputs latched off on OCP, nFAULT reports chopping ([63] Table 7-6; KTD15).",
)
part(
    "J2",
    GEN,
    "Conn_01x02",
    "MOTOR",
    "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    (330, 70),
    {"1": "MOT_OUT1", "2": "MOT_OUT2"},
    "Pololu 20D 25:1 CB 6 V gearmotor (Serenity REF-ACT-001). Actuator-positive = nacelle-positive on PORT; starboard sense is reversed in firmware (TC-6).",
)

# --- U7: brake driver -------------------------------------------------------
part(
    "U7",
    "TPL7407L",
    "TPL7407L",
    "TPL7407L",
    "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
    (260, 200),
    {
        "1": "BRAKE_EN",
        "2": "BRAKE_EN",
        "3": None,
        "4": None,
        "5": None,
        "6": None,
        "7": None,
        "16": "SOL_N",
        "15": "SOL_N",
        "14": None,
        "13": None,
        "12": None,
        "11": None,
        "10": None,
        "9": "VBAT",
        "8": "GND",
    },
    "IN1+IN2 paralleled, OUT1+OUT2 paralleled ([66] Sec. 7.1) for the ~0.5 A solenoid; unused inputs float on their internal 1 MOhm pull-downs ([66] Sec. 7.3); COM = VBAT keeps the clamp inside 8.5-40 V ([66] Sec. 6.3) and above VMOT. De-energised = engaged (KTD9).",
)
part(
    "J3",
    GEN,
    "Conn_01x02",
    "BRAKE_SOL",
    "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    (330, 200),
    {"1": "VMOT", "2": "SOL_N"},
    "Pin-brake pull solenoid (Serenity BRK-4, SOL-TILT-BRAKE): coil between VMOT and the low-side sink. Hold-in voltage to be recorded under BRK-4.",
)
passive2(
    "R32",
    GEN,
    "R",
    "100k",
    R_FP,
    (230, 215),
    "BRAKE_EN",
    "GND",
    "External BRAKE_EN pull-down (KTD9: MCU reset / Hi-Z = brake engaged), in addition to the TPL7407L's internal 1 MOhm ([66] Sec. 7.3).",
)
passive2(
    "R19",
    GEN,
    "R",
    "100k",
    R_FP,
    (300, 230),
    "SOL_N",
    "BRAKE_SENSE",
    "Brake-state readback divider upper: SOL_N ~0 V released, ~VMOT engaged.",
)
passive2(
    "R20",
    GEN,
    "R",
    "47k",
    R_FP,
    (300, 245),
    "BRAKE_SENSE",
    "GND",
    "Brake-state divider lower (VMOT 6.5 V -> ~2.1 V).",
)

# --- rail sensing ----------------------------------------------------------
passive2(
    "R21",
    GEN,
    "R",
    "100k",
    R_FP,
    (360, 100),
    "VMOT",
    "ADC_VM",
    "VMOT sense divider upper (KTD9: EN=0 before the solenoid drops out).",
)
passive2(
    "R22",
    GEN,
    "R",
    "47k",
    R_FP,
    (360, 115),
    "ADC_VM",
    "GND",
    "VMOT sense divider lower.",
)
passive2(
    "R23",
    GEN,
    "R",
    "180k",
    R_FP,
    (380, 100),
    "VBAT",
    "ADC_VBUS",
    "VBAT sense divider upper (25.2 V -> ~2.6 V).",
)
passive2(
    "R24",
    GEN,
    "R",
    "20k",
    R_FP,
    (380, 115),
    "ADC_VBUS",
    "GND",
    "VBAT sense divider lower.",
)

# --- U1: MCU ----------------------------------------------------------------
part(
    "U1",
    "MSPM0G3518_Q1_RHB_TILT",
    "MSPM0G3518_Q1_RHB_TILT",
    "MSPM0G3518-Q1 RHB",
    "Package_DFN_QFN:Texas_RHB0032E_VQFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
    (500, 120),
    {
        "1": "RS485_TXD",
        "2": "RS485_RXD",
        "10": "RS485_DE_RE",
        "16": "CAN_TX",
        "17": "CAN_RX",
        "9": "SE_I2C_SDA",
        "19": "SE_I2C_SCL",
        "18": "SE_RST",
        "23": "SWDIO",
        "24": "SWCLK",
        "11": "TRIP_IN",
        "12": "MOT_EN",
        "13": "MOT_PH",
        "7": "MOT_nSLEEP",
        "30": "MOT_nFAULT",
        "8": "BRAKE_EN",
        "6": "ENC_SPI_CS",
        "21": "ENC_SPI_SCK",
        "20": "ENC_SPI_MISO",
        "22": "ENC_SPI_MOSI",
        "14": None,
        "15": None,
        "29": None,
        "31": None,
        "28": "ADC_IPROPI",
        "27": "ADC_VM",
        "26": "BRAKE_SENSE",
        "25": "ADC_VBUS",
        "4": "3V3",
        "32": "VCORE",
        "3": "NRST",
        "5": "GND",
    },
    "Project MCU [44], tilt-build role names (symbols/specs/MSPM0G3518_Q1_RHB_TILT.json). Exposed pad to GND copper.",
)
passive2(
    "C15",
    GEN,
    "C",
    "470nF",
    C_FP,
    (470, 60),
    "VCORE",
    "GND",
    "VCORE tank, 0.47 uF +/-20 % required by [44] (verified in the 6S/50A build README).",
)
passive2("C16", GEN, "C", "100nF", C_FP, (480, 60), "3V3", "GND", "MCU VDD decoupling.")
passive2("R25", GEN, "R", "47k", R_FP, (520, 60), "3V3", "NRST", "NRST pull-up.")
passive2("C17", GEN, "C", "10nF", C_FP, (535, 60), "NRST", "GND", "NRST filter.")
part(
    "J4",
    GEN,
    "Conn_01x04",
    "SWD",
    "Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical",
    (560, 200),
    {"1": "SWDIO", "2": "SWCLK", "3": "3V3", "4": "GND"},
    "SWD debug header, as the 6S/50A build's J1.",
)
part(
    "J8",
    GEN,
    "Conn_01x02",
    "TRIP",
    "Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical",
    (560, 230),
    {"1": "TRIP_IN", "2": "GND"},
    "Differential-tilt trip input (Serenity TILT-CTL-02): executor and independence to be defined; pulled up on the MCU.",
)

# --- U2: OPTIGA Trust M -----------------------------------------------------
part(
    "U2",
    "OPTIGA_TRUST_M",
    "OPTIGA_TRUST_M",
    "OPTIGA Trust M V3",
    "Open_Secure_ESC:Infineon_PG-USON-10-2-4_3x3mm_P0.5mm_EP1.7x2.5mm",
    (640, 100),
    {
        "3": "SE_I2C_SDA",
        "8": "SE_I2C_SCL",
        "9": "SE_RST",
        "2": None,
        "4": None,
        "5": None,
        "6": None,
        "7": None,
        "10": "3V3",
        "1": "GND",
    },
    "Secure element [45]; circuit per [45] p.12 Sec. 3 Fig. 2, as the 6S/50A build.",
)
passive2("R26", GEN, "R", "10k", R_FP, (665, 80), "3V3", "SE_I2C_SDA", "I2C pull-up.")
passive2("R27", GEN, "R", "10k", R_FP, (680, 80), "3V3", "SE_I2C_SCL", "I2C pull-up.")
passive2(
    "C18", GEN, "C", "100nF", C_FP, (665, 130), "3V3", "GND", "OPTIGA VCC decoupling."
)

# --- U3: isolated CAN-FD ---------------------------------------------------
part(
    "U3",
    "ADM3055E_ADM3057E",
    "ADM3055E_ADM3057E",
    "ADM3057E",
    "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm",
    (760, 100),
    {
        "1": "GND",
        "2": "GND",
        "3": "3V3",
        "4": "3V3",
        "5": "CAN_RX",
        "6": "GND",
        "7": "CAN_TX",
        "8": "GND",
        "9": None,
        "10": "GND",
        "11": "CAN_ISO_GND",
        "12": "CAN_ISO_GND",
        "13": "CAN_L",
        "14": "CAN_H",
        "15": "CAN_ISO_GND",
        "16": "CAN_VISOIN",
        "17": None,
        "18": "CAN_GNDISO",
        "19": "CAN_VISOOUT",
        "20": "CAN_GNDISO",
    },
    "Isolated CAN-FD [10]; ADM3057E chosen over ADM3055E for lower creepage at identical timing (KTD5). Same pin-to-net map as the 6S/50A build (its netlist, 2026-09-17).",
)
part(
    "FB1",
    "BLM15HD182SN1D",
    "BLM15HD182SN1D",
    "BLM15HD182SN1D",
    "Inductor_SMD:L_0402_1005Metric",
    (800, 60),
    {"1": "CAN_VISOOUT", "2": "CAN_VISOIN"},
    "Isolated-supply ferrite ([10] p.25), as the 50A build FB1.",
)
part(
    "FB2",
    "BLM15HD182SN1D",
    "BLM15HD182SN1D",
    "BLM15HD182SN1D",
    "Inductor_SMD:L_0402_1005Metric",
    (800, 140),
    {"1": "CAN_GNDISO", "2": "CAN_ISO_GND"},
    "Isolated-ground ferrite, as the 50A build FB2.",
)
passive2(
    "C19",
    GEN,
    "C",
    "10uF",
    C_FP,
    (820, 60),
    "CAN_VISOOUT",
    "CAN_GNDISO",
    "VISOOUT reservoir.",
)
passive2(
    "C20",
    GEN,
    "C",
    "100nF",
    C_FP,
    (830, 60),
    "CAN_VISOOUT",
    "CAN_GNDISO",
    "VISOOUT bypass.",
)
passive2(
    "C21",
    GEN,
    "C",
    "10uF",
    C_FP,
    (820, 100),
    "CAN_VISOIN",
    "CAN_ISO_GND",
    "VISOIN reservoir.",
)
passive2(
    "C22",
    GEN,
    "C",
    "100nF",
    C_FP,
    (830, 100),
    "CAN_VISOIN",
    "CAN_ISO_GND",
    "VISOIN bypass.",
)
part(
    "J5",
    GEN,
    "Conn_01x02",
    "CAN",
    "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    (850, 100),
    {"1": "CAN_H", "2": "CAN_L"},
    "CAN-FD trunk (nacelle gateway relays the signed AK7455 angle).",
)

# --- U4: isolated RS-485 ---------------------------------------------------
part(
    "U4",
    "ADM2582E_ADM2587E",
    "ADM2582E_ADM2587E",
    "ADM2587E",
    "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm",
    (760, 220),
    {
        "1": "GND",
        "2": "3V3",
        "3": "GND",
        "4": "RS485_RXD",
        "5": "RS485_DE_RE",
        "6": "RS485_DE_RE",
        "7": "RS485_TXD",
        "8": "3V3",
        "9": "GND",
        "10": "GND",
        "11": "RS485_GNDISO",
        "12": "RS485_VISOOUT",
        "13": "RS485_A",
        "14": "RS485_GNDISO",
        "15": "RS485_B",
        "16": "RS485_ISO_GND",
        "17": "RS485_B",
        "18": "RS485_A",
        "19": "RS485_VISOIN",
        "20": "RS485_ISO_GND",
    },
    "Isolated RS-485 [9], half-duplex (Y/A and Z/B tied), same map as the 6S/50A build. Carries the shaft-position MV and telemetry (Serenity TILT_DRIVE_CONTROL_SPEC.md Sec. 1).",
)
part(
    "FB3",
    "BLM15HD182SN1D",
    "BLM15HD182SN1D",
    "BLM15HD182SN1D",
    "Inductor_SMD:L_0402_1005Metric",
    (800, 180),
    {"1": "RS485_VISOOUT", "2": "RS485_VISOIN"},
    "Isolated-supply ferrite, as the 50A build FB3.",
)
part(
    "FB4",
    "BLM15HD182SN1D",
    "BLM15HD182SN1D",
    "BLM15HD182SN1D",
    "Inductor_SMD:L_0402_1005Metric",
    (800, 260),
    {"1": "RS485_GNDISO", "2": "RS485_ISO_GND"},
    "Isolated-ground ferrite, as the 50A build FB4.",
)
passive2(
    "C23",
    GEN,
    "C",
    "10uF",
    C_FP,
    (820, 180),
    "RS485_VISOOUT",
    "RS485_GNDISO",
    "VISOOUT reservoir.",
)
passive2(
    "C24",
    GEN,
    "C",
    "100nF",
    C_FP,
    (830, 180),
    "RS485_VISOOUT",
    "RS485_GNDISO",
    "VISOOUT bypass.",
)
passive2(
    "C25",
    GEN,
    "C",
    "10uF",
    C_FP,
    (820, 220),
    "RS485_VISOIN",
    "RS485_ISO_GND",
    "VISOIN reservoir.",
)
passive2(
    "C26",
    GEN,
    "C",
    "100nF",
    C_FP,
    (830, 220),
    "RS485_VISOIN",
    "RS485_ISO_GND",
    "VISOIN bypass.",
)
part(
    "J6",
    GEN,
    "Conn_01x02",
    "RS485",
    "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    (850, 220),
    {"1": "RS485_A", "2": "RS485_B"},
    "RS-485 fleet segment.",
)

# --- J7: encoder header -----------------------------------------------------
part(
    "J7",
    "Connector_Generic",
    "Conn_01x06",
    "ENCODER",
    "Connector_JST:JST_GH_BM06B-GHS-TBT_1x06-1MP_P1.25mm_Vertical",
    (640, 220),
    {
        "1": "3V3",
        "2": "GND",
        "3": "ENC_SCK_J",
        "4": "ENC_MISO_J",
        "5": "ENC_CS_J",
        "6": "ENC_MOSI_J",
    },
    "Keyed 6-pin header to the off-board AEAT-8800-Q24 [64] in the Serenity brake guide (~35 mm cable); pinout 3V3, GND, SCLK, DO, NSL, DI.",
)
passive2(
    "R28",
    GEN,
    "R",
    "33R",
    R_FP,
    (600, 240),
    "ENC_SPI_SCK",
    "ENC_SCK_J",
    "Series termination, SCLK out ([64]; docs/design-speed-sensor-integration.md).",
)
passive2(
    "R29",
    GEN,
    "R",
    "33R",
    R_FP,
    (600, 255),
    "ENC_MISO_J",
    "ENC_SPI_MISO",
    "Series element, DO in.",
)
passive2(
    "R30",
    GEN,
    "R",
    "33R",
    R_FP,
    (600, 270),
    "ENC_SPI_CS",
    "ENC_CS_J",
    "Series termination, NSL out.",
)
passive2(
    "R31",
    GEN,
    "R",
    "33R",
    R_FP,
    (600, 285),
    "ENC_SPI_MOSI",
    "ENC_MOSI_J",
    "Series termination, DI out.",
)

# --- power flags ------------------------------------------------------------
FLAGS = [
    "VBAT",
    "GND",
    "VMOT",
    "3V3",
    "CAN_VISOIN",
    "CAN_ISO_GND",
    "CAN_GNDISO",
    "RS485_VISOIN",
    "RS485_ISO_GND",
    "RS485_GNDISO",
]


# ------------------------------------------------------------------ emit --
def q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def f(v: float) -> str:
    v = round(v, 4)
    return str(int(v)) if float(v).is_integer() else repr(v)


def build() -> str:
    libs: dict[str, tuple[str, list]] = {}

    def lib(libname, name):
        key = f"{libname}:{name}"
        if key not in libs:
            libs[key] = load_symbol(libname, name)
        return libs[key]

    for p in PARTS:
        lib(p[1], p[2])
    lib(GEN, "PWR_FLAG")

    out = [
        '(kicad_sch (version 20250114) (generator "open_secure_esc_schgen") (generator_version "9.0")',
        f"  (uuid {uid('sheet')})",
        '  (paper "A0")',
        "  (title_block",
        '    (title "Open-Secure-ESC -- 6S / 10A / BRUSHED / CAN-FD+RS-485 / Isolation")',
        '    (date "2026-09-17")',
        '    (rev "0.1-schematic")',
        '    (company "Griffing Technology LLC")',
        '    (comment 1 "Build spec: builds/6s/10A/BRUSHED_CAN_485_isolation/README.md")',
        '    (comment 2 "Serenity-UAV nacelle-tilt controller (plan docs/plans/2026-09-17-001)")',
        '    (comment 3 "Generated by kicad/tools/gen_schematic.py -- regenerate, do not hand-edit")',
        "  )",
        "  (lib_symbols",
    ]
    for key in sorted(libs):
        out.append(libs[key][0])
    out.append("  )")

    def instance(ref, libname, name, value, fp, x, y, pins, note, in_bom=True):
        """One placed symbol; property text sits above the body, hidden fields at the origin."""
        vis = "yes" if in_bom else "no"
        hide_ref = "" if in_bom else " (hide yes)"
        block = [
            f"  (symbol (lib_id {q(libname + ':' + name)}) (at {f(x)} {f(y)} 0) (unit 1)",
            f"    (exclude_from_sim no) (in_bom {vis}) (on_board {vis}) (dnp no)",
            f"    (uuid {uid(ref)})",
            (
                f'    (property "Reference" {q(ref)} (at {f(x)} {f(y - 20)} 0) '
                f"(effects (font (size 1.27 1.27)){hide_ref}))"
            ),
            f'    (property "Value" {q(value)} (at {f(x)} {f(y - 17.5)} 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Footprint" {q(fp)} (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
            f'    (property "Datasheet" "" (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        ]
        if note:
            block.append(
                f'    (property "Note" {q(note)} (at {f(x)} {f(y + 20)} 0) (effects (font (size 1.27 1.27)) (hide yes)))'
            )
        block += [
            f"    (pin {q(num)} (uuid {uid(ref, 'pin', num)}))" for num, *_ in pins
        ]
        block += [
            "    (instances",
            f"      (project {q(PROJECT)}",
            f"        (path {q('/' + uid('sheet'))} (reference {q(ref)}) (unit 1))",
            "      )",
            "    )",
            "  )",
        ]
        return block

    def label(net, sx, sy, rot, *key):
        return [
            f"  (global_label {q(net)} (shape passive) (at {f(sx)} {f(sy)} {rot}) (fields_autoplaced yes)",
            "    (effects (font (size 1.27 1.27)) (justify left))",
            f"    (uuid {uid(*key)})",
            "  )",
        ]

    for ref, libname, name, value, fp, (gx, gy), nets, note in PARTS:
        x, y = gx * GRID, gy * GRID  # positions are authored in 1.27 mm grid units
        _, pins = libs[f"{libname}:{name}"]
        declared = set(nets)
        actual = {p[0] for p in pins}
        if declared != actual:
            raise SystemExit(
                f"{ref}: pins {sorted(actual - declared)} unmapped / {sorted(declared - actual)} unknown"
            )
        out += instance(ref, libname, name, value, fp, x, y, pins, note)
        # Labels / no-connects at the pin connection points: sheet = instance + (px, -py).
        for num, px, py, ang, _et in pins:
            sx, sy = x + px, y - py
            net = nets[num]
            if net is None:
                out.append(
                    f"  (no_connect (at {f(sx)} {f(sy)}) (uuid {uid(ref, 'nc', num)}))"
                )
            else:
                # Label text points away from the body: pin angle 0 = pin points
                # left (label rotation 180), 180 = right, 90 = down, 270 = up.
                rot = {0: 180, 180: 0, 90: 270, 270: 90}[ang]
                out += label(net, sx, sy, rot, ref, "lbl", num)

    # Power flags: a PWR_FLAG symbol whose single pin sits on a labelled point.
    _, fpins = libs[f"{GEN}:PWR_FLAG"]
    for i, net in enumerate(FLAGS):
        x, y = (40 + 20 * i) * GRID, 330 * GRID
        ref = f"#FLG{i + 1:02d}"
        out += instance(
            ref, GEN, "PWR_FLAG", "PWR_FLAG", "", x, y, fpins, "", in_bom=False
        )
        num, px, py, ang, _et = fpins[0]
        out += label(net, x + px, y - py, 0, ref, "lbl")

    out += [
        "  (sheet_instances",
        '    (path "/" (page "1"))',
        "  )",
        ")",
    ]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check", action="store_true", help="diff against the committed sheet"
    )
    args = ap.parse_args(argv)
    target = KICAD_DIR / f"{PROJECT}.kicad_sch"
    text = build()
    if args.check:
        if target.exists() and target.read_text() == text:
            print("OK: committed sheet matches the generator")
            return 0
        print("STALE: committed sheet differs from the generator output")
        return 1
    target.write_text(text)
    print(f"wrote {target} ({len(PARTS)} parts, {len(FLAGS)} power flags)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
