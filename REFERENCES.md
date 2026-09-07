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
Candidate part for the RS-485 protocol interface (TODO.md §6.7); not
yet selected in a bill of materials.
Cited in: docs/datasheets/ (local reference only; not yet cited in
repo-root README.md pending BOM selection); symbols/specs/
ADM2582E_ADM2587E.json (full 20-pin map, verified against p.8, Table 10);
builds/6s/50A/CAN_485_faraday/README.md (Protocol BOM, variant choice
ADM2582E vs. ADM2587E left open).
Date accessed: 2026-08-02.

---

**[10]** Analog Devices, Inc., *ADM3055E/ADM3057E — 5kV rms/3kV rms,
Signal and Power Isolated, CAN Transceivers for CAN FD*, data sheet,
Rev. D, Analog Devices, Inc., Wilmington, MA, USA, 2026-03. [Online].
Available: https://www.analog.com/en/products/adm3055e.html
Local verified copy: `docs/datasheets/analog-devices-adm3055e-adm3057e-datasheet.pdf`
(27 pp.).
Section/page: p. 1, "Features" — "ISO 11898-2:2016 compliant (CAN FD)";
data rates up to 12 Mbps; ADM3055E VISO = 5000 V rms, ADM3057E VISO =
3750 V rms (both UL 1577, 1-minute rating); extended common-mode range
±25 V; bus fault protection ±40 V on CANH/CANL. p. 9, "Insulation
Specifications," Table 3/Table 4 — IEC 60747-17 reinforced insulation,
VIORM = 595 V peak. p. 15, "Pin Configuration and Function
Descriptions," Table 10 — pinout (TXD, RXD, CANH, CANL, RS, STBY,
SILENT, AUXIN/AUXOUT). p. 23, "Theory of Operation," "Remote Wake Up" —
"respond to the remote wake-up sequence as defined in ISO 11898-2:2016."
Candidate part for the CAN2.0/CAN-FD protocol interface (TODO.md
§6.8–6.9); not yet selected in a bill of materials.
Cited in: docs/datasheets/ (local reference only; not yet cited in
repo-root README.md pending BOM selection); symbols/specs/
ADM3055E_ADM3057E.json (full 20-pin map, verified against p.15, Table 10);
builds/6s/50A/CAN_485_faraday/README.md (Protocol BOM, variant choice
ADM3055E vs. ADM3057E left open).
Date accessed: 2026-08-02.

