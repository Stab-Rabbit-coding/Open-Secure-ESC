# Build: 6S / 10A / BRUSHED / CAN-FD + RS-485 / Isolation

Governed by `AGENTS.md`. This document is the per-build instantiation of the
axis options in the repo-root `README.md`, produced by walking
`docs/decision-matrix.xlsx` (exported to `docs/decision-matrix.json`,
2026-09-17) for each requested axis. It is the descriptive counterpart to
`kicad/` (schematic, ERC-clean) and `gerbers/` (empty until a layout exists).

**Host:** the Serenity-UAV nacelle-tilt actuator, two boards per aircraft
(port and starboard). The host's requirements are carried in
"Host constraints" below and trace to the Serenity-UAV plan
`docs/plans/2026-09-17-001-feat-tilt-controller-open-secure-esc-build-plan.md`
(cited there as `REF-ESC-001`). This build is the first brushed-DC instance,
the first 10 A-tier instance, and the first instance of the Holding Brake
axis.

**AI note:** authored by Claude Opus 5 (Anthropic, `claude-opus-5`) under the
direction of Steve Griffing, PE(CSE), CISSP-ISSEP, CPP, 2026-09-17. Not yet
human-reviewed.

## Requested build parameters

| Axis | Selection | Matrix row (`docs/decision-matrix.json`) |
| --- | --- | --- |
| Voltage | 6S — 22.2 V nominal, 25.2 V full charge, 15 V cutoff | `voltage.6s` |
| Amperage | 10 A tier — governs copper and connector class only; the power stage comes from the Motor sheet (brushed override note on the Amperage sheet) | `amperage.10` |
| Motor | Brushed (DC) — single integrated H-bridge, 0 shunts | `motor.brushed_dc` |
| Shaft sensor | Magnetic absolute (SPI/SSI), remote — AEAT-8800-Q24 off-board | `shaft_sensor.magnetic_absolute_spi_ssi` |
| Holding brake | Low-side solenoid driver, spring-applied — de-energised = engaged | `holding_brake.low_side_solenoid_driver_spring_applied` |
| Protocol | CAN-FD **and** RS-485, both present concurrently | `protocol.can_fd`, `protocol.rs_485` |
| Control | Closed-loop PID — inner loop on the remote encoder, outer loop on a host angle received over the bus | `control.closed_loop_pid` |
| EMI hardening | Isolation — isolated transceivers, no Faraday cabinet | `emi_hardening.isolation` |
| Wire egress | Opposite-end (default) — power/motor on one end, bus/encoder on the other, both on the host's permitted edges | `wire_egress.opposite_end_default` |
| Form factor | Flat (default) | `form_factor.flat_default` |

## Bill of materials

Every line carries its `REFERENCES.md` tag and the matrix row's Status.
`Verified (local PDF)` means the primary datasheet is in `docs/datasheets/`
and the cited figure was read from it. Passive values are engineering
defaults unless a datasheet fixes them (each schematic part carries a
`Note` property saying which).

### MCU / trust anchor (common to all builds)

| Ref | Part | Qty | Citation | Status |
| --- | --- | --- | --- | --- |
| U1 | TI MSPM0G3518-Q1, RHB (VQFN-32), `M0G3518QRHBRQ1` | 1 | [44] | Verified (local PDF) — tilt-build role symbol `symbols/specs/MSPM0G3518_Q1_RHB_TILT.json`, all 32 pins verified against [44] Fig. 6-6 / Table 6-2 |
| U2 | Infineon OPTIGA™ Trust M V3, SLS 32AIA010ML | 1 | [45] | Verified (local PDF); circuit per [45] p.12 Fig. 2 as on the 6S/50A build |
| C15 | 470 nF ±20 % VCORE tank | 1 | [44] | Verified (value required by [44], see the 50A build README) |
| C16, R25, C17 | VDD decoupling, NRST pull-up/filter | 3 | — | Generic |
| R26, R27, C18 | I²C pull-ups, OPTIGA decoupling | 3 | [45] | Generic values; topology per [45] Fig. 2 |
| J4 | SWD header 1×4, 1.27 mm | 1 | — | Generic |

### Power stage — Motor: Brushed (DC), Tier 1

