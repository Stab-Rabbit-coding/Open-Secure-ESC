# Build: 6S / 50A / CAN-FD + RS-485 / Faraday

Governed by `AGENTS.md`. This document is the per-build instantiation of the
axis options in the repo-root `README.md`, produced by walking
`docs/decision-matrix.xlsx` for each requested axis. It is the descriptive
counterpart to `kicad/` (schematic/symbols) and `gerbers/` (fab output).

## Requested build parameters

| Axis | Selection |
| --- | --- |
| Voltage | 6S |
| Amperage | 50A |
| Protocol | CAN-FD **and** RS-485 (both present simultaneously, not alternatives) |
| Control | *Not specified in this build request* — left open, see "Open items" |
| EMI Hardening | Faraday, sized against a 500 W/m² broadband RF environment |

All parts below are drawn from `docs/decision-matrix.xlsx` (generated
2026-08-02) and carry that workbook's per-row verification status. A
`Candidate (unverified)` status means the part/spec was corroborated via
≥2 independent secondary sources but this session could not open its
primary datasheet directly (every domain tried returned HTTP 403 — see
`TODO.md` 1.10); it is not yet locked into a shippable BOM. Corresponding
KiCad symbols and their own pin-map verification status are in
`symbols/README.md`.

## Bill of materials

### MCU / trust anchor (common to all builds, README.md)

| Part | Qty | Citation | Status |
| --- | --- | --- | --- |
| TI MSPM0G3507SPMR (64-pin LQFP) | 1 | [1] | Verified (local datasheet). Package choice (64-LQFP, out of the 5 offered) is this build's own decision — needs CAN-FD + spare UART + dual SPI + 4 analog channels + SWD concurrently; see `symbols/specs/MSPM0G3507.json`. |
| Infineon SLB9672 TPM 2.0 | 1 | [2] | Verified (local datasheet) |

### Voltage tier — 6S

| Part | Qty | Citation | Status |
| --- | --- | --- | --- |
| Molicel INR-21700-P42A cell | 6 (series) | [14] | Candidate — datasheet VERIFIED locally 2026-08-02 (`docs/datasheets/INR21700P42A-V4-80092.pdf`), not yet locked into BOM — pack: 21.6 V nominal / 25.2 V max / 15.0 V min |
| Bulk input capacitor, V ≥ 25.2 V (≈2× margin recommended → ≥50 V rated) | TBD (generic `Device:C_Polarized`) | [14], [20], [21] | Generic part, not sourced individually — size against final layout |

### Amperage tier — 50A

| Part | Qty | Citation | Status |
| --- | --- | --- | --- |
| Infineon IRFB4110PBF power MOSFET | 6 (1 per switch position × 2 positions × 3 phases; "FET Qty/Phase Leg" = 1 at 50A) | [20] | Candidate — datasheet VERIFIED locally 2026-08-02 (`docs/datasheets/infineon-irfb4110-datasheet-en.pdf`), not yet locked into BOM |
| TI DRV8353S 3-phase gate driver (SPI variant) | 1 | [21] | Candidate — datasheet VERIFIED locally 2026-08-02 (`docs/datasheets/drv8353.pdf`), not yet locked into BOM — integrates 3 per-phase shunt-sense amplifiers itself |
| Vishay WSLP2512 shunt, 1 mΩ | 3 (one per phase; "Shunt Qty Needed" = 1 parallel device per location at 50A) | [23] | Candidate — datasheet VERIFIED locally 2026-08-02 (`docs/datasheets/wslp.pdf`), not yet locked into BOM |
| TI INA240 current-sense amp, 200 V/V gain | 3 (one per phase) — **open, see note below** | [22] | Candidate — datasheet VERIFIED locally 2026-08-02 (`docs/datasheets/ina240.pdf`), not yet locked into BOM |