**Variant resolution (2026-09-06), per the BOM/creepage audit in
`docs/solutions/architecture-patterns/bom-creepage-audit-can485-faraday.md`:**
p. 7, Table 2 "Timing Characteristics" is a SINGLE shared table covering both
ADM3055E and ADM3057E — Maximum Data Rate 12 Mbps for both, with no
per-variant split anywhere in that table. p. 9–10, Table 3 (ADM3055E, "20-Lead
Increased Creepage SOIC [SOIC_IC] (RI-20-1)") gives CLR/CRP = 8.3 mm; Table 4
(ADM3057E, "20-Lead Wide SOIC [SOIC_W] (RW-20)") gives CLR/CRP = 7.8 mm — both
at the identical VIORM 595 V peak / VIOWM 420 V rms reinforced rating; the
only other difference is the UL 1577 1-minute proof voltage (5000 V rms vs.
3750 V rms). Since the two variants are electrically and timing-identical,
**ADM3057E is the correct default selection** (0.5 mm less creepage, no
functional cost) unless a specific downstream requirement calls out the UL
5000 V rms figure by name. The PCB footprint already placed for U3 in
`builds/6s/50A/CAN_485_faraday/kicad/*.kicad_pcb`
("SOIC-20W_7.5x12.8mm_P1.27mm") is dimensionally the RW-20 package, i.e. the
board is already built as if ADM3057E were selected — the BOM/schematic
`Value`/`Description` fields and this repository's README should be updated
to close the "left open" note rather than carry it forward, and the footprint
should be independently re-verified against the RW-20 land pattern (this
citation does not itself confirm the KiCad footprint's pad dimensions match
[10] p. 27 "Outline Dimensions" for RW-20 — that check is still open, see
TODO.md).

---

**[11]** Alta Data Technologies LLC, *MEZ-E1553 — 1-2 MIL-STD-1553
Channels, Small Mezzanine with Ethernet Host Interface*, product data
sheet, doc. no. 2108-1, Alta Data Technologies LLC, Rio Rancho, NM,
USA. [Online]. Available:
https://www.altadt.com/product/mez-e1553-embedded-1553-with-ethernet/
Direct download (unverified by fetch): https://www.altadt.com/download/mez-e1553-data-sheet
Local verified copy: `docs/datasheets/alta-data-technologies-meze-1553-datasheet.pdf`
(2 pp.).
Section/page: p. 1, "Key Features" — "Fully Compliant to MIL-STD-1553B/C
Notice II/IV, 1553A and Link-16"; "Guaranteed MIL-STD-1553A/B/C
Compliant," AS4111 5.2 protocol test reports; 1–2 independent dual
redundant channels; 10/100/1000 Ethernet host interface. p. 2,
"General" — MIL-STD-1553B/C Notice II & IV, 1553A and Link-16; 3.3 V
power, 1 A/1.5 A max; operating temperature −40°C to +85°C (extended).
This is a host-interface mezzanine module, not a bus-transceiver IC;
confirms MIL-STD-1553B/C compliance at the module level but does not
substitute for the DoD standard text itself, [7].
Candidate module for the MIL-STD-1553B protocol interface (TODO.md
§6.10); not yet selected in a bill of materials.
Cited in: docs/datasheets/ (local reference only; not yet cited in
README.md pending BOM selection).
Date accessed: 2026-08-02.

---

**[12]** Analog Devices, Inc., *ADM3232E — ±15 kV ESD Protected, 3.3 V,
RS-232 Line Driver/Receiver*, data sheet, Rev. B, Analog Devices, Inc.,
Wilmington, MA, USA. [Online]. Available:
https://www.analog.com/media/en/technical-documentation/data-sheets/ADM3232E.pdf
(live fetch blocked: HTTP 403, 2026-08-02).
Product page: https://www.analog.com/en/products/adm3232e.html
(live fetch blocked: HTTP 403, 2026-08-02).
No local copy yet — `UNVERIFIED — needs primary source (see TODO.md)`.
Section/page: not verified — this session's WebFetch tool returned HTTP
403 for every domain attempted (ti.com, analog.com, digikey.com, and a
neutral non-vendor control URL), so no PDF could be opened directly.
Specs below are corroborated across multiple independent distributor/
search-indexed excerpts of the manufacturer's own datasheet text, not
read from the primary document: 2-channel RS-232/V.28 transceiver;
operates from a single 3.3 V supply (matches the project MCU's native
logic rail, [1]); data rates up to 460 kbps; conforms to EIA/TIA-232-E
and ITU-T V.28; ±15 kV ESD protection on both RS-232 and TTL/CMOS I/O
pins; 16-lead SOIC/TSSOP. Alternative considered: Texas Instruments
MAX3232 (literature number SLLS410, exact current revision letter
conflicting across sources — UNVERIFIED), 3–5.5 V supply, ±15 kV ESD,
up to 250 kbit/s; not selected over ADM3232E because it needs a wider
supply range for the same 3.3 V-native benefit.
Candidate part for the RS-232 protocol interface (TODO.md §6.6); not yet
selected in a bill of materials; needs a local verified PDF copy before
citation can be upgraded from candidate to settled.
Cited in: docs/datasheets/ (not yet present; not yet cited in README.md
pending BOM selection).
Date accessed: 2026-08-02.

---

**[13]** Texas Instruments Incorporated, *BLDC and PMSM Control Using
Sensorless FOC Algorithm Based on MSPM0 MCUs*, application brief, doc.
SLAAE96A, Texas Instruments Incorporated, Dallas, TX, USA. [Online].
Available: https://www.ti.com/lit/ab/slaae96a/slaae96a.pdf
(live fetch blocked: HTTP 403, 2026-08-02); also
https://www.ti.com/document-viewer/lit/html/SLAAE96
(live fetch blocked: HTTP 403, 2026-08-02).
No local copy yet — `UNVERIFIED — needs primary source (see TODO.md)`.
Section/page: not verified — live fetch blocked this session (same
tooling failure as [12]); content corroborated via multiple independent
search-indexed excerpts, not read from the primary PDF. Indexed content
explicitly lists MSPM0G3505/3506/3507 (this project's MCU family, [1])
among supported devices; describes an observer-based sensorless
field-oriented-control algorithm that estimates rotor position/speed
from motor electrical signals using the MCU's own ADC/OPA/COMP
peripherals (already present per [1], p. 77, Table 10-1: "2x ADC, 2x
OPA, 3x COMP") — requiring no additional feedback-sensor BOM part for
either Closed-loop differential or Closed-loop PID control (TODO.md
§§8.2–8.3). Related TI documents surfaced but not independently
verified: SLAAE95A ("Trapezoidal control of BLDC motors using MSPM0")
and SPRAD34 ("MSPM0 Motor Control" middleware application note), both
suggesting a sensored/hybrid path is also supported by the same SDK.
Fallback candidate if a Hall-sensored (or hybrid start-up) topology is
preferred instead: Texas Instruments, *DRV5013 Digital-Latch Hall
Effect Sensor*, datasheet (revision letter conflicting across sources,
Rev. N vs. Rev. K — UNVERIFIED), with companion application brief doc.
SLVAEG3 ("Brushless DC Motor Commutation Using Hall-Effect Sensors")
naming DRV5013 for BLDC commutation feedback; indexed specs: 2.5–38 V
supply with reverse-polarity protection to −22 V, open-drain output
(30 mA sink, pullable to the MCU's 3.3 V rail), 30 kHz bandwidth,
SOT-23/TO-92. URL: https://www.ti.com/lit/ds/symlink/drv5013.pdf (live
fetch blocked: HTTP 403, 2026-08-02).
Candidate design decision for the control-loop feedback question
(TODO.md §§8.2–8.3); not yet settled in a design doc.
Cited in: docs/datasheets/ (not yet present; not yet cited in README.md).
Date accessed: 2026-08-02.

---

**[14]** E-One Moli Energy Corp. (Molicel), *Product Data Sheet, Model
INR-21700-P42A Lithium-Ion Rechargeable Battery*, doc.
INR21700P42A-V4-80092 (revision provenance inconsistent across mirrors —
one mirror captioned "Doc #: INR21700P42A-01, Rev.: 0.2," another
"Version 1.7" — exact current revision still `UNVERIFIED`, the local
PDF's single page does not itself print a revision code), E-One Moli
Energy Corp., Taiwan. [Online]. Available:
https://www.molicel.com/wp-content/uploads/INR21700P42A-V4-80092.pdf
(live fetch blocked: HTTP 403, 2026-08-02).
Local copy: `docs/datasheets/INR21700P42A-V4-80092.pdf` — `VERIFIED`
(added 2026-08-02).
Section/page: single-page datasheet, "Cell Characteristics" /
"Physical Characteristics" tables. Confirmed directly from the local
PDF, matching every figure previously corroborated only via secondary
sources — no discrepancy found: nominal 3.6 V; charge 4.2 V; discharge
2.5 V; standard charge current 4.2 A (1.5 h); capacity 4200 mAh
typical / 4000 mAh minimum (15.5 Wh / 14.7 Wh); continuous discharge
45 A; AC impedance (1 kHz) 10 mΩ, DC impedance (10 A/1 s) 16 mΩ;
charge temperature 0°C–45°C, discharge temperature −40°C–60°C; energy
density 615 Wh/l / 230 Wh/kg; diameter 21.7 mm max, height 70.2 mm max,
weight 70 g max, steel can.
Cross-check source (pouch/LiPo format, corroborating but not primary):
Kokam Co., Ltd., *Cell Specification Data, SLPB 65216216*, Kokam Co.,
Ltd., Republic of Korea, available
https://liionbms.com/pdf/kokam/SLPB65216216.pdf (live fetch blocked,
2026-08-02) — indexed content: nominal 3.7 V, charge 4.2 V ±0.03 V,
discharge cutoff 2.7 V, differing from [14]'s 2.5 V cutoff because
minimum cutoff voltage is cell-model-dependent (industry range ≈2.5–3.0
V/cell). Standards considered as regulatory backing but not used as the
numeric source (paywalled, catalog-only): IEC 62133-2:2017, IEC, Geneva,
https://webstore.iec.ch/en/publication/32662 (section/page not verified
— paywalled); UL 2054, Ed. 3 (2021-11-17), UL Standards & Engagement,
https://www.shopulstandards.com/ProductDetail.aspx?productId=UL2054_3_S_20211117
(section/page not verified — paywalled).
Per-tier pack voltage table derived from this entry (nominal / max /
min, cells × per-cell value): 2S 7.2/8.4/5.0 V; 4S 14.4/16.8/10.0 V; 6S
21.6/25.2/15.0 V; 8S 28.8/33.6/20.0 V; 12S 43.2/50.4/30.0 V. Design
decision flagged per `AGENTS.md` §4: the 2.5 V/cell minimum is specific
to this cell; a different cell selection (e.g. [14]'s Kokam cross-check
at 2.7 V/cell, or the commonly-seen 3.0 V/cell convention) shifts the
"min" column upward. Recommend re-deriving this table against the
actual cell selected at BOM finalization (TODO.md §10.2) and using the
highest (most conservative) published cutoff among candidates for
FET/regulator voltage-margin derating in the interim.
Alternative real cells considered: E-One Moli Energy's own
INR-21700-P45B, primary datasheet now local — see [26], `VERIFIED`;
and Samsung SDI INR21700-40T, primary datasheet now local — see [27],
`VERIFIED` but see that entry's confidentiality-marking flag before
redistributing it further. No US/UK/EU-headquartered cell manufacturer
was found competing in this high-drain 21700 cylindrical-cell class —
production is concentrated in Taiwan/South Korea/Japan/China
industry-wide, not a gap specific to this BOM choice.
Candidate cell for voltage-tier derating (TODO.md §5.2); not yet
selected in a bill of materials.
Cited in: docs/datasheets/INR21700P42A-V4-80092.pdf;
symbols/specs/INR21700_P42A.json (generic 2-terminal cell symbol);
builds/6s/50A/CAN_485_faraday/README.md (6S pack BOM, ×6 cells).
Date accessed: 2026-08-02.

---

**[15]** Department of Defense (USA), *Interface Standard: Requirements
for the Control of Electromagnetic Interference Characteristics of
Subsystems and Equipment*, MIL-STD-461G, U.S. Department of Defense,
2015-12-11 (supersedes MIL-STD-461F, 2007-12-10). [Online,
government-hosted mirror]. Available:
https://s3vi.ndc.nasa.gov/ssri-kb/static/resources/MIL-STD-461G.pdf
(live fetch blocked: HTTP 403, 2026-08-02 — not independently
re-verified against this repo's [7], which uses the same host class).
Section/page: not verified — live fetch blocked this session; content
corroborated via independent secondary technical summaries (Interference
Technology magazine's reviews of MIL-STD-461 bonding/grounding and
general requirements), not read from the primary PDF. Corroborated
scope: general requirements for EUT bonding to a ground plane (or a
defined metallic ground plane when installation is unspecified), and
dedicated radiated/conducted emissions and susceptibility test methods
(e.g. RE102, CE102, CS101/CS114/CS115/CS116) whose rationale motivates
shielding and grounding as mitigations. Scope gap flagged explicitly per
`AGENTS.md` §1.3: MIL-STD-461G's own text treats "isolation" mainly as
test-setup isolation transformers (protecting measurement equipment),
not as a named EUT design-mitigation category — it is a fitting
citation for the Grounding and Faraday/shielding EMI tiers (TODO.md
§7.1) but not for the Isolation tier; see [16] for that.
Cited in: README.md (Protocol/EMI hardening context — Grounding, Faraday
tiers); TODO.md §7.1; builds/6s/50A/CAN_485_faraday/README.md (Faraday-tier
justification, RE102/CE102 shielding-effectiveness rationale against the
500 W/m² broadband RF requirement's derived ~434 V/m field strength).
Date accessed: 2026-08-02.

---

**[16]** International Electrotechnical Commission, *Audio/video,
information and communication technology equipment — Part 1: Safety
requirements*, IEC 62368-1:2018, Ed. 3.0, IEC, Geneva, Switzerland,
2018-10. [Online]. Available: https://webstore.iec.ch/en/publication/27412
Section/page: not verified — standard is paywalled; only the IEC
catalog/scope listing is accessible without purchase (same pattern as
this repo's [6]). Cited as the authoritative basis for basic/reinforced
insulation and creepage/clearance classification, against which
isolation components such as [18] are certified — used for the
Isolation EMI-hardening tier (TODO.md §7.1) rather than MIL-STD-461G
([15]), whose own scope does not name "isolation" as a design
mitigation category (see [15]'s scope-gap note).
Cited in: README.md (EMI hardening — Isolation tier); TODO.md §7.1.
Date accessed: 2026-08-02.

---

**[17]** International Electrotechnical Commission, *Electromagnetic
compatibility (EMC) — Part 5: Installation and mitigation guidelines —
Section 2: Earthing and cabling*, IEC/TR 61000-5-2:1997, Ed. 1.0, IEC,
Geneva, Switzerland, 1997-11 (Technical Report, not a full International
Standard; current withdrawal/stabilization status not verified this
session). [Online]. Available:
https://webstore.iec.ch/en/publication/4234
Section/page: not verified — paywalled; catalog abstract confirms scope
is "earthing practices ... in industrial, commercial and residential
installations" for EMC-sensitive equipment — a layout/practice
guideline, not a purchasable component spec. Used to support treating
the Grounding EMI-hardening tier (TODO.md §7.1) as layout/practice-only
(single-point ground topology, continuous ground-plane layout,
star-grounding of high-di/dt power-stage return paths) rather than a
BOM part, alongside [15]'s general bonding requirements.
Cited in: README.md (EMI hardening — Grounding tier); TODO.md §7.1–7.2.
Date accessed: 2026-08-02.

---

**[18]** Analog Devices, Inc., *ADuM4221/ADuM4221-1/ADuM4221-2 —
Isolated, Half-Bridge Gate Drivers with Adjustable Dead Time, 4 A
Output*, data sheet, Rev. B, Analog Devices, Inc., Wilmington, MA, USA.
[Online]. Available:
https://www.analog.com/media/en/technical-documentation/data-sheets/adum4221_4221-1_4221-2.pdf
(live fetch blocked: HTTP 403, 2026-08-02).
No local copy yet — `UNVERIFIED — needs primary source (see TODO.md)`.
Section/page: not verified — live fetch blocked this session; content
corroborated via independent search-indexed excerpts, not read from the
primary PDF. Indexed content: ADI iCoupler-based digital isolation;
5700 V rms isolation rating; datasheet's own safety limit data table
indicates suitability for reinforced isolation per [16]; UL 1577 proof
test at ≥6840 V rms for 1 s; 16-lead wide-body SOIC (increased
creepage/clearance). Candidate for galvanic isolation on the gate-drive
signal path between MCU-side logic and high-side/low-side FET gates —
the Isolation EMI-hardening tier (TODO.md §7.1). Note: TODO.md §7.1
should specify whether the Isolation tier covers gate-drive isolation,
feedback/telemetry signal isolation, or both, before final part
selection — ADuM4221's non-gate-driver siblings (e.g. ADuM3220,
ADuM1200-series) would apply to the signal-only case.
Candidate part; not yet selected in a bill of materials.
Cited in: docs/datasheets/ (not yet present; not yet cited in README.md).
Date accessed: 2026-08-02.

---

**[19]** Würth Elektronik eiSos GmbH & Co. KG, *WE-SHC Two-piece
Seamless Shielding Cabinet*, order code 3671375, datasheet rev.
ViM 002.000 (2025-05-12), Würth Elektronik eiSos GmbH & Co. KG,
Waldenburg, Germany. [Online]. Available:
https://www.we-online.com/components/products/datasheet/3671375.pdf
(live fetch blocked: HTTP 403, 2026-08-02).
Local copy: `docs/datasheets/3671375.pdf` — `VERIFIED` (added 2026-08-02).
Section/page: p.1 dimensional drawing and general information, p.1
"Assembly with Frame." Confirmed directly from the local PDF: inner
29.5 mm × 37.7 mm / outer 30.1 mm × 38.3 mm, height 3.8 mm (ref); core
steel, tin plating; operating temperature −40 °C to +125 °C; RoHS/REACh
compliant. **Correction from the previously secondary-sourced entry:**
order code 3671375 is the **cover only** — the datasheet's own text
reads "Assembly with Frame: Frame (3670375), Cover (3671375)." A
complete shield requires both order codes. **Update 2026-08-02: the
frame's own datasheet has since been added and verified — see [30].**
This local datasheet is a 5-page mechanical/packaging spec only and
does **not** contain a shielding-effectiveness figure — the "up to
60 dB, 500 MHz–3 GHz" claim carried over from the prior
secondary-sourced pass remains unverified against a primary source
(the frame's datasheet [30] doesn't state it either); strike it from
any "verified" claim until a shielding-effectiveness test report is
obtained.
Candidate for board-level shielding over the gate-drive/high-di/dt
switching node area — the Faraday EMI-hardening tier (TODO.md §7.1).
Alternative real manufacturers in this space, not further verified:
Laird Technologies, Leader Tech.
Candidate part; not yet selected in a bill of materials.
Cited in: docs/datasheets/3671375.pdf; symbols/WE_SHC_3671375.kicad_sym
(mechanical placeholder symbol, cover only — see [30]/`WE_SHC_3670375.kicad_sym`
for the frame); symbols/specs/WE_SHC_3671375.json (verification field
updated with the frame/cover correction);
builds/6s/50A/CAN_485_faraday/README.md (Faraday-tier BOM).
Date accessed: 2026-08-02.

---

**[20]** Infineon Technologies AG, *IRFB4110PbF — HEXFET Power MOSFET*,
datasheet (revision/date not printed as a discrete field in the local
PDF's extracted text; page footer shows a 2014-era International
Rectifier copyright artifact, pre-dating Infineon's acquisition of IR —
exact current revision still `UNVERIFIED`), Infineon Technologies AG,
Neubiberg, Germany. [Online]. Available:
https://www.infineon.com/assets/row/public/documents/24/49/infineon-irfb4110-datasheet-en.pdf
(live fetch blocked: HTTP 403, 2026-08-02).
Local copy: `docs/datasheets/infineon-irfb4110-datasheet-en.pdf` —
`VERIFIED` (added 2026-08-02).
Section/page: p.1 "Absolute Maximum Ratings" / electrical summary table,
p.2 "Static @ TJ = 25°C" table. Confirmed directly from the local PDF,
matching every figure previously corroborated only via secondary
sources — no discrepancy found: VDSS = 100 V; RDS(on) = 3.7 mΩ
typ./4.5 mΩ max; ID (silicon-limited, TC = 25°C) = 180 A; ID
(package/wire-bond-limited, TC = 25°C) = 120 A (the datasheet's own
footnote: "Bond wire current limit is 120A... current limitations
arising from heating of the device leads may occur with some lead
mounting arrangements" — confirms the more conservative 120 A figure,
already used in this build's design margin, is the correct one to
design against); VGS(th) = 2.0–4.0 V; package TO-220AB.
Voltage-headroom design assumption (judgment call per `AGENTS.md` §4,
not itself a datasheet claim): sized against a 4.2 V/cell LiPo/Li-ion
max-charge convention (cf. [14]) → 12S max ≈ 50.4 V, giving ~2× headroom
against this FET's 100 V rating; this convention is not yet tied to the
project's actual selected cell.
Proposed for all 7 amperage tiers (10A–120A) with parallel count per
phase leg varying: 1× (10A–50A), 2× (80A), 3× (120A) — chosen to
maximize BOM commonality across tiers per the research brief, at the
cost of being oversized/cost-inefficient for the smallest tiers (10A–30A),
where a smaller SO-8 SMD FET would be leaner if part-count commonality
were not prioritized.
Alternative real manufacturers in this space, not further verified
(2026-08-02 search pass, secondary/distributor listings only — no
primary datasheet opened for any of them either): onsemi (USA),
STMicroelectronics (Switzerland/EU), Toshiba (Japan) each publish
comparable 100 V TO-220 N-channel power MOSFETs aimed at motor-drive
applications; none was found with a head-to-head RDS(on)/ID spec
comparison from a primary source this session, so no like-for-like
numeric comparison is possible yet.
Candidate part for the power stage (TODO.md §5.1); not yet selected in
a bill of materials.
Cited in: docs/datasheets/infineon-irfb4110-datasheet-en.pdf;
symbols/IRFB4110PBF.kicad_sym (standard TO-220 G/D/S pinout);
builds/6s/50A/CAN_485_faraday/README.md (50A-tier BOM, ×6: 1 per switch
position × 2 positions × 3 phases).
Date accessed: 2026-08-02.

---

**[21]** Texas Instruments Incorporated, *DRV8350, DRV8350R, DRV8353,
DRV8353R: 9-V to 100-V Three-Phase Smart Gate Driver*, datasheet,
literature no. SLVSDY6A, August 2018 (revised June 2019), Texas
Instruments Incorporated, Dallas, TX, USA. [Online]. Available:
https://www.ti.com/lit/ds/symlink/drv8353.pdf.
Local copy: `docs/datasheets/drv8353.pdf` (101 pp.) — `VERIFIED` (added
2026-08-02). Corrects the prior revision guess ("Rev. A, Aug. 2018,
later revision letter likely exists") — SLVSDY6A *is* the current
revision, per the local PDF's own header on every page.
Section/page: p.3, Sec. 5 "Device Comparison Table" — confirms DRV8353S
= 3 integrated shunt amplifiers, no buck regulator, SPI interface,
distinct from DRV8353H (same shunt/buck config, hardware-pin
configuration instead of SPI) and from the DRV8350-family (0 shunt
amplifiers) and DRV8353R-family (adds a 350 mA buck regulator) parts
covered by the same document. pp.6-7, Sec. 6 "Pin Configuration and
Functions," "DRV8353S RTA Package, 40-Pin WQFN With Exposed Thermal
Pad" and "Pin Functions — 40-Pin DRV8353 Devices" — full verified
40-pin map, see `symbols/specs/DRV8353S.json`. Absolute max ratings
(p.11 area): applied PWM 0-200 kHz (INHx/INLx); gate-drive current
0-25 mA average (GHx/GLx); shunt-amp output current 0-5 mA (SOx). Sec.
8.3.1.4.1 "IDRIVE: MOSFET Slew-Rate Control" (p.36) confirms IDRIVE is
a real, documented feature of this device family for controlling
MOSFET VDS slew rate via gate-drive current — but on the S (SPI)
variant used here it is set through an SPI register, not the
dedicated IDRIVE pin that exists only on the H (hardware-configured)
variant (that pin is correctly absent from `DRV8353S.json`'s pin map).
Recommended VM operating range (device-family absolute max is 9-100 V
per the front-page banner; VM-specific recommended-operating figures
were not independently re-extracted this pass) spans this repo's 2S
through 12S pack-voltage range per [14] with meaningful headroom at
every tier — the previously-flagged "~25 V headroom at 12S, tighter
than the FET's ~2×" concern is unchanged by this verification pass and
still needs the transient/spike analysis (e.g. a TVS clamp on VM) noted
before locking the 10S/12S BOM variant.
Proposed as the same part for all 7 amperage tiers — the SPI-programmable
IDRIVE setting and CSA gain register absorb the per-tier differences
rather than requiring a different gate-driver part.
Alternative real manufacturer considered: Infineon MOTIX™
TLE9180D-31QK, primary datasheet now local — see [29], `VERIFIED`.
Candidate part for the power stage (TODO.md §5.1); not yet selected in
a bill of materials.
Cited in: docs/datasheets/drv8353.pdf; symbols/DRV8353S.kicad_sym
(VERIFIED full 40-pin RTA/WQFN pin numbering — see
symbols/specs/DRV8353S.json "verification" field);
builds/6s/50A/CAN_485_faraday/README.md (50A-tier BOM; note on possible
overlap with INA240 [22]'s external current-sense function).
Date accessed: 2026-08-02.

---

**[22]** Texas Instruments Incorporated, *INA240 −4-V to 80-V,
Bidirectional, Ultra-Precise Current Sense Amplifier With Enhanced PWM
Rejection*, datasheet, literature no. SBOS662C, July 2016 (revised
December 2021), Texas Instruments Incorporated, Dallas, TX, USA.
[Online]. Available: https://www.ti.com/lit/gpn/INA240 (live fetch
blocked: HTTP 403, 2026-08-02).
Local copy: `docs/datasheets/ina240.pdf` — `VERIFIED` (added 2026-08-02).
**Correction from the previously secondary-sourced entry:** the literature
number is SBOS662C, not the previously guessed/unverified SBOS633.
Section/page: p.3 Sec. 5 "Device Comparison" Table 5-1, Sec. 6 "Pin
Configuration and Functions" Table 6-1 and Figures 6-1/6-2. Confirmed
directly from the local PDF, matching every figure previously
corroborated only via secondary sources — no discrepancy found:
common-mode voltage range −4 V to +80 V independent of supply (for a
low-side per-phase shunt referenced near ground, this covers all
voltage tiers 2S–12S per [14]); four fixed gains, one per part suffix
(INA240A1 = 20 V/V, A2 = 50 V/V, A3 = 100 V/V, A4 = 200 V/V); enhanced
PWM rejection, explicitly marketed for motor-drive/PWM common-mode
transients; supply 2.7–5.5 V, 2.4 mA max; 132 dB DC CMRR / 93 dB AC
CMRR at 50 kHz; offered in 8-pin TSSOP (PW) and 8-pin SOIC (D)
packages, which use *different* pin numbering for the same 8 signals
(NC, IN+, IN−, GND, VS, REF1, REF2, OUT) — see
`symbols/specs/INA240.json` for the full per-package pin table.
Candidate part answering the current-sensing selection (TODO.md §5.3);
proposed as the same part for all 7 amperage tiers, paired with the
Vishay shunt series [23] whose resistance value (and, at 80A/120A,
parallel count) varies by tier.
Alternative real manufacturer considered: Analog Devices AD8410A,
primary datasheet now local — see [28], `VERIFIED`.
Candidate part for the power stage; not yet selected in a bill of
materials.
Cited in: docs/datasheets/ina240.pdf; symbols/INA240.kicad_sym (VERIFIED
D/SOIC-8 pin numbering — see symbols/specs/INA240.json "verification"
field); builds/6s/50A/CAN_485_faraday/README.md (50A-tier BOM; open
question on overlap with DRV8353S [21]'s integrated shunt-sense
amplifiers).
Date accessed: 2026-08-02.

---

**[23]** Vishay Dale (Vishay Intertechnology, Inc.), *WSLP — Power Metal
Strip® Resistors, Very High Power (to 3 W), Low Value (Down to
0.0005 Ω), Surface-Mount*, datasheet, document no. 30122, revision
09-Sep-2024, Vishay Intertechnology, Inc., Malvern, PA, USA. [Online].
Available: https://www.vishay.com/docs/30122/wslp.pdf.
Local copy: `docs/datasheets/wslp.pdf` — `VERIFIED` (added 2026-08-02).
Section/page: p.1 "Standard Electrical Specifications" table.
Confirmed directly from the local PDF, matching every figure previously
corroborated only via secondary sources — no discrepancy found:
WSLP2512 power rating 3.0 W at 70°C; resistance value range 0.003 Ω to
0.01 Ω (±0.5% tolerance) or 0.0005 Ω to 0.01 Ω (±1.0% tolerance,
i.e. the previously-cited 0.5 mΩ–10 mΩ range); weight 63.6 g/1000
pieces; AEC-Q200 rev. D qualified; welded (not clad) construction.
Per-tier sizing (engineering calculation against the 3 W/2512-package
rating, not itself a datasheet claim): 10 mΩ (10A), 5 mΩ (20A), 2 mΩ
(30A), 1.5 mΩ (40A), 1 mΩ (50A); at 80A/120A a single WSLP2512 exceeds
its 3 W rating (3.2 W and 7.2 W respectively at the sizes that would
otherwise apply), so 2–4 devices in parallel (or a higher-power Vishay
sibling part, not yet selected) are required — flagged as an open gap,
not a drop-in substitution. Alternative considered: Allegro
MicroSystems ACS732/ACS733 galvanically-isolated Hall-effect current
sensor ICs (up to ±65 A, e.g. ACS733KLATR-65AB-T, 20 mV/A, <1 mΩ
internal resistance, 3600–4800 VRMS isolation) — not selected because
the family tops out below the 80A/120A tiers, breaking BOM commonality;
a higher-range Allegro part (e.g. ACS781/ACS758 family) would be needed
for those tiers and was not pursued further.
Candidate part answering the current-sensing selection (TODO.md §5.3);
not yet selected in a bill of materials; the 80A/120A shunt sizing gap
remains open.
Cited in: docs/datasheets/wslp.pdf; symbols/WSLP2512.kicad_sym (generic
2-terminal pinout);
builds/6s/50A/CAN_485_faraday/README.md (50A-tier BOM, 1 mΩ ×3, one per
phase).
Date accessed: 2026-08-02.

---

**[24]** Vishay Dale (Vishay Intertechnology, Inc.), *WSL — Power Metal
Strip® Resistors, Low Value (Down to 0.0005 Ω), Surface-Mount*,
datasheet, document no. 30100, revision 23-Nov-2023, Vishay
Intertechnology, Inc., Malvern, PA, USA. [Online]. Available:
https://www.vishay.com/docs/30100/wsl.pdf.
Local copy: `docs/datasheets/wsl.pdf` — `VERIFIED` (added 2026-08-02).
**This is NOT the part cited at [23].** [23] (WSLP2512, this build's
actual BOM candidate) is document no. 30122, a *different* Vishay
family — the WSLP series. This document's own subtitle reads "Upgrade
for Higher Current to WSLP..." i.e. the WSL family's own datasheet
directs customers *away* from WSL and toward WSLP when higher current
handling (which is exactly why WSLP2512 was selected for this BOM) is
needed. Section/page: p.2, "Technical Specifications" table — WSL2512
exists as a sibling size in this family, but its power/resistance
range is a different (generally lower) figure than WSLP2512's 3 W/2512
rating already cited at [23]; p.3, "Packaging" table confirms WSL2512
as one of six sizes (WSL0603 through WSL2816) in this document, none
of which is the WSLP2512 part number itself. Not currently used to
satisfy any BOM line — kept as a reference in case the WSL (not WSLP)
family becomes relevant to a lower-current tier later, or as a
cross-check for the "P" upgrade's baseline family.
Cited in: docs/datasheets/wsl.pdf only — not yet referenced from any
build BOM or symbol.
Date accessed: 2026-08-02.

---

**[25]** Würth Elektronik eiSos GmbH & Co. KG, *WE-SHC Shielding
Cabinet*, order code 3690103020, datasheet rev. ViMa 001.002
(2020-11-12), Würth Elektronik eiSos GmbH & Co. KG, Waldenburg,
Germany. [Online]. Available:
https://www.we-online.com/components/products/datasheet/3690103020.pdf
(not independently re-fetched — local copy provided directly).
Local copy: `docs/datasheets/3690103020.pdf` — `VERIFIED` (added
2026-08-02).
**This is NOT a substitute for the missing WE-SHC Frame (3670375) that
[19]'s BOM line needs.** Section/page: p.1 dimensional drawing —
confirmed directly from the local PDF: this is a "One Piece Cover"
type, inner 2.59 mm × 2.59 mm, outer 3.1 mm × 3.1 mm, brass core with
Ni-flash/Sn plating. That is a single-component-scale shield (roughly
3 mm square) for shielding one small IC or coil, not a board-area
shield over a switching-node region like the 29.5 mm × 37.7 mm
[19]/3671375 cover this build actually uses. Adding this part does not
close the "3670375 frame missing" gap noted at [19] and in
`builds/6s/50A/CAN_485_faraday/README.md` — it is a different WE-SHC
product entirely, at a different scale, for a different application.
Not currently used to satisfy any BOM line in this repo.
Cited in: docs/datasheets/3690103020.pdf only — not yet referenced from
any build BOM or symbol.
Date accessed: 2026-08-02.

---

**[26]** E-One Moli Energy Corp. (Molicel), *Product Data Sheet, Model
INR-21700-P45B Lithium-Ion Rechargeable Battery*, Version 1.2, E-One
Moli Energy Corp., Taiwan. [Online]. Available:
https://www.molicel.com/inr-21700-p45b/ (not independently re-fetched —
local copy provided directly).
Local copy: `docs/datasheets/molicel_p45b.pdf` — `VERIFIED` (added
2026-08-02).
Alternative to [14] considered for TODO.md §5.2, same manufacturer/
family. Section/page: single-page datasheet, "Cell Characteristics" /
"Physical Characteristics" tables. Confirmed directly from the local
PDF: nominal 3.6 V; charge 4.2 V; discharge 2.5 V; standard charge
current 4.5 A, maximum charge current 13.5 A (70°C cut-off); continuous
discharge 45 A (80°C cut-off); capacity 4500 mAh typical / 4300 mAh
minimum (16.2 Wh / 15.5 Wh) — vs. [14]'s 4200/4000 mAh, roughly +7%
capacity, matching the figure previously cited from secondary sources;
AC impedance (30% SOC) 7 mΩ, DC impedance (50% SOC) 15 mΩ — not
directly comparable to [14]'s stated test conditions (1 kHz AC / 10A
DC), so the previously-cited "~22% lower DCR" figure is **not**
independently confirmed by this primary source and should be treated
as still secondary-sourced until both cells are measured under
identical conditions; diameter 21.55 mm max, height 70.15 mm max,
weight 70 g max, steel can (both dimensions marginally larger diameter,
marginally shorter height than [14] — confirm mechanical fit before
any swap). Not currently selected in this repo's BOM.
Cited in: docs/datasheets/molicel_p45b.pdf only — not yet referenced
from any build BOM or symbol.
Date accessed: 2026-08-02.

---

**[27]** Samsung SDI Co., Ltd., *Specification of Product: Lithium-ion
Rechargeable Cell for Power Tools, Model INR21700-40T*, Spec. No.
INR21700-40T, Version No. 0.0, Samsung SDI Co., Ltd., Republic of
Korea, 2017-12.
Local copy: `docs/datasheets/samsung_40T.pdf` — `VERIFIED` (added
2026-08-02), **but flagged**: the document's own header/footer marks
every page "SAMSUNG SDI Confidential Proprietary." This repo has no
license or distribution agreement with Samsung SDI on file. Committing
a vendor-marked-confidential document to a shared/public repository may
not be permitted under Samsung SDI's own terms regardless of technical
citation value — this is a distribution/IP question for the repo owner
to resolve (e.g. remove the file and cite it as `UNVERIFIED — local
copy withheld, confidentiality-marked` instead), not something this
citation entry can wave through on AGENTS.md sourcing grounds alone.
Alternative to [14] considered for TODO.md §5.2. Section/page: p.1
(Sec. 3.0) "Nominal specifications." Confirmed directly from the local
PDF: nominal voltage 3.6 V; standard discharge capacity min. 4000 mAh
(0.5C charge/0.2C discharge); rated discharge capacity min. 3900 mAh
(1.5C charge/10A discharge); standard charge CCCV 2A/4.2V/200mA
cut-off; max. continuous discharge 35A without a temperature cut, 45A
with an 80°C surface-temperature cut (directly comparable to [14]'s
45A rating, which does not state whether it is temperature-cut-limited
— an open comparability gap); discharge cut-off 2.5V; cycle life
≥2400mAh (60% of standard capacity) after 250 cycles; weight 70.0g max;
height 70.30mm max, diameter 21.22mm max. This is closer to a
like-for-like primary-source comparison against [14] than the earlier
secondary-sourced "P42A outperforms 40T" claim, but the two datasheets'
test conditions (charge/discharge C-rates, temperature cuts) are not
identical, so a precise capacity/DCR ranking still isn't possible from
these two documents alone. Not currently selected in this repo's BOM.
Cited in: docs/datasheets/samsung_40T.pdf only — not yet referenced
from any build BOM or symbol.
Date accessed: 2026-08-02.

---

**[28]** Analog Devices, Inc., *AD8410A: −2 V to 70 V Wide Input
Voltage Range, 2.2 MHz High Bandwidth, Current-Sense Amplifier with PWM
Rejection and Gain 20 V/V*, data sheet, Rev. D (2025-12), Analog
Devices, Inc., Wilmington, MA, USA. [Online]. Available:
https://www.analog.com/media/en/technical-documentation/data-sheets/ad8410a.pdf
(not independently re-fetched — local copy provided directly).
Local copy: `docs/datasheets/ad8410a.pdf` — `VERIFIED` (added
2026-08-02).
Alternative to [22] considered for TODO.md §5.3. Section/page: p.1
"Features." Confirmed directly from the local PDF, correcting the
prior secondary-sourced figures: 2.2 MHz small-signal −3 dB bandwidth;
typical ±0.21 µV/°C offset drift; maximum ±200 µV offset over
temperature; typical DC CMRR 142 dB (vs. [22]'s 132 dB — AD8410A is
*better* here, reversing the earlier unverified assumption); typical AC
CMRR at 50 kHz 96 dB (vs. [22]'s 93 dB, also marginally better);
common-mode range −2 V to +70 V continuous operation, −20 V to +85 V
continuous survival (narrower operating range than [22]'s −4 V to
+80 V, as previously noted, but confirmed now from the primary source);
single fixed initial gain of 20 V/V (vs. [22]'s four selectable gains
20/50/100/200 V/V — still the key practical drawback for this BOM's
per-tier gain flexibility, confirmed); supply 2.9 V–5.5 V; packages
8-lead SOIC_N, 8-lead MSOP, 10-lead MSOP; AEC-Q100 qualified for
automotive use (a qualification tier [22]'s datasheet does not claim
for the base INA240, only for a separate INA240-Q1 automotive variant
not otherwise discussed in this repo). Not currently selected in this
repo's BOM.
Cited in: docs/datasheets/ad8410a.pdf only — not yet referenced from
any build BOM or symbol.
Date accessed: 2026-08-02.

---

**[29]** Infineon Technologies AG, *TLE9180D-31QK: Bridge Driver IC*,
datasheet, Infineon Technologies AG, Neubiberg, Germany. [Online].
Available: https://www.infineon.com/part/TLE9180D-31QK (not
independently re-fetched — local copy provided directly).
Local copy: `docs/datasheets/infineon-tle9180d-31qk-datasheet-en.pdf`
(212 pp.) — `VERIFIED` (added 2026-08-02).
Alternative to [21] considered for TODO.md §5.1. Section/page: p.1
"Features." Confirmed directly from the local PDF, resolving the prior
"unconfirmed against this build's voltage span" hedge: specified supply
voltage range 5.5 V to 60 V — this **does** comfortably cover the
6S (≤25.2 V) through 12S (≤50.4 V) pack-voltage span already derived
from [14], with more margin at 12S than [21]'s DRV8353S 9–75 V range
gives relative to its own previously-flagged transient/spike concern
(60 V ceiling vs. 50.4 V max pack voltage is ~19% headroom, tighter
than [20]'s FET headroom but not a hard blocker); high-voltage robustness
of motor-connection pins to −15 V/+90 V; logic operation down to 3 V;
0–100% adjustable PWM duty cycle; SPI control and supervision readout;
3 integrated current-sense amplifiers for shunt signal conditioning;
reverse-diode FET temperature sensing; AEC-Q qualified; PRO-SIL™ safety
documentation (Safety Manual, Safety Analysis Summary Report) available
up to 28 V rails — this project's own 6S/8S tiers are within that 28 V
safety-documentation ceiling, but 12S (50.4 V) is not, so the ISO 26262
pedigree previously cited as a reason to consider this part does not
uniformly apply across every voltage tier in this repo's shared-BOM
design. Package/pinout not extracted — this part has not been adopted
into any symbol or BOM. Not currently selected in this repo's BOM;
adopting it would still require the separate firmware-driver work
already flagged (TODO.md §8.4).
Cited in: docs/datasheets/infineon-tle9180d-31qk-datasheet-en.pdf only
— not yet referenced from any build BOM or symbol.
Date accessed: 2026-08-02.

---

**[30]** Würth Elektronik eiSos GmbH & Co. KG, *WE-SHC Two-piece
Seamless Shielding Cabinet*, order code 3670375, datasheet rev.
ViM 002.000 (2025-05-12), Würth Elektronik eiSos GmbH & Co. KG,
Waldenburg, Germany. [Online]. Available:
https://www.we-online.com/components/products/datasheet/3670375.pdf
(not independently re-fetched — local copy provided directly).
Local copy: `docs/datasheets/3670375.pdf` (6 pp.) — `VERIFIED` (added
2026-08-02).
This is the **frame** half of the two-piece shield whose cover
(order code 3671375) is cited at [19] — same revision code and date
(ViM 002.000, 2025-05-12) as the cover, consistent with a matched-pair
release. Section/page: p.1 dimensional drawing, "Assembly with Frame."
Confirmed directly from the local PDF: "Assembly with Frame: Frame
(3670375), Cover (3671375)" — text matches [19]'s citation of the same
sentence from the cover's side, closing the loop. Inner 28.7 mm ×
36.9 mm / outer 29.3 mm × 37.5 mm (marginally smaller than the cover's
29.5 mm × 37.7 mm inner / 30.1 mm × 38.3 mm outer, consistent with the
frame nesting inside the cover); frame wall height 6.2 mm / 6.5 mm
(±0.2 mm, two figures given for different wall features, not
independently resolved from the extracted text which package feature
each applies to); an 8.0 mm (±0.2 mm) diameter feature, likely a
clip/mounting cutout — not confirmed from text alone, would need the
actual drawing image to pin down; core steel, tin plating; operating
temperature −40 °C to +125 °C; RoHS/REACh compliant — all matching the
cover's material/certification claims. Does not contain a
shielding-effectiveness (dB) figure, same gap as [19].
This closes the "3670375 frame missing" gap flagged when [19] (the
cover) was first verified — both order codes needed for a complete
Faraday-tier shield are now locally verified, though neither is yet
placed in the build's actual `kicad/` schematic or locked into a
bill of materials (TODO.md §7.1, §12.1).
Cited in: docs/datasheets/3670375.pdf; symbols/WE_SHC_3670375.kicad_sym
(mechanical placeholder symbol, frame); symbols/specs/WE_SHC_3670375.json;
builds/6s/50A/CAN_485_faraday/README.md (Faraday-tier BOM).
Date accessed: 2026-08-02.

---

**[31]** NXP Semiconductors, *S32K1xx Data Sheet* (covers S32K116, S32K118,
S32K142, S32K142W, S32K144, S32K144W, S32K146, S32K148), document S32K1XX,
Rev. 15, NXP Semiconductors, 5 March 2026 — Product data sheet. [Online].
Available: https://www.nxp.com/products/S32K144 (product page; live fetch
blocked: HTTP 403, 2026-08-03) and
https://www.nxp.com/docs/en/data-sheet/S32K1XXDS.pdf (guessed-at-standard
NXP doc-ID URL pattern, NOT independently confirmed to resolve — also
blocked: HTTP 403, 2026-08-03 — do not treat either URL as verified;
resolve properly before quoting it elsewhere).
Local copy: `docs/datasheets/S32K1xx.pdf` (108 pp.) — `VERIFIED` (provided
locally 2026-08-02/03; document's own title page, revision, and date read
directly from the local PDF, independent of the unverified URLs above).
Section/page: p.3, §1.1 "Key Features," "Safety and security" — "Cryptographic
Services Engine (CSEc) implements a comprehensive set of cryptographic
functions as described in the SHE (Secure Hardware Extension) Functional
Specification." p.6, Figure 3 "S32K1xx product series comparison" — S32K144
column: Arm Cortex-M4F core, 80 MHz (RUN) / 112 MHz (HSRUN); CSEc present
(♦ marker); CRC, ISO 26262 capable up to ASIL-B, MPU, EWM all present; 512 KB
flash, 64 KB system RAM (+4 KB FlexRAM, +4 KB cache), 4 KB EEPROM emulated by
FlexRAM (up to 64 KB D-Flash); single supply 2.7-5.5 V; ambient operating
temperature -40 °C to +105 °C/+125 °C (per ordering option, p.8); packages
48-pin LQFP, 64-pin LQFP, 100-pin LQFP, 100-pin MAPBGA (this build selects
64-pin LQFP, document number SOT1699-1 per p.89 Dimensions table — see
below). Note: several rows in this same figure (e.g. "Number of I/Os,"
FlexTimer/FlexCAN/LPUART/LPSPI channel counts) render as a single value
spanning what appear to be two adjacent device columns (K142/K144 or
K144/K146) once extracted to text — the underlying PDF table clearly shows
one column per device but pdftotext's text-extraction merges some
equal-valued adjacent cells, so which exact device each merged figure
belongs to is not resolved with certainty from this pass; the only such
figure carried into this repo's design docs ("up to 128 I/Os") is cited with
that caveat rather than asserted as an exact single-device count. This
build's actual peripheral use (1 FlexCAN-FD instance, 1 LPUART, 1 LPSPI, 4
ADC channels, 6 PWM channels) is comfortably below every family member's
*minimum* published figure in this same table, so the merge ambiguity does
not affect any design decision actually made here.
p.8, §4 "Ordering information" — CSEc appears explicitly as an orderable
feature-option letter ("A1: CAN FD, FlexIO, Security"; "S: Security"),
package-code table confirms 64-pin LQFP = ordering code "LH"; S32K14x memory
digit 4 = 512 KB flash (matches "S32K144" naming, cross-checked against the
512 KB figure in Figure 3). p.13, §5.4 "Power and ground pins," 64 LQFP
package diagram — real, distinct power/analog-reference pin names: VDD,
VSS, VDDA, VREFH, and a combined VREFL/VSSA/VSS pin (external CDEC/CREF
decoupling shown but not itself a package pin). p.14 note — "VSSA and VSS
are shorted at package level," confirming the combined pin above is a real
package-level short, not a schematic simplification. p.26, Table
(AC/DC electrical specifications) — symbol "RESET_B," confirming the real
reset pin name used by this device family (not the generic "NRST" label
this repo's now-superseded MSPM0G3507 spec used). p.77, Table (LPSPI/SWD AC
electrical specifications) — symbols "SWD_CLK" and "SWD_DIO," confirming
the real 2-wire SWD debug pin names (also referenced by name at p.3, "Up to
20 MHz TCLK and 25 MHz SWD_CLK"). p.89, "9.1 Obtaining package dimensions"
table — 64-pin LQFP package document number SOT1699-1, manufacture code
98ASS23234W (exact package body dimensions not printed in this data sheet;
would need that SOT drawing itself, not yet obtained).
**Not verified / explicitly out of scope this pass:** this data sheet
states, p.89, §10.1 "Package pinouts and signal descriptions": "For package
pinouts and signal descriptions, refer to the Reference Manual" — i.e. the
physical package-pin-NUMBER-to-signal assignment (which pin is FlexCAN0_TX,
which is LPSPI0_SCK, etc.) is NOT contained in this document at all, by the
document's own statement. The S32K1xx Series Reference Manual is now
available locally (see "Local copy — Reference Manual" below), but its
pinout chapter has not yet been read to resolve this specific gap — that is
a separate, larger task (regenerating `symbols/specs/S32K144.json`'s pin
map), tracked in `TODO.md` 1.11(a) and not attempted as part of this update.
`symbols/specs/S32K144.json`'s pin `"num"` values remain an
`UNVERIFIED PLACEHOLDER PIN MAP` per `AGENTS.md` §1.3/§3 until that pass is
done.
**2026-08-03 update — CSEc algorithm detail now VERIFIED:** this data sheet
names the "SHE (Secure Hardware Extension) Functional Specification" but
does not itself spell out the algorithm-level detail of CSEc's
message-authentication function. That detail — previously flagged
`UNVERIFIED — needs primary source` in `TODO.md` 1.11(b) — is now confirmed
directly against the local S32K1xx Series Reference Manual, Rev. 14,
09/2021 (`docs/datasheets/S32K-RM.pdf`, 2210 pp.), Chapter 36 "Flash Memory
Module (FTFC)," §36.5.13: `CMD_GENERATE_MAC` (§36.5.13.9, Table 36-82)
computes `MAC = CMAC_KEY,KEY_ID(MESSAGE, MESSAGE_LENGTH)` — i.e. AES-128
CMAC — and `CMD_VERIFY_MAC` (§36.5.13.11, Table 36-83) recomputes and
compares it. The full command set in this chapter is `ENC_ECB`/`DEC_ECB`/
`ENC_CBC`/`DEC_CBC`/`GENERATE_MAC`/`VERIFY_MAC`/`LOAD_KEY`/`LOAD_PLAIN_KEY`/
`EXPORT_RAM_KEY` plus RNG/ID commands — no RSA/ECC/certificate command
exists anywhere in this chapter, confirming CSEc is symmetric-only. Key
catalog (Table 36-75): `SECRET_KEY` (ROM), `MASTER_ECU_KEY`, `BOOT_MAC_KEY`
(both Flash), up to 17 user keys `KEY_01`–`KEY_17` (Flash, partition is
user-configurable, not all 17 simultaneously per §5 of the Data Sheet
portion above), and the volatile `RAM_KEY` — all AES-128 (16-byte). See
`docs/security-mcu-comparison.md` §3.1/§7 for the full comparison write-up
this update supports.
Local copy — Reference Manual: `docs/datasheets/S32K-RM.pdf` (NXP
Semiconductors, *S32K1xx Series Reference Manual*, Rev. 14, 09/2021,
2210 pp.) — `VERIFIED` (local copy read directly, 2026-08-03; live nxp.com
fetch not reattempted this session, same 403 pattern as the Data Sheet
above is assumed to still apply and was not retested).
Candidate replacement decision for the project MCU (was MSPM0G3507, [1],
now S32K144), and for the project's message-authentication mechanism (was
external SLB9672 TPM, [2], now on-chip CSEc) — see `README.md`,
`builds/6s/50A/CAN_485_faraday/README.md`, `symbols/specs/S32K144.json`.
Date accessed: 2026-08-03.

---

**[32]** Infineon Technologies AG, *Infineon.TLE987x_DFP* (CMSIS device
family pack description), Infineon GitHub organization, `cmsis_packs`
repository, path `TLE987x/Infineon.TLE987x_DFP.pdsc`. [Online]. Available:
https://raw.githubusercontent.com/Infineon/cmsis_packs/master/TLE987x/Infineon.TLE987x_DFP.pdsc
— `VERIFIED` (live fetch succeeded 2026-08-03; this is the only external
source in this citation range that was not blocked by HTTP 403 this
session).
Section/page: this is a machine-readable device-family-pack XML, not a
paginated document; the peripheral list it declares for the TLE987x/TLE9879
family (ADC, timers, UART, SPI, LIN transceiver, bridge driver (BDRV),
power management unit, DMA) contains no AES/CRC/HSM/SHE or any other
cryptographic peripheral entry. Used to support the claim in
`docs/security-mcu-comparison.md` §8.1 that this family's CMSIS-exposed
peripheral set has no on-chip security/crypto engine. This is verified for
"not present in this file" specifically — it is not a substitute for the
full TLE987x/TLE9879 datasheet or user manual, neither of which was
reachable this session (infineon.com and mouser.com PDF links both
returned HTTP 403). Package (VQFN-48-EP, 7×7 mm) and pricing figures cited
alongside this in `docs/security-mcu-comparison.md` §8.1 come from
distributor search-result snippets (LCSC/JLCPCB), not this source, and are
marked `UNVERIFIED` there accordingly.
Cited in: `docs/security-mcu-comparison.md` §8.1.
Date accessed: 2026-08-03.

---

**[33]** Microchip Technology Inc., *dsPIC33CK512MPT608 Family Data Sheet*,
DS70005501B, Microchip Technology Inc., Chandler, AZ, USA, © 2022.
[Online]. Available:
https://www.microchip.com/en-us/products/microcontrollers/dspic-dscs/dspic33c/secure-dscs
(product page; live fetch blocked: HTTP 403, 2026-08-03 — see below for the
resolved local copy).
Local copy: `docs/datasheets/dsPIC33CK512MPT608-Family-Data-Sheet-DS70005501.pdf`
(999 pp., PDF permissions-encrypted with an empty user password — opens/
extracts cleanly without a password) — `VERIFIED` (added to the repo by the
repo owner 2026-08-03, after this citation was first logged as
`UNVERIFIED`; superseding note below).
Section/page: p.1, "Description"/"Operating Conditions" — "Secure Digital
Signal Controllers (DSCs) ... intended for automotive, industrial or
commercial systems," code authentication (secure boot), MAC generation,
trusted firmware updates, mutual node authentication, TLS and other
roots-of-trust operations; operating conditions "3V to 3.6V, -40°C to
+125°C: DC to 100 MIPS." p.1–2, "Security Features"/"Qualification
Support" — "Secure Subsystem with Advanced Crypto Engine (ACE)"; sign/
verify: ECDSA (P224, P256, P384, 256-bit Brainpool, SECP256K1), RSA
2048-bit sign+verify, RSA 3072-bit verify-only; ECDH/ECDHE (P224/P256/
P384/Brainpool) and ECBD (P224) key agreement; internal EC and 2048-bit
RSA and AES-16-byte key generation; AES ECB/GCM and RSA 1024/2048-bit
OAEP/MGF encrypt/decrypt; AES-CMAC and SHA-256/SHA-HMAC; NIST SP800-90
A/B/C RNG; 16 MHz internal SPI link between core and Secure Subsystem;
JIL HIGH-rated, FIPS CAVP-certified ACE algorithms; Secure Subsystem FIPS
140-2 Level 2 with Physical Security Level 3 "in progress"; "AEC-Q100
REV-H (Grade 1: -40°C to +125°C) Compliant." p.116–118, Ch. 6 "Secure
Subsystem," §6.1–6.3 — architecture (command processor/ACE + parallel Fast
Crypto Engine), full feature list repeated with **"X.509 Certificate
Storage, Parsing, Validation and Revocation, Supporting both ECC and
RSA"** (p.116, §6.1) — the PKI/certificate-handling claim central to
`docs/security-mcu-comparison.md` §8.2. p.942–944, Ch. 33 "Electrical
Characteristics," Table 33-1 "Absolute Maximum Ratings" (VDD -0.3V to
+4.0V; 5V-tolerant I/O pins only, up to +5.5V when VDD ≥ 3.0V) and Table
33-5 "Operating Voltage Specifications" (VDD 3.0–3.6V) — confirms this
part is a 3.3V-class device, **not** natively 5V (this corrects the
`UNVERIFIED` note originally logged under this tag, which had relayed an
unverified search-snippet claim of "5V configurations" for the dsPIC33C
line in general). Ch. 33's own text states "Additional information will
be provided in future revisions of this document as it becomes available"
(p.942) — no ESD (HBM/CDM)-kV table, no radiated-emissions figure, and no
ACE-command execution-time table are published in this Rev. B document;
those remain `UNVERIFIED — needs primary source`. p.7 "Pin Diagram," p.996
"Product Identification System" — single package option, 100-Lead TQFP
12×12×1 mm; order codes `dsPIC33CK512MPT608-I/PT` (industrial, -40°C to
+85°C) and `-E/PT` (extended, -40°C to +125°C).
Cited in: `docs/security-mcu-comparison.md` §8.2.
Date accessed: 2026-08-03 (product-page search only, blocked); local
datasheet added and read same day.
**Superseded note:** this tag was first logged 2026-08-03 as `UNVERIFIED`
against only a WebSearch snippet of the product page above. Per
`AGENTS.md` §2.5, the tag is not renumbered — this entry has instead been
rewritten in place now that a primary source (the local datasheet) is
available, which `AGENTS.md` §3 permits (the marker is removed once "a real
citation replaces it").

---

**[34]** Renesas Electronics Corporation, *RH850/U2A16*, product page.
[Online]. Available:
https://www.renesas.com/eu/en/products/microcontrollers-microprocessors/rh850/rh850u2x/rh850u2a16.html
(live fetch blocked: HTTP 403, 2026-08-03) — **`UNVERIFIED — needs primary
source`**, section/page not verified; this repo has only a WebSearch
result-snippet summary (flexible power supply typ. 1.12 V/3.3 V/5.0 V; "HSM
for Evita-full with dedicated CPU/Flash and HW crypt algorithm support";
four 400 MHz CPU cores in dual-core lockstep ×2; 16 MB flash; 3.6 MB SRAM;
a 516-pin package referenced in a separate piggyback-board document), not
the product page, datasheet, or user's manual itself. Whether this part's
HSM supports asymmetric/PKI operations (as the general "EVITA-Full" HSM
tier is understood to, in contrast with SHE/CSEc-class "EVITA-Light" HSMs)
is not established by anything this repo has independently read for this
specific part.
Cited in: `docs/security-mcu-comparison.md` §8.3.
Date accessed (search only, not page fetch): 2026-08-03.

---

**[35]** STMicroelectronics, *STM32G431x6 STM32G431x8 STM32G431xB — Arm®
Cortex®-M4 32-bit MCU*, datasheet, DS12589, Rev. 6, STMicroelectronics,
Geneva, Switzerland, 2019-05 (revised 2021-10). [Online]. Available:
https://www.st.com/resource/en/datasheet/stm32g431c6.pdf (live fetch not
reattempted this session — see TODO.md 1.10 for this repo's established
403 pattern on st.com).
Local copy: `docs/datasheets/stm32g431c6.pdf` (198 pp.) — `VERIFIED`. This
file was removed from the repo 2026-08-02 when the project MCU changed from
STM32G431C6 to the MSPM0G3507 (superseded [1]) and was not previously
cited in this file under any tag; it has been restored to the repo from
git history (commit `33530d4`) 2026-08-03 specifically to support the
STM32G431K + SLB9672 combo comparison in `docs/security-mcu-comparison.md`
§8.4, and is cited under this new tag rather than reusing [1] (a different
document, the MSPM0G3507 datasheet) per `AGENTS.md` §2.5.
Section/page: p.1, "Features" — operating voltage VDD/VDDA 1.71 V to
3.6 V; LQFP32 (7×7 mm) and UFQFPN32 (5×5 mm) package options shown on the
cover package-list figure. p.2, Table 1 "Device summary" — STM32G431x6/
x8/xB subfamily includes ordering codes with pin-count letter K = 32 pins
(also C=48/49, R=64, M=80, V=100). p.15 (§3.11.1 "Power supply schemes")
and p.1 restate VDD = 1.71–3.6 V as the single external supply voltage.
p.109, Table 48 "EMS characteristics" — voltage limits to induce a
functional disturbance, tested per IEC 61000-4-2 (ESD immunity during
operation); "EMI Level 4" radiated-emissions class table (bands 130 MHz–
1 GHz: 25 dBµV/m equivalent; 1 GHz–2 GHz: 18) per IEC 61967-2. p.109,
Table 50 "ESD absolute maximum ratings" — HBM ±2000 V per ANSI/ESDA/JEDEC
JS-001 Class 2; CDM ±250 V per ANSI/ESDA/JEDEC JS-002 Class C1. p.110,
Table 51 "Electrical sensitivities" — static latch-up Class II Level A at
125 °C per JESD78E. p.194, Table 101 "Ordering information scheme" —
Temperature-range codes "6" and "3" are both labeled "Industrial
temperature range" (-40 °C to 85/125 °C); mission-profile compliance is
stated (p.~65 area) against JEDEC JESD47, not AEC-Q100. The string
"AEC-Q100" does not appear anywhere in this 198-page document (confirmed
by full-text search) — this part is **not** shown to be AEC-Q100 qualified
by its own datasheet, in contrast to [31] and [33].
Cited in: `docs/security-mcu-comparison.md` §8.4.
Date accessed: 2026-08-03.

---

**[36]** Microchip Technology Inc., *SAM D5x/E5x Family Data Sheet*,
DS60001507, Rev. G, Microchip Technology Inc., Chandler, AZ, USA, 2021.
[Online]. Available:
https://www.microchip.com/en-us/product/atsame51g19a (product page;
live fetch blocked: HTTP 403, 2026-08-03).
Local copy: `docs/datasheets/SAM_D5x_E5x_Family_Data_Sheet_DS60001507G.pdf`
(1934 pp., password-empty-encrypted) — `VERIFIED`.
Section/page: p.1, "Features" — operating conditions 1.71 V to 3.63 V;
"One Advanced Encryption System (AES) with 256-bit key length and up to
2 MB/s data rate"; "True Random Number Generator (TRNG)"; "Public Key
Cryptography Controller (PUKCC) and associated Classical Public Key
Cryptography Library." p.3, package/qualification bullets — package
options VQFN/TQFP/TFBGA/WLCSP; "AEC-Q100 Grade 1 (-40°C to 125°C)."
p.4/p.19, ordering/package tables — 48-pin VQFN (5×5×0.9 mm), 64-pin
TQFP/VQFN/WLCSP, 100-pin TQFP, 120-ball TFBGA, 128-pin TQFP; "the AEC-Q100
Grade 1 qualified version is only offered in the TQFP, VQFN and BGA
packages" (WLCSP excluded). p.1307–1308, Ch. 43 "Public Key Cryptography
Controller (PUKCC)" — "processes public key cryptography algorithm
calculus in both GF(p) and GF(2n) fields"; library (PUKCL, ROM-resident)
implements RSA/DSA modular exponentiation up to 7168-bit (with CRT) or
5376-bit (without), ECDSA over GF(p) up to 521-bit and GF(2n) up to
571-bit for common curves; described as "a peripheral that can be used to
accelerate public key cryptography" accessed via a software API — no
isolated/protected key storage, certificate handling, or FIPS/CC
certification is claimed for this peripheral anywhere in this chapter (a
math accelerator, not a self-contained secure element, in contrast to
[2] and [33]). p.626, Ch. 26 "ICM - Integrity Check Monitor" — DMA-driven
SHA1/SHA224/SHA256 hashing (FIPS PUB 180-2 compliant) over up to four
memory regions, with published run-time periods of 85 or 209 clock cycles
(SHA1) and 72 or 194 clock cycles (SHA224/SHA256) — the only cycle-count
hashing-latency figures found anywhere in this whole comparison's source
set. p.1787, Table 54-1 "Absolute Maximum Ratings" — HBM 2000 V per
JESD22-A114; CDM 750 V (mid and corner) per AEC Q100-011.
Cited in: `docs/security-mcu-comparison.md` §8.5.
Date accessed: 2026-08-03.

