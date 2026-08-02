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
"Version 1.7" — exact current revision `UNVERIFIED`), E-One Moli Energy
Corp., Taiwan. [Online]. Available:
https://www.molicel.com/wp-content/uploads/INR21700P42A-V4-80092.pdf
(live fetch blocked: HTTP 403, 2026-08-02).
No local copy yet — `UNVERIFIED — needs primary source (see TODO.md)`.
Section/page: not verified — live fetch blocked this session; content
corroborated identically across four independent distributor/mirror
sources (dnkpower.com, 18650batterystore.com, batemo.com, aboutenergy.io)
quoting the same per-cell table: nominal 3.60 V, max charge 4.20 V,
discharge cutoff 2.50 V; standard charge 4.2 A (1.5 h); capacity 4200 mAh
typ./4000 mAh min. Cross-check source (pouch/LiPo format, corroborating
but not primary): Kokam Co., Ltd., *Cell Specification Data, SLPB
65216216*, Kokam Co., Ltd., Republic of Korea, available
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
Candidate cell for voltage-tier derating (TODO.md §5.2); not yet
selected in a bill of materials.
Cited in: docs/datasheets/ (not yet present; not yet cited in repo-root
README.md); symbols/specs/INR21700_P42A.json (generic 2-terminal cell
symbol); builds/6s/50A/CAN_485_faraday/README.md (6S pack BOM, ×6 cells).
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
Seamless Shielding Cabinet*, part no. 3671375, datasheet, Würth
Elektronik eiSos GmbH & Co. KG, Waldenburg, Germany. [Online].
Available: https://www.we-online.com/components/products/datasheet/3671375.pdf
(live fetch blocked: HTTP 403, 2026-08-02).
No local copy yet — `UNVERIFIED — needs primary source (see TODO.md)`.
Section/page: not verified — live fetch blocked this session; content
corroborated across the WE-SHC product-family page and distributor
(Mouser/DigiKey) listings, not read from the primary PDF. Indexed
content: tin-plated two-piece (grid frame + removable cover) board-level
shield; shielding effectiveness up to 60 dB over 500 MHz–3 GHz; part
3671375 inner 29.5 mm ±0.2 mm / outer 30.1 mm ±0.2 mm, height ≈3.8 mm
(ref). Candidate for board-level shielding over the gate-drive/high-di/dt
switching node area — the Faraday EMI-hardening tier (TODO.md §7.1).
Alternative real manufacturers in this space, not further verified:
Laird Technologies, Leader Tech.
Candidate part; not yet selected in a bill of materials.
Cited in: docs/datasheets/ (not yet present; not yet cited in repo-root
README.md); symbols/WE_SHC_3671375.kicad_sym (mechanical placeholder
symbol); builds/6s/50A/CAN_485_faraday/README.md (Faraday-tier BOM).
Date accessed: 2026-08-02.

---

**[20]** Infineon Technologies AG, *IRFB4110PbF — HEXFET Power MOSFET*,
datasheet, Rev. 01-01 (filename-inferred; cover-page date `UNVERIFIED`),
Infineon Technologies AG, Neubiberg, Germany. [Online]. Available:
https://www.infineon.com/assets/row/public/documents/24/49/infineon-irfb4110-datasheet-en.pdf
(live fetch blocked: HTTP 403, 2026-08-02).
No local copy yet — `UNVERIFIED — needs primary source (see TODO.md)`.
Section/page: not verified — this session's WebFetch tool returned HTTP
403 for every domain attempted, including ti.com, infineon.com, vishay.com,
analog.com, allegromicro.com, distributor mirrors, and a neutral
non-vendor control URL — no PDF was opened directly. Specs below are
corroborated across ≥2 independent distributor listings (DigiKey, RS,
LCSC), not read from the primary document: VDSS = 100 V; RDS(on) = 3.7 mΩ
typ./4.5 mΩ max (exact test condition, e.g. VGS, `UNVERIFIED`); ID = 120 A
package-limited continuous rating (exact Tc binding `UNVERIFIED`; a
higher 180 A "silicon-limited" figure also appears in listings — the
more conservative 120 A figure is used here); TO-220AB package.
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
Candidate part for the power stage (TODO.md §5.1); not yet selected in
a bill of materials.
Cited in: docs/datasheets/ (not yet present; not yet cited in repo-root
README.md); symbols/IRFB4110PBF.kicad_sym (standard TO-220 G/D/S pinout);
builds/6s/50A/CAN_485_faraday/README.md (50A-tier BOM, ×6: 1 per switch
position × 2 positions × 3 phases).
Date accessed: 2026-08-02.

