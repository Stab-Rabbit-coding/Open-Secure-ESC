# Open Source Trustworthy Electronic Speed Control

All builds:

MCU: **TI MSPM0G3518-Q1**, package PM (LQFP-64), orderable `M0G3518QPMRQ1` [44] — pin map VERIFIED. Supersedes the NXP S32K144 [31] as of 2026-08-10 (`TODO.md` §13.1; migration record in [`docs/HANDOFF-mcu-swap-s32k144-to-mspm0g3518.md`](docs/HANDOFF-mcu-swap-s32k144-to-mspm0g3518.md)), for its AES-128/256 accelerator with GCM/CMAC and hardware keystore, which lifted the AES-128 ceiling the S32K144's SHE-compliant CSEc imposed.

> **The two lines below still describe the S32K144 and its CSEc, which is no longer the MCU in any build.** They are left in place because the swap's *security* consequences are unfinished work, not a documentation lag — `docs/secure-element-architecture.md` has not yet been revisited (`TODO.md` §13.1.e), so rewriting the summary here would assert a conclusion nobody has reached. Treat every CSEc statement below as describing a superseded design until §13.1.e closes. The OPTIGA Trust M's role is unaffected: the MSPM0's AES engine is still symmetric, so the asymmetric layer is still required.

Message authentication: on-chip CSEc (Cryptographic Services Engine, SHE-compliant) security module built into the S32K144 [31] — no discrete TPM (the previously used Infineon SLB9672 [2] has been dropped from this design)
Root of trust: Infineon OPTIGA™ Trust M V3 secure element [45] over I²C (schematic `U2`) — device identity (ECDSA over a fab-provisioned key + X.509 certificate) and ephemeral session-key agreement (ECDHE). This is a secure element, **not** a TPM: it supplies the asymmetric layer CSEc structurally lacks, while CSEc keeps the per-frame AES-128 CMAC hot path. The split, and the 5 s security-monitor budget that forces it, are documented in [`docs/secure-element-architecture.md`](docs/secure-element-architecture.md)

Build Options:

* Motor speed sensor: ADC/DIO/SPI shaft sensor input (Hall / encoder / analog tach)
* Motor type: Brushed / Brushless
* Voltage: 2S, 4S, 6S, 8S, 12S
* Amperage: 10A, 20A, 30A, 40A, 50A, 80A, 120A
* Protocol: PWM, SBus, DBus, UART, TTL, SPI, RS-232 [3], RS-485 [4], CAN2.0 [5], CAN-FD [6], MIL-STD-1553B [7]
* Control: Open, Closed-Diff, Closed-PID
* EMI Hardening: None, Isolation, Grounding, Faraday
* Wire Egress: Opposite-end (default), Same-end opposite faces (both conductor groups leave one board end, phases on F.Cu and pack on B.Cu, shielded by the inner GND planes)
* Form Factor: Flat (default), Faceted rigid-flex (for mounting inside a curved host; strip width and sagitta derive from the host bore radius — see `docs/tools/strip_width.py`)
* Ingress & environmental protection: Splash/spray variants (target IPX4–IPX6, IEC 60529 [56]) air-cooled via an open aspirated path; Sealed/immersion variants (target IPX7–IPX8, up to NEMA 6P equivalent) MUST use a metal conduction cooling path with no air exchange — these are two distinct mechanical designs, not one IP-rating dial (see `docs/design-waterproofing-and-thermal-management.md`).

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
* `PROJECT_INDEX.md` — index of every active folder and file, with the
  conventions worth knowing before editing.

## License

Licensed under the CERN Open Hardware Licence Version 2 — Permissive
(CERN-OHL-P v2) [8]. See `LICENSE`.

## Governance

Contributions (human or AI) are governed by `AGENTS.md`. All citations
above are indexed in `REFERENCES.md`. Work is tracked in `TODO.md`.
