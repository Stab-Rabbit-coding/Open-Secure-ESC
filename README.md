# Open Source Trustworthy Electronic Speed Control

All builds:

MCU: NXP S32K144 [31] (historical) — active MCU is now TI MSPM0G3518-Q1 (see docs/HANDOFF-mcu-swap-s32k144-to-mspm0g3518.md)
Message authentication: on-chip CSEc (Cryptographic Services Engine, SHE-compliant) security module built into the MCU family — no discrete TPM (the previously used Infineon SLB9672 [2] has been dropped; OPTIGA™ Trust M used as asymmetric root of trust where required).
Root of trust: Infineon OPTIGA™ Trust M V3 secure element [45] over I²C (schematic `U2`) — device identity (ECDSA over a fab-provisioned key + X.509 certificate) and ephemeral session-key agreement where needed.

Build Options:
* Motor speed sensor: ADC/DIO/SPI shaft sensor input (Hall / encoder / analog tach)
* Motor type: Brushed / Brushless
* Voltage: 2S, 4S, 6S, 8S, 12S
* Amperage: 10A, 20A, 30A, 40A, 50A, 80A, 120A
* Protocol: PWM, SBus, DBus, UART, TTL, SPI, RS-232 [3], RS-485 [4], CAN2.0 [5], CAN-FD [6], MIL-STD-1553B [7]
* Control: Open, Closed-Diff, Closed-PID
* EMI Hardening: None, Isolation, Grounding, Faraday
* Ingress & environmental protection: IP ratings up to IP68 and NEMA equivalents up to NEMA 6P. Submersible variants MUST include cooling strategies that operate correctly in both air and water (see docs/design-submersible-cooling.md DRAFT).

## Repository layout

* `symbols/` — shared KiCad symbol library (one `.kicad_sym` per component),
  generated from citable pin specs; see `symbols/README.md`.
* `builds/<voltage>/<amperage>/<variant>/` — per-build instantiation of the
  axis options above: a descriptive `README.md` (BOM drawn from
  `docs/decision-matrix.xlsx`, with citations), a `kicad/` subfolder
  (schematic + shared-library wiring), and a `gerbers/` subfolder
  (fabrication output once a layout exists). Example:
  `builds/6s/50A/CAN_485_faraday/`.
* `docs/decision-matrix.xlsx` — per-axis BOM/workflow decision matrix that
  every build folder is generated from.

## License

Licensed under the CERN Open Hardware Licence Version 2 — Permissive
(CERN-OHL-P v2) [8]. See `LICENSE`.

## Governance

Contributions (human or AI) are governed by `AGENTS.md`. All citations
above are indexed in `REFERENCES.md`. Work is tracked in `TODO.md`.
