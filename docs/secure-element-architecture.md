# Secure Element Architecture — OPTIGA™ Trust M + MSPM0G3518-Q1 AESADV

**Status:** design record, 2026-08-10; **revised 2026-08-22** to describe the
project MCU that is actually on the schematic (see `TODO.md` §13).
**Applies to:** `builds/6s/50A/CAN_485_faraday` (schematic `U1` =
**MSPM0G3518-Q1**, `U2` = OPTIGA™ Trust M).
**Governing rules:** `AGENTS.md` §1–§5. Every claim below is either traced to a
primary source in `REFERENCES.md` or explicitly marked `UNVERIFIED` / `OPEN`.

This document is the "full split and security-monitor budget" referenced by
`symbols/specs/OPTIGA_TRUST_M.json`, `symbols/specs/MSPM0G3518_Q1_PM.json`, and
the corresponding `.kicad_sym` Description properties.

> **2026-08-22 revision note.** The 2026-08-10 version of this document
> described the NXP S32K144's CSEc module throughout. The MCU swap decided
> 2026-08-10 ([44], `TODO.md` §13) replaced `U1` with the TI MSPM0G3518-Q1
> **before** this document was updated to match — confirmed by reading the
> schematic directly: `U1`'s `lib_id` is `MSPM0G3518_Q1_PM:MSPM0G3518_Q1_PM`
> (`open_secure_esc_6s_50a_can485_faraday.kicad_sch` line 4489), and the
> `VCORE`/`NRST`/`SE_I2C_SCL`/`SE_I2C_SDA`/`SE_RST` nets and the dedicated
> 470 nF `C_VCORE` cap are present and wired (schematic notes at lines 949,
> 953, 1041–1049, 3147, 3329, 3924, 3952, 3959–3973, 4022–4036, 5267, 6064).
> This pass rewrites every CSEc-specific claim below for the MSPM0's AESADV
> engine and Keystore, closing `TODO.md` 13.1.e. The S32K144 material is kept
> in §9 as history, not deleted, per this repo's convention of not erasing
> superseded design record. **The Trust M's own justification (§1) does not
> change** — the MSPM0's AES engine is still symmetric-only, so the Trust M is
> still the only source of asymmetric identity and key agreement in this
> design.

---

## 1. Why a secure element, and why not a TPM

The ESC needs an **independent hardware root of trust**: a key store whose
private keys cannot be extracted by compromising the application MCU, and which
can prove the board's identity to a peer.

Three options were considered across this repo's history:

| Option | Verdict | Reason |
| --- | --- | --- |
| Discrete TPM 2.0 (Infineon SLB9672, [2]) | **Dropped 2026-08-03** | Full TPM 2.0 stack (TSS, PCRs, attestation state machine) is far more machinery than an ESC needs, and it consumed an LPSPI channel. See `TODO.md` 4.1 / 11.3. |
| On-chip MCU AES engine alone (S32K144 CSEc [31], superseded; MSPM0G3518-Q1 AESADV [44], current) | **Insufficient alone** | Symmetric-only on both parts considered. See §2. |
| **Secure element (OPTIGA™ Trust M, [45])** | **Selected** | Supplies exactly the asymmetric layer neither MCU option has, over I²C, in a 3 mm × 3 mm (0.118 in × 0.118 in) package. |

**The Trust M is not a reinstatement of the SLB9672.** It is a different device
class. A TPM is a platform-integrity module built around PCRs and attestation; a
secure element is a key vault with a crypto engine. The Trust M reuses only the
schematic designator `U2` that the SLB9672 vacated. It is also **unaffected by
the S32K144 → MSPM0G3518-Q1 MCU swap**: its own datasheet, pin count, and
justification are independent of which MCU it talks to over I²C.

### 1.1 The gap the MCU's own AES engine cannot close

The MSPM0G3518-Q1's `AESADV` peripheral provides an AES-128/256 accelerator
with GCM support and a hardware-backed `Keystore` for up to four AES keys
([44] p.1 "Features"; §8.20/§8.21 exist as device sections per [44] p.5 TOC).
The wider MSPM0 platform security architecture — Customer Secure Code (CSC),
Boot Image Manager (BIM), the Keystore's access model, and a hardware
monotonic counter — is described in [40] (SLAAE29A). Per [40] p.2 Table 1-1:
"Only CSC can configure keys into Keystore and the main application can
configure the crypto engine (AES) to use one of the stored keys but can never
access any stored keys." [40] also states plainly that **SHA2-256 and ECDSA
P-256 exist only as software libraries on MSPM0** — "Only supported via
software in MSPM0 devices" (p.2 Table 1-1) — with **no hardware acceleration**
for either, and **no certificate-handling command** anywhere in the cited
material.

