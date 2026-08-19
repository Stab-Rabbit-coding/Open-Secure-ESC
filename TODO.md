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
      `pins[].num` remains an `UNVERIFIED PLACEHOLDER PIN MAP`.
      **2026-08-10: (a) is now UNBLOCKED — the source has been located.** The
      RM body does not contain the per-pin map either: its Ch. 4 §4.1 defers to
      an "IO Signal Description Input Multiplexing sheet(s) attached to the
      Reference Manual." Those sheets are **embedded files inside
      `docs/datasheets/S32K-RM.pdf`** and extract cleanly:
      `pdfdetach -savefile 'S32K144_IO_Signal_Description_Input_Multiplexing.xlsx'
      -o S32K144_IO.xlsx docs/datasheets/S32K-RM.pdf`. Its "IO Signal Table" tab
      carries an `S32K144_64lqfp` column giving the real pin number for every
      port/function pair — e.g. the LPI2C0 options for the secure element are
      PTA2/PTA3 = pins 48/47 (ALT3) and PTB6/PTB7 = pins 12/11 (ALT2). Those
      candidates are recorded in `docs/secure-element-architecture.md` §6.1 but
      deliberately **not** committed to the symbol: three real pin numbers
      cannot be conflict-checked against 27 placeholders, so the whole 64-pin
      map must be resolved in one pass. That pass is the remaining work here.
      **2026-08-03:
      (b) RESOLVED** — CSEc's message-authentication algorithm
      (AES-128-CMAC, `CMD_GENERATE_MAC`/`CMD_VERIFY_MAC`) is now VERIFIED
      directly against the local S32K1xx Reference Manual Ch. 36 §36.5.13;
      see [31] and `docs/security-mcu-comparison.md` §3.1/§7. The Reference
      Manual also confirms CSEc's command set is symmetric-only (no
      RSA/ECC/certificate commands anywhere in Ch. 36) — used in the new
      security-module comparison doc, see 1.12 below.
