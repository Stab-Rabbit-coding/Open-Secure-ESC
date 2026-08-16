---
date: 2026-08-16
problem_type: architecture_pattern
category: architecture-patterns
module: builds
component: development_workflow
severity: high
applies_when:
  - "Starting a new builds/<voltage>/<amperage>/<variant>/ folder"
  - "Changing the power-stage topology (brushed vs brushless)"
  - "Adding a shaft-sensor interface to an existing build"
  - "Authoring a KiCad footprint from a manufacturer drawing"
  - "Taking any build from schematic to routed board"
tags:
  - esc
  - kicad
  - build-workflow
  - footprints
  - datasheet-verification
  - power-stage
  - erc-drc
related_components:
  - symbols
  - docs/decision-matrix.xlsx
  - REFERENCES.md
---

# Instantiating a new ESC build from amperage, voltage, shaft sensor and motor type

## Context

`builds/6s/50A/CAN_485_faraday/` was taken from a schematic with no reference
designators and a PCB whose every pad sat on net 0, through to an ERC-clean
schematic (0 errors), a netted 4-layer board with poured planes and an
isolation keepout, and a routed result (588 tracks, 88 vias, 114 → 23
unrouted). It was then respun for a 30 × 70 mm envelope.

Doing it once surfaced a set of traps that are not obvious from the KiCad
files and that will recur on every subsequent build. This document is the
repeatable procedure plus those traps.

**Two of the four inputs this workflow takes were missing axes.**
`docs/decision-matrix.xlsx` shipped with Voltage, Amperage, Protocol, Control
and EMI Hardening only. **Motor** and **Shaft Sensor** sheets were added
2026-08-16 (`docs/tools/add_motor_and_shaft_sensor_sheets.py`), and the whole
workbook now exports to `docs/decision-matrix.json` for scripting
(`docs/tools/decision_matrix_to_json.py`). Motor type is not a parameter
tweak — it changes the power-stage topology, the gate-driver part number, the
switch-position count and the shunt count.

**Status of the source build:** the 150 × 140 mm version reached routed +
DRC-clean-apart-from-cosmetics. The 30 × 70 mm respin is **in flight** — FET
and shield parts are selected, verified and footprinted; the schematic swap,
double-sided layout and re-route are not done. Nothing here should be read as
"the build shipped".

## Guidance

### Step 0 — Resolve the four axes into topology before touching KiCad

| Input | What it determines |
| --- | --- |
| **Motor type** | Bridge topology. Brushless → 3 half-bridges, 6 switch positions, a 3-phase gate driver, 3 phase shunts. Brushed → H-bridge, 4 switch positions, a different driver part, 1–2 shunts. **Different gate driver part number**, not a configuration bit. |
| **Amperage** | FET R_DS(on) and package, shunt value and power rating, conductor strategy, connector class, cooling requirement. |
| **Voltage (nS)** | FET V_DSS margin, bulk capacitor rating, isolation requirements. Pack max = nS × 4.2 V. |
| **Shaft sensor** | MCU pin budget, connector count, and extra BOM: Hall → 3 digital in + sensor supply; quadrature encoder → 2–3 inputs (+ index); resolver → excitation drive + a resolver-to-digital converter, a whole extra IC; sensorless → 3 phase-voltage dividers into ADC and no connector at all. |

Resolve these together. A sensorless brushed build and a resolver-fed
brushless build share almost no power-stage BOM.

### Step 1 — BOM, with verification discipline

Walk the decision matrix per axis, then apply `AGENTS.md` §1.3 to every line:
a part is not in the BOM until its **primary datasheet is held locally and
read**. Secondary corroboration is not verification. Record the verification
state in `symbols/specs/<PART>.json` `verification`, not in prose.

Screen **country of origin on every IC**, including parts you are copying
from a reference design (see Trap 4).

### Step 2 — Symbols from specs, never hand-edited

`symbols/specs/<PART>.json` is the source of truth; run
`symbols/tools/gen_kicad_symbol.py` to produce the `.kicad_sym`. The JSON
carries the citation and verification record, which is what makes the symbol
auditable.

### Step 3 — Footprints: find the published land before deriving one

See Trap 2 — this is where the most time was lost. Order of preference:

1. The manufacturer's published land pattern, wherever it lives.
2. A KiCad system footprint whose geometry you have **checked against** the
   manufacturer drawing.
3. An IPC-7351-style derivation, explicitly flagged per `AGENTS.md` §4.

Every generator's docstring must name the drawing each dimension came from
and state which numbers are derivations.

### Step 4 — Schematic to zero ERC errors

Annotate first (unannotated refs collapse the netlist). Then drive ERC errors
to zero. Warnings may remain if each is understood and documented; errors may
not. Read pin *types*, not just names — see Trap 6.

### Step 5 — PCB built from the exported netlist, not by hand

Generate the board from `kicad-cli sch export netlist` so the board cannot
drift from the sheet. Assign every pad its real net; report any pad with no
netlist node rather than leaving it on net 0.

Carry high-current nets as **planes and pours**, not tracks (Trap 5). Put a
copper keepout under any isolation barrier — a ground plane running beneath
an isolator defeats it.

### Step 6 — Route, then DRC

Inject net classes into the Specctra DSN (Trap 5). Re-pour zones after the
SES import.

## Why This Matters

Each trap below was found by a check, not by inspection, and each would have
produced a board that fails in a different way — a dead short, an
unbuildable land, a silently merged net, an export-controlled part, or a
conductor that melts.

### Trap 1 — Land-pattern datum errors are silent until DRC

TI's RTA0040B drawing dimensions `2X (5.8)` as the **centre-to-centre**
distance between opposite pad rows. Read as the outer copper extent, it puts
every pad 0.3 mm too far inboard and overlaps the corner pads — a dead short
between pin 1 (CPL) and pin 40 (VGLS). DRC caught it; reading the drawing had
not.

**Rule:** after reading a land pattern, verify it against an *independent*
dimension on the same drawing. For RTA0040B, calibrating on the 4.5 mm row
span (fixed by "36X 0.5") made three separate dimensions — pad centre axis
2.901, pad size 0.621 × 0.236, thermal pad 4.170 × 4.165 — all land on their
printed callouts simultaneously. Agreement across independent dimensions is
what distinguishes a measured value from a plausible one.

The same check validated the Würth shield: ring centreline from the land
pattern (10.35, 7.55) equals wall centreline from the body dimensions to the
last digit.

### Trap 2 — Where the land pattern lives is vendor-specific

| Vendor | Where the land pattern is |
| --- | --- |
| **TI** | In the part datasheet — "EXAMPLE BOARD LAYOUT" and "EXAMPLE STENCIL DESIGN" sheets. |
| **Toshiba** | **NOT in the part datasheet.** In the *MOSFET Product Catalog*, which tabulates package dimensions and land patterns side by side for the whole surface-mount family. |
| **Würth** | In the part datasheet, "Recommended Land Pattern". |
| **Infineon** | Not published for some packages (e.g. OPTIGA PG-USON-10) — derivation is unavoidable and must be flagged. |

Searching all 10 pages of the Toshiba TPHR8504PL datasheet for "land",
"mounting" and "recommend" returned nothing, which looked like "no published
land" and triggered an IPC derivation. The catalog had it. The derivation was
**46 % short on drain-land area and 86 % short on lead-pad area**.

**Rule:** a part datasheet with no land pattern means *check the vendor's
package/catalog document*, not *derive one*.

### Trap 3 — Bulk geometry transforms can short the sheet

`genlib.py` separates parallel routes by **0.01–0.02 mm lane offsets**, not
by whole grid steps. Snapping every coordinate to KiCad's 1.27 mm connection
grid — to clear 347 `endpoint_off_grid` warnings — collapsed those lanes onto
single grid lines and merged the nets.

Measured damage, 73 nets → 63: VM shorted to GND; all six PWM lines merged
into one net; CPH shorted to CPL across the charge-pump capacitor; NRST and
GD_SPI_MISO merged into 3V3.

**Rule:** export the netlist before and after any bulk geometry
transformation and require them identical. That diff is what caught this; the
transform itself looked correct and preserved every symbol-pin relationship.
`builds/6s/50A/CAN_485_faraday/kicad/tools/snap_to_grid.py` now
refuses to run without `--force`.

### Trap 4 — Screen country of origin in reference designs too