| Ref | Part | Qty | Citation | Status |
| --- | --- | --- | --- | --- |
| U5 | TI DRV8874-Q1 integrated H-bridge, HTSSOP-16 PWP, 4.5–37 V, 6 A peak, PH/EN mode | 1 | [62], [63] | Verified (local PDF); footprint from TI's PWP0016J land pattern |
| C11 | CVM1 100 nF 50 V at VM | 1 | [63] Table 7-1 | Verified |
| C5, C6 | CVM2 bulk 22 µF 16 V ×2 on VMOT (sized per [63] §9.1 in the layout follow-up) | 2 | [63] | Value pending |
| C12 | CVCP 100 nF 16 V, VCP–VM | 1 | [63] Table 7-1 | Verified |
| C13 | CFLY 22 nF 50 V, CPH–CPL | 1 | [63] Table 7-1 | Verified |
| R13 | RnFAULT 10 kΩ pull-up to 3V3 | 1 | [63] Table 7-1 | Verified (IOD ≤ 5 mA) |
| R18 | RIMODE 62 kΩ to GND — quad-level 3: cycle-by-cycle chopping, latched-off OCP, nFAULT reports chopping | 1 | [63] Table 7-6 | Verified (KTD15) |
| — | PMODE strapped to GND — PH/EN control mode | — | [63] Table 7-2 | Verified |
| R14, R15 | VREF divider from 3V3 (sets ITRIP = VVREF / (AIPROPI · RIPROPI)) | 2 | [63] Eq. 3 | Values pending — ITRIP set just above the 2.9 A motor stall (stall backstop, not a working limit) |
| R16 | RIPROPI to GND (VIPROPI = IPROPI · RIPROPI, AIPROPI 450 µA/A) | 1 | [63] §7.3.3.1 | Value pending — ~2.5 V at ITRIP |
| R17, C14 | IPROPI RC filter into ADC A0_3 | 2 | — | Generic |
| J2 | Motor connector 1×2 | 1 | Serenity REF-ACT-001 | Pololu 20D 25:1 CB 6 V #3712 — 2.9 A stall, 0.74 A max-efficiency, 0.15 A free-run; sense declared per side in firmware |

The Amperage sheet's IRFB4110 / DRV8353S / WSLP2512 / INA240 columns do not
apply (brushed override, `docs/decision-matrix.xlsx` Amperage notes).

### Power rails — 6S in, buck to VMOT and 3V3

| Ref | Part | Qty | Citation | Status |
| --- | --- | --- | --- | --- |
| J1 | VBAT input 1×2 (the 3 A branch fuse is in the host harness) | 1 | Serenity `POWER_DISTRIBUTION.md` §3.3a | Connector class placeholder |
| C1, C2 | Input bulk 10 µF 50 V + 100 nF | 2 | [65] §8.2 | Generic |
| U6 | TI TPS54560B, 4.5–60 V in, 5 A, HSOIC-8 DDA — **VMOT 6.5 V** motor/solenoid rail | 1 | [65] | Verified (local PDF); footprint from TI's DDA0008B land pattern |
| U8 | TI TPS54560B — **3V3** logic rail (same part for BOM commonality; judgment call, `AGENTS.md` §4) | 1 | [65] | Verified (local PDF) |
| R1/R2, R7/R8 | EN/UVLO dividers | 4 | [65] §7.3.7 | Values pending (design procedure) |
| R3, R9 | RT/CLK 500 kHz | 2 | [65] §7.3.9 | Values pending |
| R4/R5, R10/R11 | FB dividers, VOUT = 0.8 V·(1 + RHI/RLO) | 4 | [65] §7.3.6 | Values pending |
| R6/C3, R12/C7 | Type-II compensation | 4 | [65] §8.2.2.7 | Values pending |
| C4, C8 | BOOT 100 nF | 2 | [65] §7.3.4 | Verified (value) |
| L1, L2 | Buck inductors | 2 | — | **UNVERIFIED — needs primary source (see TODO.md 18.3)**: part not selected; ≤ 4 mm height on the web-facing side is a hard host constraint |
| D1, D2 | Catch diodes, ≥ 60 V, ≥ 5 A avg | 2 | — | **UNVERIFIED — needs primary source (see TODO.md 18.3)** |
| C9, C10 | 3V3 output bulk + bypass | 2 | — | Generic |
| R21/R22 | VMOT sense divider → ADC A1_12 | 2 | — | Generic (KTD9 rail-droop rule) |
| R23/R24 | VBAT sense divider → ADC A1_7 | 2 | — | Generic |

