# TODO.md — Work Breakdown Structure

Governed by `AGENTS.md`. Status: `[ ]` open, `[~]` in progress, `[x]` done,
`[!]` blocked. `Cn` = REFERENCES.md tag needed/used. Keep entries terse;
detail belongs in design docs, not here.

## 1. Governance & Docs

- [x] 1.1 AGENTS.md — contributor/agent rules
- [x] 1.2 REFERENCES.md — IEEE bibliography scaffold
- [x] 1.3 TODO.md — this WBS
- [x] 1.4 Verify [1] MSPM0G3507 datasheet doc ID/rev/page (local copy
      verified 2026-08-02; live ti.com fetch blocked: 403). **[1] superseded
      2026-08-03 — project MCU changed, see 13.**
- [x] 1.5 Verify [2] SLB9672 datasheet page refs for compliance claims — DROPPED
      (external TPM removed; see 4.1).
- [~] 1.11 Verify [31] NXP S32K1xx Data Sheet claims used historically (local
      copy VERIFIED); S32K144 removed as project MCU (see 13). Keep artifacts
      for audit/history; do not reuse the S32K144 symbol as an active part.
- [~] 1.12 `docs/security-mcu-comparison.md` — updated to reflect MCU swap and
      Trust M justification; ensure any claim referencing MCU crypto or SHE
      is traced to an authoritative source (Cn).

## 2. Requirements

- [ ] 2.1 Functional requirements spec (per voltage/amperage/protocol/control/EMI variant)
- [ ] 2.2 Safety requirements (motor runaway, overcurrent, thermal, CSEc/SE-based message-authentication trust boundary)
- [ ] 2.3 Regulatory/EMC targets per market (cite standard, Cn)
- [ ] 2.4 Requirements traceability matrix → REFERENCES.md tags
- [ ] 2.5 Motor speed-sensor requirement (ALL variants): define required accuracy, latency, interfaces and failure modes; enumerate supported sensor types (Hall/low-voltage digital, optical encoder/quadrature, analog tachometer → ADC). Trace to authoritative references where applicable (Cn). See `docs/design-speed-sensor-integration.md`.
- [ ] 2.6 Environmental & ingress protection requirements: specify supported IP ratings (up to IP68) and NEMA equivalents (up to NEMA 6P); define temperature, humidity, condensation and immersion duration/pressure profiles per-variant; submersible variants MUST include cooling strategies that operate in both air and water and have verification tests (see `docs/design-submersible-cooling.md` — DRAFT to author). Mark any environmental spec values UNVERIFIED until primary-source standards are cited (Cn).

## 3. Hardware — MCU Subsystem

- [~] 3.1 S32K144 schematic (historical) — kept for record; S32K144 removed as active MCU.
- [~] 3.2 Programming/debug interface — update mapping to new MCU (see 13).
- [~] 3.3 Peripheral pin mapping vs. protocol variant matrix — update and verify for MSPM0G3518-Q1 (Cn).
- [~] 3.4 Motor speed-sensor pin/interface mapping: allocate pins + ADC channels/OPAMP/COMP/interrupts/Quadrature timers for Hall/encoder/analog tach across the active MCU symbol/spec; add to `symbols/specs/*` and per-build variants. Mark pin numbers UNVERIFIED until primary-source pinmap read (Cn).

## 4. Hardware — Trust/Security Subsystem

- [x] 4.1 External SLB9672 TPM (historical) — removed 2026-08-03. OPTIGA™ Trust M (`U2`) integrated for asymmetric identity where required — see `docs/secure-element-architecture.md` and `docs/design-se-integration.md`.
- [ ] 4.2 Secure boot / attestation chain design doc (CSEc + Trust M): finish and VERIFY against primary sources (Cn).
- [ ] 4.3 Key provisioning process (Trust M provisioning profile, platform binding secret, SE Shielded Connection) — MUST be specified & verified (Cn).
- [ ] 4.4 CSEc firmware integration: message authentication (CMAC generate/verify per SHE); reconcile clock/CSEc execution budget vs hot-path control timing (Cn).

## 5. Hardware — Power Stage

