# TODO.md — Work Breakdown Structure

Governed by `AGENTS.md`. Status: `[ ]` open, `[~]` in progress, `[x]` done,
`[!]` blocked. `Cn` = REFERENCES.md tag needed/used. Keep entries terse;
detail belongs in design docs, not here.

## 1. Governance & Docs
- [x] 1.1 AGENTS.md — contributor/agent rules
- [x] 1.2 REFERENCES.md — IEEE bibliography scaffold
- [x] 1.3 TODO.md — this WBS
- [ ] 1.4 Verify [1] STM32L431 datasheet doc ID/rev/page (blocked: 403 on st.com)
- [ ] 1.5 Verify [2] SLB9672 datasheet page refs for compliance claims (blocked: 403 on infineon.com)
- [ ] 1.6 Verify [3]-[7] section/page pins once standards obtained (paywalled)
- [ ] 1.7 Confirm MIL-STD-1553B vs -1553C target revision, update [7]
- [ ] 1.8 Source authoritative refs: SBus, DBus, PWM-interface, UART/TTL/SPI, EMI tiers
- [ ] 1.9 CONTRIBUTING.md — citation workflow quick-reference (derive from AGENTS.md §2)

## 2. Requirements
- [ ] 2.1 Functional requirements spec (per voltage/amperage/protocol/control/EMI variant)
- [ ] 2.2 Safety requirements (motor runaway, overcurrent, thermal, TPM attestation trust boundary)
- [ ] 2.3 Regulatory/EMC targets per market (cite standard, C6)
- [ ] 2.4 Requirements traceability matrix → REFERENCES.md tags

## 3. Hardware — MCU Subsystem
- [ ] 3.1 STM32L431KCU6 schematic (power, clock, decoupling per [1])
- [ ] 3.2 Programming/debug interface (SWD)
- [ ] 3.3 Peripheral pin mapping vs. protocol variant matrix

## 4. Hardware — Trust/Security Subsystem
- [ ] 4.1 SLB9672 TPM schematic (SPI per [2])
- [ ] 4.2 Secure boot / attestation chain design doc
- [ ] 4.3 Key provisioning process

## 5. Hardware — Power Stage
- [ ] 5.1 Gate driver + FET selection per amperage tier (10/20/30/40/50/80/120 A)
- [ ] 5.2 Voltage tier variants (2S/4S/6S/8S/12S) — component derating table
- [ ] 5.3 Current sensing (shunt/hall) selection + citation

## 6. Hardware — Protocol Interfaces
- [ ] 6.1 PWM input stage
- [ ] 6.2 SBus input stage (flag UNVERIFIED spec, C-pending)
- [ ] 6.3 DBus input stage (flag UNVERIFIED spec, C-pending)
- [ ] 6.4 UART/TTL transceiver
- [ ] 6.5 SPI interface
- [ ] 6.6 RS-232 transceiver per [3]
- [ ] 6.7 RS-485 transceiver per [4]
- [ ] 6.8 CAN 2.0 controller/transceiver per [5]
- [ ] 6.9 CAN-FD controller/transceiver per [6]
- [ ] 6.10 MIL-STD-1553B interface per [7]

## 7. Hardware — EMI Hardening
- [ ] 7.1 Define tier requirements: None / Isolation / Grounding / Faraday (needs C, see REFERENCES.md pending)
- [ ] 7.2 Layout guidelines per tier
- [ ] 7.3 Pre-compliance test plan

## 8. Firmware
- [ ] 8.1 Control loop: Open-loop
- [ ] 8.2 Control loop: Closed-loop differential
- [ ] 8.3 Control loop: Closed-loop PID
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