**Open design question, not resolved here:** REFERENCES.md [21] states
DRV8353S already integrates 3 low-side per-phase shunt-sense amplifiers.
`docs/decision-matrix.xlsx`'s Amperage sheet nonetheless lists INA240 as a
separate BOM line for every tier. Whether this build needs external INA240
devices at all (e.g. for an MCU-independent overcurrent trip path separate
from DRV8353S's own CSA outputs) or can rely solely on DRV8353S's
integrated sensing is an open design-review question — flagged per
`AGENTS.md` §4 rather than silently picked. The MCU's `ADC_IU`/`ADC_IV`/
`ADC_IW` pins (`symbols/specs/MSPM0G3507.json`) work with either sourcing
choice.

### Protocol — CAN-FD + RS-485 (both, concurrently)

| Part | Qty | Citation | Status |
| --- | --- | --- | --- |
| Analog Devices ADM3055E **or** ADM3057E isolated CAN-FD transceiver | 1 | [6], [10] | Candidate (unverified) — **open**: ADM3055E (5000 V rms isolation) vs. ADM3057E (3750 V rms) not chosen here; pick per this build's actual isolation requirement (not specified by the request) |
| Analog Devices ADM2582E **or** ADM2587E isolated RS-485 transceiver | 1 | [4], [9] | Candidate (unverified) — **open**: ADM2582E (16 Mbps) vs. ADM2587E (500 kbps) not chosen here; pick per this build's actual RS-485 data-rate requirement (not specified by the request) |

Both protocol stacks fit on the MCU concurrently without pin conflicts: CAN
on the dedicated CAN peripheral (PA12/PA13, [1] Table 6-2), RS-485 on a
spare UART (UART3 on PB12/PB13) plus one GPIO for combined DE/RE control of
the half-duplex transceiver — see `symbols/specs/MSPM0G3507.json` for the
full pin assignment and its sourcing.

### EMI Hardening — Faraday tier

| Part | Qty | Citation | Status |
| --- | --- | --- | --- |
| Würth Elektronik WE-SHC 3671375 shielding **cover** | 1 (sized to the gate-drive / high-di/dt switching-node area) | [15], [19] | Candidate — datasheet VERIFIED locally 2026-08-02 (`docs/datasheets/3671375.pdf`), mechanical part, no schematic signal pins, see `symbols/WE_SHC_3671375.kicad_sym` |
| Würth Elektronik WE-SHC 3670375 shielding **frame** (required pair to the 3671375 cover above — both datasheets' own text: "Assembly with Frame: Frame (3670375), Cover (3671375)") | 1 | [15], [19], [30] | Candidate — datasheet VERIFIED locally 2026-08-02 (`docs/datasheets/3670375.pdf`), mechanical part, no schematic signal pins, see `symbols/WE_SHC_3670375.kicad_sym` |

**Why Faraday, not a lower tier, for this environment:** the stated
requirement is a 500 W/m² broadband RF environment. Converting that power
density to an equivalent far-field RMS field strength via the standard
plane-wave relation `E_rms = sqrt(S · η₀)` (S = power density, η₀ ≈ 376.73 Ω
free-space impedance — a physical constant, not a project-specific
citation):

```text
E_rms = sqrt(500 W/m² × 376.73 Ω) ≈ 434 V/m
```

That is well above the field strengths conventionally mitigated by
grounding/layout practice alone, and above typical MIL-STD-461G RS103
radiated-susceptibility test limits for most platform categories (commonly
≤200 V/m; only the most severe avionics zones reach 400-800 V/m) — see
[15]'s RE102/CE102 shielding-effectiveness rationale, cited in the
`docs/decision-matrix.xlsx` EMI Hardening sheet for exactly this tier. This
places the requirement in board-level shielding-can territory rather than
the Isolation or Grounding tiers, hence Faraday. This derivation is an
engineering calculation applying a standard electromagnetics identity, not
itself a standards citation — flagged as a judgment call per `AGENTS.md` §4.
The requirement is framed as *broadband*, i.e. a radiated-susceptibility
scenario; it does not by itself specify conducted-immunity limits (MIL-STD-
461G CS101/CS114/CS115/CS116) — those remain open per the Grounding tier's
existing layout guidance ([15], [17]) already in the base decision matrix.

## Open items (not resolved in this document)

- Control-loop topology (Open / Closed-Diff / Closed-PID) — not specified
  in the build request; see `docs/decision-matrix.xlsx` Control sheet.
- CAN-FD transceiver variant (ADM3055E vs. ADM3057E) and RS-485 transceiver
  variant (ADM2582E vs. ADM2587E) — isolation-voltage / data-rate tradeoff,
  not specified in the build request.
- DRV8353S vs. external INA240 current-sense sourcing (see BOM note above)
  — a design-review question, unaffected by DRV8353S's datasheet now
  being verified.
- **Every part in this build's BOM now has a locally verified primary
  datasheet** — the last two gaps (TI DRV8353S [21] and the WE-SHC
  3670375 frame [30]) were closed 2026-08-02. Two earlier lookalike PDFs
  (`docs/datasheets/wsl.pdf`, `docs/datasheets/3690103020.pdf`) had not
  resolved these gaps — see [24]/[25] in `REFERENCES.md` for why (wrong
  Vishay family, and a shield at the wrong physical scale) — the actual
  correct documents (`docs/datasheets/drv8353.pdf`, `.../3670375.pdf`)
  were added separately and confirmed to match.
- None of this means the BOM is "settled" per `AGENTS.md` §5 — every
  line is still "Candidate" in the sense that no part has been formally
  locked in, and several open design questions above (control-loop
  topology, transceiver variants, DRV8353S-vs-INA240 sourcing) remain
  genuinely unresolved. Datasheet verification and BOM lock-in are two
  different gates.
- Four alternative-manufacturer datasheets were also added 2026-08-02
  (Molicel P45B, Samsung SDI 40T, Analog Devices AD8410A, Infineon
  TLE9180D-31QK — see `REFERENCES.md` [26]-[29]) but none is adopted
  into this BOM; they're reference material for the open design
  questions above. **The Samsung 40T datasheet is marked "Confidential
  Proprietary" by Samsung on every page** — flagged in [27] for the
  repo owner to decide whether it belongs in a shared/public repo at
  all, independent of its technical accuracy.

## Folder contents

- `README.md` — this file.
- `kicad/` — KiCad project skeleton (schematic sheet + shared-library
  wiring); see `kicad/README.md` for exact status.
- `gerbers/` — fabrication output; empty until a PCB layout exists, see
  `gerbers/README.md`.

Symbols referenced by this build live in the repo-root `symbols/` library,
shared across all builds — see `symbols/README.md` for citation/
verification status per component and the workflow for adding more.