- [x] 1.12 `docs/security-mcu-comparison.md` — NXP S32K144 CSEc vs.
      Infineon SLB9672 TPM 2.0 comparison (authentication/message-signing
      latency, PKI capability, footprint, EMI/ESD/EMC, pricing), expanded
      2026-08-03 into a full 8-candidate survey as more datasheets were
      added to the repo: Infineon TLE987x/TLE9879 (§9.1, no crypto engine,
      [32] `UNVERIFIED` beyond the CMSIS pack); Microchip dsPIC33CK512MPT608
      (§9.2, [33], VERIFIED — full on-die PKI/X.509, AEC-Q100 Grade 1,
      100-TQFP, 3.0–3.6V not 5V, availability unclear); Renesas RH850/U2A16
      (§9.3, [34], `UNVERIFIED`); STM32G431K + SLB9672 combo (§9.4, [35]
      restored from git history + [2], VERIFIED — weakest option: no
      AEC-Q100, worst ESD, no on-die crypto fallback); Microchip SAM E51G19
      (§9.5, [36], VERIFIED — AES/TRNG/PUKCC math accelerator + ICM hash
      engine with real cycle counts, AEC-Q100 Grade 1, 25 mm²); TI
      TMS320F280025(-Q1) (§9.6, [37], VERIFIED — **excluded**, no crypto
      module, only DCSM code-protection); TI MSPM0G3107 (§9.7, [38]-[42],
      VERIFIED — AES/CRC/TRNG + platform secure-boot/Keystore/software-ECDSA
      per the cybersecurity app note [40], real AES cycle-count latency
      data from the TRM [39], Cortex-M0+ core is the one weak point); TI
      MSPM0G350x-Q1 (§9.8, [43], VERIFIED — same security model as 9.7 plus
      ISO 26262 ASIL B TÜV certification and AEC-Q100 Grade 1 stated
      directly, smallest footprint (~21 mm²) in the whole survey). New §8
      resolves the standing "can the bus/crypto keep up" question with the
      MSPM0/SAM cycle-count data: symmetric MAC is always fast enough
      (microseconds); only asymmetric/PKI primitives are architecturally
      unsuited to per-frame authentication, regardless of chip. §6.1 records
      the 5V-vs-3.3V EMI/SNR design-rationale discussion (repo owner
      confirmed most of the rest of this project is 3.3V-class). Supports
      4.2. Repo owner separately confirmed CSC-vs-BIM secure-boot choice is
      a firmware/SDK decision usable on either MSPM0 part, not gated by
      silicon variant (noted in [40]'s entry and §9.7/§9.8).
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

- [~] 12.3 Secure element (`U2`, OPTIGA™ Trust M V3, [45]) — added to
      `builds/6s/50A/CAN_485_faraday` 2026-08-10. Symbol, footprint, 3D model,
      schematic placement and LPI2C wiring are **done and verified** (pin map
      from [45] p.17 Table 6; reference circuit from [45] p.12 §3 Fig. 2; ERC
      shows no new errors). Design rationale and the full assessment are in
      `docs/secure-element-architecture.md`. The items below are **OPEN and
      must be closed before this build flies** — they are firmware and policy
      decisions, not layout work.
  - [ ] 12.3.a **(High, safety-critical)** Define the behaviour on CSEc MAC
        verification failure. If a failed MAC hard-stops a motor in flight,
        a single corrupted frame — or a transient bus fault — becomes a
        shutdown primitive, i.e. the security control becomes the attack.
        Decide fail-operational vs fail-safe and over what window of
        consecutive failures. See `docs/secure-element-architecture.md` O-04.
  - [ ] 12.3.b **(High)** Specify an anti-replay freshness scheme. AES-128
        CMAC authenticates content, not recency; without a freshness value a
        recorded throttle command replays as valid. The Trust M's 4 monotonic
        counters ([45] p.10 Fig. 1) are boot-scale and cannot serve per-frame.
        See C-03.
  - [ ] 12.3.c **(High)** Enable the Trust M I²C **Shielded Connection** and
        provision the platform binding secret ([45] p.1 Features, p.10 Fig. 1).
        Without it the agreed session key crosses an exposed 2-wire bus in
        clear and the whole asymmetric layer buys nothing against an attacker
        with board access. See C-06.
  - [ ] 12.3.d **(Medium)** Decide `MAC_LENGTH` for CAN-FD frames and the
        verification-failure rate limit. CAN-FD carries at most 64 byte
        ([31] RM Rev. 14 §55.2.2, p. 1802); a full 128-bit CMAC is 16 byte.
        Truncation to 32 bit gives 2⁻³² per attempt, which is insufficient
        without a lockout. Interacts directly with 12.3.a. See C-04.
  - [ ] 12.3.e **(Medium)** Reconcile the control-loop clock budget with the
        CSEc/HSRUN exclusion: [31] §1.1 states the device must drop from
        HSRUN (112 MHz) to RUN (80 MHz) to execute CSEc. Any budget assuming
        112 MHz *and* per-frame CMAC is wrong. See C-05.
  - [ ] 12.3.f **(Medium)** Design fleet key lifecycle and revocation. With 4
        certificate slots and 3 trust anchors there is no room for a
        conventional CRL, and there is no defined process for retiring a
        compromised controller. See O-05.
  - [ ] 12.3.g **(Low)** Pin the ECC curve in the provisioning profile
        (P-256 minimum, P-384 preferred). The device also supports RSA-1024
        ([45] pp. 8–9 Table 4), which must not be selected. See C-07.
  - [ ] 12.3.h Port the secure-element placement into
        `kicad/tools/gen_schematic.py`. It was deliberately **not** written
        blind: `kiutils` is unavailable on the machine where this work was
        done, so the code could not have been executed even once, and
        unverified generator code that silently overwrites a verified
        schematic is precisely what `AGENTS.md` §1.3 guards against. The
        schematic was extended by `kicad/tools/inject_optiga_secure_element.py`
        instead, and `gen_schematic.py` now carries a divergence warning. Do
        this on a machine with `kiutils`, then diff against the committed
        sheet before trusting the result.
  - [ ] 12.3.i Annotate the sheet. Every reference on
        `open_secure_esc_6s_50a_can485_faraday.kicad_sch` is still `R?`/`C?`/
        `U?`, which is why a netlist export collapses passives. Pre-existing,
        but it blocks BOM/CPL generation and PCB placement of `U2`.
  - [ ] 12.3.j Place `U2` and its three passives on the PCB
        (`gen_pcb.py` / manual). Schematic-only at present.

- [~] 12.4 **Layout completion pass for `builds/6s/50A/CAN_485_faraday`**
      (2026-08-15). The build went from "schematic populated, PCB net-less and
      unrouted" to an annotated schematic with **0 ERC errors** and a
      4-layer PCB carrying every part, real nets, poured planes and routed
      copper. Generators live in that build's `kicad/tools/`. What was closed:
  - [x] 12.4.a Schematic annotated — all 57 symbols; closes 12.3.i. The 8
        `PWR_FLAG` symbols were also virtualised (`#FLGnn`, out of BOM, off
        board); they had been ordinary in-BOM parts.
        (`tools/finish_annotate_and_footprints.py`)
  - [x] 12.4.b **DRV8353S footprint authored** from TI's own RTA0040B
        EXAMPLE BOARD LAYOUT / EXAMPLE STENCIL DESIGN sheets [21] — closes the
        "No footprint for U5" gap. Land, paste apertures and the 12x 0.2 mm
        thermal vias are manufacturer values, not an IPC derivation.
        (`symbols/tools/gen_drv8353s_rta0040b_footprint.py`)
  - [x] 12.4.c **WE-SHC 3670375 frame footprint authored** from Wurth's own
        Recommended Land Pattern [30]. The 3671375 COVER correctly gets no
        footprint — it clips on and is not soldered, so it is now
        schematic/BOM-only like BT1-BT6.
        (`symbols/tools/gen_we_shc_3670375_footprint.py`)
  - [x] 12.4.d **Missing SDO pull-up added (R14, 10k).** [21]'s pin table
        gives DRV8353S SDO (pin 27) as type **OD** and states "This pin
        requires an external pullup resistor." There was none, so every SPI
        register read from the gate driver would have failed. nFAULT already
        had its pull-up (R11); SDO did not.
  - [x] 12.4.e **Gate-driver thermal pad given electrical existence.** Pin 41
        added to the DRV8353S symbol and tied to GND, so the exposed pad is
        not imported as an isolated copper island under the power stage. The
        GND assignment is an engineering default — see 12.4.n.
  - [x] 12.4.f **Four isolated-side power flags reconnected.** #FLG04-07 and
        their L-routes never touched their target pins (legs landed on the
        right Y at x = 381.5 while the pins are at x = 380.01), leaving 4
        `power_pin_not_driven` errors on the transceivers' isolated supplies.
        Replaced with short stubs and rail labels.
  - [x] 12.4.g **32 `lib_symbol_mismatch` warnings cleared** by moving the
        generic R/C/connector/flag stand-ins into a repo-owned library,
        `symbols/Open_Secure_ESC_Generic.kicad_sym`. They had been stored
        under KiCad's own `Device:`/`Connector_Generic:`/`power:` names
        despite different pin geometry. `kicad/README.md`'s claim that these
        are "KiCad's own standard" parts was wrong and is now corrected.
  - [x] 12.4.h **Battery input added (J5).** VM had no connector at all — the
        pack is off-board, so the board could not be energised. The previous
        PCB had a J5 footprint with no schematic counterpart, i.e. two netless
        pads. J5 is now a real schematic part on VM/GND.
  - [x] 12.4.i **PCB rebuilt from the exported netlist** — 44 footprints, 73
        nets, every pad netted from the schematic rather than left on net 0.
        4-layer stack: In1.Cu solid GND, In2.Cu VM over the power stage and
        GND elsewhere, GND pours on both outer layers.
        (`tools/build_pcb.py`)
  - [x] 12.4.j **Isolation barrier made real** — a copper keepout removes
        every plane and pour from the isolated band, and both transceivers are
        rotated so their isolated pin rows face the board edge. Without it the
        GND plane ran straight under the isolation barrier.
  - [ ] 12.4.k **(High, blocks fab) Size the power conductors against
        IPC-2152 [46].** No conductor width in this build is a computed value.
        VM and GND are poured planes so they do not depend on track width, but
        the three PHASE nets reach the motor connector partly as routed
        track, and that IS load-bearing at 50 A. [46] is paywalled: only its
        Table of Contents has been read, so per `AGENTS.md` §1.3 nothing may
        be derived from it yet. Buy the standard, then size the phase copper,
        the plane cross-sections, the vias and the connector pads, and choose
        the copper weight to match.
  - [ ] 12.4.l **(High, blocks fab) Select real power connectors.** J4
        (phases) and J5 (pack) are currently KiCad 6 mm^2 (~10 AWG) solder-wire
        pads — the largest in the stock library, chosen because the previous
        J4 was a 2.54 mm pin header, which is not a 50 A part. No connector
        has actually been selected and no current rating verified. Depends on
        12.4.k.
  - [ ] 12.4.m **(Medium) Set the isolation barrier width from the chosen
        transceiver variant.** The keepout band is sized to clear the isolated
        pin rows, not to any creepage/clearance table. The real figure follows
        from the still-open ADM3055E-vs-ADM3057E (5000 vs 3750 V rms) and
        ADM2582E-vs-ADM2587E choices in this build's README.
  - [ ] 12.4.n **(Medium) Confirm the DRV8353S exposed pad may be tied to
        GND.** [21] requires the pad to be soldered (RTA0040B note 3) and
        requires a ground-plane connection at the GND pin (§11.1), but does
        not state that the pad is internally common with GND. Currently an
        engineering default per `AGENTS.md` §4.
  - [ ] 12.4.o **(Medium) Confirm the WE-SHC frame's two 1.3 mm locating
        holes should be PLATED.** [30] dimensions them but does not say.
        Generated as plated on the shield net.
  - [ ] 12.4.p **(Medium) Model the MCU's remaining 36 package pins.**
        `symbols/specs/MSPM0G3518_Q1_PM.json` maps 28 of the LQFP-64's 64
        pins, so 36 pads import with no net. Fine electrically (unused GPIO),
        but the symbol does not describe the package.
  - [ ] 12.4.q **(Medium) Finish component placement.** `build_pcb.py`'s
        placement table is legible and DRC-clean and respects [21] §11.1's
        gate-loop and bulk-capacitor constraints, but it is a starting point,
        not a solved placement. Thermal, EMI and manufacturability review of
        the power stage is a human task.
  - [ ] 12.4.r **(Low) 347 `endpoint_off_grid` ERC warnings.** `genlib.py`
        lays the sheet out on a 10 mm grid, which is not a multiple of KiCad's
        1.27 mm connection grid. **Do not "fix" this with a coordinate
        snap** — it was tried and reverted: the generator separates parallel
        routes by 0.01-0.02 mm lane offsets, and snapping merges them
        (VM shorted to GND, all six PWM lines merged, CPH shorted to CPL;
        73 nets collapsed to 63). See `tools/snap_to_grid.py`, which now
        refuses to write without `--force`. A real fix means re-laying out
        the drawing with >= 1.27 mm lane spacing.
  - [ ] 12.4.s (Low) 4 `silk_over_copper` and 1 `starved_thermal` DRC
        warnings remain; cosmetic/fab-preference, not electrical.

- [~] 12.5 **Compact respin of `builds/6s/50A/CAN_485_faraday`, landed at
      25.4 x 60.1 mm** (2026-08-16). Triggered by the repo owner: the
      150 x 140 mm board from 12.4 was "way too big for a single channel ESC
      ... it won't fit where it needs to". Drawn for a 30 x 60 envelope, then
      hand-placed by the repo owner and narrowed to 1 inch wide without
      shrinking any phase pour. Schematic complete and ERC-clean; placement
      converged. **Next session starts at 12.5.t.**
  - [x] 12.5.a **FET swapped to Toshiba TPHR8504PL** [49], package 2-5W1A
        "SOP Advance(N)", chosen by the repo owner over TI CSD19532Q5B [48].
        Symbol, spec and footprint authored. TO-220 -> SMD is what makes
        double-sided assembly possible at all.
  - [x] 12.5.b **Land pattern taken from Toshiba's catalog** [50] p.46, not
        derived. An IPC-7351 derivation made first (before [50] was located)
        was 46% short on drain-land area and 86% short on lead-pad area.
        Toshiba does not publish land patterns in part datasheets.
  - [x] 12.5.c **Shield swapped to WE-SHC 3670209/3671209** [51]/[52],
        saving 812 mm^2 -- the single biggest area win available.
  - [x] 12.5.d Shunts 1 mOhm -> **0.5 mOhm**; C1 radial -> 1210 SMD;
        J4/J5 split into per-terminal pads; J1-J4 moved to SMD solder pads.
  - [x] 12.5.e **Schematic swap complete, 0 ERC errors.** All six gate nets
        preserved by placing the new symbol so its gate pin lands on the old
        gate pin's exact coordinate; drains and sources rewired and the
        netlist verified pin-by-pin (high-side drains on VM, low-side drains
        on the phases, low-side sources on the shunts).
  - [x] 12.5.f **Hand-place the PCB -- DONE by the repo owner** (2026-08-16),
        then narrowed to 25.4 x 60.1 mm. DRC: **0 courtyard overlaps, 0
        clearance, 0 hole-clearance, 0 same-layer pad conflicts.** Tightest
        copper-to-edge 0.83 mm (U3). Constraints that must survive future
        edits are tabulated in `kicad/README.md` "Placement guide".
        Re-running `tools/build_pcb.py` discards this placement -- its
        PLACEMENT table still describes the old 30 x 60 layout.
  - [x] 12.5.g **(High, electrical) U5's thermal via field vs the FETs --
        RESOLVED by the hand placement** (verified 2026-08-16: no U5 thermal
        via intersects any pad of any other footprint). Kept below as the
        standing re-check after any move of U5 or a Q.**
        U5 sits on the bottom directly beneath the top-side MOSFETs and its
        footprint carries 12 thermal vias on GND. A via under a FET drain pad
        shorts **GND to VM or to a phase**. [21] RTA0040B note 5 makes the
        vias optional, so deleting them is a legitimate fix. Check after any
        move of U5 or any Q.
  - [x] 12.5.p **Conductor sizing answered as an interim derivation**
        (2026-08-16). `docs/tools/conductor_sizing.py` derives phase-pour
        resistance and dissipation from copper's resistivity: **2 oz outer is
        the floor**, because at 1 oz the three phase pours dissipate 13.3 W
        against the FETs' 10.5 W -- the copper would be the dominant heat
        source. A phase changing layers needs ~23 x 0.3 mm vias to match the
        pour. This is an AGENTS.md Sec.4 engineering derivation giving WATTS,
        not degrees; **IPC-2152 [46] stays open** (12.4.k) because turning
        watts into temperature rise is exactly what it provides and this does
        not.
  - [ ] 12.5.q **(High) Set IDRIVE from a bench measurement, not a table.**
        Overshoot is 25.2 + L_loop x dI/dt. At 5 nH every IDRIVE setting is
        survivable; at 20 nH almost none are. Minimise the commutation loop
        first, then raise IDRIVE as far as measured V_DS allows. Table in
        `kicad/README.md`. Closes the open half of 12.5.n.
  - [ ] 12.5.r **(Low) Two PCB reference sets were consulted 2026-08-16 and
        both need treating with care.** One labelled the **IPC-2221**
        Appendix A equation (k=0.048/0.024, b=0.44, c=0.725) as "the IPC-2152
        formula" -- different standards, and 2152 exists because 2221's curves
        were found inaccurate -- and its own quick-reference table disagreed
        with that formula by ~2x at 10 A. Neither was used as a source. Noted
        so nobody adopts those numbers later believing they are IPC-2152.
  - [ ] 12.5.h Route (`tools/autoroute.py`), then DRC to zero errors.
  - [ ] 12.5.i Fab outputs, then documentation.
  - [x] 12.5.j **Where the next session picks up** -- superseded; placement
        is done (12.5.f) and 12.5.g is resolved. See 12.5.t.
  - [ ] 12.5.k **(Medium) Strain relief for J2/J3.** They are now bare SMD
        solder pads with no mechanical retention, and they leave the board in
        service. J1 (debug) is fine as-is. Needs a tie-down, potting, or a
        real connector selected.
  - [ ] 12.5.l **(Medium) On-board bulk capacitance.** C1 went from a 10 mm
        radial to a 1210, which holds far less. [47] carries 470 uF 63 V
        EXTERNAL to the board. Decide whether external bulk is required.
  - [ ] 12.5.m **(Medium) Confirm the sense chain still resolves.** Halving
        the shunt halves the sense voltage; check the DRV8353S CSA gain and
        the INA240 range against the overcurrent trip threshold.
  - [ ] 12.5.n **(High, carried from the FET choice) Bound the drain
        overshoot.** [49] is a 40 V part on a 25.2 V pack -- 1.59x, down from
        3.97x. Set the DRV8353S IDRIVE slew rate via SPI and bench-measure
        V_DS at the switching node before fab.
  - [ ] 12.5.o (Low) `tools/respin_30x70_schematic.py` is named for the
        70 mm target that became 60 mm. Rename or note it.
  - [~] 12.5.s **(electrical) VM HAD NO TOP-SIDE COPPER -- top-side half
        DONE 2026-08-16, via stitching still open.** The VM
        plane is on **In2.Cu only**, but every part carrying pack current is
        on **F.Cu**: J5A (pack +), C1 (bulk), and the three high-side drains
        Q1/Q3/Q5. KiCad reports **8 unconnected VM items** -- J5A to Q1, Q1 to
        Q3, Q3 to Q5, Q3 to C1, and the rest. Nothing joins them to each other
        or down to the plane. Top-side VM pads span x 2.20..22.81,
        y 4.60..13.05 mm, so a single **F.Cu VM pour of about 22.6 x 10.5 mm**
        reaches all of them; stitch it to In2 where there is room. Worst-case
        lateral run J5A -> far Q5 drain is ~20.6 mm; at 2 oz that is **5.2 W
        as a 3.0 mm router track vs 0.7 W as the full pour**. The band is
        already reserved for the pack input and the high-side drains, so the
        pour costs no area. **Do not let the autorouter close this.**
        **DONE:** `tools/add_vm_top_pour.py` poured 235.1 mm^2 of VM on F.Cu
        over y 0.60..15.50 at priority 2 (below the phase pours' 3, above the
        F.Cu GND pour's 0), pad connection FULL so no thermal spokes sit in
        series with a 50 A drain. J5A, C1 and all three high-side drains are
        now one piece of copper; 4 of the 8 VM connections closed. The other 4
        are bottom-side low-current taps (U5 supply, R8 sense divider, C6
        decoupling) and are ordinary routing.
        **STILL OPEN -- the pour alone is NOT the finished conductor.**
        Measured on the filled result, it necks to **2.39 mm of copper height
        at x = 17.3 mm**, pinched between J5B (the GND pack terminal,
        y 1.10..8.10) above and the PH_C pour (y >= 11.10) below. That neck is
        the sole F.Cu path to Q5's drain: ~2.2 mm long, ~0.9 squares,
        0.28 mOhm, **0.7 W concentrated in about 5 mm^2** -- a hot spot, not a
        margin. Fix is via stitching to the unobstructed In2 VM plane so the
        neck stops being the sole path. NOT done here because it needs two
        decisions: (a) via count/placement -- ~23 x 0.3 mm vias to match 2 oz,
        with free pour area either side of the neck, versus putting them in
        the drain lands; (b) **via-in-pad is a paid fab option** -- filled and
        capped costs extra, unfilled wicks paste and starves the joint. On
        flight hardware that is the repo owner's call. Also check any new via
        against U5's 12 GND thermal vias directly underneath -- that pair has
        already produced one verified GND-to-VM short on this board.
        REFERRED TO USER.
  - [ ] 12.5.t **(BLOCKING, electrical) THE PHASE GAP -- the phase nets do
        not reach their own terminals in copper.** Measured off the board
        2026-08-16: the PH_A/PH_B/PH_C pours are on **F.Cu** and end at
        y = 33.10 mm; their terminals J4A/J4B/J4C are on **B.Cu** starting at
        y = 48.10 mm. Each phase therefore has a **15 mm gap AND a layer
        change** between its pour and its terminal. The x-alignment is
        already correct -- each terminal sits under its own column.
        **This must not be handed to the autorouter.** `tools/autoroute.py`
        puts PH_* in a 3.0 mm "power" class, and at 2 oz a 3.0 mm track
        across this gap dissipates **11.4 W across the three phases -- more
        than all six FETs' conduction loss combined (10.5 W)**, in series
        with the pours' own 6.7 W. Run `docs/tools/conductor_sizing.py`,
        which now models this gap. Three closures, cheapest first:
        (1) **move J4A/B/C to F.Cu and extend each pour down to its terminal**
        -- zero vias, zero added dissipation, but J2 (x 6.0) and J3 (x 18.5)
        currently occupy that top-side band, so it is a PLACEMENT decision
        and the repo owner's call; (2) keep the terminals on B.Cu, add a B.Cu
        phase pour per column and stitch with **23 x 0.3 mm vias per phase**
        (69 total, 2.2 A each) in a region that must also clear U1/U2 and the
        resistor columns; (3) widen to full pour width on B.Cu without a
        matching via count -- easiest to draw, easiest to get wrong, because
        the via field then becomes the narrowest point. **Option 1
        recommended:** 2 and 3 both pay for a layer change the geometry does
        not require. REFERRED TO USER.
  - [~] 12.5.y **Front/back re-placement by the repo owner (2026-08-17).**
        Front now carries power (pack -> FETs -> phase terminals), back
        carries control and comms (U1/U2, U3/U4, J2/J3), comms and pack input
        at the same end. **This opened the F.Cu corridor U3/U4 used to block**
        -- the structural fix for 12.5.t. `tools/fix_after_replacement.py`
        applied the four mechanical consequences: swapped J4A<->J4C (they were
        crossed -- J4A sat at x 21.6 with its FETs at x 2.2-6.0, a 19.4 mm
        span with two 50 A nets having to cross; now 3.8 mm each), pulled 5
        footprints off the board edge, removed 400 stale FreeRouting items,
        and rebuilt the 3 phase pours + the F.Cu VM pour from the pads they
        actually have to reach. DRC 713 -> 63 violations; 0 shorts, 0
        clearance, 0 edge-clearance. Remaining: 43 silkscreen (12.5.u), 12
        drill (12.5.x), 8 starved_thermal on GND.
  - [ ] 12.5.z **(BLOCKING, electrical) The isolation keepout now sits on top
        of the phase terminals.** It is a 4-layer no-copper-pour rule area at
        x 0.85..24.65, y 50.60..59.30 -- placed when the isolated parts were
        at the bottom. They are now at y 0.19..22.77 on the back, so the
        keepout protects nothing and instead blocks the phase pours from
        their own terminals: PH_B is cut clean at y 50.60, and PH_A/PH_C only
        get past through a **0.30 mm strip** along the board edge (x 0.55..0.85
        and 24.65..24.95) that does not even reach the pads. All three phases
        still read 1 unconnected each. **The phase gap is NOT closed until
        this moves.**
        Moving it is not mechanical. The pack input is now at the top
        (y 1.10..8.62) and the FETs are in the middle (y 23.35..44.35), so VM
        has to traverse the band a relocated keepout would occupy. Barrier
        geometry measured 2026-08-17: U3 isolated pins x 1.98 / non-isolated
        x 11.28; U4 isolated x 14.45 / non-isolated x 23.75; both y
        10.38..21.82. A keepout as two narrow edge bands (rather than one
        full-width rectangle) would clear the middle for VM -- but that
        depends on 12.5.aa. REFERRED TO USER.
  - [x] 12.5.aa **J2/U3 isolation RESOLVED 2026-08-17** -- the repo owner
        rotated U3 by 180 deg, putting its isolated row at x 11.28 facing J2.
        The CAN runs are now **0.05 mm and 2.59 mm** (were 9.35 and 11.89).
        U4/J3 was already correct at 0.58/3.12 mm. Original finding kept
        below for the record.
  - [x] 12.5.aa-orig **(was BLOCKING) J2 was on the wrong side of U3 --
        the CAN channel's isolation is defeated.** Measured 2026-08-17:
        U3's isolated pins sit at x 1.98, but J2's pads are at x 11.33..13.87,
        on the far side of U3's own NON-isolated row (x 11.28). The isolated
        CAN conductors therefore run **9.35 mm and 11.89 mm in x**, straight
        across the U3 package and past its non-isolated pins. J3/U4 is fine by
        contrast (0.58 and 3.12 mm, directly adjacent to U4's isolated row).
        Fix is either mirroring U3 so its isolated row faces J2, or moving J2
        to the left edge beside U3's isolated pins. Which one is chosen sets
        the keepout shape in 12.5.z, so decide these two together.
        REFERRED TO USER.
  - [~] 12.5.ac **(electrical) ISOLATION CREEPAGE — board widened to 32 mm
        2026-08-19; the U1 half is CLOSED, the pack-versus-comms half is not.**
        `tools/widen_board_to_32mm.py` took the board **25.40 -> 32.00 mm**
        (length unchanged at 60.10). U1 is centred and U4 re-anchored to the
        new right edge. **U1's closest approach to an isolated conductor went
        4.27 mm -> 9.50 mm** (U3.11 <-> U1.48), clearing the 7.5 mm
        requirement with 2.0 mm spare.
        The power stage did not move and did not need to: SH1 is a Wurth
        WE-SHC 3670209 [51] with a fixed 22.2 mm land that must sit under the
        FETs, so the FET columns are capped at the shield width however wide
        the board gets. Every added millimetre went to the isolated section
        and U1 — which is what needed it.
        **STILL OPEN — the pack terminals and the isolated comms share the top
        end:**
            J2.1  <-> J5A.1   4.35 mm
            J3.2  <-> J5B.1   4.83 mm
            U3.20 <-> J5A.1   6.35 mm
        Widening cannot fix this: J5A spans x 1.10..8.10 and J5B x 17.60..24.60,
        overlapping in x with where both isolated groups must live, so they can
        only separate in Y. The options remain as recorded below — (a) pack
        terminals to the bottom beside the phase terminals, (b) isolated
        section to the bottom, (c) accept the added length. REFERRED TO USER.
        **Also outstanding from this move:** U1's new centred position overlaps
        J1 and several of the parked isolated capacitors (58 electrical DRC
        violations). Those parts were already outside [9]'s 10 mm lead-length
        limit and were always going to be re-placed — 12.5.af.
  - [x] 12.5.ac-orig **(was BLOCKING) the constraint set was over-determined
        at 25.4 mm width.** Repo owner's decision 2026-08-18: **do not weaken the
        isolation.** Reason recorded verbatim, because it should not be
        silently revisited — "the whole reason for isolation and an emi shield
        is that this board is designed to survive harsh emi environments,
        which is also why it has redundant control paths. so weakening its
        design isn't the correct course." The IEC 60664-1 route (deriving a
        smaller creepage from a lower system working voltage) is therefore
        CLOSED. 7.5 mm per [9] Table 6 stands.
        **Arithmetic established 2026-08-18, U1 half:** with U3/U4 rotated so
        both isolated rows face the board edges (x 1.98 and x 23.75), the
        7.5 mm exclusions leave only x 9.48..16.25 = 6.77 mm of legal
        non-isolated width, and U1 is 13.45 mm wide -- so U1 cannot sit
        beside the isolated section at any x and must clear it in y. Centred,
        U1's top must reach y >= 27.63 (binding pad U3.11 at (1.98, 21.32),
        dx 4.04), a 4.76 mm move down; SH1 cannot absorb it because it is
        locked under the FETs. Rounded to 4.80 mm, the board goes
        60.20 -> 65.00 mm. `tools/grow_board_for_creepage.py` implements this.
        **NOT APPLIED, because it does not finish the job.** Running it and
        re-measuring showed creepage still fails, now against the PACK
        TERMINALS rather than U1:
            J2.1  <-> J5A.1   4.35 mm
            J3.2  <-> J5B.1   4.83 mm
            U3.20 <-> J5A.1   6.35 mm
            U4.11 <-> J5B.1   6.36 mm
        The 50 A pack input and the isolated comms section both live at the
        top of the board, overlapping in x (J5A spans x 0.73..9.28; U3's
        isolated group must live at x ~2). They can only separate in y, and
        J5A's bottom edge at y 8.62 would push the isolated section down to
        y >= 16.12 -- about 7 mm, on top of U1's 4.8 mm. That is ~72 mm of
        board, past the original 70 mm target.
        **This is an architecture question, not a length question:** the pack
        input and the isolated section cannot share the top end. Options:
        (a) pack terminals move to the bottom beside the phase terminals --
        VM then runs the board length, ~1.9 W at 50 A across the In2 plane at
        full width, which is tolerable; (b) the isolated section moves to the
        bottom -- gives up the same-end wiring convenience that motivated the
        current arrangement; (c) accept ~72 mm of board length. REFERRED TO
        USER.
  - [x] 12.5.ac-orig **(was BLOCKING) creepage measured 3.49 mm against a
        7.5 mm requirement.** [9] Table 6 (verified 2026-08-17 in
        `docs/datasheets/analog-devices-adm2582e-adm2587e-datasheet.pdf` p.5)
        specifies **7.5 mm minimum external air gap (clearance) AND 7.5 mm
        creepage, measured input terminals to output terminals**, with
        footnote 2: "Consideration must be given to pad layout to ensure the
        minimum required distance for clearance is maintained." Measured on
        the 2026-08-17 placement, closest isolated-to-non-isolated pads on a
        shared layer, different parts:
          U4.11 (isolated) <-> U2.10  **3.49 mm**
          U4.11 (isolated) <-> U2.9     3.97 mm
          U4.11 (isolated) <-> U1.1     4.58 mm
        The board therefore undercuts the transceiver's own 5 kV rating --
        the barrier is only as good as its weakest external gap. U1 (MCU) and
        U2 (OPTIGA) need to move about 4 mm further from U4's isolated row,
        or the transceivers need to move. PLACEMENT CALL. REFERRED TO USER.
  - [x] 12.5.ad **DONE 2026-08-17 -- isolated-supply ferrites fitted, and
        they turned out to be fixing a BROKEN SUPPLY, not adding EMC polish.**
        Reading [9] p.8 and [10] p.15 pin tables showed the isolated side of
        both transceivers was simply unwired: `CAN_VISOOUT` reached only
        U3.19, `CAN_VISOIN_OPEN` only U3.16, `RS485_VISOOUT` only U4.12,
        `RS485_VISOIN_OPEN` only U4.19 -- all dangling. Both datasheets
        require VISOOUT to feed VISOIN ([10]: "Connect this pin through a
        ferrite bead and short the PCB trace to VISOIN **for operation**";
        [9]: "This pin must be connected externally to VISOIN"). It did not,
        so neither bus side had a supply at all. Both also had their isolated
        grounds MERGED where the datasheets require a ferrite split, and [9]'s
        pin-16 entry says outright "Ground, Bus Side. **Do not connect this
        pin to Pin 14 and Pin 11**" -- the pre-existing net merged exactly
        those pins.
        Fitted four Murata BLM15HD182SN1D [53] (1800 Ohm @100 MHz / 2700 Ohm
        @1 GHz, meeting [9] p.17's "approximately 2 kOhm between the 100 MHz
        and 1 GHz frequency range"; the part [10] Table 12 names by number for
        this role). `tools/add_isolated_supply_ferrites.py` (schematic) and
        `tools/add_ferrites_to_pcb.py` (PCB). Resulting topology:
          FB1  CAN_VISOOUT(U3.19)   -- CAN_VISOIN(U3.16)
          FB2  CAN_GNDISO(U3.18,20) -- CAN_ISO_GND(U3.11,12,15)
          FB3  RS485_VISOOUT(U4.12) -- RS485_VISOIN(U4.19)
          FB4  RS485_GNDISO(U4.11,14) -- RS485_ISO_GND(U4.16,20)
        **ERC 0 errors** (was 0, but `CAN_VISOOUT`/`RS485_VISOOUT` dangling
        warnings are now gone); **DRC 0 electrical violations.** Current
        rating checked, not assumed: [53] rates 200 mA / 2.2 Ohm max DCR, and
        the beads carry only isolated-side transceiver current -- [9] Table 14
        confirms the ADM2582E has "no current available externally on
        VISOOUT". Correction recorded: an earlier note in this file claimed
        the ADM3055E did not want ferrites. It does ([10] p.25, "filter both
        the VISOOUT power supply pin and GNDISO power supply return pin ...
        Use surface-mount ferrite beads in series"); what [10] says is NOT
        required is stitching capacitance and HV safety capacitors.
  - [~] 12.5.af **(placement, WITH THE REPO OWNER) The isolated section's
        twelve support parts are on the board and PARKED OFF-BOARD for hand
        placement** (2026-08-17, at the repo owner's request). All twelve now
        exist and are netted: FB1-FB4 [53] in a staging column at x = 32 mm,
        C11-C18 at x = 40 mm, both outside the 25.45 mm board outline.
        **ERC 0 errors, DRC 0 electrical violations.** Capacitor values and
        pin pairings are quoted, not chosen: [10] p.15 pin 19 "requires
        0.22uF and 10uF capacitors to GNDISO" and pin 16 "requires 0.01uF and
        0.1uF decoupling capacitors"; [9] p.17 "0.1 uF and 10 uF for VISOOUT
        at Pin 11 and Pin 12 ... 0.01 uF and 0.1 uF ... for VISOIN at Pin 19
        and Pin 20". Package (0805) and voltage rating are AGENTS.md Sec.4
        engineering defaults matching C2..C10; no MPN is claimed for the
        capacitors -- none has been selected.
        **When placing, the two isolated grounds are NOT interchangeable:**
        the VISOOUT reservoirs return to the dc-to-dc converter ground
        (CAN_GNDISO / RS485_GNDISO), the VISOIN decouplers to the bus-side
        ground (CAN_ISO_GND / RS485_ISO_GND), and the beads bridge the two.
        Constraints to honour: [10] p.15 "short the PCB trace to VISOIN";
        [9] p.17 "total lead length between both ends of the capacitor and
        the input power supply pin should not exceed 10 mm"; and [9]'s
        ordering "the C1 capacitor connects between VISOOUT (Pin 12) and GND2
        (Pin 11) on the device side of the L1 and L2 ferrites".
        Still needs room: U3's isolated pin row is at x 11.28 and U4's at
        x 14.45, 3.17 mm apart with a 0.55 mm channel between courtyards,
        J2/J3 above and U1/U2 below. The same move also fixes 12.5.ac
        (creepage 3.49 mm against 7.5 mm required).
  - [x] 12.5.af-orig **(was BLOCKING) The isolated section had no room for
        its own support components.** The four beads are on the board with
        correct nets but are PARKED at x 19.4..24.9, y 24.5..28.6 -- the only
        free back-side pocket -- 9.3 to 16.9 mm from the pins they serve,
        against [10] p.15's "short the PCB trace to VISOIN". There is nowhere
        closer: U3's isolated pin row is at x 11.28 and U4's at x 14.45,
        facing each other across 3.17 mm, with the two courtyards (U3 to
        12.59, U4 from 13.14) leaving a 0.55 mm channel. Everything else
        adjacent is J2/J3 above and U1/U2 below.
        Worse, the datasheets also require **eight capacitors** this board
        does not have: [10] wants 0.22 uF + 10 uF on VISOOUT to GNDISO and
        0.01 uF + 0.1 uF on VISOIN; [9] wants 10 uF + 0.1 uF on VISOOUT and
        0.1 uF + 0.01 uF between pins 19 and 20 -- and [9] fixes their
        position relative to the beads ("the C1 capacitor connects between
        VISOOUT (Pin 12) and GND2 (Pin 11) on the device side of the L1 and L2
        ferrites"). Twelve parts total need a channel along both isolated pin
        rows. This compounds 12.5.ac (creepage 3.49 mm vs 7.5 mm required),
        which also wants U1/U2 moved away from U4. Both are solved by the same
        move. REFERRED TO USER.
  - [x] 12.5.ad-orig **(was High, EMC) The ADM2582E's recommended L1/L2
        ferrites are absent from the design.** [9] "PCB Layout and Electromagnetic
        Interference (EMI)" (p.17) instructs: "filter both the GND2 pins
        (Pin 11 and Pin 14) and VISOOUT signals of the integrated dc-to-dc
        converter for high frequency currents. Use surface-mount ferrite
        beads in series with the signals before routing back to the device",
        impedance ~2 kOhm over 100 MHz-1 GHz, to suppress the 180 MHz
        primary and 360 MHz secondary switching harmonics; Figure 35 is the
        recommended layout. The board carries **no ferrites at all** --
        reference designators present are only J, U, R, Q, C, SH. This is a
        schematic/BOM gap, not a layout one, and it matters directly to the
        Faraday EMI tier. Note the ADM3055E (CAN, [10] p.25) states the
        opposite for itself: "Neither PCB stitching capacitance nor high
        voltage surface-mounted technology (SMT) safety capacitors are
        required" -- so this applies to the RS-485 part, U4.
  - [ ] 12.5.ae **(Medium) The isolation keepout is not datasheet-driven and
        should be replaced, not relocated.** The existing rule area is a
        full-width, 4-layer no-copper-pour rectangle. [9] p.17 asks for the
        **opposite** on a 4-layer board: "place an embedded stitching
        capacitor between GND1 and GND2 using internal layers of the PCB
        planes. An embedded PCB capacitor is created when two metal planes in
        a PCB overlap each other and are separated by dielectric material.
        This capacitor provides a return path for high frequency common-mode
        noise currents across the isolation gap." The **only** keepout [9]
        specifies is narrow and conditional: "there must not be a GND2 fill
        on any layer below the L1 and L2 ferrites" -- i.e. a keepout of the
        ISOLATED ground fill around ferrites this design does not yet have
        (12.5.ad). So the full-width cut removes the plane overlap AD wants,
        while the constraint that actually binds is creepage (12.5.ac).
        Two options, both needing sign-off:
        (a) delete the rule area and rely on creepage + the stitching-
            capacitor plane overlap, per [9];
        (b) keep a cut but shrink it to the U3/U4 package bodies between the
            pin rows, and drop F.Cu from its layer set -- F.Cu is the far
            face, 1.6 mm of FR4 from the B.Cu isolated pads, and it is the
            layer VM must cross to get from the top-end pack to the
            mid-board FETs.
        Either way the current rectangle must go: it sits at y 50.60..59.30,
        on top of the phase terminals, where it blocks all three phase pours
        (12.5.z) and protects nothing.
  - [ ] 12.5.ab **(High, electrical) Two constraints regressed in the
        re-placement.** Measured before -> after:
        **shunt to sense amp 1.2/2.6/2.6 mm -> 28.0/22.0/28.0 mm** (millivolt
        differential taps across a 0.5 mOhm shunt, now running the length of
        the board past three switching nodes -- the README constraint was
        "each sense amp under its own shunt"); and **C1 to high-side drain
        4.1/7.1/9.7 mm -> 17.6/23.6/24.0 mm**, the commutation loop the 40 V
        FET choice on a 25.2 V pack depends on. Per the README's own table a
        ~20 nH loop leaves only IDRIVE <= 300 mA under 40 V, and that lands at
        38.2 V -- under 5% margin. Gate loops also stretched to 3.8-13.9 mm
        (Q3 worst) from U5 sitting directly under the array. All three are
        placement calls. REFERRED TO USER.
  - [ ] 12.5.ag **(High, security) Permanent write/debug lock — use the MCU's
        internal capability, NOT a board-level fuse** (repo owner's decision,
        2026-08-18). The board keeps a plain 4-pad SWD probe pattern at J1
        (12.5.ah); **no fusible link, solder-bridge or series fuse is added**.
        Rationale: a board-level fusible link is re-bridgeable by anyone who
        can solder, so it provides tamper-evidence rather than a seal. The
        MSPM0G3507's own one-time configuration is the only irreversible
        option, and it costs no board area.
        **Verified locally from [1]** (`docs/datasheets/mspm0g3507.pdf`, read
        2026-08-18): §8.33 p.73 — "Access to the device memory and
        configuration through the BSL is protected by a 256-bit user-defined
        password, and it is possible to completely disable the BSL in the
        device configuration, if desired. The BSL is enabled by default from
        TI." §7 memory map — the NONMAIN configuration NVM sits at
        0x41C0.0000–0x41C0.0200 (512 bytes), separate from main flash, and is
        where boot/debug configuration lives.
        **NOT verified locally, and required before implementation:** the
        register-level debug-disable mechanism. [1] §8.32 p.73 defers it
        entirely — "For a complete description of the debug functionality
        offered on MSPM0 devices, see the debug chapter of the technical
        reference manual." That manual is [54] and **is not in
        `docs/datasheets/`**. Obtain it, then specify: which NONMAIN field
        sets the debug policy, whether the permanent state is genuinely
        one-way, the interaction with the 256-bit BSL password, and the
        production sequence (program → verify → seal), since sealing before a
        verified image is unrecoverable.
        Note the ordering constraint against 12.5.b/12.5.q: the lock must be
        the LAST production step, after the IDRIVE bench measurement and any
        firmware trim, or the board is bricked for tuning.
  - [x] 12.5.ah **J1 shrunk to a 1.27 mm probe pattern** (2026-08-17),
        `SolderPad_1x04_SMD_P1.27mm_Probe`: 9.22 x 3.20 mm / 36.0 mm^2 ->
        4.71 x 1.80 mm / 12.0 mm^2. J1 is SWD only (SWDIO/SWCLK to U1.12/13
        plus 3V3 and GND) and is a bring-up interface, not a flight
        connection, so it does not need J2/J3's wire-solder pad area. 1.27 mm
        is the standard pogo-jig pitch; single-row keeps the fixture trivial.
        Rejected: Tag-Connect TC2030 — its three through-board alignment holes
        cost their area on both sides, a net loss here. J2/J3 keep the 2.54 mm
        wire variant (12.5.k).
  - [x] 12.5.ai **50 A RATING VALIDATED against the load it actually drives**
        (2026-08-18). The airframe this build feeds — Serenity-UAV — turns
        four XFly Galaxy X5 50 mm 12-blade 6S EDFs, two per nacelle, each
        with its own ESC. Manufacturer figures [55]: **38 A draw, 843 W,
        1240 g thrust, recommended ESC 50 A**, with the note "The controller
        should be chosen 20% over rated due to the long lasting load."
        38 A x 1.20 = 45.6 A, so **50 A is the manufacturer's own answer and
        this build matches it at 1.32x the draw.** 843 W / 22.2 V = 38.0 A
        confirms the figures are self-consistent. Four fans draw 152 A / 3372 W
        from the pack in total.
        This closes a spread that looked alarming: the Serenity archive
        `docs-superseded/POWER_SYSTEM_Q.md` carries 55 A peak (L241) and
        84 A peak / 55 A continuous (L248) for these fans, recommending 60 A
        and 120 A ESCs. Those are superseded and do not match the fan's own
        published 38 A. Every figure sized in this repo against 50 A — the
        TPHR8504PL choice, the 0.5 mOhm shunts, the 7.5 mm phase pours, the
        2 oz copper floor — stands.
  - [ ] 12.5.aj **(Medium, cross-repo) Serenity-UAV's own ESC line is
        under-spec and still names a different part.** `airframe/README.md`
        L57 and `TODO.md` L546 specify **40 A BLHeli32** ESCs for these fans.
        Against [55] that is 40/38 = **1.05x the draw**, well under the
        manufacturer's own 20% margin rule, where this build's 50 A gives
        1.32x. Two further notes for that repo, found while checking:
        (a) the BOM specifies **BLHeli32**, whose control path is DShot —
        replacing those units with Open-Secure-ESC moves command onto CAN-FD
        or RS-485, and DShot is not on this project's protocol axis at all;
        (b) `airframe/README.md` L57 budgets "battery + PDB + ESCs" at ~500 g
        while its own §4.3 puts the two batteries alone at 1,180 g;
        (c) [55] gives the EDF unit mass as **75 g**, not the 70 g in
        `bom_revS.json` — 4 x 75 = 300 g, not 280 g, which bears on the
        EDF-mass discrepancy already open in that repo's
        `SPEC_VERIFICATION_0.6.1.md`. Raise upstream; not actionable here.
  - [ ] 12.5.u **(Medium) Silkscreen cleanup, deferred by the repo owner
        until after routing** ("silkscreen can wait till after routing",
        2026-08-16). Routing has now run, so this is unblocked. Outstanding:
        32 `silk_over_copper`, 21 `silk_overlap`, 2 `silk_edge_clearance`.
        None electrical; all block a clean fab package.
  - [ ] 12.5.w **(Medium) Finish routing.** FreeRouting (2.2.4, 100 passes,
        15 min 26 s) took the board 124 -> 56 unrouted, 381 segments, 48 vias.
        After stripping its 29 VM tracks (12.5.s) and adding the VM pour, the
        board stands at **352 segments, 48 vias, 57 open**. Of those: 3 phase
        nets to terminals (BLOCKED on 12.5.t), 3 phase-to-U5 sense, 4 VM
        bottom-side taps, 9 GND stitches, 38 ordinary signal nets. Re-run with
        more passes or finish by hand -- but re-run
        `tools/strip_high_current_tracks.py` afterwards every time.
  - [ ] 12.5.x **(High, fab) U5's 12 thermal vias are 0.20 mm drill and DO
        violate this project's own rule.** `open_secure_esc_6s_50a_can485_faraday.kicad_pro`
        sets `min_through_hole_diameter = 0.3`, and kicad-cli reports 12 x
        `drill_out_of_range` against it. **Correction:** an earlier note in
        this file claimed the opposite, on the strength of the board file's
        cached `m_MinThroughDrill` (0.2 mm). The project file is what
        kicad-cli enforces, and it is authoritative. Three fixes: enlarge the
        vias to 0.3 mm, delete them ([21] RTA0040B note 5 makes them
        optional), or lower the project rule to 0.2 mm and confirm the fab
        supports it (0.3 mm is standard at many vendors; 0.2 mm is an
        upcharge or a redesign at some).
  - [ ] 12.5.v **(Low) 5 `starved_thermal` and 2 `isolated_copper` DRC
        warnings** at the 25.4 mm placement. Fab-preference and pour-shape
        respectively; confirm each is intentional before generating gerbers.

- [x] 12.6 **Decision matrix gained its two missing axes** (2026-08-16).
      `docs/decision-matrix.xlsx` now carries **Motor** (brushed vs brushless)
      and **Shaft Sensor** (sensorless / Hall / quadrature / resolver) sheets,
      added by `docs/tools/add_motor_and_shaft_sensor_sheets.py`. The whole
      workbook exports to `docs/decision-matrix.json` via
      `docs/tools/decision_matrix_to_json.py` (`--check` fails when the JSON
      goes stale against the workbook hash), so a build can be walked
      programmatically. Cells with no sourced part read `TBD -- requires
      primary-source verification` and their rows are `Open / unresolved`:
      the brushed-DC gate driver, all three sensored shaft-sensor options,
      and SBus/DBus. `unresolved_cells()` exists so a build script refuses
      them rather than emitting a BOM line.
  - [ ] 12.6.a Source an H-bridge gate driver for the brushed row, or vet
        the noted option of using two of a 3-phase driver's three
        half-bridges.
  - [ ] 12.6.b Source a resolver-to-digital converter for the resolver row.
  - [ ] 12.6.c Verify a Hall-sensor part (TI DRV5013 is carried from the
        Control sheet as a candidate only).

## 13. MCU Swap — S32K144 → MSPM0G3518-Q1 (PARTIALLY APPLIED)

> **Status corrected 2026-08-15.** This section was headed "NOT STARTED",
> but the swap is already in the design: `symbols/MSPM0G3518_Q1_PM.kicad_sym`
> and `symbols/specs/MSPM0G3518_Q1_PM.json` exist, `kicad/sym-lib-table`
> records the MSPM0G3518 as "Project MCU as of 2026-08-10; supersedes
> S32K144", and U1 in the build schematic **is** the MSPM0G3518-Q1. So
> 13.1.c, 13.1.d and 13.1.g below are done — the pin numbers are VERIFIED,
> not placeholders, and `SE_I2C_SCL`/`SE_I2C_SDA`/`SE_RST` survived the swap
> (the OPTIGA is still connected). 13.1.b is also closed: `C_VCORE` is
> **470 nF ±20 %**, read from [44]'s Recommended Operating Conditions and
> confirmed by its "A 0.47 µF tank capacitor is required for the VCORE pin",
> and C3 on the sheet is 470 nF.
>
> What remains open is the part that matters most: **the security
> documentation still describes the S32K144's CSEc.** 13.1.e and 13.1.h below
> are untouched, and `builds/6s/50A/CAN_485_faraday/README.md` carries an
> as-built correction note pointing here. Do not treat any CSEc statement in
> the design docs as describing this build until 13.1.e is closed.

- [ ] 13.1 **Replace the NXP S32K144 with the TI MSPM0G3518-Q1**, package PM
      (LQFP-64), orderable `M0G3518QPMRQ1` [44]. Decided 2026-08-10: the
      S32K144's CSEc is SHE-compliant and therefore **AES-128 only**, which
      capped the authenticated hot path; the MSPM0G351x provides an
      **AES-128/256 accelerator with GCM/CMAC** and a 4-key secure keystore
      ([44] p.1; crypto architecture in [40]). This retires finding C-01 in
      `docs/secure-element-architecture.md`.
      **Full plan, verified facts, and constraints:**
      `docs/HANDOFF-mcu-swap-s32k144-to-mspm0g3518.md`. Start there.
  - [ ] 13.1.a **(Hazard — read before editing the schematic.)** `VCORE` is
        NOT the equivalent of the S32K144's `VDDA`. `VDDA` is an analog supply
        input tied to 3V3; `VCORE` is a regulator **output**, and [44] p.52
        states "The VCORE pin must only be connected to C_VCORE. Do not supply
        any voltage or apply any external load to the VCORE pin." A
        slot-for-slot swap would tie VCORE to 3V3 and violate the datasheet.
        **Decided 2026-08-10: drop VDDA's rail connection and give VCORE its
        own dedicated capacitor to VSS, with nothing else on that net.**
  - [ ] 13.1.b `UNVERIFIED — needs primary source` : the C_VCORE capacitance
        value. It is in the [44] p.51 Recommended Operating Conditions table,
        whose columns do not survive `pdftotext`. Do not guess it. The ±20%
        tolerance requirement IS verified and belongs on the BOM line.
  - [ ] 13.1.c Author `symbols/specs/MSPM0G3518_Q1_PM.json` + `.kicad_sym`,
        mirroring the S32K144's functional signal-role names so the existing
        schematic wiring survives. Do not reuse
        `symbols/MSPM0G3518_Q1_RHB.kicad_sym` — that is the VQFN-32 package.
  - [ ] 13.1.d Pin numbers will again be an `UNVERIFIED PLACEHOLDER PIN MAP`
        unless [44]'s Table 6-2 can be read. **Try `pdfdetach -list` on
        `docs/datasheets/mspm0g3518-q1.pdf` first** — that trick is what
        unblocked the S32K144 map (see 1.11(a)) and may avoid the caveat.
  - [ ] 13.1.e Rewrite `docs/secure-element-architecture.md`: C-01 becomes
        RESOLVED, C-05 (CSEc/HSRUN exclusion) no longer applies, and every
        "CSEc" reference needs revisiting. **The Trust M's justification does
        NOT change** — the MSPM0's AES engine is still symmetric, so the
        asymmetric layer is still required.
  - [ ] 13.1.f Check the keystore reduction: MSPM0 holds **4** AES keys
        ([44] p.1) against CSEc's 17 ([31] Table 36-75). Confirm that suits the
        intended key hierarchy before closing 13.1.
  - [ ] 13.1.g Preserve `SE_I2C_SCL` / `SE_I2C_SDA` / `SE_RST` on the new
        symbol, or the OPTIGA Trust M silently disconnects.
  - [ ] 13.1.h Update `docs/security-mcu-comparison.md` — its S32K144-vs-
        alternatives argument is the document this decision overturns.

---

## 14. Repo-Resident ESC Build Skill (planned — not yet started)

**Goal.** One invocable skill that walks an agent from a chosen point on the
decision matrix to a fabrication-ready build, grounded in artifacts this repo
already holds rather than prose re-derived each session. The matrix admits
5 × 7 × 2 × 4 × 11 × 3 × 4 = **36,960 combinations**, so the skill must be
parameterised; enumerating builds is not an option.

**Why now.** `builds/6s/50A/CAN_485_faraday` was taken from netless PCB to
placed, poured and part-routed across many sessions. Roughly two thirds of
that effort was rediscovery — traps, calculations and datasheet topology that
are now written down but are not yet *reachable* from a cold start. The
grounding already exists and is the whole point of the skill:

| Artifact | Count | What it grounds |
| --- | --- | --- |
| `docs/solutions/` | 2 docs | traps and decisions already paid for |
| `docs/tools/*.py` | 4 calculations | conductor sizing, isolation envelope, matrix export, sheet authoring |
| `symbols/specs/*.json` | 17 | citable pin maps, source of truth for symbols |
| `REFERENCES.md` | 55 entries | every value that may be asserted |
| `docs/decision-matrix.json` | 7 axes | the parameter space itself |
| `builds/…/kicad/tools/*.py` | 24 scripts | the build steps, currently build-local |

- [ ] 14.1 **Separate the generic build scripts from the build-specific ones.**
      The 24 scripts under `builds/6s/50A/CAN_485_faraday/kicad/tools/` are the
      raw material. Triage each into: **generic** (works for any build given
      parameters — `autoroute.py`, `set_netclasses.py`, `check_shorts.py`,
      `strip_high_current_tracks.py`, `snap_to_grid.py`, `trace_nets.py`),
      **generic-after-parameterisation** (`build_pcb.py`,
      `finish_annotate_and_footprints.py`, `add_power_connectors.py`,
      `add_vm_top_pour.py`, `fix_after_replacement.py`), and **one-off**
      (`swap_s32k144_for_mspm0g3518.py`, `respin_30x70_schematic.py`,
      `inject_optiga_secure_element.py` — history, not tooling). Promote the
      first two classes to `tools/` at repo root; leave the one-offs where they
      are. **Verification:** every promoted script runs against the existing
      build and produces byte-identical output apart from UUIDs.
- [ ] 14.2 **Give the skill a machine-readable build descriptor.** One JSON
      per build — the seven axis choices plus envelope (width, length, layer
      count, copper weight) and the mount constraint. `decision_matrix_to_json.py`
      already exports the axes; this is the per-build selection against them.
      The descriptor is what every promoted script takes instead of module-level
      constants. **Verification:** a descriptor reconstructed from
      `builds/6s/50A/CAN_485_faraday` reproduces its current net classes,
      keepout and pour geometry.
- [ ] 14.3 **Make the pre-placement calculations gate the build, not follow
      it.** `docs/tools/isolation_envelope.py` and `conductor_sizing.py` must
      run from the descriptor *before* placement and their results recorded in
      the build README — that is the specific failure this whole exercise came
      from (§12.5.ac). Add the missing third calculation: **component stack
      height against the mount envelope**, which the nacelle annulus
      (4.00–11.65 mm radial, 185.2 mm long) made binding on this build and
      which nothing currently checks. **Verification:** running the gate
      against the 25.4 mm envelope reports the creepage failure that cost this
      build several re-placements.
- [ ] 14.4 **Encode the datasheet-derived support topology as data, not
      prose.** Each isolator, gate driver and sense amp brings required support
      components with datasheet-fixed values, pin pairings and ordering — the
      ADM2582E/ADM3055E ferrite-and-reservoir topology (§12.5.ad) is the worked
      example, and it existed only because the pin tables were read line by
      line. Extend `symbols/specs/<PART>.json` with a `support_topology` block
      carrying required parts, values, which pins they bridge, and the
      REFERENCES tag and section each came from. **Verification:** generating
      U3/U4's support network from the spec reproduces FB1–FB4 and C11–C18 with
      their current nets exactly.
- [ ] 14.5 **Author the skill itself.** `SKILL.md` at repo root under the
      project's skill convention, whose body is mostly *pointers*: read the
      descriptor, run the §14.3 gates, consult `docs/solutions/` by
      `applies_when`, generate from `symbols/specs/`, cite from
      `REFERENCES.md`, then run the promoted scripts in order. It must assert
      no electrical value of its own — every number comes from a cited
      artifact, per `AGENTS.md` §1.3. **Verification:** a cold agent given only
      the skill and a descriptor reaches ERC-clean on a new build without
      re-deriving anything already in the repo.
- [ ] 14.6 **Capture the remaining learnings first — the skill is only as good
      as what it points at.** Three are known and uncaptured; each is a
      separate `ce-compound` run: (a) **datasheet-derived support topology** —
      reading a pin table found an isolated supply that was never wired and
      grounds merged in the way the datasheet explicitly forbids; (b) **KiCad
      scripting traps** — threshold-on-an-exact-edge (a part failed its own
      test at 22879999 nm vs 22880000 nm), courtyard-vs-bounding-box,
      through-hole parts blocking both sides, zones stretching instead of
      translating; (c) **rating validation against the actual load** — the
      manufacturer's own page resolved a 40/50/55/84/120 A spread in minutes
      (§12.5.ai). This item gates 14.5, not 14.1–14.4.
- [ ] 14.7 **(Low) Re-point the existing workflow doc.**
      `docs/solutions/architecture-patterns/esc-build-instantiation-workflow.md`
      treats placement as the starting point; it should defer to the §14.3
      gates first. Candidate for `ce-compound-refresh`.

**Sequencing.** 14.6 → 14.1 → 14.2 → 14.3 → 14.4 → 14.5, with 14.7 any time.
14.1–14.4 are independent of each other once 14.2's descriptor shape is fixed.

**Scope boundary.** The skill builds *supported* matrix options only. New axis
options (a protocol the repo has never carried, an amperage tier with no
verified FET) remain manual work that ends in a new `REFERENCES.md` entry —
the skill must refuse rather than extrapolate, per `AGENTS.md` §1.3.

**Deferred.** Firmware generation, gerber/CPL emission, and BOM sourcing are
out of scope; the skill stops at a DRC-clean routed board.