That means the MSPM0's on-chip crypto — like the S32K144's CSEc before it —
structurally cannot cheaply perform:

- public-key **device authentication** with hardware-accelerated signing
  (proving identity to a party that holds no shared secret);
- **key agreement** with a peer it has never met;
- any form of certificate validation.

A firmware-only ECDSA-P256/SHA-256 software stack is *possible* on the MSPM0
(the SDK libraries exist per [40]), but it runs on the Cortex-M0+ core with no
hardware acceleration, has no protection against key extraction beyond
ordinary flash-read protection, and cannot replicate the Trust M's
fab-provisioned, non-exportable private key or its certificate store. This
repo's design does not attempt to substitute software ECDSA for the Trust M;
the finding survives the MCU swap unchanged.

**The Trust M closes this gap on both MCUs equally** — nothing about the
asymmetric-layer requirement is MCU-specific.

---

## 2. Division of labour

| Concern | Device | Rationale |
| --- | --- | --- |
| Device identity, ECDSA signature over a fab-provisioned private key | **Trust M** | Private key never leaves the SE; provisioned at Infineon's fab with the public key signed by a customer CA ([45] p.11 §2 Note). |
| Certificate storage / trust anchors | **Trust M** | 4 × X.509 slots, 3 × trust-anchor slots ([45] p.10 Fig. 1). |
| Ephemeral session-key agreement (ECDHE + KDF) | **Trust M** | ECC NIST P-256/384/521, Brainpool r1, HKDF SHA-256/384/512, TLS v1.2 PRF ([45] pp. 8–9 Table 4). |
| **Per-frame message authentication (hot path)** | **MSPM0 `AESADV`** | AES-128/256 CMAC-class authentication in hardware on the MCU, no I²C round trip to the Trust M, no security-monitor throttle. |
| Session-key custody during flight | **MSPM0 `Keystore`** — **mechanism `OPEN`, see C-08** | Up to 4 AES key slots ([44] p.1); how a *runtime-negotiated* ECDHE session key gets loaded into a Keystore slot that [40] states only CSC can configure is not yet designed. See C-08 below. |

The one-sentence version: **the Trust M decides *who you are* once; the MCU's
own AES engine proves *this frame is from you* continuously** — the same
division of labour as before the swap, on a different MCU.

**What changed from the S32K144 design, concretely:**

- The S32K144's CSEc had an explicit `RAM_KEY` volatile slot documented for
  exactly this purpose ([31] Table 36-75) — load a session key at runtime,
  outside the flash-resident key catalog, no CSC-equivalent gatekeeper. The
  MSPM0G3518-Q1's Keystore, per the only primary-source description found
  ([40] p.2 Table 1-1), is described as CSC-configured only. Whether the
  `AESADV` engine can also consume a key supplied directly from application
  RAM/registers (bypassing Keystore, the way CSEc's `RAM_KEY` bypassed its own
  flash catalog) is **not confirmed from the cited sources** — see C-08.
- The key budget dropped from CSEc's 20 non-volatile slots
  (`SECRET_KEY`, `MASTER_ECU_KEY`, `BOOT_MAC_KEY`, `KEY_01`–`KEY_17` — [31]
  Table 36-75) plus 1 volatile `RAM_KEY`, to the MSPM0's 4 Keystore slots
  ([44] p.1). See §4 C-08 / `TODO.md` 13.1.f for the headroom analysis.

---

## 3. The security-monitor budget — the constraint that shapes the design

This is the single most important integration constraint, and it is the reason
the hot path *cannot* live on the secure element. **This section is entirely
about the Trust M and is unaffected by the MCU swap** — the numbers below come
from [45], not from whichever MCU is on the other end of the I²C bus.

The Trust M contains a security monitor that throttles operations it classes as
**protected** ([45] p.28 §7.1–§7.2, read from the local verified copy):