### Holding brake — low-side solenoid driver

| Ref | Part | Qty | Citation | Status |
| --- | --- | --- | --- | --- |
| U7 | TI TPL7407L, TSSOP-16 — IN1+IN2 paralleled on `BRAKE_EN`, OUT1+OUT2 sink the coil, COM = VBAT | 1 | [66] | Verified (local PDF): 600 mA/ch, parallelable (§7.1), 1 MΩ input pull-down (§7.3), clamp diodes to COM, COM 8.5–40 V (§6.3) |
| R32 | External `BRAKE_EN` pull-down 100 kΩ | 1 | — | Generic (KTD9: MCU reset / Hi-Z = brake engaged) |
| R19/R20 | Brake-state readback divider on `SOL_N` → ADC A0_7 | 2 | — | Generic |
| J3 | Solenoid connector 1×2 (VMOT, SOL_N) | 1 | — | Generic |
| — | Pull solenoid itself | — | Serenity BRK-4 | **Host-side part, not in this BOM**; hold-in / dropout voltage to be recorded under BRK-4 |

### Shaft sensor — magnetic absolute, remote

| Ref | Part | Qty | Citation | Status |
| --- | --- | --- | --- | --- |
| J7 | Encoder header 1×6, 1.25 mm keyed: 3V3, GND, SCLK, DO, NSL, DI | 1 | [64] | Connector class placeholder |
| R28–R31 | 33 Ω series on the four SPI lines | 4 | `docs/design-speed-sensor-integration.md` | Generic |
| (off-board) | Broadcom AEAT-8800-Q24 on the sensor daughter in the host's brake guide, ~35 mm cable | — | [64] | Verified (local PDF); symbol `symbols/AEAT_8800_Q24.kicad_sym` carried for the daughter |

### Protocol — CAN-FD + RS-485, Isolation tier

| Ref | Part | Qty | Citation | Status |
| --- | --- | --- | --- | --- |
| U3 | ADI ADM3057E isolated CAN-FD transceiver (chosen over ADM3055E: identical timing, lower creepage) | 1 | [6], [10] | Candidate (unverified) — same standing as on the 6S/50A build; pin map VERIFIED |
| U4 | ADI ADM2587E isolated RS-485 transceiver, half-duplex (Y/A, Z/B tied) | 1 | [4], [9] | Candidate (unverified); pin map VERIFIED |
| FB1–FB4 | Murata BLM15HD182SN1D ferrites on the isolated supplies and grounds | 4 | [53] | As the 6S/50A build ([10] p.25) |
| C19–C26 | 10 µF + 100 nF reservoirs on VISOIN/VISOOUT, both transceivers | 8 | [9], [10] | As the 6S/50A build |
| J5, J6 | CAN (H/L) and RS-485 (A/B) connectors 1×2 | 2 | — | Generic |

Isolation creepage: 7.5 mm ([9] Table 6) is the binding figure; the board
width check is in `kicad/README.md`.

### Host I/O

| Ref | Part | Qty | Citation | Status |
| --- | --- | --- | --- | --- |
| J8 | Differential-tilt trip input 1×2 → PA7 | 1 | Serenity `TILT_DRIVE_CONTROL_SPEC.md` §5.4 | Executor and independence to be defined (TILT-CTL-02) |

## Host constraints — Serenity-UAV nacelle tilt (Rev T5e)

Source: Serenity-UAV `airframe/openscad/fuselage/cargo/tilt_actuator_bracket.scad`
(`BOARD_*`, `RAIL_*`), `tools/cargo_layout_fit.py` (`BOARD_L`, `BOARD_W`,
`BOARD_T`), `docs/TILT_ACTUATOR_SELECTION.md` §4–§6,
`docs/TILT_DRIVE_CONTROL_SPEC.md` §1, §5.2–§5.5, `docs/POWER_DISTRIBUTION.md`
§3.3a. Units imperial-primary per the host's convention.

