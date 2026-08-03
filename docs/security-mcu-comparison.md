# Security Module Comparison: NXP S32K144 CSEc vs. Infineon SLB9672 TPM 2.0, and a Survey of Automotive-Class MCU Security Options

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
surveys other automotive-class MCUs with on-chip security engines, in case a
future build variant revisits the trade-off. The survey started scoped to
"5V-class" parts, then the repo owner clarified that most of the rest of
this project's design is 3.3V-class, so §9 below covers both, noting each
part's actual supply voltage rather than filtering by it.

## 1. Scope and method

Requested comparison axes: EMI/EMC resiliency, message-signing/authentication
latency, PKI capability, authentication mechanism, physical footprint, and
pricing.

Primary sources used:

- [31] NXP *S32K1xx Data Sheet*, Rev. 15 (local copy `docs/datasheets/S32K1xx.pdf`)
- **NXP *S32K1xx Series Reference Manual*, Rev. 14, 09/2021** (local copy
  `docs/datasheets/S32K-RM.pdf`, 2210 pp.) — closes the CSEc-algorithm-detail
  gap flagged in TODO.md 1.11(b) — see §7 below. The 64-pin LQFP physical
  pin-**number** gap (TODO.md 1.11(a)) is a separate, larger task
  (regenerating `symbols/specs/S32K144.json`) and is **not** addressed by
  this document; it remains open.
- [2] Infineon *OPTIGA™ TPM SLB9672 TPM 2.0 FW16.xx Datasheet*, Rev. 1.3
- [33] Microchip *dsPIC33CK512MPT608 Family Data Sheet*, DS70005501B
- [35] STMicroelectronics *STM32G431x6/x8/xB* datasheet, DS12589 Rev. 6
  (restored to the repo from git history 2026-08-03 specifically for §9.4)
- [36] Microchip *SAM D5x/E5x Family Data Sheet*, DS60001507G
- [37] Texas Instruments *TMS320F28002x Real-Time Microcontrollers*
  datasheet, SPRSP45C
- [38] Texas Instruments *MSPM0G310x* datasheet, SLASF12D
- [39] Texas Instruments *MSPM0 G-Series 80MHz Microcontrollers Technical
  Reference Manual*, SLAU846E (2521 pp.)
- [40] Texas Instruments *Cybersecurity Enablers in MSPM0 MCUs* application
  note, SLAAE29A
- [41] Texas Instruments *EMC Improvement Guide for MSPM0* application
  note, SLAAET8A
- [42] Texas Instruments *MSPM0G3x0x/G1x0x/G3x0x-Q1 Errata*, SLAZ742G
- [43] Texas Instruments *MSPM0G350x-Q1* automotive datasheet

Every direct vendor/distributor fetch attempted this session (nxp.com,
infineon.com, microchip.com, renesas.com, ti.com, digikey.com, mouser.com,
alldatasheet.com) returned HTTP 403, matching this repo's established
pattern (TODO.md 1.10/1.11), with two exceptions: an Infineon-hosted GitHub
CMSIS file (§9.1) and GitHub itself (used to recover the historical
STM32G431C6 datasheet from this repo's own git history — see [35]'s entry).
Where a part's datasheet was **not** obtained locally this session (Infineon
TLE987x/TLE9879, §9.1; Renesas RH850/U2A16, §9.3), claims are sourced from
WebSearch result snippets and marked `UNVERIFIED — needs primary source`
throughout. Pricing for every part in this document (§10) is a distributor
listing snapshot, not a negotiated or contract price, and is marked
accordingly. Two datasheets were added to the repo but not deeply mined this
pass and are not separately cited: `docs/datasheets/slaae76e.pdf` (MSPM0
G-Series Hardware Development Guide application note) — present locally,
available for a future pass if a specific claim is needed from it.

## 2. Executive summary

| Axis | S32K144 CSEc [31] | SLB9672 TPM 2.0 [2] |
| --- | --- | --- |
| Trust anchor type | On-chip HSE, SHE-compliant (symmetric only) | Discrete TPM 2.0 (TCG PTP 1.05), FIPS 140-2 L2, CC EAL4+ |
| PKI / asymmetric crypto | **None** — no RSA/ECC/certificate commands in the CSEc command set | Full: RSA up to 4096-bit, ECC (NIST P256/P384, BN P256), 4 pre-provisioned EK + EK certs |
| Authentication primitive | AES-128 CMAC (`GENERATE_MAC`/`VERIFY_MAC`) | HMAC / RSA-PSS / RSA-SSA / ECDSA sessions, TPM policy/HMAC sessions |
| Supply voltage | 2.7–5.5 V single supply (native 5V, runs fine at 3.3V too) | 1.65–3.6 V (needs a regulator/level-shift off a 5V rail) |
| Automotive qualification | AEC-Q100 (ESD/latch-up tested per -002/-011/-004) | Not stated in datasheet; qualified only to JEDEC JESD22 / J-STD-020 (commercial/industrial) |
| Package | 64-pin LQFP, 10×10 mm (shared with the whole MCU) | PG-UQFN-32, 5×5 mm (discrete add-on part + BOM/board area) |
| Extra bus/pins needed | None (internal command interface) | Yes — SPI (4 signals) + PIRQ#/RST# |
| Command latency | Not separately published; bounded by the FTFC command interface it shares with flash ops | SPI clock up to 34.65 MHz typ.; command execution latency not published |
| Indicative unit price | ~US$3.75–8.42 (whole MCU; see §10) | ~US$5.21–6.69 (added on top of a separate host MCU; see §10) |

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