> `t_max` is set to 5 seconds (± 5%) … One protected operation … per `t_max`
> period. In other words it must not allow more than one out of the protected
> operations per `t_max` period (worst case).

The protected events are ([45] p.28 Table 19):

| Event | Triggered by |
| --- | --- |
| Decryption failure | Failed integrity check during protected update |
| Key derivation | `DeriveKey` on a **persistent** data object |
| **Private key use** | Any internal service using an SE-hosted private key **except** temporary keys from session context |
| Secret key use | Any use of an SE-hosted symmetric key, except session-context temporaries |
| Suspect system behaviour | Internal consistency check failure |

**Design consequences, in order of importance:**

1. **Device authentication is a boot-time event, not a runtime one.** An ECDSA
   signature with the fab-provisioned identity key is "private key use" — one
   per 5 s, worst case. Authenticating per frame, per command, or even per
   second is impossible by construction.
2. **The motor-control hot path must never call the Trust M.** A 6s/50 A ESC
   updating at kHz rates would exceed the budget by three orders of magnitude
   and be throttled into failure. The MCU's own AES engine carries the hot
   path; this is a hard architectural boundary, not a preference, and it holds
   for the MSPM0G3518-Q1 exactly as it held for the S32K144.
3. **Session-context keys are exempt.** The exemption for "temporary keys from
   the session context" is what makes an ECDHE handshake practical: the
   ephemeral key operations inside an established session context are not
   counted as protected operations. The *identity* key use that bootstraps the
   session is.
4. **Re-keying is expensive.** Because re-authentication costs a ≥5 s budget
   slot, sessions are necessarily long-lived, which raises the value of the
   session key and argues for deriving successive MCU-side keys from a KDF
   ladder rather than repeatedly returning to the SE.

---

## 4. Cryptographic assessment

Findings from a cryptographic review of the combined design. Severity is
engineering judgment; the underlying facts are cited.

### C-01 — AES-128 ceiling on the authenticated hot path (RESOLVED 2026-08-10 by the MCU swap)

