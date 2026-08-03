# Security Module Comparison: NXP S32K144 CSEc vs. Infineon SLB9672 TPM 2.0, and a Survey of 5V-Class Automotive MCU Security Options

Governed by `AGENTS.md`. This is a research/design-reference document, not a
BOM or schematic change. It supports TODO.md items 1.11 and 4.2 (secure boot
/ attestation chain design doc). Every technical claim below is either cited
to a locally verified primary datasheet/reference manual, or explicitly
marked `UNVERIFIED` per `AGENTS.md` §3 when only a secondary source (search
snippet, distributor listing) was reachable this session.

**Context:** this project's current design ([31], README.md) uses the
S32K144's on-chip CSEc for message authentication and does **not** carry an
external TPM; the SLB9672 ([2]) was evaluated and dropped 2026-08-03. This
document compares the two on their technical merits for the record, and
surveys other 5V-capable automotive-class MCUs with on-chip security
engines, in case a future build variant revisits the trade-off.

## 1. Scope and method

Requested comparison axes: EMI/EMC resiliency, message-signing/authentication
latency, PKI capability, authentication mechanism, physical footprint, and
pricing.

Primary sources used:

- [31] NXP *S32K1xx Data Sheet*, Rev. 15 (local copy `docs/datasheets/S32K1xx.pdf`)
- **NXP *S32K1xx Series Reference Manual*, Rev. 14, 09/2021** (local copy
  `docs/datasheets/S32K-RM.pdf`, 2210 pp.) — this document is now available
  locally; previously (TODO.md 1.11) it had not been obtained. This closes
  the CSEc-algorithm-detail gap flagged in TODO.md 1.11(b) — see §7 below.
  The 64-pin LQFP physical pin-**number** gap (TODO.md 1.11(a)) is a separate,
  larger task (regenerating `symbols/specs/S32K144.json`) and is **not**
  addressed by this document; it remains open.
- [2] Infineon *OPTIGA™ TPM SLB9672 TPM 2.0 FW16.xx Datasheet*, Rev. 1.3
  (local copy `docs/datasheets/infineon-slb9672-tpm20-spi-fw16.xx-datasheet-rev1.3.pdf`)

For the "other 5V automotive MCUs" survey (§8), NXP/Infineon/DigiKey/Mouser
direct fetches were blocked with HTTP 403 for every domain tried this
session — the same pattern already documented in TODO.md 1.10/1.11 for this
repo's live-fetch tooling. That section's claims are therefore sourced from
search-result snippets of vendor product pages (and, where noted, one
official Infineon GitHub CMSIS device-family-pack file that *did* fetch
successfully) and are marked `UNVERIFIED — needs primary source` throughout.
Pricing for every part in this document (§9) is a distributor listing
snapshot, not a negotiated or contract price, and is marked accordingly.

## 2. Executive summary

| Axis | S32K144 CSEc [31] | SLB9672 TPM 2.0 [2] |
| --- | --- | --- |
| Trust anchor type | On-chip HSE, SHE-compliant (symmetric only) | Discrete TPM 2.0 (TCG PTP 1.05), FIPS 140-2 L2, CC EAL4+ |
| PKI / asymmetric crypto | **None** — no RSA/ECC/certificate commands in the CSEc command set | Full: RSA up to 4096-bit, ECC (NIST P256/P384, BN P256), 4 pre-provisioned EK + EK certs |
| Authentication primitive | AES-128 CMAC (`GENERATE_MAC`/`VERIFY_MAC`) | HMAC / RSA-PSS / RSA-SSA / ECDSA sessions, TPM policy/HMAC sessions |
| Supply voltage | 2.7–5.5 V single supply (native 5V) | 1.65–3.6 V (needs a regulator/level-shift off a 5V rail) |
| Automotive qualification | AEC-Q100 (ESD/latch-up tested per -002/-011/-004) | Not stated in datasheet; qualified only to JEDEC JESD22 / J-STD-020 (commercial/industrial) |
| Package | 64-pin LQFP, 10×10 mm (shared with the whole MCU) | PG-UQFN-32, 5×5 mm (discrete add-on part + BOM/board area) |
| Extra bus/pins needed | None (internal command interface) | Yes — SPI (4 signals) + PIRQ#/RST# |
| Command latency | Not separately published; bounded by the FTFC command interface it shares with flash ops | SPI clock up to 34.65 MHz typ.; command execution latency not published |
| Indicative unit price | ~US$3.75–8.42 (whole MCU; see §9) | ~US$5.21–6.69 (added on top of a separate host MCU; see §9) |