The Vimdrones S50 was mined as a technique reference for fitting 50 A into
40 × 17 mm. Its gate driver is a **Fortior FD62880 — Fortior Technology is
Shenzhen, PRC**. Copying the reference design's driver would have imported a
restricted-origin part while every other IC in this project is US/EU/Japan.

**Rule:** screen the manufacturer of every IC, and screen reference designs
before mining them for parts as opposed to technique.

### Trap 5 — The auto-router will route 50 A at 0.2 mm

Net classes live in the `.kicad_pro` **project** file. `pcbnew.LoadBoard()`
used standalone does not read it, so `ExportSpecctraDSN` puts every net in one
`kicad_default` class at the default width. The first routed board came back
with the pack net and all three motor phases on 0.2 mm track.

**Rule:** carry the current in copper pours and planes, and inject the net
classes into the DSN before routing. Verify afterwards by querying the actual
track widths per net — not by trusting the project settings.

### Trap 6 — Read pin *types*, not just pin names

DRV8353S `SDO` is type **OD**, and the datasheet states "This pin requires an
external pullup resistor." The schematic had none, so every SPI register read
from the gate driver would have failed silently. `nFAULT`, the other
open-drain pin, already had its pull-up — so the omission looked like a
complete design.

**Rule:** when transcribing a pin table, carry the *type* column into the
spec JSON, and treat OD/OC as a required-external-component flag.

### Trap 7 — Rated current is a thermal claim, not an electrical one

Vimdrones' instrumented test measured **103 °C at 50.18 A** with EDF airflow
at 29 °C ambient, and their own spec says "50 A (cooling required above
30 A)". A 50 A rating without a stated cooling condition is not a rating.

Related: a 1 mΩ shunt at 50 A dissipates I²R = **2.5 W into a 3.0 W part**
(83 % of rating, before derating, in a board already running hot). The
reference design used 0.5 mΩ, halving it.

## When to Apply

- Every new `builds/<voltage>/<amperage>/<variant>/` instantiation.
- Any time a footprint is authored from a manufacturer drawing.
- Before running a bulk coordinate transform on a generated schematic.
- Before auto-routing any board carrying more than a few amps.

## Examples

### Walking the axes from the JSON export

The workbook is the human-editable source; `docs/decision-matrix.json` is what
a build script reads. Rows are keyed by a slug of their first column, so
inserting a row never breaks a caller:

```python
db = json.load(open("docs/decision-matrix.json"))
v  = db["axes"]["voltage"]["rows_by_key"]["6s"]        # 21.6 / 25.2 / 15.0 V
m  = db["axes"]["motor"]["rows_by_key"]["brushless_bldc_pmsm"]
s  = db["axes"]["shaft_sensor"]["rows_by_key"]["none_sensorless"]
```

**Check `Status` before consuming a row.** `unresolved_cells(db)` returns every
cell that is either explicitly TBD or sits on an `Open / unresolved` row —
currently the brushed-DC gate driver, all three sensored shaft-sensor options,
and SBus/DBus. A build script must refuse those rather than emit a BOM line,
per `AGENTS.md` §1.3.

### The verification gate at each phase

```text
Symbol      spec JSON `verification` names the datasheet section read
Footprint   generator docstring names the drawing; a second dimension
            on that drawing independently confirms the reading
Schematic   kicad-cli sch erc → 0 errors; every warning explained
Netlist     exported netlist identical across any geometry transform
PCB         every pad has a net; no pad left on net 0
Route       per-net track widths queried, not assumed
Fab         conductor sizing traced to a standard, or explicitly open
```

### What "engineering default" means in practice

Values that are judgement calls, not sourced, must say so at the point of
use — the 10 kΩ pull-up values, the connector selection, the gate-driver
thermal-pad net, the shield hole plating, and every conductor width in the
source build are all recorded this way per `AGENTS.md` §4. The discipline is
what makes the genuinely-verified numbers trustworthy.

## Related

- `AGENTS.md` §1.3 (no fabrication), §4 (design-decision rationale)
- `REFERENCES.md` — every citation tag used above
- `symbols/README.md` — footprint provenance table and the Toshiba catalog note
- `builds/6s/50A/CAN_485_faraday/kicad/README.md` — the source build's state
- `TODO.md` §12.4 — the open items this build carries into fab
