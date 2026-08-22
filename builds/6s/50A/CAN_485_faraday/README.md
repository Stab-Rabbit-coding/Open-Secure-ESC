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

> **AS-BUILT CORRECTION (2026-08-15).** This section describes the NXP
> S32K144. **The KiCad schematic in `kicad/` does not contain an S32K144.**
> U1 is a **TI MSPM0G3518-Q1, package PM (LQFP-64), orderable
> `M0G3518QPMRQ1`** — REFERENCES.md [44] — swapped in per TODO.md §13.1 and
> recorded in `kicad/sym-lib-table` ("Project MCU as of 2026-08-10;
> supersedes S32K144"). Unlike the S32K144's, its pin numbers are **VERIFIED**
> against [44] (`symbols/specs/MSPM0G3518_Q1_PM.json`), so the
> "UNVERIFIED PLACEHOLDER PIN MAP" caveat below no longer applies to the part
> actually in the design.
>
> The text below is left in place rather than rewritten, because it is
> historical BOM record for a part no longer on the schematic, not because
> the swap's documentation is still lagging. **Update 2026-08-22: TODO.md
> §13.1.e is closed** — `docs/secure-element-architecture.md` has been
> rewritten for the MSPM0's `AESADV`/Keystore (C-01 RESOLVED; the CSEc/HSRUN
> exclusion C-05 marked SUPERSEDED, with the MSPM0's own clock/crypto
> interaction explicitly flagged `UNVERIFIED` rather than assumed absent).
> **§13.1.f raised a new finding (C-08) rather than closing cleanly:** the
> keystore slot count (4 vs. CSEc's 17) was not the real problem — the real
> gap is that CSEc's runtime-loadable volatile `RAM_KEY` has no confirmed
> MSPM0 equivalent, so how a freshly ECDHE-negotiated session key reaches the
> MCU's AES engine is undesigned. See `docs/secure-element-architecture.md`
> §4 C-08 and `TODO.md` 13.1.f/13.1.i. Every "CSEc" statement below therefore
> still describes a part that is no longer in this build; read it as history,
> not as this build's current security architecture. The OPTIGA Trust M's
> justification is unaffected — the MSPM0's AES engine is still symmetric, so
> the asymmetric layer is still required.
>
> Two other things below are also now stale: `C_VCORE` is **verified at
> 470 nF, +/-20%** ([44] Recommended Operating Conditions, and "A 0.47 µF tank
> capacitor is required for the VCORE pin"), which closes TODO.md §13.1.b; and
> the LPSPI/LPI2C channel names are S32K144 peripheral names.

| Part | Qty | Citation | Status |
| --- | --- | --- | --- |
| NXP S32K144 (64-pin LQFP) | 1 | [31] | Feature-level facts verified (local datasheet); physical pin-number map is an UNVERIFIED PLACEHOLDER pending the S32K1xx Reference Manual (see `symbols/specs/S32K144.json`). Package choice (64-LQFP, one of four this device ships in) is this build's own decision — needs 1 FlexCAN-FD instance, 1 spare LPUART, 1 LPSPI (gate driver only — see below), 4 analog channels, SWD concurrently, comfortably within every S32K14x family member's minimum peripheral count. |

**2026-08-03: TPM dropped.** This build no longer includes a discrete TPM.
The Infineon SLB9672 TPM 2.0 (previously listed here, [2]) has been removed
from the design; message authentication is instead provided by the S32K144's
own on-chip CSEc (Cryptographic Services Engine) security module [31], which
implements the SHE (Secure Hardware Extension) Functional Specification's
cryptographic function set. Because CSEc has no dedicated external pins (it
is driven entirely over an internal firmware command interface), dropping
the SLB9672 also frees the LPSPI channel this build previously reserved for
TPM SPI traffic — see `symbols/specs/S32K144.json`. The algorithm-level
detail of CSEc's message-authentication function (e.g. AES-128-CMAC) is not
yet independently verified against a primary NXP/HIS source in this repo —
flagged `UNVERIFIED — needs primary source (see TODO.md)` per `AGENTS.md`
§1.3, tracked in `TODO.md` §4.

**2026-08-10: secure element added (`U2`).** The TPM stays dropped, but CSEc
alone was never a complete root of trust — it is symmetric-only, so it cannot
do public-key device authentication, key agreement with an unknown peer, or
certificate validation. An **Infineon OPTIGA™ Trust M V3** secure element
(sales code SLS 32AIA010ML, ETR −40 °C to +105 °C, PG-USON-10-2,-4,
3 mm × 3 mm / 0.118 in × 0.118 in) [45] now occupies the `U2` designator the
SLB9672 vacated and supplies exactly that asymmetric layer over LPI2C.

| Part | Qty | Citation | Status |
| --- | --- | --- | --- |
| Infineon OPTIGA™ Trust M V3 (PG-USON-10-2,-4) | 1 | [45] | Pin map VERIFIED from [45] p.17 Table 6. Footprint hand-authored for this repo; its LAND PATTERN is an IPC-7351-style derivation, **not** an Infineon recommendation — [45] publishes none. |
| 10 kΩ 0805 I²C pull-up | 2 | [45] p.12 Fig. 2 | Datasheet reference value; [45] notes the correct value depends on bus capacitance and I²C frequency — confirm before fab. |
| 100 nF 0805 VCC decoupling | 1 | [45] p.12 Fig. 2 | — |

It is a **secure element, not a TPM** — a key vault with a crypto engine,
not a platform-integrity module with PCRs and attestation. The division of
labour is deliberate and load-bearing: the Trust M establishes identity and
agrees a session key at boot; CSEc consumes that key for every frame
thereafter. The hot path **must not** call the secure element — [45] p.28
§7.2 permits only one protected operation per 5 s `t_max` period, and any use
of the fab-provisioned identity key is a protected operation.

Full rationale, the security-monitor budget, the cryptographic assessment
(including anti-replay, MAC truncation on CAN-FD, and the CSEc/HSRUN clock
exclusion), and the OT-style review are in
[`../../../../docs/secure-element-architecture.md`](../../../../docs/secure-element-architecture.md).
Several items there are **OPEN and safety-relevant** — in particular, the
behaviour on MAC verification failure is undefined and must be decided before
this build flies.

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
`ADC_IW` pins (`symbols/specs/S32K144.json`) work with either sourcing
choice.

### Protocol — CAN-FD + RS-485 (both, concurrently)

| Part | Qty | Citation | Status |
| --- | --- | --- | --- |
| Analog Devices ADM3055E **or** ADM3057E isolated CAN-FD transceiver | 1 | [6], [10] | Candidate (unverified) — **open**: ADM3055E (5000 V rms isolation) vs. ADM3057E (3750 V rms) not chosen here; pick per this build's actual isolation requirement (not specified by the request) |
| Analog Devices ADM2582E **or** ADM2587E isolated RS-485 transceiver | 1 | [4], [9] | Candidate (unverified) — **open**: ADM2582E (16 Mbps) vs. ADM2587E (500 kbps) not chosen here; pick per this build's actual RS-485 data-rate requirement (not specified by the request) |

Both protocol stacks fit on the MCU concurrently without pin conflicts: CAN
on one of the S32K144's FlexCAN instances (1 of which supports CAN-FD),
RS-485 on a spare LPUART plus one GPIO for combined DE/RE control of the
half-duplex transceiver — see `symbols/specs/S32K144.json` for the full
signal-role assignment. Note: unlike the now-superseded MSPM0G3507 spec,
which pinned each signal to a specific verified physical pin number, the
S32K144 spec's pin numbers are an UNVERIFIED PLACEHOLDER (the local S32K1xx
data sheet [31] does not contain the physical pinout table — see that
entry's "Not verified" note) — the module-level claim above (CAN-FD + spare
LPUART + GPIO fit concurrently) rests on the datasheet's verified
family-wide peripheral *counts*, not on a specific verified pin location.

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

### Parts added by the 2026-08-15 layout pass

| Part | Ref | Qty | Citation | Status |
| --- | --- | --- | --- | --- |
| 10 kΩ 0805 pull-up on the gate driver's SDO line | R14 | 1 | [21] | **Required by the datasheet, was missing.** [21]'s "Pin Functions — 40-Pin DRV8353 Devices" gives SDO (pin 27) as type **OD** and states "This pin requires an external pullup resistor." Without it no SPI register read from the gate driver can work. The 10 kΩ *value* is an engineering default matched to R11 (nFAULT, the other open-drain pin); [21] specifies no value. |
| Pack input terminal, 6 mm² solder-wire pads | J5 | 1 | — | **Engineering default, not a selected part.** VM previously had no connector of any kind, so the board could not be energised (BT1–BT6 are an off-board assembly). Sized as the largest pad in KiCad's stock library, not against a current rating. See TODO.md §12.4.k/§12.4.l. |
| Motor phase terminal, 6 mm² solder-wire pads | J4 | 1 | — | **Footprint changed 2026-08-15**, was a 2.54 mm pin header — not a 50 A part. Same engineering-default caveat as J5. |

Conductor sizing for all of the above is governed by IPC-2152 [46], whose body
is paywalled and has **not** been read; only its Table of Contents is verified.
No width, plane cross-section or pad in this build is an IPC-2152 result.

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
- `kicad/` — populated KiCad project: schematic (all BOM parts below placed
  and wired), `.kicad_pro`, and a PCB with footprints placed and a board
  outline (not yet routed). Title block company: **Griffing Technology
  LLC**. See `kicad/README.md` for exact status, including what's still
  open (no footprint for the DRV8353S gate driver, no netlist/routing yet,
  and the open design questions noted in this document are deliberately
  left open there too, not silently resolved).
- `gerbers/` — fabrication output; still empty, the PCB isn't routed yet,
  see `gerbers/README.md`.

Symbols referenced by this build live in the repo-root `symbols/` library,
shared across all builds — see `symbols/README.md` for citation/
verification status per component and the workflow for adding more.