---

**[37]** Texas Instruments Incorporated, *TMS320F28002x Real-Time
Microcontrollers*, datasheet, SPRSP45C, Texas Instruments Incorporated,
Dallas, TX, USA, 2020-03 (revised 2024-04). [Online]. Available:
https://www.ti.com/lit/ds/symlink/tms320f280025.pdf (live fetch blocked:
HTTP 403, 2026-08-03, same pattern as [1]).
Local copy: `docs/datasheets/tms320f280025.pdf` (243 pp.) — `VERIFIED`.
Section/page: p.1, "Features" — "Dual-zone security" under On-chip
memory; "Single 3.3V supply." p.3, "Package options" — 80-pin LQFP [PN],
64-pin LQFP [PM], 48-pin LQFP [PT]. p.188, §7.11 "Dual Code Security
Module" — DCSM prevents access to on-chip secure memories via a 128-bit
zone password; the datasheet's own Code Security Module Disclaimer states
TI "does not... warrant or represent that the CSM cannot be compromised or
breached." No AES, RSA, ECC, SHA, or other cryptographic-authentication
peripheral is named anywhere in this device's own feature list, memory
map, or register summary (confirmed by full-text search for "AES" — the
only 3 occurrences in the whole document are inside an unrelated
"Merchant Telecom Rectifier" application-circuit block diagram (p.203–
205), not this device's own peripheral list, and could not be confirmed
to describe an on-chip AES engine on this specific part rather than a
broader reference-design security goal). p.48–49, §6.2–6.3 "ESD Ratings —
Commercial" / "ESD Ratings — Automotive" — commercial parts: HBM ±2000 V
(JS-001), CDM ±500 V all pins/±750 V corner (JS-002); **automotive
(-Q1) parts have a separate table**: HBM ±2000 V per AEC Q100-002, CDM
±500 V all pins/±750 V corner per AEC Q100-011. p.204, "Package
Information" table — TMS320F280025-Q1 exists as a genuine, separately
AEC-Q100-tested catalog part (PN/PM/PT package bodies 12×12/10×10/7×7 mm).
No IEC 61000-4-x citation found anywhere in this document (full-text
search).
Cited in: `docs/security-mcu-comparison.md` §8.6 (excluded from the
security-module shortlist — see that section's Assessment).
Date accessed: 2026-08-03.

---

**[38]** Texas Instruments Incorporated, *MSPM0G310x Mixed-Signal
Microcontrollers With CAN-FD Interface*, datasheet, SLASF12D, Texas
Instruments Incorporated, Dallas, TX, USA, 2023-02 (revised 2025-10).
[Online]. Available: https://www.ti.com/lit/ds/symlink/mspm0g3107.pdf
(live fetch blocked: HTTP 403, 2026-08-03, same pattern as [1]).
Local copy: `docs/datasheets/mspm0g3107.pdf` (98 pp.) — `VERIFIED`.
Section/page: p.1, "Features" — Arm Cortex-M0+ up to 80 MHz; "Wide supply
voltage range: 1.62V to 3.6V"; "Data integrity and encryption: Cyclic
redundancy checker (CRC-16, CRC-32); True random number generator (TRNG);
AES encryption with 128-bit or 256-bit key" — no RSA/ECC/certificate
capability listed. Package options: 32-pin VQFN (RHB, 0.5 mm pitch),
28-pin VSSOP (28DGS), 20-pin VSSOP (20DGS); family members MSPM0G3105
(32 KB flash/16 KB RAM), MSPM0G3106 (64 KB/32 KB), MSPM0G3107 (128 KB/
32 KB). p.2, Table 3-1 "Device Comparison" — 32 VQFN = 5 mm×5 mm; 28
VSSOP = 7.1 mm×4.9 mm; 20 VSSOP = 5.1 mm×4.9 mm, for all three flash-size
variants. p.13, Table 6-3 "Signal Descriptions" — CAN_TX/CAN_RX are
broken out on all three packages (pin 16/17 on the 32-VQFN; present down
to the 20-pin VSSOP), confirming CAN-FD is available even on the smallest
package. p.39, §7.2 "ESD Ratings" — HBM ±2000 V per ANSI/ESDA/JEDEC
JS-001; CDM ±500 V per JEDEC JESD22-C101 — this is the base/commercial
part's rating; no separate automotive ESD table is present in this
document. p.53, §8.17 "AES" — "DMA support for ECB, CBC, OFB, and CFB
cipher modes," identifying this as the basic AES module (TRM [39] Ch. 12),
not the more capable AESADV module (TRM [39] Ch. 13, which adds native
CMAC/GCM/CCM) — this part does not have hardware-native CMAC. Ordering
addendum (p.~24-Jun-2026 revision date shown in-document) lists
"Automotive: MSPM0G3105-Q1, MSPM0G3106-Q1, MSPM0G3107-Q1," described as
"Q100 devices qualified for high-reliability automotive applications
targeting zero defects" — the automotive variant's own dedicated
datasheet (distinct from this document) was not obtained this session; do
not treat this base part's ESD/electrical figures as applying to the -Q1
variant. No IEC 61000-4-x citation found in this document.
Cited in: `docs/security-mcu-comparison.md` §8.7.
Date accessed: 2026-08-03.

---

**[39]** Texas Instruments Incorporated, *MSPM0 G-Series 80MHz
Microcontrollers Technical Reference Manual*, SLAU846E, Texas Instruments
Incorporated, Dallas, TX, USA, 2023-06 (revised 2026-07). [Online].
Available: https://www.ti.com/lit/ug/slau846e/slau846e.pdf (live fetch
blocked: HTTP 403, 2026-08-03, same pattern as [1]).
Local copy: `docs/datasheets/slau846e.pdf` (2521 pp.) — `VERIFIED`.
Section/page: p.767–768, Ch. 12 "AES," §12.1.1 "AES Performance," Table
12-1 "AES Hardware Accelerator Key Performance Metrics" — the only
block-cipher execution-time table found anywhere in this comparison's
entire source set: AES-128 encrypt 168 cycles (2.10 µs @ 80 MHz, 5.25 µs
@ 32 MHz); AES-256 encrypt 234 cycles (2.93 µs / 7.31 µs); decrypt with
pregenerated key same cycle counts as encrypt; Table 12-2 additionally
gives raw (non-pregenerated-key) decryption at 215 cycles (AES-128) / 292
cycles (AES-256), and key-schedule generation at 53/68 cycles. This is
the basic "AES" module — confirmed present on the MSPM0G3107 [38] via its
own §8.17. p.830–831, Ch. 13 "AESADV" — a separate, more capable AES
peripheral supporting native hardware CMAC, GCM, and CCM authentication
modes in addition to ECB/CBC/CFB/OFB/CTR — present on some other MSPM0
G-series devices, not confirmed present on the MSPM0G3107 specifically
(see [38]'s note).
Cited in: `docs/security-mcu-comparison.md` §8.7, §9 (message-signing
latency section).
Date accessed: 2026-08-03.

---

**[40]** Texas Instruments Incorporated, *Cybersecurity Enablers in
MSPM0 MCUs*, application note, SLAAE29A, Texas Instruments Incorporated,
Dallas, TX, USA, 2023-01 (revised 2025-12). [Online]. Available:
https://www.ti.com/lit/an/slaae29a/slaae29a.pdf (live fetch blocked:
HTTP 403, 2026-08-03, same pattern as [1]).
Local copy: `docs/datasheets/slaae29a.pdf` (44 pp.) — `VERIFIED`.
Section/page: p.2, Table 1-1 "Key Concepts" — defines Secure Boot,
Customer Secure Code (CSC, a secure-boot solution for devices with the
INITDONE hardware-isolation mechanism), Boot Image Manager (BIM, the
equivalent solution for devices without INITDONE), Root of Trust (ROM
boot code plus statically write-protected CSC), Keystore ("secure storage
for AES key. Only CSC can configure keys into Keystore and the main
application can configure the crypto engine (AES) to use one of the
stored keys but can never access any stored keys"), Firewall (dynamic
flash write/read-execute/IP protection). Also in this table: "SHA2-256...
Only supported via software in MSPM0 devices" and "ECDSA P256, an
asymmetric algorithm to verify message authenticity... Only supported via
software in MSPM0 devices" — i.e. no hardware acceleration for either
primitive, but the capability exists as an SDK-provided software library,
which is more than CSEc [31] offers (CSEc has no asymmetric-crypto path
at all, hardware or software, per its command set). p.17, Table
"Secure Boot Solution: Boot Image Manager (BIM) | Customer Secure Code
(CSC)" — "Keystore: No | Yes," showing Keystore is only available via the
CSC (INITDONE-based) secure-boot path, not the BIM one. **2026-08-03
update:** the repo owner's own direct investigation found that the choice
between CSC and BIM is a firmware/SDK-level implementation decision, not a
hardware capability gated to a specific MSPM0 sub-family/part — this is
attributed to that investigation rather than re-derived from a specific
page of this document in this session (see
`docs/security-mcu-comparison.md` §9.7/§9.8 for where it's used; a precise
section/page citation for the INITDONE-availability claim itself would
upgrade this from attributed-finding to independently `VERIFIED`).
p.37, §4.7 "Hardware Monotonic Counter" — anti-rollback protection
mechanism for firmware updates.
Cited in: `docs/security-mcu-comparison.md` §8.7 and §9;
`docs/secure-element-architecture.md` §1.1/§2/§4 C-08 (Keystore access model,
software-only ECDSA-P256/SHA-256, hardware monotonic counter — added
2026-08-22 during the `TODO.md` §13 verification pass).
Date accessed: 2026-08-03.

