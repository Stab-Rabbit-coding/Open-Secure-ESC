# REFERENCES.md — IEEE Bibliography

Governed by `AGENTS.md`. IEEE reference style. Each entry lists the verified
source URL and the chapter/section/page/paragraph the repo relies on, plus
the date it was accessed. Fields that could not be independently verified
(e.g. behind a purchase paywall, or blocked by anti-bot access controls) are
marked explicitly — never guessed. Tags are cited in-repo as `[n]`.

Last reviewed: 2026-08-02.

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

## Pending Verification — Not Yet Cited

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

Track resolution of these items in `TODO.md`.