- [~] 5.1 Gate driver + FET selection per amperage tier (10/20/30/40/50/80/120 A) — maintain candidate list; verify datasheets for final BOM lines (Cn).
- [~] 5.2 Voltage tier variants (2S/4S/6S/8S/12S) — component derating table; verify cell choices (Cn).
- [~] 5.3 Current sensing (shunt/hall) selection + citation — verify across tiers; INA240/WSLP candidates remain.
- [ ] 5.4 Brushed-ESC power-stage variant: add H-bridge / half-bridge design task, BOM candidate(s), protections (reverse current, flyback diodes, current sensing placement), and interaction with control firmware. See `docs/design-brushed-esc-variant.md`. Mark part-selection claims UNVERIFIED until datasheets cited (Cn).

## 6. Hardware — Protocol Interfaces

- [ ] 6.1 PWM input stage
- [ ] 6.2 SBus input stage (flag UNVERIFIED spec, C-pending)
- [ ] 6.3 DBus input stage (flag UNVERIFIED spec, C-pending)
- [ ] 6.4 UART/TTL transceiver
- [ ] 6.5 SPI interface
- [~] 6.6 RS-232 transceiver per [3]; candidate part ADM3232E [Cn]
- [ ] 6.7 RS-485 transceiver per [4]; candidate part ADM2582E/ADM2587E [Cn]
- [ ] 6.8 CAN 2.0 controller/transceiver per [5]; candidate part ADM3055E/ADM3057E [Cn]
- [ ] 6.9 CAN-FD controller/transceiver per [6]; candidate part ADM3055E/ADM3057E [Cn]
- [ ] 6.10 MIL-STD-1553B interface per [7]; candidate module Alta MEZ-E1553 [Cn]
- [ ] 6.11 Motor speed-sensor interfaces (ALL variants required):
      - 6.11.a Hall-effect: digital input(s) with interrupt and optional differential input path.
      - 6.11.b Quadrature encoder: A/B ±index input with pull resistors and optional hardware quadrature decoder (or ISR fallback).
      - 6.11.c Analog tachometer: analog front-end → ADC channel with anti-alias filtering, input protection and op-amp/comp front-end where needed.
      Add BOM candidates, level shifting, input protection and EMI filtering guidance; cite datasheets/standards where applicable (Cn). See `docs/design-speed-sensor-integration.md`.

## 7. Hardware — EMI Hardening

- [~] 7.1 Define tier requirements: None / Isolation / Grounding / Faraday; source clauses (Cn).
- [ ] 7.2 Layout guidelines per tier
- [ ] 7.3 Pre-compliance test plan
- [ ] 7.4 EMI considerations for speed-sensor inputs: ground referencing, filtered inputs for analog tach, twisted-pair differential routing for encoder/Hall lines, comparator hysteresis, input common-mode and ESD protection. Add to layout checklist and per-build README.

## 8. Firmware

- [ ] 8.1 Control loop: Open-loop
- [~] 8.2 Control loop: Closed-loop differential — sensorless FOC (where applicable) and sensors fallback.
- [~] 8.3 Control loop: Closed-loop PID
- [ ] 8.4 Protocol drivers (per §6)
- [ ] 8.5 Secure-boot / trust-chain firmware integration (CSEc + Trust M)
- [ ] 8.6 Fault handling (overcurrent/thermal/comm-loss)
- [ ] 8.7 Brushed-ESC firmware variant: H-bridge control, commutation strategy, regen handling, and safety limits. See `docs/design-brushed-esc-variant.md`.
- [ ] 8.8 Motor-speed sensor drivers and abstractions (common API): Hall (edge interrupts + debounce), quadrature decoder (hardware timer or ISR fallback), analog tachometer (ADC sampling + filtering). Include failure modes and fallback behavior per safety reqs (2.2).
- [ ] 8.9 Sensor fusion + control use-cases: map sensor input selection to control loop modes (sensorless fallback → sensor-based closed-loop), calibrations, and per-build configuration stored in NVM.

## 9. Verification & Test