**Original finding (S32K144 design):** the Trust M offers AES up to 256 bit and
ECC to P-521 ([45] pp. 8–9 Table 4), but none of that raised the strength of
the hot path, because the hot path ran on CSEc, which is AES-128 only ([31] RM
Rev. 14 §5.2.2, printed p. 97: "AES-128, CBC, ECB, CMAC"; "All cryptographic
functions are processed by an AES-128 engine", printed p. 880).

**Resolution:** the MSPM0G3518-Q1 was selected specifically to retire this
ceiling — "AES-128/**256** accelerator with support for GCM" ([44] p.1
"Features") — because, in the repo owner's own words (`docs/HANDOFF-mcu-swap-
s32k144-to-mspm0g3518.md` §1), *"I'd rather have AES-256 than be limited to
128."* The hot path can now run at AES-256 if firmware configures it to.

**Kept for the record, because the underlying observation still matters:**
128-bit symmetric strength was and remains adequate well beyond 2030 under
current NIST guidance — the original finding was informational/accepted, not a
defect, and the swap is a strength upgrade, not a fix for a broken design.

### C-02 — No post-quantum algorithm anywhere in the chain; the identity key cannot be rotated to one (Medium, one-way door — unaffected by the MCU swap)

Neither the MSPM0's `AESADV`/software crypto nor the Trust M offers ML-KEM
(FIPS 203), ML-DSA (FIPS 204), or SLH-DSA (FIPS 205). The Trust M's crypto set
is classical ECC/RSA ([45] pp. 8–9 Table 4); [40] describes only classical
software ECDSA-P256/SHA-256 on the MSPM0 side.

The aggravating factor is **immutability**: the identity private key and its
X.509 certificate are generated and provisioned **at Infineon's fab** ([45] p.11
§2 Note). A field firmware update cannot migrate that key to a PQC algorithm,
and this is true regardless of which MCU sits next to the Trust M.
Crypto-agility for device identity therefore requires a **hardware** change.

Mitigating: session keys are ephemeral (ECDHE), so "harvest-now-decrypt-later"
exposure is bounded to identity and attestation, not to bulk flight data — and
the bus is not confidential in the first place (see O-02). This is filed as a
known, accepted limitation of the device class, not a blocker.

### C-03 — Authentication alone does not stop replay; a freshness value is required (High, OPEN — unaffected by the MCU swap)

AES CMAC-class authentication authenticates *content*, not *recency*. Without a
freshness input, a recorded valid frame replays as a valid frame — which on a
motor-control bus means a recorded throttle command can be re-injected. This
holds regardless of which MCU computes the MAC.

The Trust M's 4 monotonic counters ([45] p.10 Fig. 1) are boot/session-scale
objects and are far too slow to serve as a per-frame freshness source (each use
risks the §3 budget). The MSPM0 has its own hardware monotonic counter ([40]
p.37 §4.7) intended for firmware anti-rollback, not per-frame freshness at
control-loop rates; using it per-frame has not been evaluated and is not
assumed to be appropriate.

**Required:** a monotonically increasing freshness value inside the
MCU-authenticated payload, maintained by firmware and reset only on
re-authentication. **This is a firmware design obligation and is not yet
specified.** Tracked in `TODO.md` §12.3.

### C-04 — CAN-FD frame budget forces MAC truncation (Medium, design decision required — API details now `UNVERIFIED` for the new MCU)

CAN-FD carries at most 64 byte of payload — the S32K144's FlexCAN module
declared "Zero to sixty four bytes data length" ([31], S32K1xx Series
Reference Manual Rev. 14, §55.2.2 "Features", printed p. 1802), and [44] p.1
lists CAN-FD support for the MSPM0G3518-Q1 without contradicting the 64-byte
CAN-FD payload ceiling, which is a protocol-level (ISO 11898-1, [6]) limit, not
a silicon-specific one. The governing ISO text [6] is cited for the protocol
itself but is paywalled and its clause content is `UNVERIFIED` in
`REFERENCES.md`.

A full 128-bit CMAC is 16 byte — 25% of a maximum-size frame, and it does not
fit at all alongside useful data in a classic 8-byte frame.

**API-level change from the MCU swap:** CSEc exposed truncation directly —
`MAC = TRUNCATE(CMAC_KEY,KEY_ID(MESSAGE, MESSAGE_LENGTH), MAC_LENGTH)` ([31] RM
Rev. 14, printed p. 894). Whether the MSPM0's `AESADV` CMAC/GCM path exposes an
equivalent truncated-tag option, or whether firmware must truncate the full tag
itself post-computation, is **`UNVERIFIED — needs primary source`**: [44]'s
p.1 feature summary and [40]'s architecture overview do not go to that level
of API detail, and the AESADV chapter body ([44] §8.20) has not been read this
pass. Tracked as a new item, `TODO.md` 13.1.i.

The security math is unchanged either way: truncating to 32 bit gives a 2⁻³²
per-attempt forgery probability. On a bus an attacker can hammer, that is
**not** sufficient on its own — it must be paired with a verification-failure
rate limit or lockout, or the effective security degrades to the attacker's
attempt rate. **The chosen `MAC_LENGTH` and the failure-handling policy are not
yet decided.** Tracked in `TODO.md` §12.3.

### C-05 — SUPERSEDED 2026-08-10 by the MCU swap: CSEc's 112 MHz HSRUN exclusion no longer applies; MSPM0 equivalent `UNVERIFIED`

**Original finding (S32K144 design, kept for the record):** [31] stated, in the
§1.1 "Key Features" notes (pp. 2–3, repeated as a numbered table footnote at
pp. 4 and 8): "CSEc (Security) or EEPROM writes/erase will trigger error flags
in HSRUN mode (112 MHz) because this use case is not allowed to execute
simultaneously. The device will need to switch to RUN mode (80 MHz) to execute
CSEc." That constraint was S32K144-silicon-specific (it is a documented
HSRUN/RUN clock-domain exclusion around CSEc and flash write/erase) and does
not carry over by default to a different MCU family.

**Status on the MSPM0G3518-Q1: `UNVERIFIED`, not "resolved."** Neither [44]'s
p.1 Features list nor [40]'s architecture overview — the two sources read for
the MCU swap — states whether the MSPM0's clock/power modes (RUN/SLEEP/STOP/
STANDBY/SHUTDOWN, per the MSPM0 clock-tree literature generally) impose any
restriction on `AESADV` execution, or whether AES operations are unrestricted
across all active clock configurations. **Do not assume there is no
equivalent constraint just because it has not been found yet** — per
`AGENTS.md` §1.3, absence of a citation is not evidence of absence. This must
be checked against the MSPM0 Technical Reference Manual's clock/power chapter
(the MSPM0 G-Series TRM is [39] in `docs/security-mcu-comparison.md`'s source
list, `SLAU846E`) before any control-loop timing budget is finalized. Tracked
as a new item, `TODO.md` 13.1.i.

### C-06 — Enable the Shielded Connection on the I²C link (High, OPEN — unaffected by the MCU swap)

The session key agreed by the Trust M must reach the MCU's crypto engine, and
the path between them is a 2-wire I²C bus on an exposed board. Plain I²C is
trivially probed. The Trust M supports an encrypted **Shielded Connection** and
holds a platform binding secret for exactly this purpose ([45] p.1 "Features";
p.10 Fig. 1). This requirement is on the Trust M side of the link and does not
depend on which MCU is the I²C controller; the physical link is now
`U1` (MSPM0G3518-Q1) pins 8/9 (`SE_I2C_SCL`/`SE_I2C_SDA`) — see §6.

**The Shielded Connection must be enabled and the platform binding secret
provisioned**, or the asymmetric layer buys nothing against an attacker with
board access — they simply read the session key off SDA. Tracked in
`TODO.md` §12.3.

### C-07 — RSA-1024 is present in the device's capability set and must not be used (Low, policy — unaffected by the MCU swap)

The Trust M supports RSA 1024 and 2048 ([45] pp. 8–9 Table 4). RSA-1024 is below
every current minimum. Device identity should use **ECC P-256 minimum, P-384
preferred**. The provisioning profile must pin the curve explicitly rather than
accepting a device default. Tracked in `TODO.md` §12.3.

### C-08 — NEW 2026-08-22: how a runtime session key reaches the MSPM0 Keystore is undesigned (High, OPEN)

This finding did not exist in the S32K144 version of this document because
CSEc's `RAM_KEY` made the answer trivial: a dedicated volatile slot, loadable
at runtime, outside the flash key catalog ([31] Table 36-75).

The only primary-source description of the MSPM0's Keystore found so far
states the opposite access model: **"Only CSC can configure keys into
Keystore and the main application can configure the crypto engine (AES) to
use one of the stored keys but can never access any stored keys"** ([40] p.2
Table 1-1). Read literally, that describes a **provisioning-time** key store
(configured by Customer Secure Code, presumably at boot or during a secure
update), not a mechanism for loading a **freshly ECDHE-negotiated ephemeral
session key** at arbitrary runtime moments once the Trust M agrees one.

Two readings are possible and neither is confirmed:

1. The `AESADV` engine can also be pointed at a key held in ordinary
   application RAM/registers, bypassing Keystore entirely for session keys —
   functionally similar to CSEc's `RAM_KEY`, just not called that. If so, the
   security properties differ: the key sits in general-purpose memory rather
   than a hardware-isolated slot, which is a materially weaker guarantee than
   CSEc's `RAM_KEY` provided (`RAM_KEY` was still inside the CSEc security
   perimeter; a RAM-resident AES key is not).
2. Session keys must instead be re-provisioned into a Keystore slot through
   the CSC path on some cadence, which would be far slower than a per-session
   operation needs and may not be architecturally possible at runtime at all.

**This must be resolved by reading the MSPM0 AESADV/Keystore chapter body
([44] §8.20/§8.21) and, if needed, the CSC/BIM secure-boot chapters of the TRM
([39], SLAU846E) before firmware work on the session-key path begins.** Until
then, the "Session-key custody during flight" row in §2 is a placeholder, not
a verified design. Tracked as a new item, `TODO.md` 13.1.i.

---

## 5. OT / ICS perspective

**Framing caveat, stated up front:** IEC 62443 and NIST SP 800-82 govern
*industrial* automation and control systems. A UAV propulsion bus is **not** in
their scope, and this design is not claiming IEC 62443 compliance. The framework
is used here only as a *structured lens* — it asks the right questions about a
command-and-control bus attached to a physical actuator. Airworthiness
obligations are governed by separate authority and are out of scope for this
document.

With that caveat, mapping the ESC bus to a Purdue-style hierarchy:

| Analogue level | This design |
| --- | --- |
| L0 — process | Motor, phase currents, position/temperature sensing |
| L1 — control | **ESC (MSPM0G3518-Q1 + DRV8353S) and servo controllers — this bus** |
| L2 — supervisory | Flight controller |
| L3+ — operations | Ground control station, telemetry link |

### O-01 — CAN is unauthenticated by design; the MCU's AES engine is the compensating control (accepted, by design)

CAN and RS-485 are broadcast media with no native authentication: any node
electrically on the bus can transmit any identifier. This is the normal ICS
condition, and it is precisely what the MCU's own AES-CMAC-class layer
compensates for (cf. IEC 62443-3-3 FR1 identification/authentication, FR3
system integrity). The design is *correct* here — this entry exists to record
that the compensating control is the only thing standing between bus access
and actuator control, on the MSPM0G3518-Q1 exactly as it was on the S32K144.
Relevant adversary behaviours: manipulation of control, modify parameter.

### O-02 — The bus is authenticated but not confidential (accepted, deliberate — unaffected by the MCU swap)

The MAC provides integrity and origin authentication, not secrecy (FR4, data
confidentiality). Throttle and position commands are observable to anyone on the
bus. **This is a deliberate and appropriate trade**: motor commands are not
secret, and adding encryption to the hot path would cost latency for no
meaningful gain. Recorded so it reads as a decision, not an oversight.

### O-03 — Availability attacks are unaddressed and unaddressable by crypto (accepted, residual — unaffected by the MCU swap)

Bus-off attacks, dominant-bit flooding, and physical shorting deny control
regardless of how strong the authentication is (FR7, resource availability). No
cryptographic control mitigates these. The galvanic isolation on the RS-485
(ADM2582E/ADM2587E) and CAN-FD (ADM3055E/ADM3057E) transceivers limits *fault
propagation* between segments, but it is a fault-containment measure, not a
security control. Residual risk; requires physical access.

### O-04 — Authentication failure must not become a safety hazard (High, OPEN — most important item here, unaffected by the MCU swap)

This is where a security control can *create* a hazard. If a MAC verification
failure hard-stops a motor in flight, an attacker who can corrupt a single frame
— or a transient bus fault that flips a bit — can command a shutdown. The
security control becomes the attack. This risk is identical regardless of which
MCU computes the MAC.

**The fail-behaviour must be explicitly designed and stated**: whether the ESC
fails operational (continue on last valid command, degrade gracefully, alarm) or
fails safe (stop), and over what window of consecutive failures. For an airborne
propulsion unit, silently choosing "reject the frame and stop" is the wrong
default.

**This is not yet specified and must not be left to implementation.** Tracked in
`TODO.md` §12.3. It also interacts directly with C-04: the tighter the MAC
truncation, the higher the false-rejection rate.

### O-05 — No key revocation path (Medium, OPEN — unaffected by the MCU swap)

The Trust M holds 3 trust-anchor slots and 4 certificate slots ([45] p.10
Fig. 1). There is no defined process for what happens when a controller is
retired, lost, or compromised: how a peer learns not to trust it, and who
re-provisions the remaining nodes. A 4-slot store does not accommodate a
conventional CRL. Fleet key lifecycle is undesigned. Tracked in `TODO.md` §12.3.

---

## 6. Electrical integration

Reference circuit per [45] p.12 §3 Figure 2, with the MCU-side pins **VERIFIED**
against [44] (`symbols/specs/MSPM0G3518_Q1_PM.json`) rather than the
placeholder pin numbers the S32K144 version of this table used:

| Net | From | To | Notes |
| --- | --- | --- | --- |
| `SE_I2C_SDA` | `U1` pin 9 (MSPM0 pad `PA16`, `I2C1_SDA`) | `U2` pin 3 | 10 kΩ pull-up to +3V3 |
| `SE_I2C_SCL` | `U1` pin 8 (MSPM0 pad `PA15`, `I2C1_SCL`) | `U2` pin 8 | 10 kΩ pull-up to +3V3 |
| `SE_RST` | `U1` pin 7 (MSPM0 pad `PA14`, GPIO output) | `U2` pin 9 | Active-low reset input |
| `+3V3` | — | `U2` pin 10 (VCC) | 100 nF decoupling to GND |
| `GND` | — | `U2` pin 1 | — |

- Pull-up value 10 kΩ is the datasheet's own reference value; [45] p.12 notes
  that the correct value depends on the target circuit and I²C frequency, so it
  is a starting point to be confirmed against the final bus capacitance, not a
  fixed answer. This did not change with the MCU swap.
- I²C runs up to 1 MHz (FM+) on the Trust M side; default device address is
  0x30 ([45] p.7 §1.5, p.34 §A.2). The MSPM0's `I2C1` peripheral is confirmed
  present ([44] p.1 "3x I2C (FM+)"), matching the Trust M's own top speed —
  the specific configured bus frequency is a firmware setting, not yet fixed.
- The five NC contacts (2, 4, 5, 6, 7) **must be left floating** — [45] p.17
  Table 6 states "Not connected/Do not connect externally. Shall be left
  floating." This is a datasheet requirement, not a layout preference.
- The exposed pad is internally `n.c.` and exists for thermal dissipation ([45]
  p.16 Figure 7); it carries no net. At I_CCAVG ≈ 14 mA ([45] p.20 Table 11) the
  device dissipates on the order of 50 mW, so no thermal vias are required.
- Reset may alternatively be the `IFX_I2C_SOFT_RESET` command rather than the
  hardware line ([45] p.12 §3 Note); the hardware line is wired anyway so the
  MCU can recover the SE unconditionally.
- Hibernation circuits ([45] p.12 §3.1 Fig. 3, p.13 Figs. 4–5) are **not** used
  by this design.

### 6.1 Pin assignment status

**VERIFIED, not a placeholder.** `U1`'s pin **numbers** for the SE link are
real, datasheet-confirmed MSPM0G3518-Q1 PM (LQFP-64) package pins:
`SE_I2C_SCL` = pin 8 (pad `PA15`), `SE_I2C_SDA` = pin 9 (pad `PA16`), `SE_RST`
= pin 7 (pad `PA14`). Method and cross-checks are recorded in
`symbols/specs/MSPM0G3518_Q1_PM.json`'s `"verification"` field: two independent
extractions of [44] (Figure 6-3 package diagram and Table 6-2 pin-attribute
table, both requiring `pdftotext -layout` rather than a bare `pdftotext`) were
cross-checked against each other and against the per-peripheral signal tables
in [44] §6.3, with zero discrepancies across all 64 PM pads.

**Historical note — this section previously described the S32K144.** Under
that superseded design, `U1`'s pin numbers were an `UNVERIFIED PLACEHOLDER PIN
MAP` (the SE signals were placeholders 28/29/30), and this section documented
how to extract the S32K1xx Series Reference Manual's embedded IO-signal
spreadsheet via `pdfdetach` to resolve them (`TODO.md` 1.11(a)). That
extraction method and its LPI2C0 pin-candidate table (PTA2/PTA3 or PTB6/PTB7
on the 64-LQFP) are preserved in §9 below for audit continuity; they no longer
describe any signal on the current schematic.

---

## 7. Open items

Every `OPEN` finding above is carried into `TODO.md` §12.3 or §13. Summary:

| ID | Item | Severity |
| --- | --- | --- |
| C-08 | Runtime session-key path into the MSPM0 Keystore is undesigned | High |
| C-03 | Freshness/anti-replay scheme undefined | High |
| C-06 | Shielded Connection + platform binding secret not provisioned | High |
| O-04 | MAC-failure fail-behaviour undefined (safety-critical) | High |
| C-04 | `MAC_LENGTH`/truncation API on `AESADV` `UNVERIFIED`; failure rate-limit undecided | Medium |
| C-05 | MSPM0 clock/power-mode interaction with `AESADV` execution `UNVERIFIED` (was CSEc/HSRUN, S32K144-specific, now superseded) | Medium |
| O-05 | No key revocation / fleet lifecycle design | Medium |
| C-02 | No PQC path; identity key immutable (accepted limitation) | Medium |
| C-07 | Pin the ECC curve in the provisioning profile | Low |
| C-01 | **RESOLVED** — AES-128 ceiling lifted to AES-256 by the MCU swap | — |

---

## 8. References

Cited by tag; full IEEE entries in `REFERENCES.md`.

- **[2]** Infineon SLB9672 TPM 2.0 datasheet — dropped part, cited for history.
- **[6]** ISO 11898-1:2015, CAN data link layer and physical signalling.
- **[31]** NXP *S32K1xx Data Sheet* (Rev. 15) and *S32K1xx Series Reference
  Manual* (Rev. 14) — the **superseded** MCU's CSEc, LPI2C, clocking, and the
  embedded IO signal description attachments. Retained for §9 history and for
  the C-04/C-05 "what changed" comparisons above; no longer describes the
  active build's MCU.
- **[40]** Texas Instruments *Cybersecurity Enablers in MSPM0 MCUs*
  application note, SLAAE29A — Keystore access model, CSC/BIM, hardware
  monotonic counter, software-only ECDSA-P256/SHA-256.
- **[44]** Texas Instruments *MSPM0G351x-Q1* datasheet, SLASFA6B — the current
  project MCU's `AESADV`/Keystore feature summary, package, and pin map.
- **[45]** Infineon *OPTIGA™ Trust M Datasheet*, Rev. 3.70, 2024-10-09 — the
  secure element.

---

## 9. History — the S32K144-era text (superseded 2026-08-10, not deleted)

The following is the pre-2026-08-22 §1.1/§6.1 content verbatim, kept so the
extraction method it documents (embedded-spreadsheet recovery from the S32K1xx
Reference Manual) stays discoverable, and so this rewrite is auditable against
what it replaced.

> ### 1.1 The gap CSEc cannot close (S32K144, superseded)
>
> CSEc implements the SHE (Secure Hardware Extension) function set ([31], p.3
> §1.1). Its entire command set is symmetric: `ENC_ECB`/`DEC_ECB`, `ENC_CBC`/
> `DEC_CBC`, `GENERATE_MAC`/`VERIFY_MAC`, `LOAD_KEY`, `LOAD_PLAIN_KEY`,
> `EXPORT_RAM_KEY`, plus RNG/ID commands — no RSA, ECC, or certificate command
> exists anywhere in the chapter ([31], S32K1xx Series Reference Manual
> Rev. 14, Ch. 36 §36.5.13). All keys are AES-128, 16 byte ([31], Table
> 36-75).
>
> ### 6.1 Pin assignment status (S32K144, superseded)
>
> `U1`'s pin **numbers** remain an `UNVERIFIED PLACEHOLDER PIN MAP` per
> `AGENTS.md` §1.3/§3, consistent with every other signal on this symbol. The
> SE signals are placeholders 28/29/30.
>
> The per-pin signal mapping is *not* in the Reference Manual body; Ch. 4 §4.1
> defers it to an "IO Signal Description Input Multiplexing sheet(s) attached
> to the Reference Manual". Those sheets **are embedded in the local PDF** and
> can be extracted:
>
> ```bash
> pdfdetach -list docs/datasheets/S32K-RM.pdf
> pdfdetach -savefile 'S32K144_IO_Signal_Description_Input_Multiplexing.xlsx' \
>     -o S32K144_IO.xlsx docs/datasheets/S32K-RM.pdf
> ```
>
> Read from that sheet ("IO Signal Table" tab, `S32K144_64lqfp` column), the
> LPI2C0 options on the 64-pin LQFP were:
>
> | Port | Function | ALT (SSS) | 64-LQFP pin |
> | --- | --- | --- | --- |
> | PTA2 | `LPI2C0_SDA` | `0000_0011` | **48** |
> | PTA3 | `LPI2C0_SCL` | `0000_0011` | **47** |
> | PTB6 | `LPI2C0_SDA` | `0000_0010` | **12** |
> | PTB7 | `LPI2C0_SCL` | `0000_0010` | **11** |
>
> These were never committed to the S32K144 symbol before the MCU swap
> superseded the whole part.

---

*Authored 2026-08-10 under human direction. §1–§8 revised 2026-08-22 during a
`TODO.md` §13 verification pass cross-checking this document against the
schematic, `symbols/specs/MSPM0G3518_Q1_PM.json`, `REFERENCES.md`, and the
locally available datasheet text for [44]/[40]. Cryptographic and OT/ICS
findings in §4–§5 are engineering analysis of cited primary sources, not a
certified security assessment; the `OPEN` items require human decision before
fabrication.*