| Constraint | Value | Why |
| --- | --- | --- |
| Board outline | ≤ 1.69 × 1.44 in (42.9 × 36.5 mm), no mounting holes needed | Card-edge rails on the bracket web's outboard face; board slides in along +Y, retained by a cable tie |
| Component height, web-facing side | ≤ 0.16 in (4.0 mm) (`RAIL_H`) | Standoff between the component side and the bracket web; the envelope has 0 mm to spare outboard |
| Back face | Bare (no components) | Faces the hull skin |
| Connector edges | Aft (+Y) or inboard (−X) only | The outboard edge faces the 2 mm rail lip |
| Feed | VBAT 22.2 V nominal / 25.2 V full, own fused branch `F_TILT_P` / `F_TILT_S`, 3 A mini blade in the harness | Per-path fusing so no single failure cascades; the buck's current limit and soft-start, not the fuse, bound the rail |
| Motor | Pololu 20D 25:1 CB 6 V (#3712): 2.9 A stall, 0.74 A max-eff, 0.15 A free-run | REF-ACT-001; six-start worm, 23.8:1 overall |
| Solenoid | ~0.5 A at 6 V continuous or PWM-held, pull type, Ø12 × 24 mm class | BRK-4 (part open on the host side) |
| Sensor | AEAT-8800-Q24 in the brake guide reading a Ø6 diametric magnet in the worm's brake collar; ~1.38 in (35 mm) cable | `TILT_ACTUATOR_SELECTION.md` §4; 9.6 turns over the sweep, firmware accumulates turns |
| Outer loop | AK7455 nacelle angle, signed by the nacelle gateway, received over CAN-FD | `CAN-PERIPH-GW-1.md` Deployment §1; the angle frame is a trust boundary the controller verifies |
| Sense | Actuator-positive = nacelle-positive on **port**; **starboard reversed** (same right-hand worm, mirrored bracket) — declared per side in firmware, never discovered | `tilt_actuator_bracket.scad` header (TC-6) |
| Thermal | ≈ 2 W in the DRV8874-Q1 at stall (2.9 A² × 0.24 Ω) with the component side facing the web at 4 mm | [63] §8.2.1.2 thermal design; thermal vias under the PWP pad at layout |

### Fail-state table (owner: Serenity plan, System-Wide Impact)

| Event | Motor (DRV8874-Q1) | Brake | Bus sees |
| --- | --- | --- | --- |
| Branch fuse opens | VM → 0, UVLO, all FETs off ([63] §7.3.4.1) | Engages (coil unpowered) | Node silent |
| Buck U6 fails open | as above | Engages; MCU alive on 3V3 | nFAULT + brake state, node alive |
| VMOT droop (stall / current limit) | drives down to VUVLO 4.35 V typ ([63] §6.5) | may drop out above UVLO → firmware: on `ADC_VM` < V_hold, EN = 0 (slow decay) before the coil drops out | VM alarm |
| OCP / TSD / CPUV | all FETs off, latched (level 3, [63] Table 7-6/7-7) | released until firmware engages it on nFAULT | fault frame |
| ITRIP chopping (jam) | slow-decay chopping ([63] §7.3.3.2.1) | released | nFAULT + IPROPI |
| MCU reset / brown-out | all FETs off via input pull-downs ([63] §7.3.2) | engages: R32 + TPL7407L internal pull-down | node off the bus |
| Bus lost | inner loop holds on the encoder | engage after timeout, then nSLEEP | — |
| Differential-tilt trip | undefined (TILT-CTL-02) | if "engage both": a bus command with latency + authorization | trip frame |

**Fail-safe resolution for this build** (`docs/design-brushed-esc-variant.md`
"Safety & failure modes", `TODO.md` 12.3.a): fail-safe = brake engaged,
motor coasting. Fail-operational applies only to a MAC failure on a position
frame (hold the last valid command; never engage mid-manoeuvre).

## Firmware requirements (recorded, not implemented)

Owner of each rule is the Serenity-UAV document cited; this list is the
build's contract, not a restatement.

1. Cascade: inner velocity/position loop on the AEAT-8800 worm-shaft angle
   (turns accumulated in firmware, homed from the outer sensor); outer loop
   on the AK7455 nacelle angle received over CAN-FD — `TILT_DRIVE_CONTROL_SPEC.md` §1–§2.
2. Brake sequencing: release → move → settle → engage, where "settled" comes
   from the encoder (worm stationary) and "unloaded" from the AK7455 over
   the bus, never from IPROPI ([63] §7.3.3.1 reports one low-side FET in
   slow decay). Sequence on release: EN = 0 (damp) → encoder stationary →
   `BRAKE_EN` low → `nSLEEP` low (tSLEEP, [63] §6.5) — spec §5.2 (BRK-1..3).
3. `MOT_nFAULT` (PA26, TIMA_FAL0) is a brake-engage input; the latency budget
   plus the pin's mechanical engage time is set here — spec §5.3.
4. Rail droop: on `ADC_VM` below the solenoid hold-in voltage (BRK-4), EN = 0
   before the coil drops out.
5. Jam detection: IPROPI current at or near ITRIP with the AK7455 static → stop
   commanding into it (latched OCP mode ensures the bridge does not hammer
   the train at 500 Hz) — spec §5.3; KTD15.
6. Differential-tilt trip input on `TRIP_IN` (PA7) — spec §5.4; executor
   and independence to be defined (TILT-CTL-02).
7. Per-side sense declaration (starboard reversed) — TC-6.
8. Bus security: brake release is a distinct authenticated command class with
   its own freshness counter and an arm/confirm pair, in the per-frame CMAC
   hot path (never an OPTIGA private-key operation — `docs/secure-element-architecture.md`,
   5 s protected-op budget). Asymmetric fail policy: MAC failure on a
   position frame → fail-operational on the last valid command; MAC failure
   on a release → stay engaged. Symmetric path is the MSPM0 AES-CMAC engine,
   pending `TODO.md` 13.1.e — spec §5.5 (TILT-CTL-09).
9. Bus loss: engage after a timeout, then sleep the bridge — spec §5.1/§5.2.

## Open items (not resolved in this document)

| # | Item | Tracked |
| --- | --- | --- |
| 1 | Buck inductors L1/L2 and catch diodes D1/D2 — select against ≤ 4 mm height, fetch primary datasheets | `TODO.md` 18.3 |
| 2 | Buck design values (UVLO, RT, FB, compensation) per [65] §8.2 | `TODO.md` 18.3 |
| 3 | ITRIP / RIPROPI / VREF values against the 20D's 2.9 A stall | `TODO.md` 18.3 |
| 4 | Country-of-origin (fab / assembly) for U5–U8 and the AEAT-8800 | `TODO.md` 18.4 |
| 5 | AEAT-8800 land pattern (Broadcom Fig. 17) vs the KiCad stock QFN-24 | `TODO.md` 18.5 |
| 6 | Connector part numbers (J1–J8) against the Serenity harness spec | `TODO.md` 18.3 |
| 7 | PCB layout, routing, DRC, thermal vias, Gerbers | `TODO.md` 18.6 |
| 8 | Firmware (items 1–9 above) | `TODO.md` 8.7 |
| 9 | ADM3057E / ADM2587E part-selection status is still Candidate, as on the 50A build | `TODO.md` 6.7–6.9 |

## Folder contents

| Path | What it is |
| --- | --- |
| `README.md` | This document |
| `kicad/README.md` | Schematic status, file list, library bindings, envelope check |
| `kicad/open_secure_esc_6s_10a_brushed_can485_iso.kicad_sch` | Schematic, generated — ERC 0 errors / 0 warnings (KiCad 9.0.2) |
| `kicad/open_secure_esc_6s_10a_brushed_can485_iso.kicad_pro` | Project: net classes (Power / Motor / Isolated / Sense) |
| `kicad/open_secure_esc_6s_10a_brushed_can485_iso.kicad_dru` | Custom rules: conductor spacing, isolation-barrier via check |
| `kicad/sym-lib-table`, `kicad/fp-lib-table` | Bindings to `symbols/` with citation notes |
| `kicad/tools/gen_schematic.py` | The schematic's single source; `--check` proves the committed sheet matches |
| `gerbers/README.md` | Empty by design — see the file |