**Headline finding:** the S32K144's CSEc and the SLB9672 are not
interchangeable on a like-for-like basis. CSEc is a symmetric-only SHE HSM —
it can authenticate messages (CMAC) and protect a small set of AES-128 keys,
but it cannot do public-key operations, certificate validation, or anything
a PKI chain (e.g. X.509-based ECU/OEM authentication) would need. The
SLB9672 is a full TPM 2.0 with RSA/ECC key generation, EK certificates, and
policy-based authorization — but it is not natively 5V, is not shown to be
AEC-Q100 qualified in its own datasheet, and adds board area, BOM cost, and
an external bus (SPI) plus its own attack surface (a chip-to-chip link that
must itself be protected) that an on-chip HSE avoids.

## 3. Authentication and message signing

### 3.1 S32K144 CSEc

CSEc implements the SHE (Secure Hardware Extension) Functional
Specification's command set inside the flash controller (FTFC), driven over
an internal command interface — no external pins [31, p.3 §1.1]. Verified
against the local Reference Manual, Chapter 36 "Flash Memory Module (FTFC)",
§36.5.13:

- `CMD_GENERATE_MAC` computes `MAC = CMAC_KEY,KEY_ID(MESSAGE, MESSAGE_LENGTH)`
  — i.e., AES-128 CMAC over the message, keyed by one of the device's key
  slots (RM §36.5.13.9, Table 36-82).
- `CMD_VERIFY_MAC` recomputes the CMAC and compares it (optionally
  truncated by `MAC_LENGTH`) against a supplied MAC, returning a boolean
  `VERIFICATION_STATUS` (RM §36.5.13.11, Table 36-83).
- A "pointer method" variant of both commands can operate directly on
  program-flash-resident data without copying it through the command
  interface, provided the data doesn't cross flash read-partition
  boundaries and the start address is 128-bit aligned (RM §36.5.13.10,
  §36.5.13.12).
- The command set is otherwise `ENC_ECB`/`DEC_ECB`/`ENC_CBC`/`DEC_CBC`
  (AES-128 encrypt/decrypt), `LOAD_KEY`/`LOAD_PLAIN_KEY`/`EXPORT_RAM_KEY`,
  and RNG/ID commands (RM §36.5.13, key-ID field list at RM p.~938). There
  is **no** RSA, ECC, ECDSA, or certificate-handling command anywhere in
  this chapter — this repo's prior `UNVERIFIED` flag on "CMAC per general
  SHE-HSM industry knowledge" (TODO.md 1.11(b)) is now **VERIFIED** against
  the primary Reference Manual text quoted above.

This resolves the message-authentication mechanism for CAN/RS-485 frame
traffic: CMAC-128, generated/verified by CSEc, keyed from one of up to 20
key slots (`SECRET_KEY`, `MASTER_ECU_KEY`, `BOOT_MAC_KEY`, `KEY_01`–`KEY_17`,
and the volatile `RAM_KEY`; not all 17 user keys are available
simultaneously — the partition is user-configurable, RM §36.5.13, Table
36-75). Secure boot uses the same primitive: `BOOT_MAC_KEY` authenticates a
boot-time CMAC over flash contents before releasing the core from reset (RM
§36, "Secure Boot," SB status bit, ~p.36047 area).