**Where the wider survey (§9) landed:** no single part found matches CSEc's
cost/footprint/qualification *and* the SLB9672's PKI capability at once.
The closest things to "PKI without a discrete chip" are the dsPIC33CK512MPT608
(§9.2, full PKI, not 5V, largest footprint, availability unclear) and the
SAM E51G19 (§9.5, a math-acceleration peripheral rather than a certified
secure element, but small and AEC-Q100 qualified). The MSPM0 candidates
(§9.7–9.8) turned out to have a real software-based secure-boot/PKI-adjacent
story (Keystore, CSC/BIM, software ECDSA-P256) layered on top of hardware
AES/CRC/TRNG that this document did not initially give them credit for — see
§9.7's note. §8 below (message-signing latency) resolves, with real
cycle-count data, the standing question of whether an MCU's crypto can keep
up with the actual authentication rate this design needs. On pricing, the
MSPM0G350x-Q1 (§9.8) turned out to undercut every other candidate in this
survey by a wide margin (~US$2.79–3.00, repo-owner-confirmed live
distributor price) while carrying both AEC-Q100 Grade 1 and ISO 26262
ASIL B (TÜV) certification — the main open question for it is whether its
Cortex-M0+ core has enough headroom for this project's control loop.

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
this session. See §8 for why this gap matters less than it first appears.

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
See §8 for the design implication.

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
- See §9 for how the survey candidates compare on this axis — summarized
  in the table at the start of §9.

## 5. Footprint

