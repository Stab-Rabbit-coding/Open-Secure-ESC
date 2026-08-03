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
      2026-08-03 — project MCU changed to NXP S32K144, see 1.11/[31].**
- [x] 1.5 Verify [2] SLB9672 datasheet page refs for compliance claims —
      superseded by dropping the part before this was resolved. **[2]
      DROPPED 2026-08-03 — TPM removed from design in favor of the S32K144's
      on-chip CSEc, see 1.11/4.1/[31].**
- [~] 1.11 Verify [31] NXP S32K1xx Data Sheet claims used in
      `symbols/specs/S32K144.json`/README.md (local copy VERIFIED
      2026-08-03 for CSEc, packages, memory, clock, power-pin names,
      RESET_B/SWD_CLK/SWD_DIO pin names — see [31] for exact pages; live
      nxp.com fetch blocked: 403, same pattern as [2]/[6]/[12]-[23]). Still
      open: (a) physical package-pin **numbers** for the 64-pin LQFP — the
      local data sheet explicitly defers this to the S32K1xx Series
      Reference Manual; that RM is now locally available
      (`docs/datasheets/S32K-RM.pdf`, see [31]) but its pinout chapter has
      not yet been read/regenerated into `symbols/specs/S32K144.json`, so
      `pins[].num` remains an `UNVERIFIED PLACEHOLDER PIN MAP`. **2026-08-03:
      (b) RESOLVED** — CSEc's message-authentication algorithm
      (AES-128-CMAC, `CMD_GENERATE_MAC`/`CMD_VERIFY_MAC`) is now VERIFIED
      directly against the local S32K1xx Reference Manual Ch. 36 §36.5.13;
      see [31] and `docs/security-mcu-comparison.md` §3.1/§7. The Reference
      Manual also confirms CSEc's command set is symmetric-only (no
      RSA/ECC/certificate commands anywhere in Ch. 36) — used in the new
      security-module comparison doc, see 1.12 below.
- [x] 1.12 `docs/security-mcu-comparison.md` — NXP S32K144 CSEc vs.
      Infineon SLB9672 TPM 2.0 comparison (authentication/message-signing,
      PKI capability, footprint, EMI/ESD/EMC, indicative pricing), plus a
      survey of three other 5V-class automotive MCU security options
      (Infineon TLE987x/TLE9879 — no on-chip crypto engine found in its
      official CMSIS DFP, [32]; Microchip dsPIC33C MPT Secure DSC family,
      [33] `UNVERIFIED`; Renesas RH850/U2A16 EVITA-Full HSM, [34]
      `UNVERIFIED`). Supports 4.2. Every external vendor/distributor
      fetch attempted for the survey (§8/§9 of that doc) returned HTTP 403
      this session except one Infineon-hosted GitHub file [32]; those
      sections are explicitly marked `UNVERIFIED — needs primary source`
      pending a session where nxp.com/infineon.com/microchip.com/
      renesas.com/digikey.com/mouser.com are reachable, or manual PDF
      downloads (same workaround as 1.10).
- [ ] 1.6 Verify [3]-[7] section/page pins once standards obtained (paywalled)
- [ ] 1.7 Confirm MIL-STD-1553B vs -1553C target revision, update [7]
- [~] 1.8 Source authoritative refs: SBus, DBus, PWM-interface, UART/TTL/SPI, EMI tiers
      (EMI standards found: MIL-STD-461G [15], IEC 62368-1 [16], IEC/TR
      61000-5-2 [17]; SBus/DBus still lack an official spec — hardware
      invert note added citing [1] p.67 §8.23; PWM/UART/TTL/SPI need no
      external standard, cite MCU datasheet directly)
