# REFERENCES.md — IEEE Bibliography

Governed by `AGENTS.md`. IEEE reference style. Each entry lists the verified
source URL and the chapter/section/page/paragraph the repo relies on, plus
the date it was accessed. Fields that could not be independently verified
(e.g. behind a purchase paywall, or blocked by anti-bot access controls) are
marked explicitly — never guessed. Tags are cited in-repo as `[n]`.

Last reviewed: 2026-08-02.

---

**[1]** STMicroelectronics, *STM32L431xx — Ultra-low-power Arm® Cortex®-M4
32-bit MCU+FPU, Bluetooth® 5, up to 256 KB Flash, USB, LP-WFI 130 nA*,
datasheet, STMicroelectronics, Geneva, Switzerland. [Online]. Available:
https://www.st.com/resource/en/datasheet/stm32l431cb.pdf
Product page: https://www.st.com/en/microcontrollers-microprocessors/stm32l431kc.html
Section/page: covers the STM32L431xx family (includes STM32L431KC); exact
document ID, revision, and page/section for the KCU6 (UFQFPN32, 256 KB
Flash) ordering code — **not verified**, ST's datasheet PDF and product
page returned HTTP 403 to automated fetch. A contributor with browser
access must confirm the doc ID/revision and record the specific
device-summary table page before this entry is treated as complete.
Cited in: README.md (MCU line).
Date accessed: 2026-08-02.

---

**[2]** Infineon Technologies AG, *OPTIGA™ TPM SLB 9672 TPM 2.0, FW16.xx*,
datasheet, Rev. 1.3, Infineon Technologies AG, Neubiberg, Germany,
2024-11-18. [Online]. Available:
https://www.infineon.com/assets/row/public/documents/30/49/infineon-slb9672-tpm20-spi-fw16.xx-ds-rev1-3-2024-11-18-datasheet-en.pdf
Product page: https://www.infineon.com/part/OPTIGA-TPM-SLB-9672-FW15
Section/page: document-level citation confirmed via publisher search
listing (title, revision, publication date). Specific section/page for
compliance claims (TCG TPM Library Rev. 1.59; PC Client Platform TPM
Profile v1.05; Common Criteria EAL4+; FIPS 140-2 Level 2) — **not
verified**, Infineon's PDF returned HTTP 403 to automated fetch. Confirm
against the retrieved PDF before relying on specific page citations.
Cited in: README.md (TPM line).
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
listing is accessible without purchase.
Cited in: README.md (Protocol: RS-485).
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
referenced by name in README.md.
Cited in: README.md (Protocol: CAN2.0).
Date accessed: 2026-08-02.

---

**[6]** International Organization for Standardization, *Road vehicles —
Controller area network (CAN) — Part 1: Data link layer and physical
signalling*, ISO 11898-1:2015, ISO, Geneva, Switzerland, 2015-12.
[Online]. Available: https://www.iso.org/standard/63648.html
Section/page: not verified — standard is paywalled; only the ISO catalog
listing (scope/abstract) is accessible without purchase.
Cited in: README.md (Protocol: CAN-FD).
Date accessed: 2026-08-02.

---

**[7]** Department of Defense (USA), *Interface Standard: Digital Time
Division Command/Response Multiplex Data Bus*, MIL-STD-1553B, U.S.
Department of Defense, 1978-09-21. [Online, government-hosted mirror].
Available: https://nepp.nasa.gov/docuploads/43745C0A-323E-4346-A434F4342178CD0E/MIL-STD-1553.pdf
Section/page: not yet pinned to a specific section for a repo claim;
general applicability only. Note: superseded by MIL-STD-1553C (2018) for
new designs — confirm which revision the project actually targets before
final design commitment.
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

## Pending Verification — Not Yet Cited

The following items are named in `README.md` but currently have **no**
authoritative published specification and MUST NOT be cited as conforming
to a standard until one is located and verified (see `AGENTS.md` §1.3):

- **PWM** — generic technique, no single governing standard; if a specific
  PWM interface standard applies to this design, identify and cite it.
- **SBus** — proprietary Futaba Corporation protocol; no publicly published
  official specification located. Needs authoritative sourcing (Futaba
  technical documentation) or must remain marked reverse-engineered/
  unofficial in any implementation notes.
- **DBus** — proprietary protocol (context-dependent, e.g. DJI); no
  publicly published official specification located. Same treatment as
  SBus above.
- **UART / TTL / SPI** — de facto industry conventions, not governed by a
  single ratified standard body document in the way RS-232/RS-485/CAN are.
  If a specific controller's SPI/UART peripheral behavior is being cited,
  cite the MCU datasheet section directly, not "SPI" as a standard.
- **EMI hardening tiers (Isolation, Grounding, Faraday)** — no citation yet
  tying these terms to a specific EMC standard (e.g. IEC 61000 series,
  MIL-STD-461). Required before EMI hardening claims are made in design
  docs.

Track resolution of these items in `TODO.md`.