| Part | Package | Body size | Notes |
| --- | --- | --- | --- |
| S32K144 (this build's 64-LQFP option) | LQFP-64 | 10×10 mm = 100 mm² [31, p.89 §9.1] | Whole MCU; CSEc adds zero extra footprint (internal peripheral) |
| SLB9672 | PG-UQFN-32 | 5×5 mm = 25 mm² [2, §2.1, Fig. 3] | Discrete add-on part; needs decoupling/pull-up circuit + 4-wire SPI + PIRQ#/RST# from the host MCU |
| dsPIC33CK512MPT608 | TQFP-100 | 12×12 mm = 144 mm² [33] | Only package this family ships in; largest footprint in this survey |
| STM32G431K + SLB9672 | LQFP32/UFQFPN32 (7×7 or 5×5 mm) + SLB9672 UQFN32 (5×5 mm) | 74 mm² or 50 mm² combined, **2 packages** [35] | Two-chip combo; adds an inter-chip SPI bus |
| SAM E51G19 | VQFN-48 | 5×5 mm = 25 mm² [36] | Smallest single-chip PKI-capable option (math-accelerator class, see §9.5) |
| TMS320F280025(-Q1) | LQFP-48 (smallest) | 7×7 mm = 49 mm² [37] | Excluded from the security shortlist — see §9.6 |
| MSPM0G3107 | VQFN-32 or VSSOP-20 | 5×5 mm or 5.1×4.9 mm ≈ 25 mm² [38] | Tied smallest footprint; CAN-FD present even on the 20-pin part |
| MSPM0G350x-Q1 | VSSOP-28 (smallest) | 7.1×3 mm ≈ 21 mm² [43] | Smallest footprint of every part in this survey |

Net board-area effect of adding a discrete SLB9672 to any host MCU: +5×5 mm
of a second package, plus the SPI/GPIO routing and passive components shown
in [2]'s typical schematic (3×100 nF + 1 µF bypass, 10 kΩ CS# pull-up). Any
on-die security engine (CSEc, dsPIC33's Secure Subsystem, SAM's PUKCC/AES,
MSPM0's AES/Keystore) adds none of this because it lives inside the MCU
already on the BOM.

## 6. EMI/EMC/ESD resiliency

| Parameter | S32K144 [31] | SLB9672 [2] | dsPIC33CK512MPT608 [33] | STM32G431 [35] | SAM E51G19 [36] | TMS320F280025-Q1 [37] | MSPM0G3107 [38] | MSPM0G350x-Q1 [43] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ESD, HBM | ±4000 V | ±2000 V | Not published | ±2000 V | ±2000 V | ±2000 V | ±2000 V | ±2000 V |
| ESD, CDM | ±750 V | ±500 V | Not published | ±250 V | ±750 V | ±500 V/±750 V corner | ±500 V | ±500 V/±750 V corner |
| ESD test standard | AEC-Q100-002/-011 | JEDEC JS-001/002 | — | ANSI/ESDA/JEDEC JS-001/002 | JESD22-A114 / AEC Q100-011 | AEC Q100-002/-011 | JS-001 / JESD22-C101 | AEC-Q100-002/-011 |
| Automotive qualification | AEC-Q100 | Not stated (JEDEC/J-STD only) | AEC-Q100 REV-H Grade 1 | **Not stated anywhere in datasheet** (JESD47 mission profile, "Industrial" temp codes only) | AEC-Q100 Grade 1 | AEC-Q100 (`-Q1` variant only, separate table from commercial) | Base part not automotive-specific; `-Q1` variants referenced but not detailed in this datasheet | **AEC-Q100 Grade 1**, stated directly |
| Named EMC/EMI standard cited | Not published ("available on request") | Not addressed | Not published (Ch. 33 marked incomplete) | **IEC 61000-4-2 (immunity) and IEC 61967-2 (emissions), with actual Level/Class numbers published** | Not published | Not found | Not found in datasheet; IEC 61000-4-2/-3/-4/-5/-6 and CISPR 22/25/32 named in a separate app note [41] as design *targets*, not test results | Not found |

Some observations that don't fit neatly in the table:

- The S32K144 has the best published ESD numbers of anything surveyed, and
  is the only part (besides the automotive-specific TMS320F280025-Q1 and
  MSPM0G350x-Q1 tables) whose ESD figures are explicitly tied to AEC-Q100
  test methods rather than commercial JEDEC ones.
- The STM32G431 is the *only* datasheet in this entire survey that
  publishes actual named-standard EMC numbers (IEC 61000-4-2 immunity
  levels, IEC 61967-2 emissions class) — but it has the weakest ESD figures
  of anything surveyed and states no AEC-Q100 qualification anywhere. More
  documentation, weaker part.
- TI's MSPM0 EMC application note [41] is a genuinely useful design guide
  (naming the IEC 61000-4-2/-3/-4/-5/-6 and CISPR 22/25/32 standards
  explicitly, and documenting on-chip EMS mitigation features like 4-level
  BOR) but is explicitly a checklist/methodology document, not a test
  report with numbers for any specific MSPM0 part.
- No part in this survey publishes a certified numeric radiated-emissions
  or conducted-immunity figure the way it publishes ESD kV ratings. This
  gap is universal, not specific to any one vendor.

**Design implication (unchanged from the original S32K144-vs-SLB9672
comparison, and generalizes to every combo candidate):** an on-die security
engine introduces no new signal-integrity or EMI-coupling path (no SPI bus,
no chip-to-chip crosstalk risk) beyond what the MCU package already
presents. Any two-chip combo (SLB9672 with any host MCU) adds an SPI bus
and PIRQ#/RST# lines that must be routed and, at this project's higher
EMI-hardening tiers (README.md: Isolation/Grounding/Faraday), shielded or
filtered like any other off-chip signal.

### 6.1 On the 5V-vs-3.3V rationale itself

The original motivation for scoping this survey to "5V automotive class"
parts was that a larger logic-voltage swing increases noise margin in a
noisy EMI environment. That's true as far as it goes, but it's a much
weaker lever than it first appears, for reasons discussed with the repo
owner in this design conversation (not themselves re-derived from a
datasheet, so presented here as design reasoning rather than a cited
technical claim):

- Noise margin scales with VDD (roughly 0.7×/0.3×VDD thresholds for both
  3.3V and 5V CMOS families), so the absolute gain from 5V vs. 3.3V is on
  the order of 0.6–0.7V, not an order of magnitude.
- The buses that actually carry this project's noisy long-haul traffic
  (CAN, RS-485) get their real EMI robustness from differential signaling
  and common-mode rejection, not from the host MCU's single-ended core
  voltage.
- Raising logic voltage also raises dV/dt per transition, which increases
  the device's own radiated/conducted emissions — a two-sided trade against
  the immunity gain, not a one-sided win.
- ESD robustness (an HBM/CDM manufacturing-handling stress test) and
  operational EMI immunity (IEC 61000-4-x) are different test regimes; a
  part with a better ESD number is not automatically better on operational
  EMC, and vice versa — see the STM32G431 case above.
- Most "5V-class" automotive MCUs elsewhere in the industry (AURIX, S32K3xx,
  RH850) actually run sub-2V cores with 5V-*tolerant* I/O, not a true 5V
  logic swing internally. The S32K144 is unusual in presenting as a genuine
  single-rail 2.7–5.5V part; that property is more about power-supply/BOM
  simplicity (fewer rails, no extra LDO, native compatibility with 5V
  automotive sensor/actuator rails) than about signal-integrity margin.

Given the repo owner has since confirmed most of the rest of this project's
hardware is 3.3V-class, and the S32K144 itself runs equally well at 3.3V
(its supply spec is 2.7–5.5V, not "5V only"), voltage class does not by
itself rule the S32K144 in or out — see §9's candidates, most of which are
3.3V-class parts evaluated on their security/footprint/cost merits rather
than a voltage filter.

## 7. Reference Manual note (resolves part of TODO.md 1.11)

TODO.md 1.11(b) flagged CSEc's algorithm detail (AES-128-CMAC) as
"UNVERIFIED against a primary source pending" because neither the SHE
Functional Specification nor the S32K1xx Reference Manual's CSEc chapter had
been obtained. `docs/datasheets/S32K-RM.pdf` (NXP *S32K1xx Series Reference
Manual*, Rev. 14, 09/2021, 2210 pp.) is now present in this repo and was used
throughout §3.1 above to verify that claim directly against RM Chapter 36
§36.5.13 (`CMD_GENERATE_MAC`/`CMD_VERIFY_MAC` definitions). REFERENCES.md's
[31] entry has been updated accordingly. TODO.md 1.11(a) — the 64-pin LQFP
physical pin-**number** map — is a separate, larger regeneration task
against this same Reference Manual's pinout chapter and is intentionally
**not** attempted here; it remains open.

## 8. Message-signing latency: does the crypto (or the bus) keep up?

This section resolves a question raised repeatedly in the design discussion
behind this document: if a candidate relies on a discrete TPM or a PKI
engine reached over SPI, can it actually keep up with this project's
real-time CAN/CAN-FD message-authentication rate, or does the bus/protocol
become the bottleneck?

**The bus is (almost) never the bottleneck; the crypto primitive is.** The
SLB9672's SPI runs up to 34.65 MHz typical [2] — comfortably enough raw
bandwidth for a TPM command/response, typically under 1 KB each way. The
actual constraint is TPM protocol overhead (command marshaling, wait
states) and, more fundamentally, that asymmetric operations (RSA/ECDSA
signing) are inherently expensive: TPM literature and this device's own
datasheet both note multi-digit-ms-to-minutes for RSA key generation at
larger key sizes [2]. Against a CAN-FD data-phase frame, which goes by in
roughly 100–300µs at a few Mbit/s, no discrete TPM signing every frame with
an asymmetric primitive could keep up — regardless of which chip or how
fast its bus is. **This was never actually the bus's fault; PKI primitives
are simply the wrong tool for per-frame, wire-rate authentication.**

**Symmetric authentication is fast enough, and now we have real numbers.**
TI's MSPM0 TRM [39] publishes the only genuine primary-sourced block-cipher
execution-time table found anywhere in this comparison's source set (Table
12-1, Ch. 12 "AES"):

| Operation | Key size | Cycles | Time @ 80 MHz | Time @ 32 MHz |
| --- | --- | --- | --- | --- |
| Encrypt | AES-128 | 168 | 2.10 µs | 5.25 µs |
| Encrypt | AES-256 | 234 | 2.93 µs | 7.31 µs |
| Decrypt (pregenerated key) | AES-128 | 168 | 2.10 µs | 5.25 µs |
| Decrypt (pregenerated key) | AES-256 | 234 | 2.93 µs | 7.31 µs |
| Decrypt (raw, no pregenerated key) | AES-128 | 215 | — | — |
| Decrypt (raw, no pregenerated key) | AES-256 | 292 | — | — |

A 64-byte CAN-FD payload (4×128-bit blocks) authenticates in roughly
4×2.1µs ≈ 8.4µs at 80MHz — 10–30x faster than the ~100–300µs frame period
estimated above. The SAM D5x/E5x's ICM peripheral [36] similarly publishes
72–209 clock-cycle hashing latencies (SHA1/224/256), and its AES engine is
rated up to 2 MB/s throughput [36] — all comfortably faster than this
project's actual authentication-rate requirement. **CSEc's own
GENERATE_MAC/VERIFY_MAC latency is still not published in any primary
source obtained this session (§3.1)**, but there is no architectural reason
to expect it to be meaningfully slower than a comparable AES-CMAC operation
on similar silicon — the MSPM0/SAM numbers above are offered as
order-of-magnitude corroboration for the same class of primitive, not a
substitute citation for CSEc's own timing.

**One precise nuance on the MSPM0 AES module:** the TRM [39] documents two
different AES peripherals across the MSPM0 G-Series family — a basic "AES"
module (Ch. 12, the one confirmed present on the MSPM0G3107 [38]) and a
more capable "AESADV" module (Ch. 13) that adds native hardware CMAC, GCM,
and CCM. The MSPM0G3107 has the basic module — hardware AES-CBC/ECB/CFB/OFB
and CBC-MAC tag computation, but not a single hardware "compute CMAC"
instruction the way CSEc's `GENERATE_MAC` is. Firmware would implement the
standard CMAC subkey-XOR construction on top of the raw AES-CBC primitive —
straightforward, and the 168-cycle-per-block cost still dominates, so the
speed conclusion is unaffected; it's a one-layer-less-turnkey difference
from CSEc's single command, not a performance problem.

**Bottom line:** for every symmetric-only candidate in this survey (CSEc,
MSPM0's AES, SAM's AES), the crypto is not the bottleneck for real-time
per-frame authentication — microseconds, not milliseconds. That distinction
matters a great deal for the PKI-capable candidates (SLB9672, dsPIC33's ACE,
SAM's PUKCC): none of them should be used for per-frame authentication at
CAN/CAN-FD wire rate. Their PKI capability is architecturally suited to
low-rate, session/boot-time operations — secure boot, device-identity
attestation, key provisioning, certificate validation — not high-rate
message authentication. A design that wants both should reserve the
symmetric primitive for the fast per-frame job and the asymmetric one for
the slow, infrequent job, which is exactly the split the dsPIC33CK512MPT608
and (per §9.7) the MSPM0 family's software-ECDSA-plus-hardware-AES story
both offer on a single die.

## 9. Survey: automotive-class MCUs with on-chip security

Eight candidates in total, including the two this document opened with.
Every subsection below states its verification status explicitly.

| # | Part | Security model | PKI? | Supply | Automotive qual. | Smallest footprint | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| — | S32K144 (§2–§7) | On-die CSEc, symmetric only | No | 2.7–5.5V | AEC-Q100 | 100 mm² (64-LQFP) | VERIFIED |
| — | SLB9672 (§2–§7) | Discrete TPM 2.0 | Full | 1.65–3.6V | Not stated | 25 mm² (add-on) | VERIFIED |
| 9.1 | Infineon TLE987x/TLE9879 | None found | No | Not confirmed | Not confirmed | 49 mm² | `UNVERIFIED` (partial) |
| 9.2 | Microchip dsPIC33CK512MPT608 | On-die Secure Subsystem (ACE) | Full | 3.0–3.6V | AEC-Q100 Grade 1 | 144 mm² | VERIFIED |
| 9.3 | Renesas RH850/U2A16 | EVITA-Full HSM (claimed) | Unconfirmed | 1.12/3.3/5.0V (claimed) | AEC-Q100 (implied) | Large (516-pin) | `UNVERIFIED` |
| 9.4 | STM32G431K + SLB9672 | Host has none; SLB9672 does all crypto | Full (via SLB9672) | 1.71–3.6V + 1.65–3.6V | **Neither part** | 50–74 mm² (2 chips) | VERIFIED (both parts read) |
| 9.5 | Microchip SAM E51G19 | On-die AES/TRNG + PUKCC math accelerator | Accelerator, not a secure element | 1.71–3.63V | AEC-Q100 Grade 1 | 25 mm² | VERIFIED |
| 9.6 | TI TMS320F280025(-Q1) | DCSM code-protection only | No | 3.3V | AEC-Q100 (`-Q1`) | 49 mm² | VERIFIED — **excluded**, no crypto module |
| 9.7 | TI MSPM0G3107 | On-die AES/CRC/TRNG + software secure boot/ECDSA | Software-only, boot-time | 1.62–3.6V | `-Q1` exists, not detailed here | 25 mm² | VERIFIED |
| 9.8 | TI MSPM0G350x-Q1 | Same security model as 9.7 + ISO 26262 ASIL B | Software-only, boot-time | 1.62–3.6V | **AEC-Q100 Grade 1**, stated directly | 21 mm² | VERIFIED |

### 9.1 Infineon TLE987x / TLE9879 (MOTIX™ motor-control SoC family)

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
- Pricing: ~US$10.24 (LCSC, single unit) [search snippet, not independently
  verified, volatile].

**Assessment:** not a security-equivalent alternative to the S32K144 — it
appears to ship with no on-chip cryptographic/authentication engine at all.

### 9.2 Microchip dsPIC33CK512MPT608 family ("Secure" DSC)

Fully verified against its local datasheet [33].

- **Security engine: full PKI, on-die.** A "Secure Subsystem" (Ch. 6) built
  from a command processor implementing an "Advanced Crypto Engine" (ACE,
  "can implement all symmetric and asymmetric crypto functions") and a
  parallel "Fast Crypto Engine" for AES/SHA, talking to the main core over
  an **internal** 16 MHz SPI link — no external pins:
  - Sign/verify: ECDSA (P224, P256, P384, 256-bit Brainpool, SECP256K1);
    RSA 2048-bit sign+verify; RSA 3072-bit verify-only.
  - Key agreement: ECDH/ECDHE (P224/P256/P384/Brainpool), ECBD (P224).
  - Key generation: EC (P224/P256/P384/Brainpool), RSA 2048-bit, AES
    16-byte symmetric keys.
  - Encrypt/decrypt: AES ECB/GCM; RSA 1024/2048-bit OAEP/MGF.
  - MAC/digest: AES-CMAC, SHA-256, SHA-HMAC.
  - **X.509 certificate storage, parsing, validation, and revocation** for
    both ECC and RSA — the same category of capability the SLB9672 offers
    via its EK certificates.
  - Physical tamper protection (voltage/temperature tampers, active
    shield); JIL HIGH-rated, FIPS CAVP-certified ACE algorithms; FIPS
    140-2 Level 2 with Physical Security Level 3 "in progress."
- **Supply voltage: 3.0–3.6V — not natively 5V.** Absolute maximum VDD
  4.0V; some I/O pins are 5V-tolerant, the device itself is not.
- **AEC-Q100 REV-H Grade 1** (-40°C to 125°C).
- Package: **100-Lead TQFP, 12×12×1 mm** — only package offered; largest
  footprint in this survey.
- **Latency:** not published (Ch. 33 marked "additional information will
  be provided in future revisions").
- **EMI/ESD:** not published (same Ch. 33 gap).
- **Availability:** distributor searches surfaced listings only for the
  non-secure "MP608"/"MP508" sibling parts, not the "MPT" Secure variant
  itself — no DigiKey/Mouser/Newark/RS listing found for the actual
  "MPT608" order code this session. Cannot confirm whether this reflects
  genuinely restricted distribution or an incomplete search; worth a
  direct distributor/Microchip sales check before this goes near a BOM.

**Assessment:** the strongest PKI candidate in this survey, and the only
one besides SLB9672 with certificate handling — but not 5V, largest
footprint here, and open availability questions.

### 9.3 Renesas RH850/U2A (Zone/Domain automotive MCU series)

[search: renesas.com RH850/U2A16 product page, section/page not verified —
live fetch blocked HTTP 403]

- Marketed features: "flexible, individual power supply (typ. 1.12V,
  3.3V, 5.0V)"; "HSM for Evita-full with dedicated CPU/Flash and HW crypt
  algorithm support."
- EVITA-Full HSMs are generally understood (in automotive-security
  literature, not re-derived from a primary source for this specific part)
  to include a dedicated crypto co-processor and asymmetric-crypto support,
  in contrast with EVITA-Light/SHE-class HSMs like CSEc — **this
  distinction remains `UNVERIFIED — needs primary source`** for the
  RH850/U2A16 specifically.
- Scale: 4×400 MHz CPU cores (dual-core lockstep ×2), 16 MB flash, 3.6 MB
  SRAM, a 516-pin package [search snippet] — a substantially larger/more
  expensive device class than anything else in this survey.
- Pricing: not obtained.

**Assessment:** potentially the most capable HSM in this survey if the
EVITA-Full claim is confirmed, but at a device scale/cost that isn't a
drop-in comparison to anything else here, and still fully unverified.

### 9.4 STMicroelectronics STM32G431K (32-pin) + Infineon SLB9672

This was this project's *original* MCU, before MSPM0G3507 and then the
S32K144 (superseded [1]); its datasheet was recovered from this repo's own
git history and read directly for this comparison [35].

- **Security engine: none on the STM32G431 itself.** Its own feature table
  states "AES: No" — no accelerator, no MAC engine, only a plain TRNG. All
  crypto in this combo lives in the external SLB9672, reached over SPI —
  meaning **every** authentication operation, fast or slow, has to cross
  that bus; there's no on-die fallback for the fast per-frame job the way
  the dsPIC33 or MSPM0 candidates have.
- Supply: STM32G431 1.71–3.6V; SLB9672 1.65–3.6V.
- **Not AEC-Q100 qualified.** The string "AEC-Q100" does not appear
  anywhere in the STM32G431's 198-page datasheet; its ordering codes are
  labeled "Industrial temperature range," and its reliability section cites
  JEDEC JESD47 mission-profile compliance, not AEC-Q100.
- **ESD, weakest in this survey:** HBM ±2000V, CDM ±250V — lower than every
  other part here, including the SLB9672 it would be paired with.
- **The one datasheet in this whole survey with real published EMC
  numbers:** IEC 61000-4-2 immunity levels and an IEC 61967-2 "EMI Level 4"
  emissions class table — genuinely more EMC documentation than the
  S32K144 provides, on a part with worse passing thresholds and no
  automotive qualification.
- Package: LQFP32 (7×7mm) or UFQFPN32 (5×5mm) + SLB9672 UQFN32 (5×5mm) — 2
  chips, combined 74mm² or 50mm².
- Pricing (Digi-Key, STM32G431K8T6): ~US$4.51 (qty 1) down to ~US$2.63
  (qty 500); combined with SLB9672 (~US$5.21–6.69 qty 1), roughly
  US$9.7–11.2 at qty 1.

**Assessment:** the weakest option surveyed. Doesn't beat the S32K144 on
cost at volume (two BOM lines instead of one), doesn't match it on
ESD/qualification, and inherits the SPI-bus-can't-keep-up-with-PKI problem
(§8) more fully than any other candidate, since it has no on-die fallback
for fast authentication at all.

### 9.5 Microchip SAM E51G19 (SAM D5x/E5x family)

Fully verified against its local datasheet [36]. Chosen because the SAM
E51/E54 sub-family adds CAN-FD to the D5x/E5x line.

- **Security engine: AES-256 (2 MB/s), TRNG, PUKCC (RSA up to 7168-bit
  with CRT, ECDSA up to 521/571-bit), ICM (hardware SHA1/224/256 with
  published 72–209-cycle latencies — the only hashing-latency numbers
  found anywhere in this survey).**
- **Important caveat: PUKCC is a math-acceleration peripheral, not a
  self-contained secure element.** No isolated/encrypted key storage, no
  certificate parsing, no physical tamper protection, no FIPS/CC
  certification claimed anywhere in this datasheet for PUKCC/AES/ICM/TRNG —
  keys and orchestration logic live in ordinary application RAM/flash
  unless firmware builds additional protection itself. Fast and
  cheap-looking, but a materially different threat model from the SLB9672
  or dsPIC33's certified secure elements.
- **AEC-Q100 Grade 1**; ESD HBM ±2000V / CDM ±750V (matches the S32K144's
  CDM figure, lower HBM).
- Supply: 1.71–3.63V.
- Package: **48-pin VQFN, 5×5mm = 25 mm²** — smallest single-chip
  CAN-FD-plus-crypto footprint found until the MSPM0 candidates (§9.7–9.8).
- CAN_TX/CAN_RX confirmed present down to this smallest package via the
  device's signal-description table.
- Pricing: DigiKey lists ATSAME51G19A-MU/-MUT/-MF as active parts; exact
  unit price not captured this session.

**Assessment:** genuinely strong on footprint, cost-plausibility, and
qualification; the honest limitation is that its "PKI" is acceleration
hardware for firmware to orchestrate, not a certified isolated trust
anchor the way SLB9672/dsPIC33 are.

### 9.6 TI TMS320F280025(-Q1) — excluded

Verified against its local datasheet [37], and **excluded from the
security-module shortlist** — it doesn't have one.

- No AES, RSA, ECC, SHA, or TRNG anywhere in its own feature list, memory
  map, or register summary. Its only "security" feature is **DCSM** (Dual
  Code Security Module): a 128-bit password-gated zone-access mechanism to
  block flash readout/cloning — IP protection, not message authentication.
  TI's own datasheet disclaimer states DCSM is **not warranted against
  being compromised or breached**.
- A block diagram elsewhere in the same document labels "Security: AES,
  DCSM, Secure boot" for an unrelated reference-design application (a
  telecom rectifier) — this could not be confirmed to describe this
  device's own silicon rather than a broader system-level security goal
  for that reference design, and should not be read as evidence this part
  has an on-chip AES engine.
- It does have a genuine `-Q1` automotive-qualified variant with its own
  separate AEC-Q100 ESD table (HBM ±2000V, CDM ±500/750V), 48/64/80-pin
  LQFP options (48-pin = 7×7mm, smallest), single 3.3V supply, and a real
  CAN port — a legitimately good real-time motor-control automotive part,
  just not a security-module candidate.

**Assessment:** if this part was pulled into scope because of the "AES,
DCSM, Secure boot" reference-design label, that appears to be a
search-criteria mismatch — the device itself doesn't have the crypto
engine that label implies.

### 9.7 TI MSPM0G3107 (MSPM0G310x family)

Verified against its local datasheet [38], the MSPM0 G-Series TRM [39],
the Cybersecurity Enablers app note [40], the EMC Improvement Guide [41],
and the errata [42].

- **Security engine, richer than initially assessed.** The datasheet's own
  feature list is modest — AES (128/256-bit), CRC-16/32, TRNG, no
  RSA/ECC/certificate mention. Reading the platform-wide cybersecurity app
  note [40] revealed a substantially fuller architecture that applies at
  the MSPM0 platform level: a **secure boot chain** (Customer Secure Code
  for devices with the INITDONE hardware-isolation mechanism, or Boot
  Image Manager for devices without it), an **immutable Root of Trust**
  (ROM boot code + write-protected CSC), a **Keystore** with genuine
  hardware-enforced key isolation ("only CSC can configure keys into
  Keystore and the main application can... never access any stored keys"),
  a **Firewall** (flash write/read-execute/IP protection), a **Hardware
  Monotonic Counter** (anti-rollback), and — critically — **SHA2-256 and
  ECDSA-P256 signature verification, supported in software** (not
  hardware-accelerated, but real, and something CSEc cannot do at all,
  hardware or software).
- **CSC vs. BIM resolved 2026-08-03 by the repo owner's own investigation:**
  the choice between Customer Secure Code (CSC, with Keystore) and Boot
  Image Manager (BIM, without) is a firmware/SDK-level implementation
  choice, not a hardware capability gated to specific MSPM0 sub-family
  silicon variants — either secure-boot solution is available on this
  part. This is attributed to the repo owner's direct investigation rather
  than re-derived from a specific page of [40] in this session; if a
  precise section/page citation is wanted later, that would upgrade this
  note from attributed-finding to independently `VERIFIED`.
- **Real AES latency numbers** — see §8. Confirmed via the datasheet's own
  §8.17 wording ("DMA support for ECB, CBC, OFB, and CFB cipher modes")
  that this part has the TRM's basic "AES" module (Ch. 12), not the more
  capable "AESADV" module (Ch. 13, native hardware CMAC/GCM/CCM) — see §8's
  nuance on what that does and doesn't change.
- **CAN-FD confirmed present even on the smallest (20-pin VSSOP) package**,
  via the datasheet's own pin-signal-description table.
- Supply: 1.62–3.6V.
- Package: 32-pin VQFN (5×5mm), 28-pin VSSOP (7.1×4.9mm), or **20-pin
  VSSOP (5.1×4.9mm ≈ 25mm²)** — tied for smallest single-chip
  CAN-FD-plus-crypto footprint in this survey.
- **Automotive:** `-Q1` variants exist (MSPM0G3105/3106/3107-Q1) per this
  datasheet's ordering addendum, described as "Q100 devices qualified for
  high-reliability automotive applications" — but this document is the
  base/commercial datasheet, and the dedicated `-Q1` automotive datasheet
  (separate document) was not obtained/read this session, so treat
  "AEC-Q100 Grade 1" for *this specific part's -Q1 variant* as
  `UNVERIFIED` pending that document (contrast with §9.8, where the
  automotive datasheet itself was obtained).
- **Errata:** no AES- or TRNG-specific advisories in silicon revisions
  B/C/D [42] — good sign for the crypto peripherals specifically.
- **The one real weakness relative to every other candidate here: it's an
  Arm Cortex-M0+ core** — no FPU, no DSP extensions. Every other candidate
  in this survey is a Cortex-M4F or DSC core specifically because FOC
  motor control benefits from hardware floating-point/single-cycle MAC.
  Whether this matters depends on this project's actual control-loop
  requirements, not on anything security-related.
- Pricing: not captured precisely; DigiKey/TI list both base and
  automotive SKUs as active (`-Q1` automotive SKU quoted a 12-week lead
  time in a search snippet).

**Assessment:** a real, small, cheap-looking option with more security
architecture than its own datasheet advertises — but with a genuinely
weaker CPU core than everything else surveyed, and one open item (Keystore/
CSC applicability) the repo owner is chasing down separately.

### 9.8 TI MSPM0G350x-Q1 (MSPM0G3505/3506/3507-Q1) — automotive family, ISO 26262 certified

Verified against its own dedicated automotive datasheet [43] — a distinct,
related family from §9.7, not the same part despite the superficially
similar name (this is **not** the same as the historical MSPM0G3507 [1],
either — that was the pre-`-Q1` commercial/industrial part this project
used before switching MCUs; this is a separate `-Q1` automotive-family
document).

- Same security peripheral set as §9.7 (AES 128/256, CRC-16/32, TRNG) and,
  by extension, the same platform-level secure-boot/Keystore story
  documented in [40] — CSC (with Keystore) is available here too, per the
  same repo-owner finding noted in §9.7 (a firmware/SDK choice, not a
  hardware restriction).
- **AEC-Q100 Grade 1, stated directly in this datasheet's own feature
  list** — no inference needed, in contrast with §9.7's `-Q1` variants.
- **ISO 26262 certified up to ASIL B by TÜV** — a genuine third-party
  functional-safety certification. Nothing else in this survey has a
  stated third-party safety certification (as opposed to "developed for"
  language).
- A real **automotive ESD table**: HBM ±2000V (AEC-Q100-002), CDM ±500V
  all pins / ±750V corner (AEC-Q100-011) — directly comparable to the
  S32K144's figures, on the CDM axis exactly matching it (750V corner),
  though the S32K144's HBM figure (4000V) is still higher.
- A **math accelerator** (DIV/SQRT/MAC/TRIG) plus dual zero-drift chopper
  op-amps and high-speed comparators — more explicitly FOC-motor-control
  tailored than §9.7's part.
- Supply: 1.62–3.6V; extended temperature -40°C to 125°C.
- Package: 64-pin LQFP (12×12mm) down to **28-pin VSSOP (7.1×3mm ≈
  21mm²)** — the smallest footprint of any part in this entire comparison
  — or 32-pin VQFN (5×5mm) if more pins are needed.
- Same Cortex-M0+ core caveat as §9.7 applies here too.
- **Pricing: ~US$2.79–3.00 across the family**, per the repo owner's direct
  Mouser observation 2026-08-03 (M0G3507QDGS32RQ1, 32-pin VSSOP, ~US$2.79;
  most expensive variant in the family ~US$3.00) — this is not a WebSearch
  snippet like every other price in this document, it's a live distributor
  page the repo owner read directly, so it carries more weight than this
  document's other pricing figures, though it's still a single-session
  price-point snapshot, not a negotiated/contract price. **This is
  cheaper than every other part in this entire survey**, including the
  base S32K144 (~US$3.75 at qty 100) and the STM32G431K8T6
  (~US$2.63–4.51) — by a meaningful margin once AEC-Q100 Grade 1 and
  ISO 26262 ASIL B certification are factored in as what you're getting
  for that price.

**Assessment:** on paper, the strongest all-around candidate for a
security-plus-safety-plus-footprint-plus-automotive-qualification
combination in this entire survey, and now also the cheapest, if the
Cortex-M0+ core's compute headroom is sufficient for this project's actual
control loop. It doesn't have PKI/certificate handling the way the dsPIC33
or SLB9672 do (its asymmetric capability is software-only ECDSA-P256
verification, not certificate parsing/storage), but for a
symmetric-authentication-plus-secure-boot design like this project's
current one, it's a genuine
S32K144 competitor worth the repo owner's continued investigation.

## 10. Pricing (all figures are distributor-listing snapshots, not verified against a live distributor page this session — see §1)

| Part | Listed unit price (qty 1, unless noted) | Source |
| --- | --- | --- |
| S32K144 (FS32K144HAT0MLHT, 64-LQFP) | ~US$8.42 | Digi-Key search snippet |
| S32K144 (FS32K144HFT0MLHT, 64-LQFP, qty 100) | ~US$3.75 | Digi-Key search snippet |
| SLB9672AU20FW1613XTMA1 | ~US$5.21–6.69 (qty-dependent) | Digi-Key search snippet |
| TLE9879-2QXA40 | ~US$10.24 | LCSC search snippet |
| dsPIC33CK512MPT608-E/PT | not captured; no distributor listing found for the "MPT" part at all | — |
| RH850/U2A16 | not captured | — |
| STM32G431K8T6 (32-LQFP) | ~US$4.51 (qty1) → ~US$2.63 (qty500) | Digi-Key search snippet |
| SAM E51G19A (ATSAME51G19A-MU) | not captured precisely; active listing confirmed | Digi-Key search snippet |
| TMS320F280025-Q1 | not captured precisely; active Mouser/TI listing confirmed | search snippet |
| MSPM0G3107 (base, SRHBR) | not captured precisely; active listing confirmed | Digi-Key search snippet |
| MSPM0G3107-Q1 (M0G3107QRHBRQ1) | not captured; 12-week lead time quoted | Digi-Key search snippet |
| MSPM0G350x-Q1 (M0G3507QDGS32RQ1, 32-VSSOP) | ~US$2.79; family range ~US$2.79–3.00 across variants | Repo owner, direct Mouser observation, 2026-08-03 |

Every WebFetch attempt against digikey.com, mouser.com, nxp.com,
infineon.com, microchip.com, ti.com, and renesas.com returned HTTP 403 this
session — consistent with the outbound-fetch pattern already documented in
TODO.md 1.10/1.11 for this repo. All prices above come only from WebSearch
result snippets (secondary, not independently re-verified against a live
page), and per `AGENTS.md` §1.1 must not be treated as settled figures for
a BOM. Distributor unit pricing also legitimately fluctuates day to day and
by quantity break, so even a live-fetched price would only be a snapshot.

## 11. Open items

- CSEc `GENERATE_MAC`/`VERIFY_MAC` execution latency (µs, as a function of
  message length) — not published in the local Data Sheet or Reference
  Manual; would need an NXP application note or bench measurement. §8
  argues this is very unlikely to matter in practice, but it's still
  unverified as a specific figure.
- SLB9672 per-command (HMAC/RSA-sign/ECDSA-sign) execution latency — not
  published in the local datasheet.
- dsPIC33CK512MPT608 ACE command (RSA-sign/ECDSA-sign/etc.) execution
  latency — not published (Ch. 33 incomplete in this Rev. B document).
- Radiated-emissions/conducted-immunity numeric figures against a named
  EMC standard — universally absent across every part surveyed except the
  STM32G431's IEC 61000-4-2/61967-2 numbers (see §6).
- TLE987x/TLE9879 and RH850/U2A16 still need their actual manufacturer
  datasheets (not search snippets) fetched and read before any claim in
  §9.1/§9.3 can be upgraded from `UNVERIFIED` to `VERIFIED`.
- dsPIC33CK512MPT608 real-market availability — no distributor listing
  found for the "MPT" order code itself, only its non-secure "MP608"
  sibling; needs a direct distributor/Microchip sales check.
- MSPM0G3107's own `-Q1` automotive variant's dedicated datasheet (as
  opposed to the MSPM0G350x-Q1's, which was obtained) — not obtained this
  session; its AEC-Q100 grade is inferred from the base datasheet's
  ordering addendum only.
- CRC/CRCP_ERR_01 (present in all MSPM0G3x0x silicon revisions per [42])
  — description text not extracted this session; worth reading before
  relying on the CRC peripheral for anything safety- or security-adjacent.
- S32K144 physical 64-pin LQFP pin-**number** map (TODO.md 1.11(a)) — now
  unblocked in principle since `docs/datasheets/S32K-RM.pdf` is locally
  available, but not attempted in this document; tracked separately.
- `docs/datasheets/slaae76e.pdf` (MSPM0 Hardware Development Guide) is
  present locally but was not mined for specific claims this pass.
