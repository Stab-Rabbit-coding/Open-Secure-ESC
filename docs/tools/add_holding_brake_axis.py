#!/usr/bin/env python3
"""Add the Holding Brake axis and the tilt-build rows to docs/decision-matrix.xlsx.

Governed by AGENTS.md. Companion to the Serenity-UAV plan
``docs/plans/2026-09-17-001-feat-tilt-controller-open-secure-esc-build-plan.md``
(U2) and to ``builds/6s/10A/BRUSHED_CAN_485_isolation/README.md``.

WHY THIS AXIS EXISTS
--------------------
The Serenity nacelle-tilt actuator is a brushed gearmotor driving a
multi-start worm that is NOT self-locking (Serenity
``docs/solutions/design-patterns/self-locking-worm-and-vectoring-bandwidth-
are-mutually-exclusive.md``). The only unpowered hold is a spring-applied,
power-released pin brake, and the controller must drive its solenoid so
that:

  * de-energised = engaged (the brake holds when the controller's own
    power path fails);
  * an MCU reset or a floating GPIO also engages it (the driver input needs
    a pull-down, not just firmware);
  * the coil's inductive kick is clamped;
  * brake state is readable on the bus.

None of the existing axes can express that. A brake output is a safety
property of the build, so it is carried as its own axis with a Fail-state
column rather than as a build-local note.

WHAT THIS SCRIPT CHANGES
------------------------
1. Adds (or replaces) a **Holding Brake** sheet with two rows:
   ``None`` and ``Low-side solenoid driver, spring-applied``.
2. Resolves the **Motor** sheet's ``Brushed (DC)`` row: the gate-driver
   cell was ``TBD`` since 2026-08-16 (TODO.md 12.6.a). It now names the
   TI DRV8874-Q1 integrated H-bridge [63] (non-Q1 twin [62]), and the
   shunt count drops to 0 because the driver's IPROPI current mirror
   replaces the shunt + INA240 of the brushless tiers.
3. Appends a **Magnetic absolute (SPI/SSI)** row to the **Shaft Sensor**
   sheet for the Broadcom AEAT-8800-Q24 [64], read remotely over a keyed
   header.
4. Adds an override note to the **Amperage** sheet: for a brushed build the
   Motor sheet's bridge row overrides the FET / gate-driver / shunt /
   current-sense-amp columns; the Amperage sheet still governs copper and
   connector class. The 10 A row's tag cell gains [62], [63].
5. Lists the new sheet in the **Legend**.

Every part named here has a local, verified datasheet (REFERENCES.md
[62]-[66]). Cells that have no verified answer keep the literal TBD marker.

The script is idempotent: re-running replaces the Holding Brake sheet,
rewrites the same Motor/Amperage cells to the same values, and does not
append a second Shaft Sensor row or Legend line. The workbook is backed up
to a timestamped file first so the existing ``decision-matrix.xlsx.bak`` is
not clobbered.

Requires: openpyxl

Usage:
    python3 docs/tools/add_holding_brake_axis.py [--dry-run]

Then regenerate the JSON export:
    python3 docs/tools/decision_matrix_to_json.py
"""
# Authored by Claude Opus 5 (Anthropic) 2026-09-17 under the direction of
# Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. AI-generated; every part
# selection is carried from REFERENCES.md [62]-[66] or explicitly left open.
# Not yet human-reviewed.

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

REPO = Path(__file__).resolve().parents[2]
WORKBOOK = REPO / "docs" / "decision-matrix.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="FF2F5597")
HEADER_FONT = Font(bold=True, size=10, color="FFFFFFFF")
TITLE_FONT = Font(bold=True, size=16)
SUB_FONT = Font(size=10)
BODY_ALIGN = Alignment(wrap_text=True, vertical="top")
HEADER_ALIGN = Alignment(wrap_text=True, vertical="center")