---

**[41]** Texas Instruments Incorporated, *EMC Improvement Guide for
MSPM0*, application note, SLAAET8A, Texas Instruments Incorporated,
Dallas, TX, USA, 2025-04 (revised 2025-12). [Online]. Available:
https://www.ti.com/lit/an/slaaet8a/slaaet8a.pdf (live fetch blocked:
HTTP 403, 2026-08-03, same pattern as [1]).
Local copy: `docs/datasheets/slaaet8a.pdf` (27 pp.) — `VERIFIED`.
Section/page: p.3–4, §2.2 "EMC Standards" — names IEC 61000-4-2 (ESD
immunity), -4-3 (radiated immunity), -4-4 (fast transient/burst), -4-5
(surge), -4-6 (conducted immunity) as the IEC 61000 series EMS test
standards, and CISPR 25 / CISPR 22/32 as the radiated/conducted emissions
standards, that this design-guidance document is written against. This
document is explicitly a checklist/design guide ("Most of the content is
provided in the checklist format," p.2) — it does **not** publish a
device-specific numeric pass/fail EMC test result (dB µV/m or similar)
for any MSPM0 part; it documents mitigation techniques and a root-cause
debug flow for EMC test failures. p.10, §4.1 "Susceptibility Protection
Features" — on-chip EMS features: 4-level programmable brown-out reset
(BOR0–BOR3, the highest levels raising an interrupt rather than
immediately resetting), power-on reset (POR), and dedicated NMI sources
for BOR/watchdog violations (Table 4-2).
Cited in: `docs/security-mcu-comparison.md` §6, §8.7.
Date accessed: 2026-08-03.

---

**[42]** Texas Instruments Incorporated, *MSPM0G3x0x, MSPM0G1x0x,
MSPM0G3x0x-Q1 Microcontrollers Errata*, SLAZ742G, Texas Instruments
Incorporated, Dallas, TX, USA, 2023-07 (revised 2026-07). [Online].
Available: https://www.ti.com/lit/er/slaz742g/slaz742g.pdf (live fetch
blocked: HTTP 403, 2026-08-03, same pattern as [1]).
Local copy: `docs/datasheets/slaz742g.pdf` (38 pp.) — `VERIFIED`.
Section/page: p.1, Table 1-1 "Functional Advisories" — covers silicon
revisions B, C, and D of the MSPM0G3x0x/G1x0x/G3x0x-Q1 device group (which
includes the MSPM0G3107 [38]). No `AES_ERR_*` or `TRNG_ERR_*` advisory
entries appear anywhere in the errata number list (confirmed by targeted
search) — no known silicon errata affecting the AES or TRNG peripherals
in any of the three listed revisions. A `CRC/CRCP_ERR_01` advisory is
listed as present in all three revisions (p.1); its full description
text (in the document's §6 "Advisory Descriptions") was not extracted
this session.
Cited in: `docs/security-mcu-comparison.md` §8.7.
Date accessed: 2026-08-03.

---

**[43]** Texas Instruments Incorporated, *MSPM0G350x-Q1 Automotive
Mixed-Signal Microcontrollers With CAN-FD Interface*, datasheet, Texas
Instruments Incorporated, Dallas, TX, USA. [Online]. Available:
https://www.ti.com/lit/ds/symlink/mspm0g3507-q1.pdf (guessed-at-standard
TI doc-ID URL pattern, not independently confirmed to resolve; live fetch
not attempted — see TODO.md 1.10 pattern). Document number/revision not
independently read off a title page in this extraction pass — flagged
`section/page: doc number/revision not confirmed` for that one field only;
every other field below is read directly from the local copy.
Local copy: `docs/datasheets/mspm0g3507-q1.pdf` (126 pp.) — `VERIFIED`.
**Not the same document as [1]** (the MSPM0G3507 datasheet, superseded) —
this covers the related but distinct MSPM0G350x-**Q1** automotive family
(MSPM0G3505/3506/3507-Q1); per `AGENTS.md` §2.5 a new tag is used rather
than reusing or repurposing [1].
Section/page: p.1, "Features" — Arm Cortex-M0+ up to 80 MHz; "Functional
Safety-Compliant... Documentation available to aid ISO 26262 system
design... Systematic capability up to ASIL B... Hardware integrity up to
ASIL B"; "Safety-related certification: ISO 26262 certified up to ASIL B
by TÜV"; extended temperature -40°C to 125°C; VDD 1.62V to 3.6V; "Data
integrity and encryption: CRC-16/CRC-32, TRNG, AES 128/256-bit" (p.1,
same peripheral set as [38]); math accelerator (DIV/SQRT/MAC/TRIG); two
zero-drift chopper op-amps, three high-speed comparators. p.1, "Package
options" — 64-pin LQFP (PM), 48-pin LQFP (PT), 48-pin VQFN (RGZ), 32-pin
VQFN (RHB), 32-pin VSSOP (32DGS), 28-pin VSSOP (28DGS). p.1, Qualification
bullet — "AEC-Q100 Grade 1," stated directly in this datasheet's own
feature list (unlike [38], which only references "-Q1" variants existing
without restating their qualification grade). p.2–3, package-size table —
64 LQFP 12×12 mm; 48 LQFP 9×9 mm; 48 VQFN 7×7 mm; 32 VQFN 5×5 mm; 32
VSSOP 8.1×4.9 mm; 28 VSSOP 7.1×3 mm (the smallest package footprint found
anywhere in this comparison's source set, ≈21 mm²). p.27, §7.2 "ESD
Ratings" — HBM ±2000 V per AEC-Q100-002; CDM ±500 V all pins / ±750 V
corner pins per AEC-Q100-011 — a genuine automotive-specific ESD table
(cf. [37]'s TMS320F280025-Q1, which is the only other part in this
comparison with a separately published automotive ESD table distinct from
its commercial-grade one).
Cited in: `docs/security-mcu-comparison.md` §8.8.
Date accessed: 2026-08-03.

---

**[44]** Texas Instruments Incorporated, *MSPM0G351x-Q1 Automotive
Mixed-Signal Microcontrollers With CAN-FD Interface* (covers MSPM0G3519-Q1 and
MSPM0G3518-Q1), document SLASFA6B, Rev. B, Texas Instruments Incorporated,
Dallas, TX, USA, November 2024, revised October 2025. [Online]. Available:
https://www.ti.com/lit/ds/symlink/mspm0g3519-q1.pdf
**URL follows TI's standard doc-ID pattern and was NOT independently confirmed
to resolve** — not fetched this session; do not quote it as verified without
retesting. Marked explicitly per `AGENTS.md` §2.3 rather than asserted.
Local verified copy: `docs/datasheets/mspm0g3518-q1.pdf` (144 pp.) —
`VERIFIED`; the document's own title, document number, and revision dates were
read directly from p. 1 of this local copy. A second local copy of the same
document family, `docs/datasheets/mspm0g3519-q1.pdf`, is also present.
Section/page: p. 1 title block — title, doc number SLASFA6B, "NOVEMBER 2024 –
REVISED OCTOBER 2025." §12 "Mechanical, Packaging, and Orderable Information"
begins p. 106; the RHB0032T (32-pin VQFN, 5 × 5 mm) package drawing
**4224744/A, 01/2019** appears on pp. 137–139, across the "PACKAGE OUTLINE",
"EXAMPLE BOARD LAYOUT" and "EXAMPLE STENCIL DESIGN" sheets — this is the
drawing every dimension in `symbols/tools/gen_rhb0032t_footprint.py` is taken
from.
**Provenance note (2026-08-10):** this tag was in use in the repo by
`symbols/tools/gen_rhb0032t_footprint.py` but had **no entry in this file** —
the catalog jumped [43] → [45]. That was a defect against `AGENTS.md` §1.2
(every in-repo citation must have a matching entry here), found while
correcting two symbols that were mistakenly citing [44] for the OPTIGA™ Trust M
(the correct tag for which is [45]). The entry is reconstructed here from the
local PDF and from the citing script's own recorded section/drawing numbers.
Per `AGENTS.md` §2.5 the tag was **not** renumbered or reassigned.
Cited in: `symbols/tools/gen_rhb0032t_footprint.py`;
`symbols/MSPM0G3518_Q1_RHB.kicad_sym`; `symbols/specs/MSPM0G3518_Q1_PM.json`;
`symbols/MSPM0G3518_Q1_PM.kicad_sym` (the active PM/LQFP-64 project MCU
symbol, pin map VERIFIED against this datasheet's Fig 6-3 / Table 6-2 /
§6.3 signal tables — added 2026-08-22 to close the gap where this citation
was in use but unrecorded here); `docs/secure-element-architecture.md`
§1.1/§4/§6 (added same pass).
Date accessed: 2026-08-10.

**RHB symbol re-wired for this build (2026-09-06):** `symbols/MSPM0G3518_Q1_RHB.kicad_sym`
was originally a generic, unwired symbol (pins named only "PA0".."PA27") authored
2026-08-03 for an unrelated board and internally named after that board's
character call-sign. Per the BOM/creepage audit
(`docs/solutions/architecture-patterns/bom-creepage-audit-can485-faraday.md`
finding #1), that name is scrubbed and the symbol is re-wired with this
build's own functional pin-role names (CAN_TX, RS485_TXD, GD_SPI_*, PWM_*,
ADC_*, SE_* — identical role set and local pin coordinates to
`symbols/MSPM0G3518_Q1_PM.kicad_sym`, only the physical pin numbers differ,
per the RHB pinout re-verified against [44] Figure 6-6 (p.14) and Table 6-2
(pp.15–23)). Full per-pin verification: `symbols/specs/MSPM0G3518_Q1_RHB.json`.
A defect in the prior file was found and fixed in the process: it declared 33
pins (a spurious duplicate `VSS` at pin "33"); RHB is a real 32-pin package
and the corrected symbol has no such pin.
`builds/6s/50A/CAN_485_faraday/kicad/open_secure_esc_6s_50a_can485_faraday.kicad_sch`
`U1` swapped from `MSPM0G3518_Q1_PM` to `MSPM0G3518_Q1_RHB` the same day;
`kicad-cli sch erc` re-run after the swap reports 0 errors and the identical
463 `endpoint_off_grid` / 7 `global_label_dangling` warning counts as
immediately before the swap (report diffed line-for-line apart from the
`(U1)` component references) — the swap introduced no new ERC finding.
Cited in: `symbols/MSPM0G3518_Q1_RHB.kicad_sym`;
`symbols/specs/MSPM0G3518_Q1_RHB.json`;
`builds/6s/50A/CAN_485_faraday/kicad/open_secure_esc_6s_50a_can485_faraday.kicad_sch`;
`builds/6s/50A/CAN_485_faraday/kicad/sym-lib-table`.
Date accessed: 2026-09-06.

---

**[45]** Infineon Technologies AG, *OPTIGA™ Trust M — Datasheet*
(SLS 32AIA010MH/S/K/L/M), document release reference Z8F80311641-D,
Rev. 3.70, Infineon Technologies AG, Munich, Germany, 2024-10-09.
[Online]. Available:
https://www.infineon.com/assets/row/public/documents/30/49/infineon-optiga-trust-m-datasheet-en.pdf
**URL located but NOT independently confirmed to serve this document:** a
live fetch on 2026-08-09 returned HTTP 202 with a 0-byte `text/html` body
(vendor anti-bot interstitial) rather than the PDF, and the vendor product
page `https://www.infineon.com/part/OPTIGA-TRUST-M-SLS32AIA` renders
client-side only, so neither could be used to corroborate the document.
Marked explicitly per `AGENTS.md` §2.3 rather than asserted.
Local verified copy: `docs/datasheets/infineon-optiga-trust-m-datasheet-en.pdf`
(45 pp.) — `VERIFIED`; every section/page cited below was read directly
from this local copy, which is the primary source this repo relies on.
Section/page: p. 1, "Features" — Common Criteria EAL6+ (high) certified
hardware; PSA Level 3 certified; up to 10 kB user memory; PG-USON-10-2,-4
package (3 mm × 3 mm); I2C interface with Shielded Connection (encrypted
communication); ECC NIST curves up to P-521 and Brainpool r1 up to 512;
RSA up to 2048; AES key up to 256; SHA-256, HMAC up to SHA-512; TLS v1.2
PRF and HKDF up to SHA-512; 4 monotonic up counters; hibernate leakage
current < 2.5 µA. p. 7, §1.5 "Device features" — CC certificate
BSI-DSZ-CC-0961 (Hardware Identifier IFX_CCI_00000Bh); I2C up to 1 MHz
(FM+). p. 8, Table 2 "Products for V3" — sales code **SLS 32AIA010ML**,
−40 °C to +105 °C Extended Temperature Range (ETR), PG-USON-10-2,-4
(the variant this repo selects); Table 4 "Features" V1/V3 column split.
pp. 8–9, Table 4 — V3 adds over V1: ECC NIST P-521 and Brainpool
P256/384/512 r1, TLS v1.2 PRF SHA-384/512, HKDF SHA-256/384/512, AES
128/192/256 (ECB, CBC, CBC-MAC, CMAC), and HMAC with SHA-256/384/512.
p. 10, §2 Figure 1 "System block diagram" — on-chip object inventory:
arbitrary data objects ~4.5 kB, 4 monotonic counters, 4 X.509 certificate
slots, 3 trust-anchor slots, 4 ECC key slots, 2 RSA key slots, 1 AES key
slot (V3 only), 1 platform binding secret. p. 11, §2 Note — unique ECC/RSA
private keys and X.509 certificates are generated and provisioned at the
Infineon fab, with the public key signed by a customer-specific CA.
p. 12, §3 Figure 2 "System integration schematic diagram" — reference
circuit: SCL pin 8 and SDA pin 3 each with a 10 kΩ pull-up to VCC, 100 nF
VCC decoupling, GND pin 1, VCC pin 10; accompanying Note — reset may be
either the IFX I2C soft reset (`IFX_I2C_SOFT_RESET`) or a hardware reset,
and pull-up values depend on the target circuit and I2C frequency.
p. 12, §3.1 Figure 3 and p. 13, Figures 4–5 — optional hibernation
circuits (host GPIO as VCC, or GPIO-switched VCC via FDN304P single
MOSFET / FDN304P+BSS138N dual MOSFET), not used by this repo.
p. 15, §4.1 Figure 6 "PG-USON-10-2,-4 Package Outline" — 3 mm × 3 mm body,
0.5 mm pitch, 0.6 mm max height, 0.05 mm max standoff. p. 16, Figure 7
"PG-USON-10-2,-4 top view" — pin arrangement and the note "Connect the
exposed pad with the copper area in the PCB to improve thermal
dissipation". p. 17, Table 6 "Contact definitions and functions" — full
10-pin map: 01 GND, 02 NC, 03 SDA (I/O), 04 NC, 05 NC, 06 NC, 07 NC,
08 SCL (I/O), 09 RST (IN, active low, weak internal pull-up), 10 VCC
(PWR); NC pins "Not connected/Do not connect externally. Shall be left
floating". p. 18, Table 7 — V_CC_I2C 1.62 V to 5.5 V. p. 20, §5.1.3.1
Table 11 "Electrical characteristics" — V_CC 1.62–5.5 V; I_CCAVG typ
14.0 mA while running a typical authentication profile (25 °C, V_CC =
5.0 V), with footnote "Supply current can be limited from 6mA to 15mA by
software commands"; sleep-mode I_CCS3 typ 70 µA / max 100 µA; hibernate
current < 2.5 µA; RST V_IL ≤ 0.3 × V_CC, V_IH ≥ 0.7 × V_CC. p. 21,
Table 12 — V_CC ramp time t_VCCR 1 µs to 1000 µs. p. 22, Table 13 —
power-on startup time t_STARTUP min 15 ms. p. 23, Table 14 — warm-reset
timing: t_STARTUP min 15 ms, reset-low 10 µs to 2500 µs, reset-detection
t1 min 10 µs. p. 24, §6.1 Table 15 "Command table" — the external command
set, including `OpenApplication`, `CloseApplication`, `GetRandom`,
`CalcHash`, `CalcSign`, `VerifySign`, `CalcSSec`, `DeriveKey`,
`GenKeyPair`, `GetDataObject`, `SetDataObject`, `SetObjectProtected`, and
the V3-only `EncryptSym`, `DecryptSym`, `GenSymKey`. p. 25, §6.2 Table 16
"Mapping of commands with Use cases" — "Secured Communication with (D)TLS"
maps to GetRandom, CalcHash, CalcSign, VerifySign, CalcSSec, DeriveKey,
GenKeyPair, EncryptAsym, DecryptAsym. pp. 26–27, Table 18 "Crypto
performance for V3" (measured at I2C FM 400 kHz, 25 °C, V_CC = 3.3 V) —
ECDSA sign ≈ 65 ms (≈ 70 ms with Shielded Connection); ECDSA verify
≈ 85 ms (≈ 95 ms); ECDH key agreement ≈ 60 ms (≈ 65 ms); ECC P-256 key-pair
generation ≈ 55 ms (≈ 60 ms); AES-128 encrypt ≈ 28 ms / decrypt ≈ 35 ms
(256 bytes, ECB); TLS v1.2 PRF key derivation ≈ 50 ms; HKDF-SHA256 ≈ 130 ms;
HMAC-SHA256 ≈ 90 ms (128 bytes input); SHA-256 ≈ 15 KB/s. p. 28, §7
"Security monitor", Table 19 "Security events" — the events that drive the
monitor, including "Private key use" and "Secret key use"; §7.2 "Security
policy" — the permitted usage profile is **one protected operation per
t_max period, with t_max = 5 seconds (± 5%)**, and a Suspect System
Behavior event sets the Security Event Counter to its maximum (255).
pp. 30–33, Appendix A.1 Tables 20–24 — IFX I2C v2.03 register map (DATA
0x80, DATA_REG_LEN 0x81, I2C_STATE 0x82, BASE_ADDR 0x83, MAX_SCL_FREQU
0x84, GUARD_TIME 0x85, TRANS_TIMEOUT 0x86, SOFT_RESET 0x88, I2C_MODE
0x89) and protocol-variation defaults (BASE_ADDR 0x30, MAX_SCL_FREQU
1000 kHz, GUARD_TIME 50 µs, TRANS_TIMEOUT 10 ms, TRANS_REPEAT 3,
MAX_PACKET_SIZE 0x110, PRESENT_LAYER — the presentation layer providing
confidentiality and integrity protection of APDUs, used as part of
Shielded Connection). p. 34, §A.2 — default I2C slave address 0x30.
p. 40, §A.3.2 "Low power sleep mode" — the device enters sleep
automatically after a configurable delay t_SDY and resumes as soon as its
address is detected on the I2C bus.
Cited in: `README.md`; `docs/secure-element-architecture.md`;
`docs/security-mcu-comparison.md` §3.3/§9.5;
`symbols/specs/OPTIGA_TRUST_M.json`; `symbols/README.md`;
`builds/6s/50A/CAN_485_faraday/README.md`;
`builds/6s/50A/CAN_485_faraday/kicad/` (schematic U2 + `sym-lib-table`).
Date accessed: 2026-08-09.

---

## Pending Verification — Not Yet Cited

### IPC-2152 and IPC-2221 — conductor current capacity and spacing — STANDARDS NOT OBTAINED; open secondary sources corroborated 2026-08-19

**Neither standard has been read. No numbered citation tag is issued for
either**, per `AGENTS.md` §1.3. What follows is the corroborated secondary
basis currently used, recorded so it can be replaced wholesale when a primary
copy is obtained.

**What they are needed for.**

- **IPC-2152** (*Standard for Determining Current Carrying Capacity in Printed
  Board Design*, IPC, 2009) — conductor and via current capacity. Closes
  `TODO.md` 12.5.aw and 12.5.ba: how many vias the 50 A pack terminals need,
  and whether the phase conductors are sized. IPC-2152 superseded the older
  closed-form method for this purpose.
- **IPC-2221** (*Generic Standard on Printed Board Design*, IPC) Table 6-1 —
  conductor spacing by voltage, behind the clearance values in
  `builds/6s/50A/CAN_485_faraday/kicad/open_secure_esc_6s_50a_can485_faraday.kicad_dru`.
  **Revision matters here:** IPC-2221C (2023) changed conductor-spacing
  guidance as a function of **altitude**. This is an airborne ESC, so the
  altitude column is the applicable one, not the sea-level column. Logged as
  `TODO.md` 12.5.bb.

**Secondary sources actually used, with validated URLs.** These are vendor
educational articles — dated, attributed, and openly accessible, which makes
them checkable, but they are **not** the standard and under `AGENTS.md` §1.1
may not stand in for it.

- **[S-A]** Z. Peterson, "PCB Trace Width vs. Current Table for High Power
  Designs," *Altium Resources*, created 2019-12-01, updated 2025-06-27.
  <https://resources.altium.com/p/pcb-trace-width-vs-current-table-high-voltage-design>
  Used for: the trace-width table at 1 oz copper, 10 °C rise — 1 A → 10 mil,
  2 A → 30 mil, 5 A → 110 mil, 10 A → 300 mil.
- **[S-B]** Z. Peterson, "PCB Via Current-Carrying Capacity: Is My PCB Too
  Hot?," *Altium Resources*, updated 2025-09-09.
  <https://resources.altium.com/p/pcb-current-carrying-capacity-how-hot-too-hot>
  Used for: the working rule of thumb — "If you set a less-conservative limit
  of 1 A per via, and you need to supply 5 A instantaneously, then 5 large
  vias with thick plating should be fine," noted as "much less than the 0.5 A
  rule of thumb sometimes seen on forums." **This article gives no via-area
  formula.**
- **[S-C]** Z. Peterson, "IPC-2221 Calculator for PCB Trace Current and
  Heating," *Altium Resources*, updated 2025-06-26.
  <https://resources.altium.com/p/ipc-2221-calculator-pcb-trace-current-and-heating>
  Used for: "the minimum width value that you calculate from IPC-2221 is
  probably an overestimate, thus the IPC-2152 standard attempted to expand the
  available set of data." — i.e. IPC-2221 demands *more* copper than IPC-2152,
  so figures derived from it err conservatively.
- **[S-D]** Z. Peterson, "Using an IPC-2221 PCB Clearance Calculator for High
  Voltage Design," *Altium Resources*, updated 2025-09-09.
  <https://resources.altium.com/p/using-an-ipc-2221-calculator-for-high-voltage-design>
  Used for: IPC-2221 specifies fixed spacing only up to 500 V, above which a
  per-volt increment applies (worked example given: 580 V on column B1 →
  0.25 mm + (80 V × 0.0025 mm/V) = 0.45 mm); and the note that IPC-2221C
  (2023) revised spacing versus altitude.
- **[S-F]** "Via Calculator," *CircuitsLab Wiki*, retrieved 2026-08-19.
  <https://circuitslab.wiki/via-calculator/>
  The most directly applicable secondary source found so far: it publishes
  **IPC-2221 and IPC-2152 side by side for vias specifically**, and settles
  two questions the other sources leave open.
  Used for:
  - **Barrel area**: `Area = π × ((d/2)² − ((d/2) − t)²)` — the plating grows
    **inward** from the drilled wall, so the copper is the ring between the
    drilled radius and the finished radius. This **corrected an error in this
    project's own model**, which had the plating growing outward into the
    laminate and overstated barrel area by ~7 %.
  - **Which constant applies to a via**: the **outer-layer** constant,
    *k* = 0.048, not the internal 0.024. This project had been using the
    internal constant for load-bearing figures and was therefore roughly
    2× over-conservative.
  - **IPC-2152 for vias**: *k* = 0.064, with "IPC-2152 typically rates vias
    25–35 % higher for the same geometry because it accounts for plane
    proximity heat-sinking." (0.064/0.048 = 1.33, inside that band, and
    consistent in direction with [S-C].)
  - **Plating minima**: IPC Class 2 = 20 µm, Class 3 = 25 µm.
  - **Design margin**: "Apply 20–25 % safety margin above the IPC-2221
    minimum current" — stated as advice to the designer; the calculator does
    not apply it internally.
  - **Array sizing**: `N = ⌈I_required / I_max_single⌉`.
  **KNOWN INTERNAL INCONSISTENCY, recorded so it is not taken on trust.** The
  page's own reference table disagrees with the page's own formula. Its table
  gives ~0.65 A (IPC-2221) for a 0.30 mm via at 25 µm and ΔT 10 °C; its
  formula and constants give 1.69 A for the same inputs — a factor of 2.6.
  The table's two columns are self-consistent with each other
  (0.87/0.65 = 1.34 ≈ 0.064/0.048), so the ratio between the standards is
  sound and only the absolute scale is in question. **The two readings
  straddle the design answer** for this build: on the formula basis the 7 mm
  pack pad needs 28 vias with margin against 36 that fit (OK); on the table
  basis it needs ~61 (SHORT). This project uses the formula, because its
  constants are corroborated by [S-A]/[S-E] while the table's are not
  reproducible from anything published on the page. **Resolving this is one
  of the things a primary copy of IPC-2152 would settle.**