**Latency:** Chapter 36 does not publish a cycle count or µs figure for
`GENERATE_MAC`/`VERIFY_MAC` as a function of message length — it is not one
of the flash command timing rows in the local Data Sheet's Table 35/36
[31, pp.40–44], which cover erase/program/read timings only. What *is*
established: CSEc commands and normal flash program/erase are mutually
exclusive with HSRUN (112 MHz) mode — "CSEc (Security) or EEPROM
writes/erase will trigger error flags in HSRUN mode ... device will need to
switch to RUN mode (80 MHz)" [31, p.6 note 3] — so any CMAC operation
concurrent with flash traffic forces a core-clock drop to 80 MHz for that
window. The exact GENERATE_MAC/VERIFY_MAC execution time (a function of
message length, since it's a CMAC over N 128-bit blocks) is
`UNVERIFIED — needs primary source`; it would need either NXP's SHE
benchmark application note or direct bench measurement, neither obtained
this session.

### 3.2 SLB9672 TPM 2.0

The SLB9672 exposes the full TCG TPM 2.0 command set over SPI (up to 34.65
MHz typical clock [2, Table 9]). Message authentication/signing options
include HMAC (symmetric, session-based), RSA-SSA/RSA-PSS signing, and ECDSA
(NIST P256/P384) — selectable per key object, not fixed to one primitive
[2, p.1 "Key features"]. Sessions support HMAC-authenticated and
policy-authenticated command authorization (TPM 2.0 session model — general
TPM 2.0 architecture, not itself re-derived from the local datasheet, which
documents the SLB9672's specific resource limits rather than the base TPM 2.0
session spec).

**Latency:** the local datasheet's AC/timing tables (§3.1.1.4–3.1.1.5, [2,
pp.15–16]) cover only SPI bus and reset timing (`tCLK`, `tCSS`, `tPOR` =
80 µs, `tWRST` = 2 µs) — there is no published TPM2_Sign/TPM2_Create/
TPM2_Certify execution-time table in this document. Per-command execution
latency (RSA key generation is documented elsewhere in TPM literature to
take from tens of ms to multiple minutes for 3072/4096-bit keys — this
datasheet itself notes "creation of a 3072- or 4096-bit RSA primary key may
take several minutes" [2, p.1017 area, §3.2.4.2 context]) is otherwise
`UNVERIFIED — needs primary source` for this specific firmware revision;
Infineon does not publish a full command-timing table in this datasheet.

## 4. PKI capability

- **S32K144 CSEc: none.** SHE (and therefore CSEc) is a symmetric-only
  specification — AES-128 ECB/CBC/CMAC and a fixed key catalog. There is no
  path in the CSEc command set to generate or hold an RSA/ECC key pair,
  request/validate an X.509 certificate, or perform a Diffie-Hellman
  exchange. Any PKI-based authentication scheme (e.g., OEM-issued ECU
  certificates, V2X-style certificate chains) would have to be implemented
  entirely in firmware on the Cortex-M4F core, using CSEc only for the
  symmetric primitives it does support (or not using CSEc at all for that
  part of the scheme).
- **SLB9672: full TPM 2.0 PKI stack.** RSA (1024/2048/3072/4096-bit) and ECC
  (NIST P256, NIST P384, BN P256) key generation and use; 4 factory-provisioned
  Endorsement Keys with EK certificates (RSA 2048, RSA 3072, ECC P256, ECC
  P384) for device-identity attestation; up to 7 pre-generated RSA key pairs
  and up to 7 loaded persistent objects; NIST SP 800-90A/B-based RNG for key
  generation entropy [2, p.1 "Key features"].

## 5. Footprint

| Part | Package | Body size | Notes |
| --- | --- | --- | --- |
| S32K144 (this build's 64-LQFP option) | LQFP-64 | 10×10 mm, doc. no. SOT1699-1 [31, p.89 §9.1] | Whole MCU; CSEc adds zero extra footprint (internal peripheral, no dedicated pins) [31, symbols/specs/S32K144.json] |
| SLB9672 | PG-UQFN-32 | 5×5 mm [2, §2.1, Fig. 3] | Discrete add-on part; requires its own decoupling/pull-up circuit and 4-wire SPI + PIRQ#/RST# routed from the host MCU [2, §3.1.3 Fig. 7] |

Net board-area effect of adding a discrete SLB9672 to any host MCU: +5×5 mm
of a second package, plus the SPI/GPIO routing and passive components shown
in [2]'s typical schematic (3×100 nF + 1 µF bypass, 10 kΩ CS# pull-up). CSEc
adds none of this because it lives inside the MCU already on the BOM.

## 6. EMI/EMC/ESD resiliency

| Parameter | S32K144 [31, §5.8–5.9] | SLB9672 [2, Table 2] |
| --- | --- | --- |
| ESD, HBM | ±4000 V | ±2000 V |
| ESD, CDM (corner pins) | ±750 V | ±500 V |
| Latch-up immunity | 100 mA @ 125 °C | 100 mA |
| ESD test standard | AEC-Q100-002 | EIA/JESD22-A114-B |
| CDM test standard | AEC-Q100-011 | ESD Association STM5.3.1-1999 |
| Latch-up test standard | AEC-Q100-004 | EIA/JESD78 |
| Radiated emissions | "EMC measurements to IC-level IEC standards are available from NXP on request" [31, §5.9] — not published in this datasheet | Not addressed in this datasheet at all |
| Automotive qualification | AEC-Q100 (per the ESD/latch-up footnotes citing AEC-Q100 test methods directly) [31, p.25 footnotes 2–5] | Not stated. Datasheet's own "Product validation" line: "Qualified for applications according to the test conditions in the relevant tests of JEDEC JESD22 and J-STD-020" [2, p.1] — JEDEC/J-STD are commercial/industrial reliability standards, not the AEC-Q100 automotive stress-qualification suite |

The S32K144 has roughly double the SLB9672's ESD robustness on both HBM and
CDM, and — unlike the SLB9672 — is explicitly tested to the AEC-Q100 method
suite (AEC-Q100-002/-011/-004), which is the industry baseline automotive
qualification standard. Neither datasheet publishes a radiated-emissions
(RE) figure in dB µV/m or an immunity figure against a specific EMC standard
(e.g. IEC 61000-4-x, CISPR 25) — both are `UNVERIFIED — needs primary source`
for actual EMC test data; NXP's own datasheet says such data exists but is
available only on request, not in this document.

**Design implication:** because CSEc has no external pins, it introduces no
new signal-integrity or EMI-coupling path (no SPI bus, no chip-to-chip
crosstalk risk) beyond what the MCU package already presents. A discrete
SLB9672 adds an SPI bus and two more single-ended lines (PIRQ#/RST#) that
must be routed and, at the higher EMI-hardening tiers this project defines
(README.md: Isolation/Grounding/Faraday), shielded or filtered like any
other off-chip signal.

## 7. Reference Manual note (resolves part of TODO.md 1.11)

TODO.md 1.11(b) flagged CSEc's algorithm detail (AES-128-CMAC) as
"UNVERIFIED against a primary source pending" because neither the SHE
Functional Specification nor the S32K1xx Reference Manual's CSEc chapter had
been obtained. `docs/datasheets/S32K-RM.pdf` (NXP *S32K1xx Series Reference
Manual*, Rev. 14, 09/2021, 2210 pp.) is now present in this repo and was used
throughout §3.1 above to verify that claim directly against RM Chapter 36
§36.5.13 (`CMD_GENERATE_MAC`/`CMD_VERIFY_MAC` definitions). REFERENCES.md's
[31] entry has been updated accordingly (see the citation-log diff in that
file). TODO.md 1.11(a) — the 64-pin LQFP physical pin-**number** map — is a
separate, larger regeneration task against this same Reference Manual's
pinout chapter and is intentionally **not** attempted here; it remains open.

## 8. Survey: other 5V-class automotive MCUs with on-chip security

Requested per the task: "research the security features of other 5V
automotive class MCUs." The three below were chosen because each is
marketed for automotive (motor-control or zone/domain) use and each has some
5V-related claim; none of their primary datasheets could be fetched live
this session (HTTP 403 on nxp.com/infineon.com/microchip.com/renesas.com,
matching this repo's established pattern per TODO.md 1.10/1.11). Every
line below is `UNVERIFIED — needs primary source` unless otherwise noted.

### 8.1 Infineon TLE987x / TLE9879 (MOTIX™ motor-control SoC family)

Same market segment as this project (single-chip 3-phase BLDC motor
driver + Arm Cortex-M3, LIN transceiver, integrated FET gate drive)
[search: infineon.com/part/TLE9879-2QXA40 product page, section/page not
verified — live fetch blocked HTTP 403].

- **Security engine: none found.** The device's own official CMSIS device
  family pack, fetched live from Infineon's GitHub
  (`github.com/Infineon/cmsis_packs`, `TLE987x/Infineon.TLE987x_DFP.pdsc`,
  accessed 2026-08-03), lists its peripheral set — ADC, timers, UART, SPI,
  LIN transceiver, bridge driver (BDRV), power management unit, DMA — with
  **no** AES/CRC/HSM/SHE or any other cryptographic peripheral named
  anywhere in that file. This is a primary Infineon-authored source (an
  official device-family-pack XML, not a marketing page) but it is not the
  full datasheet, so it is verified for "no security peripheral is exposed
  in the CMSIS pack" specifically, not for "the silicon has absolutely
  none" in some undocumented form.
- Package: VQFN-48-EP, 7×7 mm [search: LCSC/JLCPCB part listings for
  TLE9879-2QXA40, not independently verified].
- Supply: the TLE987x family is designed to run directly from automotive
  battery rails through an internal regulator and is used in 5V-class
  BLDC ESC designs, matching this project's own domain — but the exact
  VDD/VBAT operating range was not independently confirmed this session
  (datasheet fetch blocked).
- Pricing: ~US$10.24 (LCSC, single unit) [search snippet, not independently
  verified, volatile].

**Assessment:** if a future build wanted a competing "everything on one
5V-class automotive chip" MCU, TLE987x/TLE9879 is not a security-equivalent
alternative to the S32K144 — it appears to ship with no on-chip
cryptographic/authentication engine at all, i.e., strictly less capable
than CSEc for this project's message-authentication requirement.

### 8.2 Microchip dsPIC33C "MPT" Secure DSC family

[search: microchip.com "dsPIC33C MPT Secure Digital Signal Controllers"
product page, section/page not verified — live fetch blocked HTTP 403]

- Marketed features: "CodeGuard" security, hardware cryptographic
  accelerators (reducing crypto execution time vs. software), anti-tamper
  and side-channel protections, AEC-Q100 Grade 0/1 qualification, ISO 26262
  process compliance.
- The product line's non-secure sibling (dsPIC33CK256MP508) is documented
  by a distributor listing as an 80-pin TQFP (12×12 mm), 3–3.6 V supply
  [search: Newark listing, not independently verified]; a distinct "100-pin
  Secure DSC" variant (e.g. dsPIC33CK...MPT608) was referenced in search
  results but its package/voltage/security-command-set detail could not be
  confirmed against a primary datasheet this session.
- **This entire line item, including whether its hardware crypto engine
  supports asymmetric (RSA/ECC/PKI) operations or is symmetric-only like
  CSEc, is `UNVERIFIED — needs primary source`.** Microchip's own marketing
  copy uses the word "cryptographic accelerators" without specifying the
  algorithm set in the search snippets retrieved.
- Pricing: not obtained for the Secure ("MPT") variant specifically.

### 8.3 Renesas RH850/U2A (Zone/Domain automotive MCU series)

[search: renesas.com RH850/U2A16 product page, section/page not verified —
live fetch blocked HTTP 403]

- Marketed features: "flexible, individual power supply (typ. 1.12 V,
  3.3 V, 5.0 V)" — i.e., the U2A16 variant is described as supporting a
  native 5.0 V supply option, alongside 1.12 V/3.3 V rails for other
  domains on the same chip; "HSM for Evita-full with dedicated CPU/Flash
  and HW crypt algorithm support."
- EVITA-Full (as distinct from the EVITA-Light tier SHE/CSEc-class HSMs
  target) is understood in general automotive-security literature to
  include a dedicated crypto co-processor and asymmetric-crypto support in
  addition to symmetric primitives — this would, if confirmed, make the
  RH850/U2A16's HSM a closer PKI-capable competitor to the SLB9672 than
  CSEc is. **This distinction is `UNVERIFIED — needs primary source`** for
  this specific part; it was not independently confirmed against a Renesas
  RH850/U2A datasheet or user's manual this session (fetch blocked).
- Scale: 4× 400 MHz CPU cores (dual-core lockstep ×2), 16 MB flash, 3.6 MB
  SRAM, referenced with a 516-pin package configuration [search snippet] —
  this is a substantially larger/more expensive device class than the
  S32K144 (single 80/112 MHz Cortex-M4F, 512 KB flash, 64-pin LQFP) or the
  SLB9672 (a small companion chip), and would not be a drop-in comparison
  on cost or footprint even if its HSM capability is confirmed superior.
- Pricing: not obtained.

## 9. Pricing (all figures are distributor-listing snapshots, not verified against a live distributor page this session — see §1)

| Part | Listed unit price (qty 1, unless noted) | Source |
| --- | --- | --- |
| S32K144 (FS32K144HAT0MLHT, 64-LQFP) | ~US$8.42 | Digi-Key search snippet |
| S32K144 (FS32K144HFT0MLHT, 64-LQFP, qty 100) | ~US$3.75 | Digi-Key search snippet |
| SLB9672AU20FW1613XTMA1 | ~US$5.21–6.69 (qty-dependent) | Digi-Key search snippet |
| TLE9879-2QXA40 | ~US$10.24 | LCSC search snippet |
| dsPIC33CK256MP508 (non-Secure sibling) | not captured this session | — |
| RH850/U2A16 | not captured this session | — |

Every WebFetch attempt against digikey.com, mouser.com, nxp.com,
infineon.com, microchip.com, and renesas.com returned HTTP 403 this session
— consistent with the outbound-fetch pattern already documented in
TODO.md 1.10/1.11 for this repo. All prices above come only from WebSearch
result snippets (secondary, not independently re-verified against a live
page), and per `AGENTS.md` §1.1 must not be treated as settled figures for
a BOM. Distributor unit pricing also legitimately fluctuates day to day and
by quantity break, so even a live-fetched price would only be a snapshot.

## 10. Open items

- CSEc `GENERATE_MAC`/`VERIFY_MAC` execution latency (µs, as a function of
  message length) — not published in the local Data Sheet or Reference
  Manual; would need an NXP application note or bench measurement.
- SLB9672 per-command (HMAC/RSA-sign/ECDSA-sign) execution latency — not
  published in the local datasheet; would need a TPM performance
  application note or bench measurement.
- Both parts' radiated-emissions (dB µV/m) and conducted-immunity figures
  against a named EMC standard — neither datasheet publishes one; NXP's
  datasheet explicitly defers this to data "available from NXP on request."
- TLE987x/TLE9879, dsPIC33C MPT Secure, and RH850/U2A16 all need their
  actual manufacturer datasheets (not search snippets) fetched and read
  before any claim in §8 can be upgraded from `UNVERIFIED` to `VERIFIED`
  per `AGENTS.md` §3 — flagged in TODO.md.
- S32K144 physical 64-pin LQFP pin-**number** map (TODO.md 1.11(a)) — now
  unblocked in principle since `docs/datasheets/S32K-RM.pdf` is locally
  available, but not attempted in this document; tracked separately.