- [ ] 9.1 Unit test plan (firmware)
- [ ] 9.2 HIL bench test plan
- [ ] 9.3 EMC pre-compliance test
- [ ] 9.4 Protocol conformance test per interface
- [ ] 9.5 Motor-speed sensor functional tests (Hall pulse-train test, encoder quadrature correctness, analog ADC calibration & accuracy)
- [ ] 9.6 Brushed power-stage test procedures (H-bridge switching, dead-time verification, reverse-current handling)

## 10. Release

- [ ] 10.1 Design review gate (AGENTS.md §5 checklist)
- [ ] 10.2 BOM finalization per variant (include sensor lines for every variant)
- [ ] 10.3 Manufacturing/fab release
- [ ] 10.4 v1.0 documentation freeze

## 11. Shared KiCad Symbol Library (symbols/)

- [x] 11.1 Generator + JSON-spec workflow (`symbols/tools/gen_kicad_symbol.py`, `symbols/specs/*.json`) retained.
- [x] 11.2 Historical S32K144 symbols retained for audit, not active.
- [~] 11.7 Active MCU symbol: author `symbols/specs/MSPM0G3518_Q1_PM.json` + `.kicad_sym` (work in progress). Pin numbers remain `UNVERIFIED PLACEHOLDER` until the primary pinmap is extracted/verified (Cn).
- [x] 11.4/11.5 previously VERIFIED symbols retained.
- [ ] 11.8 Add sensor symbols & footprint candidates: Hall sensor (digital), quadrature encoder connector, analog-tach front-end parts (OPAMP/COMP), level-shifters and input protection devices. Add generator JSON entries for each and ensure tools can emit them for each build variant.

## 12. Per-Build Instances (builds/`<voltage>`/`<amperage>`/`<variant>`/)

- [~] 12.1 `builds/6s/50A/CAN_485_faraday/` — update U1 → `MSPM0G3518-Q1` (see 13). MUST include motor-speed sensor input in BOM & schematic (see 2.5/6.11/3.4).
- [~] 12.2 Add brushed-ESC build variant skeleton(s) — e.g. `builds/<voltage>/<amperage>/BRUSHED_<variant>/`:
      - README: summarize brushed vs brushless differences, H-bridge BOM lines, sensor input requirements (required), protections (mark UNVERIFIED until datasheets are added).
      - `kicad/` schematic template: H-bridge placeholders, speed-sensor connector footprint.
      - Acceptance checklist: H-bridge ERC, current-sense integration, dead-time verification tests, firmware mapping.
- [~] 12.3 Secure element (`U2`, OPTIGA™ Trust M V3) — integrated. Remaining open items:
  - [ ] 12.3.a Enable Shielded Connection on I²C and provision platform binding secret (High, Cn).
  - [ ] 12.3.b Anti-replay/freshness scheme for per-frame CMAC (High).
  - [ ] 12.3.c MAC_LENGTH and verification-failure policy (Medium).
  - [ ] 12.3.d Reconcile control-loop timing vs CSEc/SE operations (Medium).
  - [ ] 12.3.e Fleet key lifecycle and revocation strategy (Medium).
  - [ ] 12.3.f Annotate schematic and place U2 on PCB (placement/BOM).

## 13. MCU Swap — S32K144 → MSPM0G3518-Q1 (IN PROGRESS)

- [~] 13.1 Replace NXP S32K144 with TI MSPM0G3518-Q1 (PM LQFP-64) — decision 2026-08-10; work in `docs/HANDOFF-mcu-swap-s32k144-to-mspm0g3518.md`.
  - [~] 13.1.a Author `symbols/specs/MSPM0G3518_Q1_PM.json` + `.kicad_sym`; preserve functional signal names so wiring survives.
  - [~] 13.1.b Hazard: `VCORE` != `VDDA`. `VCORE` must only connect to dedicated `C_VCORE`. `C_VCORE` value = `UNVERIFIED — needs primary source` until table read.
  - [~] 13.1.c Resolve pin numbers from MSPM0 datasheet attachments (try embedded attachments extraction). Mark pin number changes VERIFIED only after primary-source confirmation.
  - [ ] 13.1.d Update `docs/security-mcu-comparison.md`, `README.md`, per-build READMEs to record swap and any security implications (Cn).