- **[S-E]** `~/.claude/skills/pcb-engineer/references/design-rules.md`,
  "Trace Width Calculator" (local tool documentation, not published).
  Used for: the conductor equation and its constants —
  *I* = *k* · Δ*T*^*b* · *A*^*c*, with *k* = 0.048 external / 0.024 internal,
  *b* = 0.44, *c* = 0.725, *A* in mil², *I* in A, Δ*T* in °C.
  **This file mislabels those constants "IPC-2152 methodology"; they are the
  IPC-2221 conductor equation.**

**Corroboration performed 2026-08-19.** [S-A]'s table was recomputed from
[S-E]'s equation using the **external** constants, 1 oz = 1.378 mil, ΔT =
10 °C. Agreement: −1.8 %, +0.7 %, +4.3 % on the 2 A, 5 A and 10 A rows
(−11.4 % on the 1 A row, a rounded table entry). Two sources that do not cite
each other produce the same numbers, so the **external** constants are treated
as sound. Reproduce with
`builds/6s/50A/CAN_485_faraday/kicad/tools/via_current_budget.py`.

**What remains uncorroborated, and must not be presented as settled:**

1. The **internal-layer constant** (*k* = 0.024) rests on [S-E] alone. [S-A]'s
   table is external-layer data and cannot confirm it.
