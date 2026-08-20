# REFERENCES.md — IEEE Bibliography

Governed by `AGENTS.md`. IEEE reference style. Each entry lists the verified
source URL and the chapter/section/page/paragraph the repo relies on, plus
the date it was accessed. Fields that could not be independently verified
(e.g. behind a purchase paywall, or blocked by anti-bot access controls) are
marked explicitly — never guessed. Tags are cited in-repo as `[n]`.

Last reviewed: 2026-08-09.

---

**[1]** Texas Instruments Incorporated, *MSPM0G350x Mixed-Signal
Microcontrollers With CAN-FD Interface*, datasheet — production data,
SLASEX6C, Rev. C, Texas Instruments Incorporated, Dallas, TX, USA,
2023-02 (revised 2025-10). [Online]. Available:
https://www.ti.com/lit/ds/symlink/mspm0g3507.pdf
(live fetch blocked: HTTP 403, 2026-08-02 — see TODO.md 1.4).
Product page: https://www.ti.com/product/MSPM0G3507
(live fetch blocked: HTTP 403, 2026-08-02).
Local verified copy: `docs/datasheets/mspm0g3507.pdf` (120 pp.).
Section/page: p. 6, Table 5-1 "Device Comparison" — MSPM0G3507SPMR/
SPTR/SRGZR/SRHBR/SDGSR28 variants: 128 KB flash, 32 KB SRAM, one CAN
peripheral; package options 64-pin LQFP, 48-pin LQFP, 48-pin VQFN,
32-pin VQFN, 28-pin VSSOP. p. 68, §8.26 "CAN-FD" — "controller area
network (CAN) controller enables communication with a CAN2.0A, CAN2.0B,
or CAN-FD bus and is compliant to ISO 11898-1:2015 standard supporting
up to 5Mbit/s bit rate" (cf. [5], [6]). p. 7, §6.1 "Pin Diagrams"; p.
11, §6.2 "Pin Attributes"; p. 14, §6.3 "Signal Descriptions" — full
pinout. p. 77, §10.2 "Device Nomenclature," Table 10-1 "Device
Nomenclature" — decodes MSPM0G3507SRHBR: MCU platform MSPM0 (Arm
Cortex-M0+), product family G (80 MHz), device subfamily 350 (CAN-FD,
2x ADC, 2x OPA, 3x COMP), flash memory 7 (128 KB), temperature range S
(-40°C to 125°C); package type and distribution format per Section 12
"Mechanical, Packaging, and Orderable Information" (select per BOM).
Cited in: README.md (MCU line); symbols/specs/MSPM0G3507.json (pin map,
64-LQFP subset used by this build); builds/6s/50A/CAN_485_faraday/README.md.
Date accessed: 2026-08-02.
**SUPERSEDED 2026-08-03: this repo's project MCU changed from the
MSPM0G3507 to the NXP S32K144 — see [31].** Entry retained in full per
`AGENTS.md` §2.5 (never renumber or repurpose an existing tag for a
different source); this citation is historical only and is no longer
referenced by README.md or any current build BOM/schematic.
`symbols/specs/MSPM0G3507.json` and `symbols/MSPM0G3507.kicad_sym` were
removed from the repo as part of the MCU swap (unused, superseded by
`symbols/specs/S32K144.json` / `symbols/S32K144.kicad_sym`, [31]); the local
datasheet copy `docs/datasheets/mspm0g3507.pdf` this entry's "Local verified
copy" line points to is kept as-is so this citation record stays resolvable.

---

