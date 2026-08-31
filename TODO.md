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
        **Cross-reference added 2026-08-20:** 12.5.ba now carries the
        conductor/via arithmetic and the corroborated secondary sources
        ([S-A]-[S-F] in `REFERENCES.md`); 12.5.bb adds the altitude question.
        This item remains the one that closes when a primary standard is in
        hand. **IPC-2152 is the document to buy.**
        IPC-2152 [46].** No conductor width in this build is a computed value.
        VM and GND are poured planes so they do not depend on track width, but
        the three PHASE nets reach the motor connector partly as routed
        track, and that IS load-bearing at 50 A. [46] is paywalled: only its
        Table of Contents has been read, so per `AGENTS.md` §1.3 nothing may
        be derived from it yet. Buy the standard, then size the phase copper,
        the plane cross-sections, the vias and the connector pads, and choose
        the copper weight to match.
  - [ ] 12.4.l **(High, blocks fab) Select real power connectors.** J4
        **Partly stale as written, verified 2026-08-20:** J4A/B/C are now
        `SolderWirePad_1x01_SMD_5x10mm` and J5A/B are
        `SolderWire-6sqmm_1x01_D3.5mm_OD7mm` converted to SMD, so the
        footprints have moved on. **The substance stands: no connector has
        been selected and no current rating verified.**
        (phases) and J5 (pack) are currently KiCad 6 mm^2 (~10 AWG) solder-wire
        pads — the largest in the stock library, chosen because the previous
        J4 was a 2.54 mm pin header, which is not a 50 A part. No connector
        has actually been selected and no current rating verified. Depends on
        12.4.k.
  - [ ] 12.4.m **(Medium) Set the isolation barrier width from the chosen
        **DUPLICATE of 12.5.ae (2026-08-20) — track it there.**
        transceiver variant.** The keepout band is sized to clear the isolated
        pin rows, not to any creepage/clearance table. The real figure follows
        from the still-open ADM3055E-vs-ADM3057E (5000 vs 3750 V rms) and
        ADM2582E-vs-ADM2587E choices in this build's README.
  - [ ] 12.4.n **(Medium) Confirm the DRV8353S exposed pad may be tied to
        **Verified 2026-08-20: the board does tie it to GND** (`U5` pad 41 net
        = GND). The open question is the datasheet confirmation, not the
        implementation.
        GND.** [21] requires the pad to be soldered (RTA0040B note 3) and
        requires a ground-plane connection at the GND pin (§11.1), but does
        not state that the pad is internally common with GND. Currently an
        engineering default per `AGENTS.md` §4.
  - [x] 12.4.o **SUPERSEDED 2026-08-20 — the part it asks about is not on
        the board.** This concerned the WE-SHC **3670375** locating holes. The
        shield was swapped to **3670209** in 12.5.c; verified on the board
        2026-08-20, `SH1` is `Wurth_WE-SHC_3670209_Frame_15.3x20.9mm`, 8 pads.
        If the 3670209's locating features need the same plating decision,
        raise it against [51]/[52] as a new item, not this one.
  - [ ] 12.4.p **(Medium) Model the MCU's remaining 36 package pins.**
        **Verified 2026-08-20: still exactly true** — `symbols/specs/
        MSPM0G3518_Q1_PM.json` maps 28 pins and U1 has 28 of 64 pads on a real
        net.
        `symbols/specs/MSPM0G3518_Q1_PM.json` maps 28 of the LQFP-64's 64
        pins, so 36 pads import with no net. Fine electrically (unused GPIO),
        but the symbol does not describe the package.
  - [x] 12.4.q **SUPERSEDED 2026-08-20 — `build_pcb.py`'s placement table
        has not been the board's placement since 2026-08-16.** The repo owner
        hand-placed it (12.5.f); it has since been widened (12.5.ac), aligned
        (12.5.ap), symmetrised (12.5.aq), had U7/U8 re-assigned (12.5.ar),
        U1/U5/SH1 centred (12.5.as), and seven passives moved out of the
        shield ring (12.5.ay). The remaining placement questions are tracked
        specifically in 12.5.z, 12.5.ax and 12.5.ay rather than as one
        open-ended item. **The thermal/EMI human review this item asks for is
        real and still outstanding** — carried to 12.4.k and 12.5.bb.
  - [ ] 12.4.r **(Low) 347 `endpoint_off_grid` ERC warnings.** `genlib.py`
        **Count corrected 2026-08-20: 463, not 347** — it grew with the
        isolated-supply and J1 schematic work. 7 `global_label_dangling` also
        remain; 470 ERC violations total, 0 errors. The analysis below is
        unchanged and still correct.
        lays the sheet out on a 10 mm grid, which is not a multiple of KiCad's
        1.27 mm connection grid. **Do not "fix" this with a coordinate
        snap** — it was tried and reverted: the generator separates parallel
        routes by 0.01-0.02 mm lane offsets, and snapping merges them
        (VM shorted to GND, all six PWM lines merged, CPH shorted to CPL;
        73 nets collapsed to 63). See `tools/snap_to_grid.py`, which now
        refuses to write without `--force`. A real fix means re-laying out
        the drawing with >= 1.27 mm lane spacing.
  - [x] 12.4.s **SUPERSEDED 2026-08-20 — the counts are from a board three
        respins ago.** Measured on the current board: **11 `silk_over_copper`,
        7 `silk_overlap`, 2 `isolated_copper`, 0 `starved_thermal`** — 20 DRC
        violations, all cosmetic; zero shorts, clearance or isolation.
        Silkscreen carries forward as 12.5.u, the `isolated_copper` as
        12.5.at.
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
        **2026-08-20: superseded in practice by 12.5.av (the routing pass) and
        blocked by 12.5.bf.** Kept as the parent goal; do not work it directly.
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
        **Status 2026-08-20 — partly addressed, not closed.** The phase pours
        now extend to y 85.50 and reach J4A/B/C (`tools/fix_phase_pours.py`,
        12.5.av(g)). **Connectivity is unproven** because the board is
        unrouted, and 12.5.av recorded the pours fragmenting into 3-4 islands
        each once routing ran. Re-verify with the `kicad` skill's
        `connectivity_graph` after the next successful route.
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
  - [x] 12.5.ak **Two isolation placement rules encoded as harness checks**
        (2026-08-19, repo owner's direction: "commit these details to the
        harness for all future boards"). Both now pass/fail in
        `tools/score_placement.py`, and written up in
        `docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md`
        because the harness is build-local and the doc is what reaches a
        future board:
        (a) **an isolating IC's pin rows must run ACROSS the board's long
        axis**, so its isolated side faces a short edge. Isolated copper near
        a long edge poisons that edge for the board's whole length on both
        faces; rotating the transceivers 90 deg moved the nearest isolated
        copper from 0.72-0.82 mm off the side edges to ~2.94 mm and relaxed
        the required opposite-inset from 5.08 mm to 2.96 mm.
        (b) **pack terminals must not share a copper layer with the isolated
        section.** A through-hole terminal spans every layer and always makes
        an in-plane creepage pair; SMD on the opposite face leaves only the
        longer around-edge path -- worth 2.80 -> 4.64 mm on its own.
        Both regression-tested by deliberate violation: (a) reports
        "PARALLEL, rotate 90" per IC, (b) names the offending refs. Neither is
        scored -- a violation is an arrangement that cannot be nudged into
        compliance.
  - [x] 12.5.al **CORRECTED AND RESOLVED — creepage is 7.83 mm with 0.33 mm
        of margin. The "ceiling" was a bug in the harness, not the board.**
        The original entry claimed 7.51 mm was structural and could only be
        improved by widening the board. That rested on `edge_path()` computing
        `insetA + thickness + insetB`, which assumes two opposite-face parts
        sit at the same position ALONG the edge. They rarely do. U3 against Q2
        are ~26 mm apart in y, so the true unfolded path is 27.15 mm, not the
        7.83 mm being reported. Corrected to
        `sqrt(along_edge_sep^2 + (insetA + T + insetB)^2)`.
        With that fixed the FETs stop being binders at all — every
        around-edge pair sits at 7.98 mm or better — and the only real
        constraint is the in-plane U3.20 <-> U4.10 pair, which spreading the
        two transceiver groups relieves. The size of the safe step was itself
        overstated on the first pass and is corrected here:

        | spread   | creepage | DRC-el | unconnected |
        |----------|----------|--------|-------------|
        | +/-0.00  | 7.51     | 0      | 159 (base)  |
        | +/-0.25  | 7.66     | 0      | 159         |
        | +/-0.50  | 7.83     | 0      | 159 APPLIED |
        | +/-0.75  | 7.98     | 0      | 160         |
        | +/-1.00  | 7.98     | 0      | 161         |

        **+/-0.5 mm is the largest spread that costs nothing**: creepage
        7.51 -> 7.83 mm, isolated lead unchanged at 9.76 mm, no new broken
        nets. +/-0.75 and +/-1.0 buy a further 0.15 mm by SEVERING GND
        connections — refilling the pour around the moved parts fragments the
        B.Cu GND pour, and two of the casualties are on U5, which never moved.
        Revisit that extra 0.15 mm only with deliberate GND stitching.
        **Three claims in the original entry were wrong and are withdrawn:**
        that the FET columns must stay within SH1's 22.20 mm land (they
        already overhang it — Q1/Q2 by 0.75 mm, Q5/Q6 by 2.75 mm, with 5.30
        and 6.30 mm of inter-column slack); that more board width was the only
        lever; and that +/-1.0 mm was clean, which held only because the
        harness was not counting broken connections. None survived checking.
  - [x] 12.5.am **WITHDRAWN — the claim was false and the board is fine.**
        This item asserted that none of the 59 footprints carried a courtyard
        and that every courtyard-clean DRC result was therefore vacuous. Both
        halves were wrong, and the cause was a one-line bug in the check, not
        anything on the board.
        The check tested `"CrtYd" in board.GetLayerName(layer)`. In KiCad 9
        `GetLayerName()` returns the **display** name, which is
        `"F.Courtyard"` / `"B.Courtyard"` — the canonical `F.CrtYd` string
        never appears in it, so the test could not match and reported 0 of 59.
        Verified three ways 2026-08-19: comparing `GetLayer()` against the
        `pcbnew.F_CrtYd`/`B_CrtYd` layer IDs gives **59 of 59**; the raw
        `.kicad_pcb` contains 306 `CrtYd` lines; and all 16 distinct source
        footprints (11 KiCad system, 5 `Open_Secure_ESC.pretty`) carry
        courtyards.
        The DRC rules are live, not suppressed: `.kicad_pro` sets
        `courtyards_overlap` = **error** and `malformed_courtyard` = **error**,
        and both report zero. (`missing_courtyard`, `pth_inside_courtyard` and
        `npth_inside_courtyard` are set to `ignore`, which is worth a
        deliberate decision but is not what this item claimed.)
        Lesson for future checks: compare layers by **ID**, never by
        substring of a display name. `tools/restore_courtyards.py` was written
        against this false premise and has been deleted.
  - [~] 12.5.an **PARTLY RESOLVED, and one claim in the original corrected.**
        The board has exactly one *authored* rule area — board-local
        x 0.85..31.25, y 56.60..65.30, all four copper layers — prohibiting
        `copperpour` only. It does clip the phase pours: PH_A/B/C fills stop
        at y 56.60 while the J4A/B/C pads span y 55.60..65.60, so pour meets
        pad over 1.00 mm of a 10 mm pad, and a 0.3 mm strip of each phase
        fills separately past y 65.30.
        **Correction:** the original entry called those strips "stranded" and
        blamed them for the 2 `isolated_copper` warnings. Wrong on both
        counts — each strip is connected through its own J4 terminal pad, and
        DRC never flagged them. The real isolated fill was a **4.313 mm² VM
        pocket on In2.Cu** inside U5's thermal-via ring, fenced off by the
        via clearance cutouts on three sides and the VM zone's own y = 40.60
        lower boundary on the fourth, with nothing on net VM inside it —
        a floating plate under a switching gate driver.
        `tools/remove_vm_island.py` excludes it with a scoped In2.Cu rule
        area. The zone's `island_removal_mode` was already `ALWAYS` and did
        not remove it; a clean reload-fill-save cycle reproduced it, so this
        was not the stale-fill trap. `isolated_copper` 2 -> 1.
        **Still open:** confirm the authored rule area over the phase
        terminals is intended, and identify the last remaining
        `isolated_copper` (1, warning).
  - [x] 12.5.ao **DONE 2026-08-19 — 11 starved GND thermals given solid zone
        connections.** `.kicad_pro` sets `min_resolved_spokes = 2`; these pads
        each resolved one, hanging off the GND pour by a single 0.5 mm neck.
        `tools/fix_starved_thermals.py` set them solid. A spoke cannot be
        conjured where the pour does not reach, so widening spokes or
        shrinking the thermal gap would not have helped.
        It is also the better design here rather than merely the expedient
        one: this board carries galvanic isolation, redundant control paths
        and a Faraday shield specifically to survive harsh EMI, and shield
        effectiveness is set by the impedance of the ground bond — SH1 bonded
        through one narrow spoke is mostly inductance. Same repo precedent as
        `add_vm_top_pour.py`.
        **DECIDED 2026-08-19 — repo owner specified professional reflow
        assembly, so all 16 pads KEEP their solid
        connections and `--skip-passives` is NOT to be used on this build.**
        A controlled reflow profile handles a solid 0805 GND bond; the relief
        was only ever worth it to protect hand-soldering and rework. The
        original trade is kept below for the record.
        **Assembly trade, as it stood before that decision:** solid pads sink heat during
        reflow. The 9 IC/shield pads (SH1 x4, U5.25, U6.1/.2, U8.1/.2) are
        low risk. The 5 two-terminal 0805 passives (**C7 C9 C10 R5 R10**) are
        the tombstoning-asymmetry case — 0805 is far more forgiving than
        0402/0201, but if this board is to be hand-soldered or reworked, run
        `tools/fix_starved_thermals.py --skip-passives` to leave those five
        on thermal relief and accept their 5 warnings.
        C7 only appeared on the second pass: solid-bonding the first ten
        changed the pour around it enough to drop it from two spokes to one.
        Zone fills are coupled, so this class of fix is iterated to a fixed
        point. `starved_thermal` 11 -> 0.
  - [x] 12.5.as **DONE 2026-08-19 — U1, U5 and SH1 centred by the repo owner;
        two follow-on defects found and fixed.** The owner moved U1 and U5
        with their surrounding components +1.000 mm in x, putting U1, U5 and
        SH1 all exactly on the centreline (x = 16.000). This is the move
        `symmetrize.py` had REFUSED (DRC electrical 1 and 28) — the guard was
        right about the tool's version, which moved the ICs *alone*; moving
        each IC together with its supporting parts is a different move and it
        passes cleanly.
        As saved it showed 155 errors, **all of them stale zone fill**. After
        a refill: 0 errors. (Same lesson as the J5B move — a GUI part move
        leaves the fill stale; refill before judging.)
        **Real cost, accepted by the owner:** the worst gate loop grew
        16.53 -> 17.36 mm, because centring the driver moves it away from
        phase A. Measured per-phase driver-pad-to-gate-pad distance is now
        Q1 12.17 / Q2 13.73 / Q3 6.85 / Q4 5.89 / Q5 14.30 / Q6 14.86 mm —
        note centring did **not** balance A against C (they still differ by
        ~1.5 mm), because U5's gate pads are not symmetric on the package.
        Worth revisiting if switching performance on phase C matters.
        **Follow-on 1 — `remove_vm_island.py` had a stale hardcoded box.**
        It carried the island extent as a literal rectangle measured once.
        When U5 moved, the via ring went with it and the rule area did not,
        letting a 1.117 mm² sliver of VM plane escape through exactly the
        millimetre no longer covered. Now DERIVED from U5.41's actual via
        positions every run, so it follows U5 anywhere. *A constant that
        describes another object's position goes stale the moment that object
        moves.*
        **Follow-on 2 — `tools/close_edge_orphans.py` (new).** The authored
        phase-terminal rule area stopped at y 85.20 while the board outline
        runs to 86.05. Pour refilled that 0.85 mm gap and, cut off from
        everything above by the rule area itself, formed orphan strips along
        the bottom edge on every layer — including 8.747 mm² of GND on In2.Cu
        running the full board width, a floating conductor on a board built to
        survive harsh EMI. Rule area extended 0.5 mm past the edge; orphan
        polygons 18 -> 14. The three phase strips were never a problem (each
        connects through its own J4 pad), confirming the correction already
        recorded in 12.5.an.
  - [~] 12.5.au **Assembly prep for professional reflow, 2026-08-19.
        `tools/prep_for_assembly.py`. NO VENDOR CHOSEN** — the repo owner
        specified "JLCPCB or another similar manufacturer", so this build
        targets the capability envelope mainstream prototype-assembly houses
        have in common, not any one vendor's spec.
        Three defects found and fixed:
        (a) **J1, J2 and J3 would have reached the placement machine.** They
        are bare wire/probe landing pads, like J4A/B/C and J5A/B — but unlike
        those they were NOT flagged `exclude from BOM` / `exclude from
        position files`, so they would have appeared as parts to buy and
        place. Now flagged to match.
        (b) J5A/J5B carried no SMD/THT attribute (leftover from
        `convert_j5_to_smd.py`, which changed the pads but not the attribute).
        Set to SMD.
        (c) **No fiducials existed, on either side, on a DOUBLE-sided
        assembly** (18 footprints F.Cu, 41 B.Cu) carrying a 0.5 mm pitch
        WQFN-40 and a 0.5 mm pitch LQFP-64. Added 3 per side, non-collinear so
        rotation is resolvable, at corner sites with a 2.2 mm clear radius;
        excluded from BOM and position files. DRC unchanged at 17 warnings.
        **OPEN — needs a verified source before ordering (AGENTS.md §3):**
        no vendor capability document has been read, because no vendor has
        been chosen. 3 × 1 mm copper with 2 mm mask opening is ordinary
        industry practice, not a sourced requirement from any house. Once the
        manufacturer is picked, check its published policy and record it in
        REFERENCES.md with a validated URL.
        **Also open for the fab order:** `docs/tools/conductor_sizing.py`
        argues 2 oz copper minimum for the 50 A phase pours; the order must
        specify that explicitly, and 4-layer 2 oz is a non-default stackup
        that needs confirming with whichever house is chosen. REFERENCES.md
        carries the board's tightest features as a table for checking against
        any candidate vendor.

  - [ ] 12.5.at **(Low) Two `isolated_copper` warnings remain, unexplained.**
        **Verified 2026-08-20: still exactly 2 `isolated_copper`** on the
        current board.
        kicad-cli reports one on `Zone [VM] on In2.Cu` and one on
        `Zone [GND] on In2.Cu`, but neither zone fills as more than one
        polygon — checked directly via `GetFilledPolysList().OutlineCount()`,
        which returns 1 for both. So the polygon-count method that found and
        fixed the earlier islands does not reproduce these, and the cause is
        not yet understood. Both are warning severity with DRC electrical at
        0, so this is not fab-blocking. Needs a look in the KiCad GUI, where
        the violation can be selected and located directly. Do not guess at a
        fix; the last two "obvious" island explanations on this board were
        both wrong.

  - [x] 12.5.ap **DONE 2026-08-19 — rows and phase columns aligned.**
        `tools/align_rows_columns.py`. Every target is a position the board
        already used; a part >0.6 mm off its group is read as intent, not
        slip, and left alone. Each move is applied, refilled, scored and
        REVERTED unless DRC electrical stays 0, unconnected does not rise,
        creepage does not fall, and gate/commutation loops do not grow.
        **The majority row is not automatically the right row.** The first
        version snapped outliers to whatever position most of the group
        shared; on the high-side FETs that moved Q1 up to join Q3/Q5, pulling
        it away from U5 and lengthening the worst gate loop 16.49 -> 16.74,
        so the guard reverted it and the row stayed crooked. The right move
        was the opposite — bring Q3/Q5 DOWN to Q1 — which aligns all six FETs
        AND shortens the commutation loop 19.60 -> 19.40. The tool now scores
        every distinct position a group occupies, not just the popular one.
  - [x] 12.5.aq **DONE 2026-08-19 — board made left/right symmetric.**
        `tools/symmetrize.py`. Centreline is **x = 16.000** from the true
        outline polygon; `GetBoardEdgesBoundingBox()` says 32.100 because it
        measures the outer edge of the 0.05 mm Edge.Cuts stroke, which would
        have put the centreline at 16.050 and every pair 0.05 mm off-grid.
        Both halves of a pair shift by the same delta, so separations set by
        hand survive exactly and only the midpoint moves.
        **Result: 12/12 mirror pairs symmetric, phase pitch 10.500/10.500,
        phase B exactly on the centreline, 0 parts off the 0.5 mm grid in x.**
        Two bugs caught in the tool before it ran: `group_x` used the mean, so
        R2's deliberate +0.5 offset would have parked phase B at 15.900 and
        called it centred (now median); and deltas were snapshotted up front,
        so the "R2 alone" job would have used a stale number after phase B
        moved (now recomputed per move).
        **Symmetry and grid conflict unless a pair's separation is a whole
        millimetre** — centring splits it in half, so 8.500 apart becomes
        +/-4.250. Centring alone dropped grid adherence 83.1% -> 44.1%.
        Fixed by rounding each half-separation to 0.5 mm, preferring the
        SAFE direction: pack terminals went outward 8.500 -> 9.000 (more
        pack+/pack- clearance, not less). "iso caps outer" outward pushed the
        isolated lead to 10.03 mm, over the limit, so the guard took inward
        instead — which improved the lead to 9.76 mm.
        **Refused and left off-centre:** U5+SH1 and U1, both needing +0.950 mm
        (DRC electrical 1 and 28). They were grid-snapped 0.05 mm instead.
        The left and right stacks are different circuits, not a mirrored pair.
  - [x] 12.5.ar **DONE 2026-08-19 — U7/U8 swapped onto their own phases.**
        Found while mapping parts to phases for 12.5.aq: every part sat on its
        own phase column except the two sense amplifiers. U8 stood in the
        phase-B column carrying `ISENSE_C_HI`; U7 stood in phase C carrying
        `ISENSE_B_HI`. FETs and shunts were all consistent (Q2/R1 = A,
        Q4/R2 = B, Q6/R3 = C) — only the amps were crossed.
        Not merely untidy: this is a millivolt-scale shunt signal running
        beside half-bridge nodes slewing 25.2 V, and crossed placement forced
        each pair across a phase column to reach its own shunt — longer
        differential loop, more pickup from the node being measured.
        `tools/swap_u7_u8.py` exchanges the two positions. Nets NOT edited —
        the parts move to match the wiring, so the schematic stays
        authoritative. Cost measured at zero: unconnected, creepage, both
        loops and DRC all unchanged (they were not yet routed).
        Follow-on: U7 then inherited the starved-thermal position and was
        added to `fix_starved_thermals.py` — the starvation belongs to the
        POSITION, not the part, so all three sense amps are now listed.

  - [ ] 12.5.w **(BLOCKER for fabrication) The board is NOT ROUTED. This
        **Verified 2026-08-20: still true, and now deliberate.** 151 unrouted.
        The route was cleared rather than committed because the shield-ring
        part moves invalidated it. Blocked on 12.5.bf.
        entry previously overstated the state and is corrected here.**
        It claimed "352 segments, 48 vias, 57 open" from the FreeRouting run.
        Measured 2026-08-19, the board carries **0 track segments, 2 vias and
        157 unconnected items.**
        Traced through history: commit `15eeaa4` ("Route the signal nets")
        did have 352 segments and 49 vias. The very next commit, `8f4791a`
        ("Repair the front/back re-placement"), dropped it to 0 segments and
        1 via — `fix_after_replacement.py` removed ALL routing, not only the
        stale segments its message described. The board has been fully
        unrouted since, through every session that followed, while this entry
        kept describing the pre-repair state.
        Nothing on this board can be fabricated or assembled until this is
        done. Everything else recorded as "ready" — creepage, symmetry,
        thermals, fiducials, assembly attributes — is necessary and none of it
        is sufficient.
        The 157 count is what the copper pours do NOT already connect. Re-run
        FreeRouting or route by hand, then re-run
        `tools/strip_high_current_tracks.py` every time, so a 3 mm signal-class
        trace never stands in for 50 A copper (12.5.s).

  - [x] 12.5.x **DONE 2026-08-19 — U5's 12 thermal vias resized to the
        board's own via spec.** `tools/fix_u5_thermal_vias.py` took them from
        0.400 mm pad / 0.200 mm drill to **0.600 / 0.300**, which is exactly
        the `Default` net class `via_diameter`/`via_drill` already in
        `.kicad_pro` — no new number was chosen. Resulting geometry satisfies
        all three governing rules by construction: drill 0.30 = the 0.30
        `min_through_hole_diameter`; annular ring 0.150 vs 0.100 minimum;
        hole-to-hole 1.15 pitch − 0.30 = 0.85 vs 0.25 minimum.
        The GND-to-VM/phase short hazard that this stack-up has produced once
        before was measured, not assumed, before growing the copper: the via
        array spans y 58.275..61.725, Q3's pads end at y 56.750 and Q4's begin
        at y 62.750, so the array sits in the ~6 mm gap between the FET rows
        with 0.725 mm of clearance at the new radius. `drill_out_of_range`
        12 -> 0.
  - [x] 12.5.v **SUPERSEDED 2026-08-20 — measured at the 25.4 mm placement,
        which no longer exists** (the board is 32.10 x 66.20 mm). Current
        board: **0 `starved_thermal`, 2 `isolated_copper`**. The two
        `isolated_copper` carry forward as 12.5.at.
  - [~] 12.5.av **FIRST REAL ROUTING PASS, 2026-08-19.** The board was found
        fully unrouted -- 0 track segments, 0 vias, 157 ratsnest connections --
        and getting it to route surfaced seven defects, **none of them routing
        defects.** Full write-up:
        `docs/solutions/architecture-patterns/what-the-autorouter-is-never-told.md`.
        Fixed in this pass:
        (a) **Net classes were gone from the `.kicad_pro`** -- only `Default`
            remained, so VM, GND and all three phases would have routed at the
            0.2 mm signal default. `tools/set_netclasses.py` re-run and
            `tools/autoroute.py` now hard-stops if they are not in effect.
        (b) **Two class net names no longer existed** (`CAN_VISOIN_OPEN`,
            `RS485_VISOIN_OPEN`, renamed by the isolated-supply ferrite
            respin). A class naming a missing net is silent; now a hard stop.
        (c) **KiCad exports every rule area as a total no-route keepout**,
            losing `tracks allowed`. The isolation rule area therefore
            declared y 76.50..86.55 unroutable on all four layers -- the band
            holding U1, U2 and J1. The MCU was unroutable.
            `strip_pour_keepouts()` in `tools/autoroute.py`.
        (d) **Inner plane layers export as `(type signal)`.** The first run
            cut 59 segments / 196.7 mm of signal through the In1.Cu GND plane
            and 29 segments / 218.3 mm through the In2.Cu VM plane. Now marked
            `(type power)`; verified 0 segments on both.
        (e) **The DSN routing boundary carries no edge-clearance margin** and
            FreeRouting holds the track centreline, not its edge, inside it.
            Boundary now inset by edge clearance + half the widest track.
        (f) **`Power` 0.4 mm / `Sense` 0.3 mm net-class clearance was
            unsatisfiable inside U5's 0.5 mm-pitch WQFN-40** (0.28 mm pin gap)
            -- 24 violations no routing could clear. This is the same defect
            already recorded for the `Isolated` class in
            `tools/set_netclasses.py`; the lesson had not been carried across.
            Clearances -> 0.2 mm, with the real conductor spacing moved to a
            scoped custom rule in the new
            `open_secure_esc_6s_50a_can485_faraday.kicad_dru`. 59 -> 35
            violations.
        (h) **Insetting the DSN routing boundary DOES NOT WORK on this board
            and is now disabled.** It cost two full router runs, each hanging
            to its time limit (2700 s, 3000 s) with no `.ses` and no error.
            First cause: a flat 0.75 mm inset put J4A/B/C (5 x 10 mm phase
            terminals, reaching y 85.50) outside the boundary. Clamping the
            inset to the pads fixed that and it hung again, because the real
            blocker is the pours -- GND, VM and the three phase `(plane ...)`
            polygons reach the board edge at x 20.45..51.45, y 20.50..85.50,
            so any inset leaves conductor outside the routable region and
            pours cannot be clamped away. `inset_boundary()` is kept, disabled
            behind `--inset-boundary`, with the finding in its docstring.
            Edge clearance is still unsolved -- see 12.5.az.
        (i) **`tools/autoroute.py` destroyed the board before it had a
            result.** It cleared tracks and SAVED over the project file before
            exporting the DSN, so each hang above left the real board with 548
            segments deleted and nothing to replace them. Recovered from
            backups twice. It now writes the cleared board to scratch and only
            touches the project file once a routed result exists.
        (g) **The three phase pours were stale**, left behind by the
            2026-08-19 alignment pass: PH_A and PH_C stopped 3.04 mm short of
            their high-side FET source pads, splitting each half-bridge switch
            node in two. PH_B was correct, so the defect was not even
            symmetric. `tools/fix_phase_pours.py` (new) re-derives the pour
            edge from the pads it has to reach.
  - [ ] 12.5.aw **(BLOCKING, electrical) The board had ZERO vias -- all four
        poured planes were floating.** In1.Cu (solid GND) and In2.Cu (VM) were
        poured, DRC-quiet, and tied to nothing. A zone fill makes every
        same-net pad on its own layer look connected, so the ratsnest stays
        quiet and the board reads as routed while the inner planes do no work.
        `tools/stitch_planes.py` (new) now places the stitching; see 12.5.ax
        for what it could NOT place.
        **STILL OPEN:** the via count needed to carry 50 A between layers is
        **UNVERIFIED**. IPC-2152 and IPC-2221 Table 6-1 govern it and neither
        is in `REFERENCES.md` (both paywalled, neither read), so per
        `AGENTS.md` Sec.1.3 no current rating is asserted. The stitching is
        sized geometrically only. Resolve before fabrication.
  - [ ] 12.5.ax **(BLOCKING, electrical) The pack return has no path to the
        ground system, and the isolation strategy is what forbids it.**
        REFERRED TO USER -- this is a placement/architecture decision.
        **Correction first.** An earlier note in this session claimed
        isolated-to-non-isolated separation had degraded to 0.000 mm. That was
        a planar pad-to-pad measurement that ignored layers and it is WRONG.
        `tools/score_placement.py` measures the closest isolated/non-isolated
        pair **on a shared layer, between different parts** and reports
        **creepage 7.83 mm against the 7.5 mm requirement of [9] Table 6 --
        PASS**, with `pack_layer_separated` PASS. Both exclusions are correct
        and deliberate: J5A/J5B are SMD on the face opposite the isolated
        parts, so the only surface path is around the board edge, and that is
        a recorded decision worth 2.80 -> 4.64 mm on this build. The barrier
        holds. The 7.25 mm figure between U3's own pin rows is the SOIC-20W
        package's internal pitch, not a layout dimension, and is likewise
        excluded by design.
        **The real problem.** J5B (pack -, 50 A return) is a 7.00 x 7.00 mm
        SMD pad on **F.Cu only**, and across the top of the board F.Cu carries
        the VM pour, not GND. Its only route to the ground system is therefore
        a via -- and a via under J5B punches GND to B.Cu a fraction of a
        millimetre from U4's isolated pin row, destroying exactly the layer
        separation the barrier depends on. `tools/stitch_planes.py` placed
        **0 of 18** pack-terminal vias; that refusal is correct, not a bug.
        **The connection the pack return needs is the connection the isolation
        forbids.** Scale of the gap, from `tools/via_current_budget.py`:
        J5B needs ~40 vias at 0.60 mm drill on the optimistic basis and ~126
        on the conservative one (12.5.ba). It can have none.
        **Options, with what each costs.**
        (1) **Pack terminals to the bottom edge, beside the phase terminals.**
            Frees the top entirely; pack vias become legal. VM then runs the
            board length -- 12.5.ac estimated ~1.9 W at 50 A across In2 at
            full width. All four high-current terminals end up at one end,
            which is arguably better for the harness. Cost: the bottom already
            holds U1, U2, J1 and J4A/B/C (3 x 5 x 10 mm); this is a packing
            problem, and the commutation loop (now 19.40 mm) grows.
        (2) **Isolated section to the bottom, pack stays at the top.** 12.5.ac
            showed the 7.5 mm exclusions leave only 6.77 mm of legal
            non-isolated width against U1's 13.45 mm, so U1 must move too.
            Gives up same-end comms wiring.
        (3) **Accept a longer board, ~72 mm** (12.5.ac's figure). Simplest;
            costs 6 mm on top of the 60.1 -> 66.1 mm already spent.
        (4) **Split the F.Cu top pour so GND reaches J5B in-plane.** NEW, and
            the only option that moves nothing: give J5B its own F.Cu GND
            region beside J5A's VM region, at Power-class clearance. The
            return then leaves the terminal on F.Cu and the F.Cu-to-plane
            stitching happens further down the board, away from the isolated
            section, where vias are legal. **Can be done now regardless of
            which of (1)-(3) is chosen later.** Cost: F.Cu at the top must
            carry VM and GND side by side, roughly halving the width each
            gets (~15 mm of the 32 mm), and the split must not shorten the
            around-edge creepage path. Both need checking before it is
            adopted.
        **Ruled out by measurement, so they need not be re-explored:**
        (5) *Separate them laterally* -- U3's isolated pins span x
            22.735..34.165 and U4's x 37.735..49.165; the only gap is
            x 34.165..37.735 = **3.57 mm**, against a 7.00 mm pad. They can
            only separate in y, confirming 12.5.ac with a fresh number.
        (6) *Shrink the pack pads to make room* -- makes it worse. At 7.0 mm
            the pad holds 36 vias at 0.60 mm drill, at 6.0 mm it holds 25, at
            5.0 mm it holds 16, against ~40 needed (12.5.ba).
  - [ ] 12.5.ba **(High) Via-current budget — CORRECTED 2026-08-19 after the
        repo owner supplied a dedicated via calculator [S-F]. The earlier
        figures in this item were wrong in two ways and are superseded.**
        **Correction 1 — barrel geometry.** This project modelled the plating
        as growing OUTWARD from the drill
        (A = pi/4 ((d+2t)^2 - d^2)). Plating grows **inward**: the copper is
        the ring between the drilled radius and the finished radius,
        A = pi ((d/2)^2 - (d/2 - t)^2) per [S-F]. The old model overstated
        barrel area by ~7 %.
        **Correction 2 — which constant.** This item previously used the
        INTERNAL constant (k = 0.024) for load-bearing figures and applied a
        50 % array derate, giving 78-126 vias. [S-F], which is specifically a
        via calculator, uses the **outer-layer** constant k = 0.048 for vias
        and advises a **20-25 % design margin**, not a 50 % derate. The old
        numbers were roughly 2x over-conservative.
        **Corrected results** (dT 10 C, barrel annulus, k = 0.048 IPC-2221 /
        0.064 IPC-2152):
            0.30 mm drill  Class 2  1.45 A / 1.94 A
            0.40 mm drill  Class 2  1.81 A / 2.42 A
            0.60 mm drill  Class 2  2.46 A / 3.28 A
            (Class 3, 25 um plating, is ~17 % higher throughout.)
        For a 50 A terminal with the 25 % margin: **0.60 mm Class 2 needs 28
        vias and 36 fit the 7.00 mm pad — OK.** At 0.30 mm drill, 46 needed
        against 81 that fit. **This reverses the earlier claim that the
        as-built terminal could not carry 50 A through vias on any reasonable
        basis.** It can, on this basis.
        **What it does NOT change:** J5B still cannot have vias at any count,
        because the isolation barrier forbids them there, not the current
        budget (12.5.ax). Option (4) remains the right call for the reason it
        was chosen. This budget now applies to J5A and to the hand-off point
        of the new F.Cu GND corridor.
        **OPEN — the source disagrees with itself.** [S-F]'s reference table
        gives ~0.65 A for a 0.30 mm via at 25 um / 10 C where its own formula
        gives 1.69 A, a factor of 2.6. Its two table columns are mutually
        consistent (0.87/0.65 = 1.34 = 0.064/0.048), so the standard-to-
        standard ratio is sound and only the absolute scale is in doubt. **The
        two readings straddle the answer**: formula basis 28 vias (fits),
        table basis ~61 (does not). `tools/via_current_budget.py` prints both
        and uses the formula, because its constants are corroborated by
        [S-A]/[S-E] and the table's are not reproducible from the page.
        **Resolving this is the single best reason to obtain IPC-2152.**
  - [x] 12.5.bc **DONE 2026-08-19/20 — pack return given an F.Cu path
        (12.5.ax option 4, repo owner's decision). Implemented twice; the
        first implementation is recorded because its failure mode is not
        obvious.**
        **Final implementation:** `tools/split_top_pour.py` **cuts the F.Cu VM
        zone back** so its top stem ends at the board centreline
        (outline vertices x 46.78 -> 35.95), letting the existing whole-board
        GND zone fill the J5B side by itself. **No zone is added.** J5B is
        verified on F.Cu GND copper as a post-condition before the board is
        saved.
        **First implementation, withdrawn:** adding a priority-4 F.Cu GND
        region over the J5B side to out-rank the VM pour. Electrically it
        worked -- J5B joined the main 66-pad GND island, GND went 25 -> 20
        islands, unrouted 66 -> 63. But it left **two overlapping GND planes
        on F.Cu**, and KiCad exports every zone as its own
        `(plane GND (polygon F.Cu ...))`. Two overlapping same-net planes are
        pathological input for FreeRouting: **the router failed to complete a
        single pass in 53 minutes**, twice, on a board it had routed in 23-34
        minutes before. Diagnosed by diffing the DSN plane inventory against
        the last board that routed normally -- the only structural difference
        was 2 F.Cu GND planes where there had been 1. **Rule of thumb: one
        plane per net per layer in the DSN, always.**
        Isolation unaffected either way: the area handed to GND was already
        primary-side copper (VM), so the net changed but not the layer or
        extent; `score_placement.py` reports creepage 7.83 mm PASS.
        **NOT VERIFIED:** whether the resulting F.Cu GND corridor carries
        50 A. No current rating asserted per AGENTS.md Sec.1.3 -- see 12.5.ba.
  - [ ] 12.5.bd **(BLOCKING, electrical — DEFECT INTRODUCED AND FIXED THE SAME
        DAY, kept for the lesson) Plane stitching put 48 vias through the
        isolation barrier.**
        `tools/stitch_planes.py` as first written had no isolation rule. It
        placed vias across the whole board wherever a net was poured on both
        an outer and an inner layer -- including the top band, where the
        isolated section lives. Audit 2026-08-19: **26 vias sat at y < 34**,
        several directly over U3/U4's isolated pin rows and the isolated
        supply capacitors. Worst measured clearance from a via to isolated
        copper: **0.340 mm** (a VM via at (29.40, 20.90) against C13.1,
        CAN_VISOIN) **against the 7.5 mm requirement of [9] Table 6**.
        A via defeats the barrier by definition: this board's isolation is
        held by keeping primary copper on the face OPPOSITE the isolated
        section (`pack_layer_separated`), and a via punches every layer. It is
        the same reason J5B cannot be stitched.
        **Nothing in the flow caught it.** KiCad DRC has no rule for it, and
        `score_placement.py`'s creepage metric compares **pads on a shared
        layer** -- a via is invisible to it. It surfaced only from an explicit
        audit of via positions against the isolated nets.
        **FIXED:** `ISOLATION_CLEARANCE_MM = 7.5` guard added to
        `stitch_planes.py`; 48 offending vias removed; worst via-to-isolated
        clearance now **7.75 mm**, creepage 7.83 mm PASS.
        **STILL OPEN:** add this as a standing check. Either a custom rule in
        `open_secure_esc_6s_50a_can485_faraday.kicad_dru` scoped to vias
        versus the isolated net class, or a new metric in
        `score_placement.py` that measures **all copper items**, not just
        pads, against the isolated nets. Until one exists, any tool that
        places copper unattended can reintroduce this silently.
  - [ ] 12.5.be **(BLOCKING, process) The custom design rules had never fired,
        and one of them still cannot be written the obvious way.**
        Found 2026-08-20 while adding an isolation rule. Two separate defects
        in `open_secure_esc_6s_50a_can485_faraday.kicad_dru`:
        **(a) A multi-line `(condition "...")` silently invalidates the WHOLE
        FILE.** Not just the offending rule -- every rule in it, including
        ones above the offending line. No error, no warning, exit 0. Verified
        on KiCad 9.0.2: a rule that fires 154 times alone fires **0** times
        with a multi-line condition anywhere in the file. `power_conductor_
        spacing` and `sense_conductor_spacing` were written multi-line on
        2026-08-19 and had therefore **never fired**. **The DRC improvement
        attributed to them in 12.5.av(f) came entirely from the net-class
        clearance change; the conductor spacing was never enforced.** Now
        single-lined and verified firing.
        **With the rules actually running**, the board shows **61
        `power_conductor_spacing` and 18 `sense_conductor_spacing`**
        violations that were hidden the whole time. Triage them before fab.
        **(b) Clause order in a two-item condition is not commutative.**
        Measured against a board known to contain 48 violating vias:
            `A.Type == 'Via'`                              -> 502 hits
            `B.NetClass == 'Isolated'`                     -> 499 hits
            `A.Type == 'Via' && B.NetClass == 'Isolated'`  ->   0 hits
            `(A&&B) || (B&&A)` (containing the working clause) -> 0 hits
            `A.NetClass == 'Isolated' && B.Type == 'Via'`  -> 154 hits
        Both halves match alone; the obvious conjunction matches nothing; even
        an OR containing the working clause matches nothing. Only one ordering
        fires. The working form and a negative-control procedure are recorded
        in the `.kicad_dru` beside the rule.
        **STANDING REQUIREMENT: every rule in that file needs a negative
        control** -- a board known to violate it, on which the rule must be
        seen to fire. A rule that matches nothing reads exactly like a rule
        passing, which is how (a) survived a full day of DRC runs being quoted
        as evidence.
  - [ ] 12.5.bf **(High, tooling) FreeRouting completes the session and does
        not write the .ses, and autoroute.py hides why.** Found 2026-08-20
        after three consecutive routing runs failed (45-53 min each).
        **Symptom:** the router logs
        `Auto-router session completed: ... final score ... (N unrouted)` and
        then produces **no output file**. Reproduced standalone at `-mp 2`
        (53 s, 58 unrouted) and `-mp 5` (1 min 59 s, 51 unrouted) -- both
        completed, neither wrote a `.ses` anywhere on the filesystem. The one
        run that DID write (2026-08-19, `-mp 60`, 33 min) logged an explicit
        `Saving '...board.ses'` line that the failing runs never reach.
        **Two wrong diagnoses were made before this, both recorded so the
        reasoning is not repeated:** (1) overlapping same-net planes in the
        DSN -- a real defect, fixed in 12.5.bc, but not the cause; (2) CPU
        starvation from running `analyze_pcb --full` and `kicad-cli drc`
        concurrently with the router -- plausible, and also not the cause, as
        the standalone runs were unloaded.
        **`tools/autoroute.py` must stream the router's output.** It uses
        `subprocess.run(..., capture_output=True)`, so on `TimeoutExpired` the
        router's entire stdout is discarded -- all three failed runs produced
        logs containing **zero** router lines. That is why the board was
        blamed three times: there was no evidence about what the router was
        doing. Redirect to a file the caller can tail, and print the tail on
        timeout as well as on success.
        **Then determine the real cause:** compare the DSN/invocation of the
        2026-08-19 run that saved against one that does not, and check whether
        `-mp` below some threshold, or completing before convergence, skips
        the write path. Until this is understood the board cannot be routed
        reproducibly.
  - [ ] 12.5.bb **(Medium, NEW) The conductor-spacing basis is sea-level, and
        this is an airborne ESC.** [S-D] records that IPC-2221C (2023) revised
        conductor spacing as a function of **altitude**, and that IPC-2221
        specifies fixed spacing only up to 500 V (above which a per-volt
        increment applies -- worked example: 580 V on column B1 gives
        0.25 mm + 80 V x 0.0025 mm/V = 0.45 mm). The 6S pack is ~25.2 V so the
        voltage band is not the issue; the **altitude derating column** is,
        and nothing in this build has been checked against it. Note this is
        separate from the isolation barrier, which is governed by [9] Table 6
        and is unaffected. Determine the airframe's service ceiling, then
        confirm which IPC-2221 column applies and whether
        `open_secure_esc_6s_50a_can485_faraday.kicad_dru` needs to change.
  - [~] 12.5.ay **(High) U5's escapes are blocked by SH1's shield land, not
        by trace width.** ROOT CAUSE FOUND 2026-08-19, partially mitigated.
        **The finding.** SH1 (Wurth WE-SHC 3670209) solders to a **closed
        rectangular land on B.Cu**, x 24.85..47.05, y 51.70..68.30, 1.5 mm
        wide. U5's pads (x 32.75..39.15, y 56.80..63.20) sit entirely inside
        it. **No B.Cu trace of any width leaves that ring.** That is why 27 of
        U5's pad connections were unrouted, and it is a placement fact, not a
        routing one.
        **What this killed.** A "Fine" net class at 0.10 mm track / 0.09 mm
        clearance -- sized so exactly one trace fits the 0.280 mm gap between
        U5's 0.5 mm-pitch pads -- was built and routed on the theory that
        Default geometry was the constraint. Measured: **72 -> 69 unrouted, a
        gain of three connections**, in exchange for leaving the fab envelope
        `kicad/README.md` commits to. **Withdrawn.** Recorded here so it is
        not retried: trace width was never the binding constraint.
        **What actually works.** The land is **B.Cu only**, so F.Cu is free to
        cross the ring. Every U5 escape has to be
        `pad -> short B.Cu stub -> via -> F.Cu -> over the ring`, and that via
        needs annulus space between U5's pads and the shield land.
        **DONE — annulus freed, minimum-movement (repo owner's instruction).**
        `tools/move_out_of_shield.py` (new) moved the seven support passives
        that can leave the ring **without adding any new B.Cu crossing**:
        R6, C2, R14, R4, R13, R5, R10. Total displacement 35.20 mm over seven
        parts, mean 5.03 mm; six of the seven are pure-y moves that preserve
        their x column, and R13/R5/R10/R4 land on one new shared row at
        y 69.80. The split is derived from the netlist, not chosen: a part may
        leave only if every one of its nets already crosses the ring or is GND
        (which the shield land itself carries). Seven parts **must stay** --
        R9, R11, C5, C6, C7, C8, C9 -- because they carry U5-only nets, and
        they are exactly U5's charge pump and supply decoupling, which belong
        within a few millimetres of the chip anyway.
        **Effect, measured with tracks cleared:** U5 escapes with a legal via
        site went **9/27 -> 13/27**; a control run that parked all 20 nearby
        parts off-board reached only 14/27, so the minimal legal move captured
        substantially all of the available gain.
        **STILL OPEN.** The residual 14 are blocked by **Q3 and Q4 on F.Cu,
        directly over U5** (6 and 5 sites respectively), plus R11 and C1. The
        FET columns are locked under the shield by design, so closing the rest
        needs either a different U5 orientation, a shield land broken into
        segments (a slot in a Faraday-tier shield -- an EMI trade, not a free
        move), or accepting hand-routing. REFERRED TO USER.
        U1 is a separate and lesser problem: its B.Cu neighbours pinch the
        escape corridors, but its binding constraints are the 1.1 mm to the
        board edge below it and J4A/J4C on F.Cu overhead. Moving its
        neighbours took it only 13/19 -> 15/19.
  - [ ] 12.5.az **(Medium) 11 `copper_edge_clearance` violations, 6 of them
        on the isolated comms nets.** Routed tracks sit as close as 0.317 mm
        to the board edge against a 0.500 mm rule, because
        `min_copper_edge_clearance` is a KiCad board-setup constraint that
        never reaches the Specctra DSN. Moving the boundary is ruled out --
        see 12.5.av(h) for the two runs that proved it. **UNTESTED candidate:**
        a Specctra clearance rule of type `wire_area` / `via_area`, which
        states clearance TO the boundary rather than moving it. Verify it is
        honoured by FreeRouting 2.2.4 before relying on it; otherwise fix the
        11 tracks by hand after 12.5.ay's fanout work re-routes the board.
        Also still open: 5 `starved_thermal`, plus 15 silkscreen warnings
        already tracked in 12.5.u.

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

- [ ] 14.0 **(High) Promote `score_placement.py` to repo-level `tools/`.**
      It is the measurement harness all the placement work runs on: creepage
      (edge-to-edge, including the around-the-edge path for opposite-face
      pairs), isolated lead length against [9]'s 10 mm, gate and commutation
      loops, DRC electrical count, grid/row/column regularity, and the two
      pass/fail isolation rules from 12.5.ak. It is generic apart from a
      handful of named nets and part refs at the top, which 14.2's build
      descriptor would supply. Every future build needs it BEFORE placement
      starts, not after — that is the whole lesson of 12.5.ac.
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

## 15. Single-End Wire Egress Variant (planned — not started)

Design plan: `docs/design-single-end-wire-egress-variant.md`. A pocket-mount
variant in which the pack conductors and the three phase conductors both
terminate at the same board end, on opposite long edges. Not a connector
move — a board re-partition that swaps the logic cluster (`U1`/`U2`/`J1`)
with the pack input.

- [ ] 15.1 **(Blocking) Confirm the egress reading.** "Opposite sides" =
      the two long edges near one end, or the two board faces? Everything
      below assumes long edges (plan §1.1); the faces reading is rejected in
      plan §7.1 and reopens §3–§6 if it was the intent.
- [ ] 15.2 **Add a Wire Egress axis to `docs/decision-matrix.xlsx`** with
      values `split-end` (as-built default) and `single-end`. Re-run
      `docs/tools/decision_matrix_to_json.py --check`; add the axis to root
      `README.md`; instantiate `builds/6s/50A/CAN_485_faraday_singleend/`.
- [ ] 15.3 **(High, blocks layout) Select the power connectors.** Promotes
      §12.4.l from a fab blocker to a layout gate: single-end egress budgets
      connector *body length along the long edge*, a dimension the baseline
      never constrained. Cite the part in `REFERENCES.md` before use (Cn).
- [ ] 15.4 **Re-place: swap logic cluster and pack input.** `U1`/`U2`/`J1`
      to Y ~25–45 mm; `J5A/B` to the −X long edge and `J4A/B/C` to the +X
      long edge at Y ~76–86 mm. **Re-run `isolation_envelope.py` with the
      new widest non-isolated part** — the LQFP-64 may displace the 12.90 mm
      input and push the minimum width past the as-built 32.00 mm, which
      would invalidate the partition rather than justify a wider board.
- [ ] 15.5 **Re-run `docs/tools/conductor_sizing.py`** for the new
      pour-edge-to-terminal gaps on both edges. Its standing conclusion
      holds: the gap is pour, not track, or the terminals move onto the
      pour's layer. No "TBD" copper weight.
- [ ] 15.6 **Common-mode choke on the pack input** — new for this variant.
      Single-end egress puts the pack and phase harnesses in one bundle,
      deleting the physical separation the split-end layout gave free. Quote
      insertion loss from the part's own datasheet; do not estimate (Cn).
- [ ] 15.7 **Split the phase-terminal rule area** (X 20.8–51.1, Y 76.5–86.5)
      into a −X `VBATT` area and a +X `PHASE` area. **Each new rule needs a
      negative control before it is trusted** — see `CLAUDE-MEMORY.md`
      *kicad-dru-silent-failure*: one-line conditions only, and clause order
      is not commutative. Record the control procedure beside the rule.
- [ ] 15.8 **Thermal re-run** over the new placement. Five wire terminals at
      one end redistributes the conduction path out of the board. Quote
      junction temperatures for `Q1`–`Q6`, `U5`, `U1`; no "TBD".
- [ ] 15.9 **Conducted-emissions pre-compliance for this variant.** The
      baseline §7.3 result does not transfer. Add this variant and its
      harness dress (twisted phase triplet, twisted pack pair, stated bundle
      separation) to the §7.3 test plan — the test is meaningless without a
      defined harness.

**Sequencing.** 15.1 → 15.2 → 15.3 → 15.4 → 15.5 → 15.7 → 15.6 → 15.8 →
15.9. 15.1 gates all of it.

**Open, non-blocking.** IPC-2221 Table 6-1 conductor spacing is used
nowhere as an asserted value — no primary copy exists and no tag is issued
(`REFERENCES.md`, "Pending Verification"). Mechanics, not spacing, decides
the terminal pitch (plan §3.1).