- [ ] 1.9 CONTRIBUTING.md — citation workflow quick-reference (derive from AGENTS.md §2)
- [~] 1.10 Re-run live fetch (or manual PDF download) for [12]-[23] once
      network access allows — this session's WebFetch returned HTTP 403
      for every domain tried (including a neutral control URL); all specs
      in [12]-[23] were originally corroborated via secondary search
      sources only, not read from a primary PDF, and none had a local
      verified copy.
      2026-08-02 update: manual PDF downloads resolved [14], [19], [20],
      [21], [22], [23], [30] (VERIFIED, local copies added) plus four
      alternative-part citations [26]-[29] (Molicel P45B, Samsung SDI
      40T, Analog Devices AD8410A, Infineon TLE9180D-31QK — none
      adopted into the BOM). **[27] (Samsung 40T) is marked "Confidential
      Proprietary" by Samsung on every page — flagged for the repo owner
      to decide whether it should be removed rather than committed; see
      [27].** Two other manual downloads added the same day turned out
      NOT to resolve any open citation — [24] (Vishay WSL, doc 30100) is
      a related-but-different family from [23] (WSLP2512, doc 30122,
      since resolved separately); [25] (Würth WE-SHC 3690103020) is a
      ~3mm single-IC-scale shield, not [19]/[30]'s 3671375/3670375
      cover+frame pair (since resolved separately). Every BOM line in
      this build's own BOM (§12.1) now has a locally verified primary
      datasheet; [12], [13], [16]-[18] (standards/parts not used by
      this build's own BOM) remain open, so this item stays `[~]`
      rather than `[x]` at the [12]-[23] range level.

## 2. Requirements

- [ ] 2.1 Functional requirements spec (per voltage/amperage/protocol/control/EMI variant)
- [ ] 2.2 Safety requirements (motor runaway, overcurrent, thermal, CSEc-based message-authentication trust boundary)
- [ ] 2.3 Regulatory/EMC targets per market (cite standard, C6)
- [ ] 2.4 Requirements traceability matrix → REFERENCES.md tags

## 3. Hardware — MCU Subsystem

- [~] 3.1 S32K144 schematic (power, clock, decoupling per [31]) — MCU/support
      passives placed and wired in `builds/6s/50A/CAN_485_faraday/kicad/`
      (VDD/VSS/VDDA/VREFH/VREFL_VSSA_VSS decoupling per [31] p.13's "VDD and
      VDDA must be shorted to a common source" requirement); physical pin
      **numbers** still UNVERIFIED PLACEHOLDER, see 1.11.
- [ ] 3.2 Programming/debug interface (SWD_CLK/SWD_DIO per [31])
- [ ] 3.3 Peripheral pin mapping vs. protocol variant matrix

## 4. Hardware — Trust/Security Subsystem

- [x] 4.1 ~~SLB9672 TPM schematic (SPI per [2])~~ — **superseded 2026-08-03:
      external TPM dropped from the design.** Message authentication is now
      provided by the S32K144's on-chip CSEc security module [31] — no
      discrete chip, no SPI schematic needed; CSEc is driven entirely by
      firmware over an internal command interface (see 4.4 below).
- [ ] 4.2 Secure boot / attestation chain design doc (now CSEc/SHE-based —
      see [31], and 1.11 for what's still open on the SHE spec itself).
      `docs/security-mcu-comparison.md` (1.12) now documents CSEc's
      symmetric-only trust model and its `BOOT_MAC_KEY`-based secure-boot
      mechanism as background, but a full attestation-chain design doc is
      still a separate, not-yet-started deliverable.
- [ ] 4.3 Key provisioning process (CSEc key slots per the SHE Functional
      Specification's command set — spec itself not yet obtained, see 1.11)
- [ ] 4.4 CSEc firmware integration: message authentication (CMAC
      generate/verify per SHE) for CAN/RS-485 frame traffic — algorithm
      detail (AES-128-CMAC) UNVERIFIED against a primary source pending 1.11

## 5. Hardware — Power Stage

- [~] 5.1 Gate driver + FET selection per amperage tier (10/20/30/40/50/80/120 A)
      — candidates: Infineon IRFB4110PBF FET [20] (1x-3x parallel per
      tier), TI DRV8353S gate driver [21] (same part all tiers); both
      VERIFIED against local datasheets 2026-08-02, not yet settled in
      a bill of materials
- [~] 5.2 Voltage tier variants (2S/4S/6S/8S/12S) — component derating table
      — candidate cell Molicel INR-21700-P42A [14], VERIFIED against
      local datasheet 2026-08-02, gives nominal/max/min table (2S
      7.2/8.4/5.0V ... 12S 43.2/50.4/30.0V); cell not yet selected in
      BOM, cutoff voltage is cell-dependent (see [14] note)
- [~] 5.3 Current sensing (shunt/hall) selection + citation — candidates:
      Vishay WSLP2512 shunt [23] (VERIFIED against local datasheet
      2026-08-02) + TI INA240 amplifier [22], same parts across tiers
      except 80A/120A where single-shunt power rating is exceeded (open
      gap, no part selected yet for those two tiers)

## 6. Hardware — Protocol Interfaces

- [ ] 6.1 PWM input stage
- [ ] 6.2 SBus input stage (flag UNVERIFIED spec, C-pending)
- [ ] 6.3 DBus input stage (flag UNVERIFIED spec, C-pending)
- [ ] 6.4 UART/TTL transceiver
- [ ] 6.5 SPI interface
- [~] 6.6 RS-232 transceiver per [3]; candidate part ADM3232E [12]
- [ ] 6.7 RS-485 transceiver per [4]; candidate part ADM2582E/ADM2587E [9]
- [ ] 6.8 CAN 2.0 controller/transceiver per [5]; candidate part ADM3055E/ADM3057E [10]
- [ ] 6.9 CAN-FD controller/transceiver per [6]; candidate part ADM3055E/ADM3057E [10]
- [ ] 6.10 MIL-STD-1553B interface per [7]; candidate module Alta MEZ-E1553 [11]

## 7. Hardware — EMI Hardening

- [~] 7.1 Define tier requirements: None / Isolation / Grounding / Faraday
      — standards found: MIL-STD-461G [15] (Grounding, Faraday), IEC
      62368-1 [16] (Isolation classification), IEC/TR 61000-5-2 [17]
      (Grounding, layout-only); candidate parts: ADuM4221 isolated gate
      driver [18] (Isolation), Würth WE-SHC 3671375 cover [19] + 3670375
      frame [30] (Faraday) — both VERIFIED against local datasheets
      2026-08-02, no shielding-effectiveness dB figure in either;
      Grounding tier confirmed layout-only, no part needed. Clause/page
      pins for [15]-[18] still open (see 1.10).
- [ ] 7.2 Layout guidelines per tier
- [ ] 7.3 Pre-compliance test plan

## 8. Firmware

- [ ] 8.1 Control loop: Open-loop
- [~] 8.2 Control loop: Closed-loop differential — feedback approach:
      sensorless FOC per TI SLAAE96A [13] (no extra BOM part; MCU's own
      ADC/OPA/COMP per [1]); Hall-sensored fallback DRV5013 noted in [13]
- [~] 8.3 Control loop: Closed-loop PID — same feedback approach as 8.2
- [ ] 8.4 Protocol drivers (per §6)
- [ ] 8.5 TPM integration / secure boot firmware
- [ ] 8.6 Fault handling (overcurrent/thermal/comm-loss)

## 9. Verification & Test

- [ ] 9.1 Unit test plan (firmware)
- [ ] 9.2 HIL bench test plan
- [ ] 9.3 EMC pre-compliance test
- [ ] 9.4 Protocol conformance test per interface

## 10. Release

- [ ] 10.1 Design review gate (AGENTS.md §5 checklist)
- [ ] 10.2 BOM finalization per variant
- [ ] 10.3 Manufacturing/fab release
- [ ] 10.4 v1.0 documentation freeze

## 11. Shared KiCad Symbol Library (symbols/)

- [x] 11.1 Generator + JSON-spec workflow (`symbols/tools/gen_kicad_symbol.py`,
      `symbols/specs/*.json`) so future components/builds source a pin map
      once and regenerate rather than hand-edit S-expressions
- [x] 11.2 ~~MSPM0G3507 [1] symbol~~ — removed 2026-08-03, superseded by
      11.7 (S32K144). Historical: pin subset VERIFIED against local PDF
      Table 6-2 (64-LQFP column); full 64-pin symbol was never built.
- [x] 11.3 ~~SLB9672 [2] symbol~~ — removed 2026-08-03, TPM dropped from
      the design (see 4.1). Historical: full 32-pin, VERIFIED,
      footprint-complete.
- [~] 11.7 S32K144 [31] symbol (`symbols/specs/S32K144.json`) — replaces
      11.2 as the project MCU. Feature-level facts VERIFIED against the
      local S32K1xx Data Sheet; pin **numbers** are an
      `UNVERIFIED PLACEHOLDER PIN MAP` — the local datasheet defers the
      physical pinout to the S32K1xx Series Reference Manual (not
      obtained, nxp.com fetch blocked: 403). Do not send to fab until
      resolved — see 1.11.
- [x] 11.4 ADM2582E/ADM2587E [9] and ADM3055E/ADM3057E [10] symbols — full
      20-pin, VERIFIED against local PDFs
- [x] 11.5 DRV8353S [21] and INA240 [22] symbols — both resolved
      2026-08-02: local datasheets added, symbols regenerated. DRV8353S:
      full 40-pin VERIFIED map (RTA/WQFN package, SPI-variant column of
      the datasheet's pin table — see `symbols/specs/DRV8353S.json`),
      replacing the prior 26-pin sequential placeholder. INA240: VERIFIED
      D/SOIC-8 8-pin map (see `symbols/specs/INA240.json`).
- [x] 11.6 IRFB4110PBF [20], WSLP2512 [23], INR21700-P42A [14],
      WE-SHC 3671375 cover [15], [19] and 3670375 frame [15], [19], [30]
      symbols — generic/mechanical pinouts, no part-specific pin diagram
      needed. All five now additionally VERIFIED (electrical/dimensional
      ratings) against local datasheets added 2026-08-02.

## 12. Per-Build Instances (builds/`<voltage>`/`<amperage>`/`<variant>`/)

- [~] 12.1 `builds/6s/50A/CAN_485_faraday/` — 6S, 50A, CAN-FD + RS-485
      (concurrent), Faraday EMI tier (sized against a 500 W/m² broadband RF
      requirement, derived ~434 V/m). BOM drafted from
      `docs/decision-matrix.xlsx` (README.md in that folder); `kicad/`
      contains a project skeleton wired to `symbols/` but no placed
      components; `gerbers/` empty pending a PCB layout. Blocked on the
      same open items as 1.10/5.1-5.3/6.7-6.9/7.1: most BOM lines are still
      `Candidate (unverified)`, and the CAN-FD/RS-485 transceiver variant
      choice (isolation voltage vs. data rate) and DRV8353S-vs-INA240
      current-sense sourcing are open design questions, not resolved in
      that build's README.
      **2026-08-03: MCU/TPM swap applied to this build** — U1 is now
      S32K144 (was MSPM0G3507), the SLB9672 TPM (U2) was removed, schematic
      and PCB regenerated via `kicad/tools/gen_schematic.py`/`gen_pcb.py`
      (connectivity check clean, `check_shorts.py` clean, kiutils
      round-trip validated). See 1.11/3.1/4.1 for what's still open.