---

**[21]** Texas Instruments Incorporated, *DRV835x 9-V to 75-V
Three-Phase Smart Gate Driver with Integrated Current Shunt Amplifiers*
(DRV8353S variant: SPI configuration interface), datasheet, literature
no. SLVSDY6, Rev. A (Aug. 2018; a later revision letter likely exists —
`UNVERIFIED`), Texas Instruments Incorporated, Dallas, TX, USA. [Online].
Available: https://www.ti.com/lit/ds/symlink/drv8353.pdf (live fetch
blocked: HTTP 403, 2026-08-02).
No local copy yet — `UNVERIFIED — needs primary source (see TODO.md)`.
Section/page: not verified — live fetch blocked this session; specs
corroborated via distributor/search-indexed excerpts, not read from the
primary PDF. Indexed content: recommended VM operating range 9 V to
75 V (spans 2S ≈8.4 V through 12S ≈50.4 V max charge per [14], with
~25 V headroom at 12S — tighter margin than the FET's [20] ~2×,
flagged as needing a transient/spike analysis, e.g. a TVS clamp on VM,
before locking the 10S/12S BOM variant); three integrated bidirectional
current-shunt amplifiers for low-side per-phase shunt sensing (gain
settings `UNVERIFIED`); configurable peak gate-drive current settings
(reported 50/100/150/300/450/700/1000 mA); integrated UVLO, gate-drive
UVLO, VDS overcurrent monitoring, and gate-driver fault detection.
Proposed as the same part for all 7 amperage tiers — the SPI-programmable
IDRIVE setting and CSA gain register absorb the per-tier differences
rather than requiring a different gate-driver part.
Candidate part for the power stage (TODO.md §5.1); not yet selected in
a bill of materials.
Cited in: docs/datasheets/ (not yet present; not yet cited in repo-root
README.md); symbols/DRV8353S.kicad_sym (UNVERIFIED placeholder pin
numbering — see symbols/specs/DRV8353S.json "verification" field);
builds/6s/50A/CAN_485_faraday/README.md (50A-tier BOM; note on possible
overlap with INA240 [22]'s external current-sense function).
Date accessed: 2026-08-02.

---

**[22]** Texas Instruments Incorporated, *INA240 −4-V to 80-V,
Bidirectional, Ultra-Precise Current Sense Amplifier With Enhanced PWM
Rejection*, datasheet, literature no. SBOS633 (`UNVERIFIED` — not
independently confirmed against the PDF cover page), Texas Instruments
Incorporated, Dallas, TX, USA. [Online]. Available:
https://www.ti.com/lit/gpn/INA240 (live fetch blocked: HTTP 403,
2026-08-02).
No local copy yet — `UNVERIFIED — needs primary source (see TODO.md)`.
Section/page: not verified — live fetch blocked this session; specs
corroborated via distributor/search-indexed excerpts, not read from the
primary PDF. Indexed content: common-mode voltage range −4 V to +80 V
independent of supply (for a low-side per-phase shunt referenced near
ground, this covers all voltage tiers 2S–12S per [14]); four fixed
gains (20/50/100/200 V/V); enhanced PWM rejection, explicitly marketed
for motor-drive/PWM common-mode transients; supply 2.7–5.5 V, ~2.4 mA
max.
Candidate part answering the current-sensing selection (TODO.md §5.3);
proposed as the same part for all 7 amperage tiers, paired with the
Vishay shunt series [23] whose resistance value (and, at 80A/120A,
parallel count) varies by tier.
Candidate part for the power stage; not yet selected in a bill of
materials.
Cited in: docs/datasheets/ (not yet present; not yet cited in repo-root
README.md); symbols/INA240.kicad_sym (UNVERIFIED placeholder pin
numbering — see symbols/specs/INA240.json "verification" field);
builds/6s/50A/CAN_485_faraday/README.md (50A-tier BOM; open question on
overlap with DRV8353S [21]'s integrated shunt-sense amplifiers).
Date accessed: 2026-08-02.

---

**[23]** Vishay Dale (Vishay Intertechnology, Inc.), *WSLP — Power Metal
Strip® Resistors*, datasheet, document no. 30122 (revision/date on one
mirror indexed as 10-Aug-2018 — exact current revision `UNVERIFIED`),
Vishay Intertechnology, Inc., Malvern, PA, USA. [Online]. Available:
https://www.vishay.com/docs/30122/wslp.pdf (live fetch blocked: HTTP
403, 2026-08-02).
No local copy yet — `UNVERIFIED — needs primary source (see TODO.md)`.
Section/page: not verified — live fetch blocked this session; specs
corroborated via distributor/search-indexed excerpts, not read from the
primary PDF. Indexed content: WSLP2512 package resistance range 0.5 mΩ
to 10 mΩ, power rating 3.0 W at 70°C, AEC-Q200 qualified metal-strip
construction. Per-tier sizing (engineering calculation against the
3 W/2512-package rating, not itself a datasheet claim): 10 mΩ (10A),
5 mΩ (20A), 2 mΩ (30A), 1.5 mΩ (40A), 1 mΩ (50A); at 80A/120A a single
WSLP2512 exceeds its 3 W rating (3.2 W and 7.2 W respectively at the
sizes that would otherwise apply), so 2–4 devices in parallel (or a
higher-power Vishay sibling part, not yet selected) are required —
flagged as an open gap, not a drop-in substitution. Alternative
considered: Allegro MicroSystems ACS732/ACS733 galvanically-isolated
Hall-effect current sensor ICs (up to ±65 A, e.g. ACS733KLATR-65AB-T,
20 mV/A, <1 mΩ internal resistance, 3600–4800 VRMS isolation) — not
selected because the family tops out below the 80A/120A tiers, breaking
BOM commonality; a higher-range Allegro part (e.g. ACS781/ACS758 family)
would be needed for those tiers and was not pursued further.
Candidate part answering the current-sensing selection (TODO.md §5.3);
not yet selected in a bill of materials; the 80A/120A shunt sizing gap
remains open.
Cited in: docs/datasheets/ (not yet present; not yet cited in repo-root
README.md); symbols/WSLP2512.kicad_sym (generic 2-terminal pinout);
builds/6s/50A/CAN_485_faraday/README.md (50A-tier BOM, 1 mΩ ×3, one per
phase).
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

**Methodology note on [12]–[23] (2026-08-02):** every new entry added in
this pass was researched with the live-fetch tool (WebFetch) returning
HTTP 403 for every domain attempted this session, including a neutral
non-vendor control URL used purely as a sanity check — a broader failure
than the vendor-specific blocks noted for [2] and [6]. All specs in
[12]–[23] are therefore corroborated via ≥2 independent secondary
sources (distributor listings, search-indexed excerpts of the
manufacturer's own datasheet text) rather than read directly from a
primary PDF, and none has a local verified copy in `docs/datasheets/`
yet. Every such entry is marked accordingly and must not be treated as
a settled citation — re-attempt direct fetch or manual PDF download in
a future session before design docs cite these as verified.

Track resolution of these items in `TODO.md`.