2. The **annular via-barrel model** (*A* = π/4 (*D*ₒᵤₜ² − *D*ᵢₙ²),
   *D*ₒᵤₜ = drill + 2 × plating) is this project's own construction. **No
   source consulted states it** — [S-B], the one article specifically about
   via current, offers only a rule of thumb.
3. Whether external or internal constants apply to a via barrel. This project
   uses internal for anything load-bearing.

Against that, three independent bases — [S-B]'s 1 A/via, this project's
IPC-2221 internal figure with a 50 % array derate, and [S-B]'s 0.5 A/via
forum figure — all put the 50 A pack return between **50 and 100 vias**. The
engineering conclusion does not depend on the paywalled text; only its
precision does.

**Access status:** open. The repo owner is seeking access under a cost ceiling
of USD 200 as of 2026-08-19. **No price, vendor, or availability claim is made
here**, because none has been verified against the issuing body. When a copy
is obtained: read it, re-run `tools/via_current_budget.py`, replace the
figures in `TODO.md` 12.5.ba, and promote this section to a numbered citation.

### Assembly and fabrication capability envelope — REQUIRES VERIFICATION

Added 2026-08-19 when the repo owner specified professional reflow assembly at
"JLCPCB or another similar manufacturer" — **no vendor has been chosen**, and
no vendor capability document has been read.

Because the house is not selected, this build should stay inside the envelope
that mainstream prototype-assembly vendors have in common (JLCPCB, PCBWay,
Aisler, Eurocircuits and similar) rather than being tuned to any one of them.
The questions below must be answered against whichever house is finally used,
and each answer recorded here with a validated URL to that vendor's own
published capability page:

- **Fiducial policy** — whether global fiducials are required, and the
  accepted size, count and clearance. `tools/prep_for_assembly.py` placed
  3 per side at 1 mm copper / 2 mm mask opening as ordinary industry
  practice, explicitly NOT as a sourced requirement from any vendor.
- **4-layer 2 oz copper availability and stackup** — `docs/tools/
  conductor_sizing.py` argues 2 oz minimum for the 50 A phase pours. 2 oz on
  a 4-layer board is a non-default option; confirm it is offered, on which
  layers, and what it does to the minimum trace/space.
- **Minimum trace/space, drill, and annular ring for the chosen tier**, to
  check against this board's measured minimums (0.300 mm drill, 0.150 mm
  annular ring on U5's thermal vias — the board's tightest features).
- **Double-sided assembly** — this board places 18 footprints on F.Cu and 41
  on B.Cu; confirm both-side SMT is supported and what it implies for cost
  and for parts that must survive two reflow passes.
- **Shield frame WE-SHC 3670209 (SH1, 22.8 × 17.1 mm)** — confirm whether the
  house will place a part this size, or whether it must be consigned or
  fitted by hand after assembly. This is the item most likely to differ
  between vendors, so it is worth asking before choosing one.
- **Part availability** — a vendor-stocked library (e.g. JLCPCB's) will not
  carry every part here; anything not stocked must be consigned. That answer
  differs per house and may drive the choice.

**This board's tightest features, for checking against any candidate vendor:**

| Feature | This board | Where |
| ------- | ---------- | ----- |
| Min drill | 0.300 mm | U5.41 thermal vias |
| Min annular ring | 0.150 mm | U5.41 thermal vias |
| Min pad pitch | 0.500 mm | U5 WQFN-40, U1 LQFP-64 |
| Board outline | 32.00 × 66.10 mm, 4 layer, 1.6 mm | — |
| Largest part | 22.8 × 17.1 mm | SH1 shield frame |
| Assembly sides | both (18 F.Cu, 41 B.Cu) | — |
| Copper weight sought | 2 oz | `docs/tools/conductor_sizing.py` |

Trace and space are not listed because the board is **not yet routed**
(TODO.md 12.5.w) — the routing that eventually lands will set them, and it
should be routed to the common envelope, not to one vendor's floor.

Until each item is verified against the chosen house, no claim of compliance
with any specific manufacturer may appear in this repository. See
TODO.md 12.5.au.

The following items are named in `README.md` but currently have **no**
authoritative published specification and MUST NOT be cited as conforming
to a standard until one is located and verified (see `AGENTS.md` §1.3):

- **PWM** — generic technique, no single governing standard; if a specific
  PWM interface standard applies to this design, identify and cite it.
- **SBus** — proprietary Futaba Corporation protocol; no publicly published
  official specification located. Needs authoritative sourcing (Futaba
  technical documentation) or must remain marked reverse-engineered/
  unofficial in any implementation notes. Hardware note (verified
  directly against the local copy of [1], p. 67, §8.23 "UART," Table
  8-15 "UART Features"): the MSPM0G3507's UART peripherals list LIN,
  DALI, IrDA, ISO7816 Smart Card, and Manchester coding modes, but no
  RX/TX signal-inversion or polarity-select feature — SBus's inverted
  UART signaling would need external hardware signal inversion (e.g. a
  single-transistor inverter or logic buffer). This is an implementation
  detail, not a standards claim, and does not resolve the "no official
  spec" gap above.
- **DBus** — proprietary protocol (context-dependent, e.g. DJI); no
  publicly published official specification located. Same treatment as
  SBus above, including the external-signal-inversion hardware note.
- **UART / TTL / SPI** — de facto industry conventions, not governed by a
  single ratified standard body document in the way RS-232/RS-485/CAN are.
  If a specific controller's SPI/UART peripheral behavior is being cited,
  cite the MCU datasheet section directly, not "SPI" as a standard.
- **EMI hardening tiers (Isolation, Grounding, Faraday)** — governing
  standards and candidate components now identified: MIL-STD-461G [15]
  (Grounding, Faraday/shielding), IEC 62368-1 [16] (Isolation
  classification), IEC/TR 61000-5-2 [17] (Grounding, layout-only
  guidance), ADuM4221 [18] (Isolation candidate part), WE-SHC 3671375
  [19] (Faraday candidate part). Still open: none of [15]–[19] has a
  locally verified PDF copy or a page/clause-level pin (this session's
  live-fetch tooling was blocked — see the methodology note below); a
  follow-up pass must open the primary documents directly before these
  move from "candidate" to "settled."
- **S32K1xx Series Reference Manual and SHE Functional Specification** —
  needed to upgrade `symbols/specs/S32K144.json`'s pin map from
  `UNVERIFIED PLACEHOLDER` to `VERIFIED` (physical package-pin numbers for
  the 64-pin LQFP are not in the local data sheet [31] itself — see that
  entry's "Not verified" note) and to independently confirm CSEc's
  message-authentication algorithm (AES-128-CMAC per general SHE-HSM
  industry knowledge, not yet confirmed against either primary document).
  Neither document was reachable this session (nxp.com fetch blocked, same
  pattern as [2]/[6]/[12]-[23]). Tracked in `TODO.md`.

**Methodology note on [12]–[23] (2026-08-02, updated same day):** every
new entry added in the first pass was researched with the live-fetch
tool (WebFetch) returning HTTP 403 for every domain attempted that
session, including a neutral non-vendor control URL used purely as a
sanity check — a broader failure than the vendor-specific blocks noted
for [2] and [6]; independently reconfirmed in a later same-day session
(curl and WebFetch both 403 on every external domain tried, including
Wikipedia and anthropic.com — a session-wide egress policy denial, not
a per-vendor block). All specs in [12]–[23] were therefore originally
corroborated via ≥2 independent secondary sources (distributor listings,
search-indexed excerpts of the manufacturer's own datasheet text) rather
than read directly from a primary PDF. **Update:** three primary PDFs —
[19] (WE-SHC 3671375 cover), [20] (IRFB4110PBF), [22] (INA240) — were
added to `docs/datasheets/` later the same day via a direct manual
push to `main` (not a live fetch — the network block was never lifted)
and have since been read directly and marked `VERIFIED` in their
entries above; no discrepancy was found against the prior
secondary-sourced figures for any of the three. [12]–[18], [21], and
[23] still have no local copy and remain secondary-sourced only —
re-attempt direct fetch or manual PDF download before design docs cite
those as verified.

**Network-access update (2026-08-09):** the session-wide egress denial
described above no longer applies — a neutral control URL
(`https://example.com`) returned HTTP 200 and general web search worked.
The remaining obstacle is **vendor-side**, not policy-side: `infineon.com`
answers document requests with HTTP 202 and a 0-byte `text/html` anti-bot
interstitial instead of the PDF, and its product pages render client-side
only, so neither can corroborate a datasheet. This was retested while
adding [45]. Consequence for the still-open items above: a direct-fetch
re-attempt is now *worth making* for the non-Infineon sources
([12]–[18], [21], [23] — Analog Devices, TIA, IEC, Würth, TI, Vishay),
which was pointless under the earlier blanket block. That re-attempt has
**not** been made yet; those entries remain secondary-sourced only and
must not be cited as verified until it is. Tracked in `TODO.md` 1.10.

**[46]** IPC, *Standard for Determining Current Carrying Capacity in
Printed Board Design*, IPC-2152, IPC, Bannockburn, IL, USA, August 2009.
Developed by the Current Carrying Capacity Task Group (1-10b) of the Printed
Board Design Committee (1-10) of IPC. [Online]. Available:
https://www.ipc.org/TOC/IPC-2152.pdf
**Partially verified — front matter and full Table of Contents only.** The
linked PDF was fetched directly on 2026-08-15 (HTTP 200, 5 pp.) and read; it
is IPC's own published front matter and carries the title, document number,
issuing committee, publisher address and issue date quoted above, plus the
complete section listing. The STANDARD BODY IS PAYWALLED and has **not** been
read: `https://shop.ipc.org/ipc-2152-english-d` returned HTTP 403 on the same
date. A local copy is therefore **not** held in `docs/datasheets/`.
Section/page: the following section numbers and page numbers are read
directly from the verified Table of Contents and are the sections this repo
relies on — §4 "Conductor Sizing Design Guidelines" (p. 2); §5 "Conductor
Sizing Charts" (p. 3); §5.1 "Conductor Sizing Charts for Still Air
Environments" (p. 6), with §5.1.1 imperial (p. 6) and §5.1.2 SI/metric
(p. 9); Appendix A §A.3.4 "Vias" (p. 26); §A.4.3 "Copper Weight" (p. 28);
§A.4.6 "Copper Planes" (p. 29), with §A.4.6.1 "Single Plane" (p. 29).
**No chart value, derating factor, temperature-rise figure or conductor
width from this standard is quoted anywhere in this repository**, because the
charts themselves are in the paywalled body. Per `AGENTS.md` §1.3, every
conductor width in
`builds/6s/50A/CAN_485_faraday/kicad/tools/set_netclasses.py` and every
plane/pour geometry in `.../tools/build_pcb.py` is recorded as an
`ENGINEERING DEFAULT`, not as an IPC-2152 result. This entry exists so that
the standard that governs those numbers is named and locatable, not so that
the numbers can be presented as verified. Closing that gap requires
purchasing the standard — tracked in `TODO.md` §12.1.

**[47]** Vimdrones, *Vimdrones ESC S50 DroneCAN — Specification and Test
Report*, product documentation, Vimdrones, 2026. [Online]. Available:
https://dev.vimdrones.com/products/vimdrones_esc_s50/
Fetched directly 2026-08-15 (HTTP 200) and read; the linked test-report images
`vimdrones_esc_s50_continuous_load_test.png` and
`vimdrones_esc_s50_62_50C_100C_battery_test.png` were fetched from the same
host (HTTP 200) and read.
Section/page: product page "Specification" table — Power supply 2S–6S; MCU ST
STM32L431KCU6; MOSFET **Toshiba TPHR8504PL**; **Continuous current 50 A
(cooling required above 30 A)**; CAN termination 120 Ω with **Solder PAD**
switch; **CAN Port Connector: Solder PAD**; **Board outline 40 mm × 17 mm**;
firmware AM32. "Test Report / 50A Continuous Test" figure — instrumented
continuous-load run: current 10.39 / 20.74 / 31.09 / 40.62 / **50.18 A**
against board temperature 54.7 / 64.2 / 73.6 / 88.3 / **103 °C**, push force
672–2108 g, RPM 12 760–22 220; setup stated as Wanptek KPS3060D at 25.2 V
(voltage spike < 27.5 V), AM32 2.18 DroneCAN, XQ QF3748 90 mm 1450 kV EDF
load, FLIR One Pro thermal camera, Mayatech MT5 force meter, **63 V 470 µF
external capacitance**, **air cooling from EDF airflow**, ambient 29 °C.
**WHAT THIS IS AND IS NOT.** This is a manufacturer's own documentation of a
shipping product, with named instruments and stated conditions — it is primary
for facts *about the S50*. It is **not** a standard, and nothing in this
repository may derive a conductor width, a creepage figure, or any other
design value from it. It is cited for three things only: an existence proof
that 6S/50 A fits in 40 × 17 mm; the measured thermal reality of that rating;
and construction techniques (mask-free solder-reinforced copper, solder-pad
connectors) visible in its published board photographs.
**ORIGIN WARNING.** The S50's gate driver is a **Fortior FD62880** (read from
the product's own board photograph), and Fortior Technology is Shenzhen, PRC.
Under the repo owner's 2026-08-15 constraint that no IC may originate in the
PRC or other restricted countries, that part **must not** be adopted here.
This project's gate driver remains the TI DRV8353S [21]. Mine this reference
for technique, not for parts.

**[48]** Texas Instruments Incorporated, *CSD19532Q5B 100 V N-Channel NexFET™
Power MOSFET*, SLPS414B, Dallas, TX, USA, Dec. 2013, rev. May 2017. [Online].
Available: https://www.ti.com/lit/ds/symlink/csd19532q5b.pdf
Local verified copy: `docs/datasheets/csd19532q5b.pdf` — fetched directly
2026-08-15 (HTTP 200, 934 kB) and read.
Section/page: title page and §3 Description — 100 V, 4 mΩ, SON 5 mm × 6 mm;
§4 Pin Configuration and Functions — pins 1/2/3 = S, 4 = G, 5/6/7/8 = D;
§6 — V_DS 100 V, continuous drain current 100 A (package limited), I_DM 400 A,
P_D 195 W at T_C = 25 °C, R_θJC 0.8 °C/W, R_θJA 50 °C/W; §7.1 Q5B Package
Dimensions; §7.2 Recommended PCB Pattern; §7.3 Recommended Stencil Pattern.
**EVALUATED 2026-08-15, NOT ADOPTED.** Selected first as the SMD replacement
for the IRFB4110PBF [20] because it preserved that part's 100 V rating
exactly. The repo owner chose the Toshiba TPHR8504PL [49] instead, accepting a
reduction in voltage margin (3.97× → 1.59× over a 6S pack) for a 5.7×
improvement in conduction loss (10 W → 1.75 W per device at 50 A). This entry
and its local datasheet are retained as the documented alternative, in the
same spirit as [26]–[29]; no symbol or footprint for it remains in the tree.

**[49]** Toshiba Electronic Devices & Storage Corporation, *TPHR8504PL — MOSFETs
Silicon N-channel MOS (U-MOS-H)*, datasheet, rev. 5.0.A, Japan, 2026-04-14.
Local verified copy: `docs/datasheets/TPHR8504PL_datasheet_en_20191024.pdf`
(10 pp.) — supplied by the repo owner 2026-08-15 and read in full.
[Online]. Available: https://toshiba.semicon-storage.com/ap-en/semiconductor/product/mosfets/detail.TPHR8504PL.html
(a direct fetch of the PDF returned HTTP 403; the local copy is the source
relied on.)
Section/page: §2 Features — R_DS(ON) 0.7 mΩ typ. at V_GS = 10 V, Q_SW 23 nC
typ., Q_oss 85.4 nC typ., V_th 1.4–2.4 V; §3 Packaging and Internal Circuit —
pins 1/2/3 = Source, 4 = Gate, 5/6/7/8 = Drain, and **two packages offered
under one part number**, 2-5Q1S "SOP Advance" (p. 8) and 2-5W1A "SOP
Advance(N)" (p. 9); §4 Absolute Maximum Ratings — V_DSS **40 V**, V_GSS ±20 V,
I_D 150 A (DC, T_c = 25 °C, package limited), 340 A silicon limit, I_DP 500 A,
P_D 170 W, E_AS 336 mJ, I_AS 120 A, T_ch 175 °C; §5 Thermal — R_th(ch-c)
0.88 °C/W, R_th(ch-a) 50 °C/W on glass-epoxy board (a).
**NO LAND PATTERN IN THIS DOCUMENT.** All 10 pages were searched: the words
"land", "mounting" and "recommend" do not appear. The land pattern is
published separately in the product catalog — see [50]. An IPC-7351-style
derivation made before [50] was located proved 46 % short on drain-land area
and 86 % short on lead-pad area, and was replaced.
**Related documents also held locally, not separately tagged** because nothing
in this repository cites them yet: 15 Toshiba application notes under
`docs/datasheets/TPHR8504PL_application_note_*.pdf`, supplied by the repo
owner 2026-08-15/16.

**[50]** Toshiba Electronic Devices & Storage Corporation, *MOSFET Product
Catalog*, ALQ00024, Japan, 2026-07-06. Local verified copy:
`docs/datasheets/TPHR8504PL_catalog_20260706_ALQ00024.pdf` (52 pp.) — supplied
by the repo owner 2026-08-16 and read.
Section/page: **p. 46 "Surface Mount Type"** — package dimensions and
"Land pattern example" published side by side for the whole surface-mount
family (DSOP Advance(WF)L/M, SOP Advance, SOP Advance(N), SOP Advance(E),
SOP Advance(EWF)). The **SOP Advance(N) (4.9 × 6.1)** cell gives the land used
by `symbols/tools/gen_tphr8504pl_footprint.py`: overall width 4.7; pad width
0.85; pitch 1.27; drain land 4.8 total height with a 1.05 castellated depth
over a 3.75 solid body; gap to lead pads 0.7; lead pad height 1.45 — total
land 4.7 × 6.95 mm.
**This is the reference to use for ANY Toshiba MOSFET package this project
adopts.** Toshiba does not put land patterns in its part datasheets; p. 46 is
where they live.

**[51]** Würth Elektronik eiSos GmbH & Co. KG, *WE-SHC Two-piece Seamless
Shielding Cabinet — FRAME*, order code 3670209, Waldenburg, Germany.
Local verified copy: `docs/datasheets/3670209.pdf` — read directly.
Section/page: p. 1 "Dimensions: [mm]" — inner 20.5 ± 0.2 × 14.9 ± 0.2, outer
20.9 ± 0.2 × 15.3 ± 0.2 (wall 0.2 mm), height 1.7 ± 0.2 mm; p. 1 "Recommended
Land Pattern: [mm]" — outer 22.2 × 16.6, ring width 1.5, outer corner R 2.15,
0.5 mm recommended tin paste mask layer. The land drawing shows **no board
holes**; the "4× ⌀0.6" callout on the same page belongs to the frame's own
Dimensions drawing, a feature of the metal part.
Cross-check: ring centreline from the land ((22.2−1.5)/2 = 10.35,
(16.6−1.5)/2 = 7.55) equals wall centreline from the body ((20.9+20.5)/4 =
10.35, (15.3+14.9)/4 = 7.55) exactly — the same two-way check that validated
[30]. Adopted 2026-08-16 in place of [30] for the 30 × 60 mm respin, saving
812 mm². **Height caution:** at 1.7 mm this frame clears the DRV8353S
(0.8 mm) and 0805 ceramics but cannot cover the MOSFETs.

**[52]** Würth Elektronik eiSos GmbH & Co. KG, *WE-SHC Two-piece Seamless
Shielding Cabinet — COVER*, order code 3671209, Waldenburg, Germany.
Local verified copy: `docs/datasheets/3671209.pdf` — read directly.
Section/page: p. 1 "Dimensions: [mm]" — inner 20.9 ± 0.2 × 15.3 ± 0.2, outer
21.3 ± 0.2 × 15.7 ± 0.2, height 1.7 mm ref.; "Assembly with Frame:
Frame(3670209), Cover(3671209)".
As with [19]/[30], the cover has **no land pattern** because nothing about it
is soldered — it clips onto the frame [51]. It is carried in the BOM and
marked "exclude from board".

**[53]** Murata Manufacturing Co., Ltd., *GHz Noise Suppression Chip Ferrite
Bead for Consumer equipment & Industrial equipment — BLM15H□□□□SN1□ Reference
Specification*, spec no. JENF243A_0024Q-01, Kyoto, Japan.
Local verified copy: `docs/datasheets/ENFA0024.pdf` — read directly
2026-08-17.
Product page: https://www.murata.com/en-global/products/productdetail?partno=BLM15HD182SN1D
Sections applied — §3 "Part Number and Rating" (BLM15HD182SN1D row): impedance
1800 Ω ±25 % at 100 MHz and 2700 Ω ±40 % at 1 GHz, rated current 200 mA, DC
resistance 2.2 Ω max initial / 2.3 Ω max after testing, remark "For high speed
signal line"; operating and storage temperature −55 °C to +125 °C. §5
"Appearance and Dimensions": 1.0 ± 0.05 mm × 0.5 ± 0.05 mm × 0.5 ± 0.05 mm,
electrode band 0.25 ± 0.1 mm, unit mass 0.001 g typical, no polarity, no
marking; equivalent circuit is L in series with R, "Resistance element becomes
dominant at high frequencies". §7.1 impedance measured per Keysight 4291A at
100 MHz / 1 GHz.
Used for: the four isolated-supply filter beads on `U3` (ADM3055E, CAN) and
`U4` (ADM2582E, RS-485) — see [10] p. 25 "Radiated Emissions and PCB Layout"
and its Table 12, which names **BLM15HD182SN1** by part number as an example
bead for exactly this role, and [9] p. 17, which specifies "approximately
2 kΩ between the 100 MHz and 1 GHz frequency range". The 1800 Ω / 2700 Ω
figures above satisfy that requirement across the band.
Land pattern: **not authored** — this part uses KiCad 9's stock
`Inductor_SMD:L_0402_1005Metric`, an IPC-7351-nominal 1005-metric land
(pads 0.59 × 0.64 mm on a 0.97 mm centre pitch), verified against §5's body
and electrode dimensions rather than assumed.
**Verification caveat (AGENTS.md §3):** `ENFA0024.pdf` is headed "Reference
Only" and is Murata's *reference* specification, not a delivery/product
specification. Every value above is read directly from it, but the delivery
spec must be obtained and re-checked before production release.

**[54]** Texas Instruments Incorporated, *MSPM0 G-Series 80MHz
Microcontrollers Technical Reference Manual*.
**NOT YET OBTAINED — `UNVERIFIED` per AGENTS.md §3.** No local copy exists in
`docs/datasheets/`, and no document number is quoted here because the
MSPM0G3507 datasheet [1] refers to it only by title (e.g. p. 73 §8.32, "see
the debug chapter of the technical reference manual"), never by number.
Guessing a SLAU number would be a fabricated citation.
Needed for: the permanent debug/write lock in TODO.md 12.5.ag. [1] establishes
that the mechanism exists and where its configuration lives, but defers every
register-level detail to this manual.
What [1] DOES verify locally (read 2026-08-18 from
`docs/datasheets/mspm0g3507.pdf`):

- §8.32 "Serial Wire Debug Interface", p. 73 — SWD is a two-wire Arm SW-DP;
  full debug functionality is described only in the TRM.
- §8.33 "Bootstrap Loader (BSL)", p. 73 — "Access to the device memory and
  configuration through the BSL is protected by a 256-bit user-defined
  password, and **it is possible to completely disable the BSL in the device
  configuration, if desired**. The BSL is enabled by default from TI."
- §7 memory map — the NONMAIN configuration NVM occupies
  0x41C0.0000–0x41C0.0200 (512 bytes), separate from main flash. This is the
  region that holds boot/debug configuration.

Obtain from https://www.ti.com/ (product folder for MSPM0G3507, "Technical
documentation") and re-cite by number and section before the lock policy is
implemented.

**[55]** XFly-Model, *EDF Ducted Fan XFly Galaxy X5 — 50 mm, 12 blades, 6S
motor 3200 KV*, product specification page.
URL: https://www.xfly-model.eu/en/edf-units/4833-edf-ducted-fan-xfly-galaxy-x5-xfly-model-50mm-12-blades-6s-motor-3200kv.html
— read 2026-08-18.
Figures as printed: thrust **1240 g**; current **38 A**; power **843 W**;
battery **6S (22.2 V)**, 2200 mAh recommended; motor 3200 KV out-runner,
26 mm diameter, 3 mm shaft; 12 blades; 50 mm class; weight **75 g**.
**Recommended ESC: 50 A**, with the manufacturer's note "The controller
should be chosen 20% over rated due to the long lasting load."
Internal consistency check: 843 W / 22.2 V = 38.0 A, matching the printed
current exactly.
Used for: validating this repository's 50 A build rating (TODO.md 12.5.ai).
38 A x 1.20 = 45.6 A required, so 50 A is the manufacturer's own answer and
this build matches it at 1.32x the draw.
**Verification caveat (AGENTS.md §3):** this is a distributor/manufacturer
product page, not a datasheet PDF. No local copy exists in
`docs/datasheets/`. Obtain a manufacturer datasheet and re-verify before
production release; in particular the page states a single "current" figure
without distinguishing continuous from peak.

**[56]** Bureau of Indian Standards, *IS/IEC 60529 (2001): Degrees of
Protection Provided by Enclosures (IP Code)* [ETD 1: Basic Electrotechnical
Standards], New Delhi, India, 2001 (reprint 2009) — verbatim national
adoption of IEC 60529. [Online]. Available:
https://law.resource.org/pub/in/bis/S05/is.iec.60529.2001.pdf
Local verified copy: `docs/datasheets/is-iec-60529-2001-ip-code.pdf` (47 pp.).
Section/page: Table 3, "Degrees of protection against water indicated by the
second characteristic numeral" — numeral 4 "Protected against splashing
water": "Water splashed against the enclosure from any direction shall have
no harmful effects," test conditions at clause 14.2.4; numeral 6 "Protected
against powerful water jets": "Water projected in powerful jets against the
enclosure from any direction shall have no harmful effects," clause 14.2.6;
numeral 7 "Protected against the effects of temporary immersion in water,"
clause 14.2.7; numeral 8 "Protected against the effects of continuous
immersion in water," clause 14.2.8, "conditions which shall be agreed between
manufacturer and user but which are more severe than for numeral 7." Clause
6, note before Table 3: "the two-digit combinations ... characteristic
numerals 5/6 (water jets) and numerals 7/8 (immersion) ... are given in
clause 6" — the two families (jet-rated vs. immersion-rated) are not
additive without an explicit dual rating (e.g. IPX6/IPX7).
Cited in: `docs/design-waterproofing-and-thermal-management.md`; README.md
(Ingress & environmental protection line); TODO.md §2.6.
Date accessed: 2026-09-06.
**Edition caveat:** the current IEC-published edition is IEC 60529 Ed. 2.2
consolidated with Amendments 1 (1999) and 2 (2013) [NEMA/ANSI contents
listing, https://www.nema.org/docs/default-source/about-us-document-library/ansi-iec_60529-2020-contents-and-scopef0908377-f8db-4395-8aaa-97331d276fef.pdf,
accessed 2026-09-06, live IEC/ANSI store fetch blocked: HTTP 403]. This
entry's local copy is the 2001 national adoption; the second-characteristic-
numeral definitions and clause numbers above are read directly from that
copy. Whether Amendments 1/2 changed clause numbering or definitions for
IPX4/6/7/8 specifically is **UNVERIFIED — needs primary source** (see
TODO.md §2.6); nothing in this repository currently relies on a difference
between editions.

**[57]** IPC (Global Electronics Association), *IPC-CC-830C: Qualification
and Performance of Electrical Insulating Compound for Printed Wiring
Assemblies*, developed by the Conformal Coating Task Group (5-33a) of the
Cleaning and Coating Committee (5-30), December 2018 (supersedes IPC-CC-830B
Amendment 1, 2008).
Local verified copy: `docs/datasheets/ipc-cc-830c-toc-scope.pdf` (4 pp.:
cover, table of contents, §1 Scope) — table of contents fetched from
https://www.electronics.org/TOC/IPC-CC-830C-toc.pdf, 2026-09-06; full
standard text is IPC-member/purchase-gated and **not held locally beyond
these 4 pages** (`webstore.ansi.org/standards/ipc/ipccc830c2019` — live fetch
not attempted for the full text).
Section/page: §1.1 "Scope," p. 1 — "The conformal coating is intended to
provide protection from moisture and contamination and provide electrical
insulation; not as a sole source of mechanical support." §1.3.1 "Types," p. 1
— coating chemistries: Type AR (acrylic), ER (epoxy), SR (silicone), UR
(polyurethane), XY (paraxylylene/Parylene), UT (ultra-thin, ≤12.5 µm target
thickness), SC (styrene block co-polymer). Table of Contents, p. vii —
§3.5.5 "Flexibility" and §3.7.2 "Thermal Shock" are both listed qualification
tests under §3.5 "Physical Requirements" / §3.7 "Environmental Requirements"
respectively; the specific pass/fail criteria and test method (mandrel
diameter, cycle count, temperature range) are **UNVERIFIED — needs primary
source**, since those clauses fall on pages 5–6 of the full standard, not the
4 pages held locally.
Cited in: `docs/design-waterproofing-and-thermal-management.md`.
Date accessed: 2026-09-06.

**[58]** W. L. Gore & Associates, Inc., *GORE Protective Vents, Screw-In
Series*, product page, Gore.com, Newark, DE, USA.
URL: https://www.gore.com/products/screw-protective-vents-outdoor-electronics-enclosures
Section/page: not paginated (product web page, not a datasheet PDF); as
read 2026-09-06 — IP ratings by model range "IP68" to "IP68 and IP69K"
(PolyVent Standard/High Airflow/High Airflow PRO/XL), stainless-steel variant
adds "IK10 (IEC 62262)"; High Airflow PRO airflow "7600 ml/min at 70 mbar";
thread options include "M12x1 and M12x1.5". The membrane material (ePTFE)
and its function — passing air/water-vapor while blocking liquid water and
particulate ingress — are stated on the parent page
https://www.gore.com/solutions-enclosure-pressure-relief (same access date).
**Verification caveat (AGENTS.md §3):** manufacturer product/marketing page,
not a datasheet PDF; no local copy in `docs/datasheets/`. Pore size and
liquid-entry-pressure figures were NOT stated on either page and are
**UNVERIFIED — needs primary source** (a part-specific datasheet, not yet
obtained). Do not select a specific PolyVent part number for BOM until a
datasheet is held locally per `AGENTS.md` §1.3.
Cited in: `docs/design-waterproofing-and-thermal-management.md`.

**[59]** Texas Instruments Incorporated, *ISO1042 Isolated CAN Transceiver
With 70-V Bus Fault Protection and Flexible Data Rate*, datasheet,
SLLSF09F, Texas Instruments Incorporated, Dallas, TX, USA, 2017-12
(revised 2026-08). [Online]. Available:
https://www.ti.com/lit/ds/symlink/iso1042.pdf
Local verified copy: `docs/datasheets/ti-iso1042-datasheet.pdf` (10 pp.).
Section/page: p. 1, "Device Information" table — DWV (SOIC-8) package,
body size 5.85 mm × 7.50 mm nominal (5.85 mm × 11.50 mm including pins);
DW (SOIC-16), body 10.30 mm × 10.30 mm. p. 1, General Description — "This
device uses a silicon dioxide (SiO2) insulation barrier with a withstand
voltage of 5000VRMS and a working voltage of 1060VRMS." §5.7 "Insulation
Specifications," Table — DWV-8: External Clearance (CLR) >8.5 mm, External
Creepage (CPG) >8.5 mm (IEC 60664-1); DW-16: >8.15 mm both. VIORM 1500 VPK,
VIOWM 1060 VRMS / 2121 VDC, reinforced isolation, Pollution Degree 2. This
is a **CAN transceiver**, functionally equivalent to ADM3055E/ADM3057E
[10], not to the RS-485 part ADM2582E/ADM2587E [9] — confirmed against
this device's own Applications/Features text ("Meets the ISO 11898-2:2016
physical layer standard," CANH/CANL pins).
Cited in: `docs/solutions/architecture-patterns/smaller-package-does-not-shrink-creepage.md`.
Date accessed: 2026-09-06.

**[60]** Texas Instruments Incorporated, *ISOW14x2 Isolated RS-485/RS-422
Transceiver with Integrated Low-Emissions, Low-Noise, High-Efficiency
DC-DC Converter (ISOW1412, ISOW1432)*, datasheet, SLLSF86D, Texas
Instruments Incorporated, Dallas, TX, USA, 2018-05 (revised 2026-08).
[Online]. Available: https://www.ti.com/lit/ds/symlink/isow1412.pdf
Local verified copy: `docs/datasheets/ti-isow1412-datasheet.pdf` (10 pp.).
Section/page: p. 1, General Description — "isolated dc-to-dc converter and
an isolated RS-485 transceiver all integrated in one package," ISOW1412
signaling rate up to 500 kbps; "20-pin wide SOIC package." Table 2-1
"Device Information" — DFM (SOIC-20) package, body size 12.83 mm ×
7.5 mm nominal. §6.6 "Insulation Specifications" — External Clearance
(CLR) >8 mm, External Creepage (CPG) >8 mm (IEC 60664-1); VIORM 1500 VPK,
VIOWM 1000 VRMS / 1500 VDC, DIN EN IEC 60747-17 reinforced isolation,
Pollution Degree 2. This is the direct **single-package** RS-485 equivalent
to ADM2582E/ADM2587E [9] (both integrate an isolated dc-dc converter and
the transceiver in one part) — it is NOT the "transceiver + separate
digital isolator + separate dc-dc + external transformer" architecture
that would be needed to build an RS-485 channel around a bare CAN-style
isolator like [59]; no such discrete RS-485 reference design or specific
dc-dc/transformer part is catalogued in this repository, and none is
selected here.
Cited in: `docs/solutions/architecture-patterns/smaller-package-does-not-shrink-creepage.md`.
Date accessed: 2026-09-06.

**[61]** Texas Instruments Incorporated, *ISOW784x High-Performance,
5000-VRMS Reinforced Quad-Channel Digital Isolators with Integrated
High-Efficiency, Low-Emissions DC-DC Converter (ISOW7840, ISOW7841,
ISOW7842, ISOW7843, ISOW7844)*, datasheet, SLLSEY2G, Texas Instruments
Incorporated, Dallas, TX, USA, 2017-03 (revised 2021-08). [Online].
Available: https://www.ti.com/lit/ds/symlink/isow7841.pdf
Local verified copy: `docs/datasheets/ti-isow7841-datasheet.pdf` (10 pp.).
Section/page: p. 1, Features/Description — "quad-channel reinforced digital
isolators with an integrated high-efficiency power converter," "up to
650 mW of isolated power," "these devices eliminate the need for a separate
isolated power supply in space-constrained isolated designs." Table
"Device Information" — SOIC-16 package, body 10.30 mm × 7.50 mm nominal.
§7.6 "Insulation Specifications" — External Clearance (CLR) >8 mm, External
Creepage (CPG) >8 mm; VIORM 1414 VPK, VIOWM 1000 VRMS / 1414 VDC, DIN V VDE
0884-11:2017-01 reinforced isolation, Pollution Degree per IEC 60664-1.
Four bidirectional-configurable data channels (INA-D/OUTA-D), NOT six —
insufficient, on its own, to carry CAN (2 signals: TX, RX) plus RS-485 in
its current 3-signal form (TXD, RXD, DE/RE) without either combining DE and
RE into one shared direction-control channel (3 total for RS-485) or
selecting an automatic-direction-sensing RS-485 transceiver that needs no
external DE/RE line (2 total for RS-485) — the latter would exactly fill the
4 available channels (CAN TX/RX + RS-485 TXD/RXD). **No specific
automatic-direction RS-485 transceiver part has been selected or verified
against a primary datasheet for this repository; this is a proposed
architecture direction only, not a BOM recommendation.**
Cited in: `docs/solutions/architecture-patterns/bom-creepage-audit-can485-faraday.md`.
Date accessed: 2026-09-06.

Track resolution of these items in `TODO.md`.