# --------------------------------------------------------- Holding Brake -----
BRAKE = {
    "title": "Holding Brake Decision Matrix",
    "subtitle": (
        "Build axis: Holding Brake (None / Low-side solenoid driver, spring-applied)"
    ),
    "widths": [28, 34, 40, 26, 40, 30, 44, 18, 22],
    "columns": [
        "Brake Option",
        "Actuation",
        "Fail-state",
        "MCU Pins Required",
        "Additional BOM Component",
        "Connector",
        "Firmware Workflow Steps",
        "REFERENCES.md Tags",
        "Status",
    ],
    "rows": [
        [
            "None",
            (
                "No holding brake. The load is held by the motor's own "
                "drag, a self-locking transmission, or nothing."
            ),
            (
                "Not applicable -- the build has no brake to fail. A "
                "non-self-locking transmission on a load that must hold "
                "unpowered may NOT select this row."
            ),
            "0",
            "None",
            "None",
            "None",
            "-",
            "No part needed",
        ],
        [
            "Low-side solenoid driver, spring-applied",
            (
                "Spring-applied, power-released pin brake. A pull "
                "solenoid retracts the pin while its coil is energised; "
                "the spring engages the pin when the coil is released. "
                "The coil is switched on its low side."
            ),
            (
                "De-energised = engaged. The driver input carries a "
                "pull-down so an MCU reset, brown-out or floating GPIO "
                "engages the brake without firmware; the coil's inductive "
                "kick is clamped; brake state (drive-pin readback) is "
                "published on the bus. Engage-on-fault: the motor driver's "
                "nFAULT is a brake-engage input for firmware."
            ),
            (
                "1 digital out (BRAKE_EN) plus 1 digital in or ADC for "
                "state readback; optionally 1 ADC for the coil supply "
                "rail so the pin is never dropped into a driven "
                "castellation."
            ),
            (
                "TI TPL7407L [66]: 40 V 7-channel NMOS low-side array, "
                "600 mA per channel (channels paralleled for the load), "
                "1 MOhm input pull-down per channel, internal clamp "
                "diodes to COM. Return COM to the pack-side rail so the "
                "clamp sits above the coil supply and inside the COM "
                "range (8.5-40 V, [66] Sec.6.3). The solenoid itself is a "
                "host-side part outside this axis (Serenity-UAV item "
                "BRK-4); this row carries only the driver."
            ),
            "2-pin (COIL+, COIL-) keyed header; polarity marked",
            (
                "Release only on an authenticated release command after "
                "the loop has unloaded the pin; sequence release -> move "
                "-> settle (encoder stationary) -> engage; engage on "
                "nFAULT, on bus loss after a timeout, and on coil-rail "
                "droop below the solenoid hold-in voltage; publish brake "
                "state every telemetry frame."
            ),
            "[66]",
            "Verified (local PDF)",
        ],
    ],
}

BRAKE_NOTES = (
    "A brake on the actuator shaft protects against loss of drive, not "
    "against a broken transmission downstream of it. The 'Fail-state' "
    "column is the safety property this axis exists to record -- a build "
    "that selects the solenoid row must reproduce every item in it, not "
    "just the part number. First instance: "
    "builds/6s/10A/BRUSHED_CAN_485_isolation/ (Serenity-UAV nacelle tilt)."
)

# ------------------------------------------------------- Shaft Sensor row ---
MAGNETIC_ROW = [
    "Magnetic absolute (SPI/SSI)",
    (
        "Single-turn absolute angle from an on-axis Hall sensor IC reading "
        "a diametric two-pole magnet on the shaft end; 10- to 16-bit "
        "absolute word over SSI/SPI, optional ABI/UVW/PWM outputs. Multi-"
        "turn position is accumulated in firmware."
    ),
    (
        "3 (SCLK, DO, NSL/CS) for SSI, 4 with DI for SPI; sensor supply "
        "3.3 V. The sensor may sit off-board on a short cable."
    ),
    (
        "Broadcom AEAT-8800-Q24 [64], QFN-24 5 x 5 mm, 3.3 V or 5 V "
        "operation, SSI 3-wire absolute output. Series resistors and ESD "
        "protection on each line per docs/design-speed-sensor-integration.md."
    ),
    "6-pin keyed (3V3, GND, SCLK, DO, NSL, DI) with shield/drain optional",
    (
        "Read the absolute word each control tick; unwrap turns across the "
        "0/full-scale boundary; home the multi-turn count from an outer "
        "absolute reference (a host sensor over the bus) at power-up; "
        "declare 'stationary' from this sensor, not from motor current."
    ),
    "[64]",
    "Verified (local PDF)",
]