**[2]** Infineon Technologies AG, *OPTIGA™ TPM SLB9672 TPM 2.0 FW16.xx —
Datasheet, Trusted Platform Module*, document release reference
Z8F80723107-B, Rev. 1.3, Infineon Technologies AG, Munich, Germany,
2024-11-18. [Online]. Available:
https://www.infineon.com/assets/row/public/documents/30/49/infineon-slb9672-tpm20-spi-fw16.xx-ds-rev1-3-2024-11-18-datasheet-en.pdf
Local verified copy: `docs/datasheets/infineon-slb9672-tpm20-spi-fw16.xx-datasheet-rev1.3.pdf`
(47 pp.).
Section/page: p. 1, "Key features" — compliant with TCG TPM Library
specification revision 1.59 and PC Client Platform TPM Profile (PTP)
version 1.05; Common Criteria EAL4+ (AVA_VAN.4, moderate) Certificate
CC-1245 (9 Oct. 2024); FIPS 140-2 Level 2 Certificate 4467 (7 Apr. 2023).
p. 8, §1.1 "Product description" — SPI interface, transfer rate up to
33 MHz typical; compliance restated with citation markers to the TCG
specs listed in the datasheet's own References section, p. 45, refs
[1]–[4]. p. 17, §3.1.2 "Pin description," Table 11 — SPI signal pinout
(CS#, SCLK, MOSI, MISO, PIRQ#, RST#). p. 19, §3.1.3 "Typical schematic,"
Figure 7 — reference decoupling/pull-up circuit (3×100 nF + 1 µF
bypass, 10 kΩ CS# pull-up).
Cited in: README.md (TPM line); symbols/specs/SLB9672.json (full 32-pin
map); builds/6s/50A/CAN_485_faraday/README.md.
Date accessed: 2026-08-02.
**DROPPED 2026-08-03: this repo removed the discrete SLB9672 TPM 2.0 from
the design.** Message authentication is now provided by the project MCU's
own on-chip security module instead of an external TPM — see [31] (NXP
S32K144, Cryptographic Services Engine / CSEc). Entry retained in full per
`AGENTS.md` §2.5 (never repurpose a citation tag); this citation is
historical only and is no longer referenced by README.md or any current
build BOM/schematic. `symbols/specs/SLB9672.json` and
`symbols/SLB9672.kicad_sym` were removed from the repo (part no longer in
any design); the local datasheet copy
`docs/datasheets/infineon-slb9672-tpm20-spi-fw16.xx-datasheet-rev1.3.pdf`
this entry's "Local verified copy" line points to is kept as-is so this
citation record stays resolvable.
**NOT SUPERSEDED BY [45] (2026-08-09).** The OPTIGA™ Trust M added that
day ([45]) is a *different device class* — an I2C secure element, not a
TCG TPM 2.0 — and it is **not** a reinstatement of this part. It occupies
the schematic designator (U2) this part vacated, but it is adopted for the
asymmetric PKI capability the S32K144's symmetric-only CSEc structurally
cannot provide, **alongside** CSEc rather than in place of it; the
2026-08-03 decision to use CSEc for per-frame message authentication
stands unchanged. See `docs/secure-element-architecture.md` for the split,
and `docs/security-mcu-comparison.md` §3.3 for the device-class
comparison. Nothing in [45] re-verifies, revives, or re-scopes any claim
made under this tag.

---

**[3]** Telecommunications Industry Association, *Interface Between Data
Terminal Equipment and Data Circuit-Terminating Equipment Employing Serial
Binary Data Interchange*, TIA-232-F, TIA, Arlington, VA, USA, 1997
(reaffirmed). [Online]. Available:
https://store.accuristech.com/standards/tia-tia-232-f?product_id=2594289
Section/page: not verified — standard is paywalled; only the catalog/store
listing is accessible without purchase.
Cited in: README.md (Protocol: RS-232).
Date accessed: 2026-08-02.

---

**[4]** Telecommunications Industry Association, *Electrical Characteristics
of Generators and Receivers for Use in Balanced Digital Multipoint
Systems*, ANSI/TIA-485-A, TIA, Arlington, VA, USA, 1998 (reaffirmed
2012-12-07). [Online]. Available:
https://store.accuristech.com/standards/tia-ansi-tia-485-a?product_id=2591400
Section/page: not verified — standard is paywalled; only the catalog/store
listing is accessible without purchase. Compliance with this standard by
name ("ANSI/TIA/EIA-485-A-98") is independently confirmed at the
component level in [9], p. 1, "Features."
Cited in: README.md (Protocol: RS-485);
builds/6s/50A/CAN_485_faraday/README.md (Protocol BOM).
Date accessed: 2026-08-02.

---

**[5]** Robert Bosch GmbH, *CAN Specification, Version 2.0*, Robert Bosch
GmbH, Stuttgart, Germany, 1991. [Online]. Available (archival mirror,
publisher no longer hosts the 1991 document directly):
http://esd.cs.ucr.edu/webres/can20.pdf
Section/page: Part A (Standard Format, 11-bit identifier) and Part B
(Extended Format, 29-bit identifier) — specific page numbers for a given
claim not yet pinned; verify against the mirrored PDF before quoting
page-level detail. Note: this specification has been superseded for new
designs by ISO 11898-1 [6]; retained here only insofar as "CAN2.0" is
referenced by name in README.md. The project MCU's embedded CAN
peripheral, [1], p. 68, §8.26 "CAN-FD," declares support for "CAN2.0A,
CAN2.0B, or CAN-FD" by name.
Cited in: README.md (Protocol: CAN2.0).
Date accessed: 2026-08-02.

---

**[6]** International Organization for Standardization, *Road vehicles —
Controller area network (CAN) — Part 1: Data link layer and physical
signalling*, ISO 11898-1:2015, ISO, Geneva, Switzerland, 2015-12.
[Online]. Available: https://www.iso.org/standard/63648.html
Section/page: not verified — standard is paywalled; only the ISO catalog
listing (scope/abstract) is accessible without purchase. Note: a CAN
FD-capable transceiver, [10], declares compliance specifically with
ISO 11898-2:2016 (physical layer), not this Part 1 (data link layer)
document — the two parts are distinct and both apply to a complete
CAN FD implementation; ISO 11898-2:2016 itself is not yet a separate
entry here pending a verified catalog URL. The project MCU's embedded
CAN peripheral, [1], p. 68, §8.26 "CAN-FD," declares itself "compliant
to ISO 11898-1:2015 standard."
Cited in: README.md (Protocol: CAN-FD);
builds/6s/50A/CAN_485_faraday/README.md (Protocol BOM).
Date accessed: 2026-08-02.

---

**[7]** Department of Defense (USA), *Interface Standard: Digital Time
Division Command/Response Multiplex Data Bus*, MIL-STD-1553B, U.S.
Department of Defense, 1978-09-21. [Online, government-hosted mirror].
Available: https://nepp.nasa.gov/docuploads/43745C0A-323E-4346-A434F4342178CD0E/MIL-STD-1553.pdf
Section/page: not yet pinned to a specific section for a repo claim;
general applicability only. Note: superseded by MIL-STD-1553C (2018) for
new designs — confirm which revision the project actually targets before
final design commitment. A candidate 1553 interface module, [11],
declares compliance specifically with "MIL-STD-1553B/C Notice II & IV."
Cited in: README.md (Protocol: MIL-STD-1553B).
Date accessed: 2026-08-02.

---

**[8]** CERN, *CERN Open Hardware Licence Version 2 — Permissive
(CERN-OHL-P v2)*, CERN, Geneva, Switzerland, 2020. [Online]. Available:
https://ohwr.org/cern_ohl_p_v2.pdf
Mirror/registry: https://spdx.org/licenses/CERN-OHL-P-2.0.html
Section/page: Preamble quoted verbatim in `LICENSE` lines 1–19; full text
in the linked PDF.
Cited in: LICENSE (full text); README.md (License section).
Date accessed: 2026-08-02.

---

**[9]** Analog Devices, Inc., *ADM2582E/ADM2587E — Signal and Power
Isolated RS-485 Transceiver with ±15 kV ESD Protection*, data sheet,
Rev. H, Analog Devices, Inc., Wilmington, MA, USA, 2025-02. [Online].
Available: https://www.analog.com/media/en/technical-documentation/data-sheets/adm2582e-2587e.pdf
Product page: https://www.analog.com/en/products/adm2582e.html
Local verified copy: `docs/datasheets/analog-devices-adm2582e-adm2587e-datasheet.pdf`
(22 pp.).
Section/page: p. 1, "Features" — "Complies with ANSI/TIA/EIA-485-A-98
and ISO 8482:1987(E)"; ADM2582E data rate 16 Mbps, ADM2587E data rate
500 kbps; ±15 kV ESD protection on RS-485 I/O pins. p. 5, "Regulatory
Information," Table 5 — UL 1577 File E214100 (2500 V rms single
protection); DIN EN IEC 60747-17 (VDE 0884-17) pending; CQC GB4943.1
Certificate CQC16001151037. p. 5, "Insulation and Safety-Related
Specifications," Table 6 — 7.5 mm minimum external clearance/creepage.
p. 8, "Pin Configuration and Function Descriptions," Table 10 — pinout
(TxD, RxD, DE, RE, A/B differential I/O, Y/Z driver outputs).