# ------------------------------------------------------------ Motor row ------
MOTOR_UPDATES = {
    "Gate Driver Part": (
        "TI DRV8874-Q1 [63] integrated N-channel H-bridge (non-Q1 twin "
        "DRV8874 [62]): 4.5-37 V VM, 6 A peak, 100 mOhm typ per FET, "
        "PH/EN or PWM control, IPROPI current mirror 450 uA/A, VREF/ITRIP "
        "current regulation, UVLO/CPUV/OCP/TSD. Tier 1 (2S-6S, 10-20 A) "
        "per docs/OpenSecureESC-Brushed-Specifications.md Sec.1; every "
        "fault coasts the bridge ([63] Table 7)."
    ),
    "Shunt Qty": (
        "0 -- the driver's IPROPI current mirror replaces the shunt and "
        "current-sense amplifier of the brushless tiers ([63] Sec.7.3.3.1)"
    ),
    "REFERENCES.md Tags": "[62], [63]",
    "Status": "Verified (local PDF)",
}

AMPERAGE_NOTE = (
    " -- BRUSHED BUILDS (2026-09-17): the FET Part, Gate Driver Part, Shunt "
    "and Current-Sense Amp columns of this sheet are brushless-shaped and "
    "are OVERRIDDEN by the Motor sheet's bridge row for a Brushed (DC) "
    "build (Tier 1: DRV8874-Q1 [63] integrated bridge, no shunt). This "
    "sheet still governs the copper and connector class for the tier."
)


def write_sheet(wb, name: str, spec: dict, notes: str) -> None:
    """Create (or replace) one axis sheet in the shipped house style."""
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)

    ws["A1"] = spec["title"]
    ws["A1"].font = TITLE_FONT
    ws["A1"].alignment = Alignment(vertical="center")
    ws["A2"] = spec["subtitle"]
    ws["A2"].font = SUB_FONT

    for col, header in enumerate(spec["columns"], start=1):
        c = ws.cell(row=4, column=col, value=header)
        c.fill, c.font, c.alignment = HEADER_FILL, HEADER_FONT, HEADER_ALIGN

    for r, row in enumerate(spec["rows"], start=5):
        for col, value in enumerate(row, start=1):
            c = ws.cell(row=r, column=col, value=value)
            c.alignment = BODY_ALIGN

    note_row = 5 + len(spec["rows"]) + 1
    nc = ws.cell(row=note_row, column=1, value="Note: " + notes)
    nc.alignment = BODY_ALIGN
    nc.font = SUB_FONT

    for col, width in enumerate(spec["widths"], start=1):
        ws.column_dimensions[ws.cell(row=4, column=col).column_letter].width = width
    ws.freeze_panes = "A5"


def header_index(ws, header_row: int = 4) -> dict:
    """Map column header text -> 1-based column number."""
    return {
        str(ws.cell(row=header_row, column=c).value).strip(): c
        for c in range(1, ws.max_column + 1)
        if ws.cell(row=header_row, column=c).value is not None
    }


def find_row(ws, key_col: int, key: str, header_row: int = 4) -> int | None:
    """Return the row whose key column equals ``key`` (data rows only)."""
    for r in range(header_row + 1, ws.max_row + 1):
        if str(ws.cell(row=r, column=key_col).value or "").strip() == key:
            return r
    return None


def resolve_motor_row(wb) -> None:
    """Fill the Brushed (DC) row's open cells from REFERENCES.md [62]/[63]."""
    ws = wb["Motor"]
    cols = header_index(ws)
    r = find_row(ws, cols["Motor Type"], "Brushed (DC)")
    if r is None:
        raise SystemExit("Motor sheet: 'Brushed (DC)' row not found")
    for header, value in MOTOR_UPDATES.items():
        c = ws.cell(row=r, column=cols[header], value=value)
        c.alignment = BODY_ALIGN


def add_magnetic_sensor_row(wb) -> None:
    """Append the magnetic-absolute row unless it is already present."""
    ws = wb["Shaft Sensor"]
    cols = header_index(ws)
    if find_row(ws, cols["Sensor Type"], MAGNETIC_ROW[0]) is not None:
        return
    # Data rows run contiguously from row 5; append after the last one.
    r = 5
    while ws.cell(row=r, column=cols["Sensor Type"]).value not in (None, ""):
        r += 1
    for col, value in enumerate(MAGNETIC_ROW, start=1):
        c = ws.cell(row=r, column=col, value=value)
        c.alignment = BODY_ALIGN


def annotate_amperage(wb) -> None:
    """Record the brushed override on the notes cell and tag the 10 A row."""
    ws = wb["Amperage"]
    cols = header_index(ws)
    r10 = find_row(ws, cols["Tier (A)"], "10")
    if r10 is None:
        raise SystemExit("Amperage sheet: 10 A row not found")
    tags = str(ws.cell(row=r10, column=cols["REFERENCES.md Tags"]).value or "")
    for tag in ("[62]", "[63]"):
        if tag not in tags:
            tags = f"{tags}, {tag}" if tags else tag
    ws.cell(row=r10, column=cols["REFERENCES.md Tags"], value=tags)

    # The notes cell is the first non-empty column-A cell after the data.
    r = r10
    while ws.cell(row=r, column=1).value not in (None, ""):
        r += 1
    while ws.cell(row=r, column=1).value in (None, "") and r < ws.max_row + 2:
        r += 1
    note = str(ws.cell(row=r, column=1).value or "")
    if "BRUSHED BUILDS" not in note:
        ws.cell(row=r, column=1, value=note + AMPERAGE_NOTE).alignment = BODY_ALIGN


def update_legend(wb) -> None:
    """Add the Holding Brake sheet to the Legend's sheet list."""
    ws = wb["Legend"]
    existing = {
        str(ws.cell(row=r, column=1).value or "").strip()
        for r in range(1, ws.max_row + 1)
    }
    if "Holding Brake" in existing:
        return
    row = ws.max_row + 1
    ws.cell(row=row, column=1, value="Holding Brake").font = Font(size=10)
    ws.cell(
        row=row,
        column=2,
        value=(
            "None / low-side solenoid driver: actuation, fail-state (the "
            "safety property), MCU pins, driver part, connector, firmware "
            "sequencing."
        ),
    ).alignment = BODY_ALIGN
    ws.cell(
        row=row + 2,
        column=1,
        value=(
            f"Amended {datetime.now(timezone.utc).date().isoformat()}: added "
            "the Holding Brake axis; resolved the Motor sheet's Brushed (DC) "
            "row (DRV8874-Q1 [63]); added the magnetic-absolute shaft-sensor "
            "row (AEAT-8800-Q24 [64])."
        ),
    ).font = Font(size=10, italic=True)


def main() -> int:
    """Apply every change to the workbook."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    wb = openpyxl.load_workbook(WORKBOOK)
    before = list(wb.sheetnames)

    write_sheet(wb, "Holding Brake", BRAKE, BRAKE_NOTES)
    resolve_motor_row(wb)
    add_magnetic_sensor_row(wb)
    annotate_amperage(wb)
    update_legend(wb)

    # Holding Brake sits after Shaft Sensor: both describe what hangs off the
    # motor shaft, and a build walks them together.
    order = [
        "Legend",
        "Voltage",
        "Amperage",
        "Motor",
        "Shaft Sensor",
        "Holding Brake",
        "Protocol",
        "Control",
        "EMI Hardening",
        "Wire Egress",
        "Form Factor",
    ]
    wb._sheets = [wb[n] for n in order if n in wb.sheetnames] + [
        wb[n] for n in wb.sheetnames if n not in order
    ]

    print(f"sheets before: {before}")
    print(f"sheets after:  {wb.sheetnames}")
    if args.dry_run:
        print("dry run -- nothing written")
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = WORKBOOK.with_suffix(f".xlsx.{stamp}.bak")
    shutil.copy2(WORKBOOK, backup)
    wb.save(WORKBOOK)
    print(f"backed up  {backup.name}")
    print(f"wrote      {WORKBOOK}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
