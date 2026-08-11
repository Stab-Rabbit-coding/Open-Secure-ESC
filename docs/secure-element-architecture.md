# Secure Element Architecture — OPTIGA™ Trust M + S32K144 CSEc

**Status:** design record, 2026-08-10
**Applies to:** `builds/6s/50A/CAN_485_faraday` (schematic `U1` = S32K144, `U2` = OPTIGA™ Trust M)
**Governing rules:** `AGENTS.md` §1–§5. Every claim below is either traced to a
primary source in `REFERENCES.md` or explicitly marked `UNVERIFIED` / `OPEN`.

This document is the "full split and security-monitor budget" referenced by
`symbols/specs/OPTIGA_TRUST_M.json`, `symbols/specs/S32K144.json`, and the
corresponding `.kicad_sym` Description properties.

---

## 1. Why a secure element, and why not a TPM

The ESC needs an **independent hardware root of trust**: a key store whose
private keys cannot be extracted by compromising the application MCU, and which
can prove the board's identity to a peer.

Three options were considered across this repo's history:

| Option | Verdict | Reason |
| --- | --- | --- |
| Discrete TPM 2.0 (Infineon SLB9672, [2]) | **Dropped 2026-08-03** | Full TPM 2.0 stack (TSS, PCRs, attestation state machine) is far more machinery than an ESC needs, and it consumed an LPSPI channel. See `TODO.md` 4.1 / 11.3. |
| On-chip CSEc alone ([31]) | **Insufficient alone** | Symmetric-only. See §2. |
| **Secure element (OPTIGA™ Trust M, [45])** | **Selected** | Supplies exactly the asymmetric layer CSEc lacks, over I²C, in a 3 mm × 3 mm (0.118 in × 0.118 in) package. |

**The Trust M is not a reinstatement of the SLB9672.** It is a different device
class. A TPM is a platform-integrity module built around PCRs and attestation; a
secure element is a key vault with a crypto engine. The Trust M reuses only the
schematic designator `U2` that the SLB9672 vacated.

### 1.1 The gap CSEc cannot close

CSEc implements the SHE (Secure Hardware Extension) function set ([31], p.3
§1.1). Its entire command set is symmetric: `ENC_ECB`/`DEC_ECB`, `ENC_CBC`/
`DEC_CBC`, `GENERATE_MAC`/`VERIFY_MAC`, `LOAD_KEY`, `LOAD_PLAIN_KEY`,
`EXPORT_RAM_KEY`, plus RNG/ID commands — **no RSA, ECC, or certificate command
exists anywhere in the chapter** ([31], S32K1xx Series Reference Manual Rev. 14,
Ch. 36 §36.5.13). All keys are AES-128, 16 byte ([31], Table 36-75).

That means CSEc structurally cannot perform:

- public-key **device authentication** (proving identity to a party that holds
  no shared secret);
- **key agreement** with a peer it has never met;
- any form of certificate validation.

This limitation was flagged as a known one-way door when the SLB9672 was dropped
(see the LibreServo sibling design note `PCB/S32K144-MCU-swap.md` §2). The Trust
M closes it.

---

## 2. Division of labour

| Concern | Device | Rationale |
| --- | --- | --- |
| Device identity, ECDSA signature over a fab-provisioned private key | **Trust M** | Private key never leaves the SE; provisioned at Infineon's fab with the public key signed by a customer CA ([45] p.11 §2 Note). |
| Certificate storage / trust anchors | **Trust M** | 4 × X.509 slots, 3 × trust-anchor slots ([45] p.10 Fig. 1). |
| Ephemeral session-key agreement (ECDHE + KDF) | **Trust M** | ECC NIST P-256/384/521, Brainpool r1, HKDF SHA-256/384/512, TLS v1.2 PRF ([45] pp. 8–9 Table 4). |
| **Per-frame message authentication (hot path)** | **CSEc** | AES-128 CMAC in hardware on the MCU, no I²C round trip, no security-monitor throttle. |
| Session-key custody during flight | **CSEc `RAM_KEY`** | Volatile key slot ([31] Table 36-75); the agreed session key is loaded here and used for every frame. |

The one-sentence version: **the Trust M decides *who you are* once; CSEc proves
*this frame is from you* continuously.**

---

## 3. The security-monitor budget — the constraint that shapes the design

This is the single most important integration constraint, and it is the reason
the hot path *cannot* live on the secure element.

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
   and be throttled into failure. CSEc carries the hot path; this is a hard
   architectural boundary, not a preference.
3. **Session-context keys are exempt.** The exemption for "temporary keys from
   the session context" is what makes an ECDHE handshake practical: the
   ephemeral key operations inside an established session context are not
   counted as protected operations. The *identity* key use that bootstraps the
   session is.
4. **Re-keying is expensive.** Because re-authentication costs a ≥5 s budget
   slot, sessions are necessarily long-lived, which raises the value of the
   session key and argues for deriving successive CSEc keys from a KDF ladder
   rather than repeatedly returning to the SE.

---

## 4. Cryptographic assessment

Findings from a cryptographic review of the combined design. Severity is
engineering judgment; the underlying facts are cited.

### C-01 — AES-128 is a hard ceiling on the authenticated hot path (Informational, accepted)

The Trust M offers AES up to 256 bit and ECC to P-521 ([45] pp. 8–9 Table 4),
but **none of that raises the strength of the hot path**, because the hot path
runs on CSEc, which is AES-128 only ([31] RM Rev. 14 §5.2.2, printed p. 97:
"AES-128, CBC, ECB, CMAC"; "All cryptographic functions are processed by an
AES-128 engine", printed p. 880).

128-bit symmetric strength remains adequate well beyond 2030 under current NIST
guidance, so this is **accepted, not a defect** — but it must be recorded as a
deliberate ceiling rather than discovered later by someone who assumes the SE's
AES-256 applies end-to-end.

### C-02 — No post-quantum algorithm anywhere in the chain; the identity key cannot be rotated to one (Medium, one-way door)

Neither CSEc nor the Trust M offers ML-KEM (FIPS 203), ML-DSA (FIPS 204), or
SLH-DSA (FIPS 205). The Trust M's crypto set is classical ECC/RSA ([45]
pp. 8–9 Table 4).

The aggravating factor is **immutability**: the identity private key and its
X.509 certificate are generated and provisioned **at Infineon's fab** ([45] p.11
§2 Note). A field firmware update cannot migrate that key to a PQC algorithm.
Crypto-agility for device identity therefore requires a **hardware** change.

Mitigating: session keys are ephemeral (ECDHE), so "harvest-now-decrypt-later"
exposure is bounded to identity and attestation, not to bulk flight data — and
the bus is not confidential in the first place (see O-02). This is filed as a
known, accepted limitation of the device class, not a blocker.

### C-03 — CMAC alone does not stop replay; a freshness value is required (High, OPEN)

AES-128 CMAC authenticates *content*, not *recency*. Without a freshness input,
a recorded valid frame replays as a valid frame — which on a motor-control bus
means a recorded throttle command can be re-injected.

The Trust M's 4 monotonic counters ([45] p.10 Fig. 1) are boot/session-scale
objects and are far too slow to serve as a per-frame freshness source (each use
risks the §3 budget).

**Required:** a monotonically increasing freshness value inside the
CSEc-authenticated payload, maintained by the MCU and reset only on
re-authentication. **This is a firmware design obligation and is not yet
specified.** Tracked in `TODO.md` §12.3.

### C-04 — CAN-FD frame budget forces MAC truncation (Medium, design decision required)

CAN-FD carries at most 64 byte of payload — the MCU's own FlexCAN module
declares "Zero to sixty four bytes data length" and "Full implementation of the
CAN with Flexible Data Rate (CAN FD) protocol specification" ([31], S32K1xx
Series Reference Manual Rev. 14, §55.2.2 "Features", printed p. 1802). The
governing ISO text [6] is cited for the protocol itself but is paywalled and its
clause content is `UNVERIFIED` in `REFERENCES.md`, so the figure above is taken
from the NXP primary source rather than from ISO 11898-1 directly.

A full 128-bit CMAC is 16 byte — 25% of a maximum-size frame, and it does not
fit at all alongside useful data in a classic 8-byte frame.

CSEc supports truncation directly:
`MAC = TRUNCATE(CMAC_KEY,KEY_ID(MESSAGE, MESSAGE_LENGTH), MAC_LENGTH)` ([31] RM
Rev. 14, printed p. 894).

Truncating to 32 bit gives a 2⁻³² per-attempt forgery probability. On a bus an
attacker can hammer, that is **not** sufficient on its own — it must be paired
with a verification-failure rate limit or lockout, or the effective security
degrades to the attacker's attempt rate. **The chosen `MAC_LENGTH` and the
failure-handling policy are not yet decided.** Tracked in `TODO.md` §12.3.

### C-05 — CSEc cannot execute at the 112 MHz HSRUN clock (Medium, timing)

[31] states plainly, in the §1.1 "Key Features" notes (pp. 2–3, repeated as a
numbered table footnote at pp. 4 and 8): "CSEc (Security) or EEPROM
writes/erase will trigger error flags in HSRUN mode (112 MHz) because this use
case is not allowed to execute simultaneously. The device will need to switch to
RUN mode (80 MHz) to execute CSEc."

Any control-loop timing budget that assumed 112 MHz **and** per-frame CMAC is
wrong. The device must be in RUN (80 MHz) whenever CSEc executes. Either the
control loop is budgeted at 80 MHz throughout, or the firmware must manage clock
transitions around every MAC operation — the latter adds latency and jitter to a
motor-control loop and is not recommended. Tracked in `TODO.md` §12.3.

### C-06 — Enable the Shielded Connection on the I²C link (High, OPEN)

The session key agreed by the Trust M must reach CSEc, and the path between them
is a 2-wire I²C bus on an exposed board. Plain I²C is trivially probed. The Trust
M supports an encrypted **Shielded Connection** and holds a platform binding
secret for exactly this purpose ([45] p.1 "Features"; p.10 Fig. 1).

**The Shielded Connection must be enabled and the platform binding secret
provisioned**, or the asymmetric layer buys nothing against an attacker with
board access — they simply read the session key off SDA. Tracked in
`TODO.md` §12.3.

### C-07 — RSA-1024 is present in the device's capability set and must not be used (Low, policy)

The Trust M supports RSA 1024 and 2048 ([45] pp. 8–9 Table 4). RSA-1024 is below
every current minimum. Device identity should use **ECC P-256 minimum, P-384
preferred**. The provisioning profile must pin the curve explicitly rather than
accepting a device default. Tracked in `TODO.md` §12.3.

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
| L1 — control | **ESC (S32K144 + DRV8353S) and servo controllers — this bus** |
| L2 — supervisory | Flight controller |
| L3+ — operations | Ground control station, telemetry link |

### O-01 — CAN is unauthenticated by design; CMAC is the compensating control (accepted, by design)

CAN and RS-485 are broadcast media with no native authentication: any node
electrically on the bus can transmit any identifier. This is the normal ICS
condition, and it is precisely what the CSEc CMAC layer compensates for
(cf. IEC 62443-3-3 FR1 identification/authentication, FR3 system integrity).
The design is *correct* here — this entry exists to record that the compensating
control is the only thing standing between bus access and actuator control.
Relevant adversary behaviours: manipulation of control, modify parameter.

### O-02 — The bus is authenticated but not confidential (accepted, deliberate)

CMAC provides integrity and origin authentication, not secrecy (FR4, data
confidentiality). Throttle and position commands are observable to anyone on the
bus. **This is a deliberate and appropriate trade**: motor commands are not
secret, and adding encryption to the hot path would cost latency for no
meaningful gain. Recorded so it reads as a decision, not an oversight.

### O-03 — Availability attacks are unaddressed and unaddressable by crypto (accepted, residual)

Bus-off attacks, dominant-bit flooding, and physical shorting deny control
regardless of how strong the authentication is (FR7, resource availability). No
cryptographic control mitigates these. The galvanic isolation on the RS-485
(ADM2582E/ADM2587E) and CAN-FD (ADM3055E/ADM3057E) transceivers limits *fault
propagation* between segments, but it is a fault-containment measure, not a
security control. Residual risk; requires physical access.

### O-04 — Authentication failure must not become a safety hazard (High, OPEN — most important item here)

This is where a security control can *create* a hazard. If a MAC verification
failure hard-stops a motor in flight, an attacker who can corrupt a single frame
— or a transient bus fault that flips a bit — can command a shutdown. The
security control becomes the attack.

**The fail-behaviour must be explicitly designed and stated**: whether the ESC
fails operational (continue on last valid command, degrade gracefully, alarm) or
fails safe (stop), and over what window of consecutive failures. For an airborne
propulsion unit, silently choosing "reject the frame and stop" is the wrong
default.

**This is not yet specified and must not be left to implementation.** Tracked in
`TODO.md` §12.3. It also interacts directly with C-04: the tighter the MAC
truncation, the higher the false-rejection rate.

### O-05 — No key revocation path (Medium, OPEN)

The Trust M holds 3 trust-anchor slots and 4 certificate slots ([45] p.10
Fig. 1). There is no defined process for what happens when a controller is
retired, lost, or compromised: how a peer learns not to trust it, and who
re-provisions the remaining nodes. A 4-slot store does not accommodate a
conventional CRL. Fleet key lifecycle is undesigned. Tracked in `TODO.md` §12.3.

---

## 6. Electrical integration

Reference circuit per [45] p.12 §3 Figure 2:

| Net | From | To | Notes |
| --- | --- | --- | --- |
| `SE_I2C_SDA` | `U1` LPI2C0 SDA | `U2` pin 3 | 10 kΩ pull-up to +3V3 |
| `SE_I2C_SCL` | `U1` LPI2C0 SCL | `U2` pin 8 | 10 kΩ pull-up to +3V3 |
| `SE_RST` | `U1` GPIO (output) | `U2` pin 9 | Active-low reset input |
| `+3V3` | — | `U2` pin 10 (VCC) | 100 nF decoupling to GND |
| `GND` | — | `U2` pin 1 | — |

- Pull-up value 10 kΩ is the datasheet's own reference value; [45] p.12 notes
  that the correct value depends on the target circuit and I²C frequency, so it
  is a starting point to be confirmed against the final bus capacitance, not a
  fixed answer.
- I²C runs up to 1 MHz (FM+); default device address is 0x30 ([45] p.7 §1.5,
  p.34 §A.2).
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

`U1`'s pin **numbers** remain an `UNVERIFIED PLACEHOLDER PIN MAP` per
`AGENTS.md` §1.3/§3, consistent with every other signal on this symbol. The SE
signals are placeholders 28/29/30.

**New this pass — the authoritative source has been located.** The
per-pin signal mapping is *not* in the Reference Manual body; Ch. 4 §4.1 defers
it to an "IO Signal Description Input Multiplexing sheet(s) attached to the
Reference Manual". Those sheets **are embedded in the local PDF** and can be
extracted:

```bash
pdfdetach -list docs/datasheets/S32K-RM.pdf
pdfdetach -savefile 'S32K144_IO_Signal_Description_Input_Multiplexing.xlsx' \
    -o S32K144_IO.xlsx docs/datasheets/S32K-RM.pdf
```

Read from that sheet ("IO Signal Table" tab, `S32K144_64lqfp` column), the
LPI2C0 options on the 64-pin LQFP are:

| Port | Function | ALT (SSS) | 64-LQFP pin |
| --- | --- | --- | --- |
| PTA2 | `LPI2C0_SDA` | `0000_0011` | **48** |
| PTA3 | `LPI2C0_SCL` | `0000_0011` | **47** |
| PTB6 | `LPI2C0_SDA` | `0000_0010` | **12** |
| PTB7 | `LPI2C0_SCL` | `0000_0010` | **11** |

These are **not** yet committed to the symbol, because assigning real numbers to
three signals while the other 27 remain placeholders cannot be conflict-checked
— PTA2/PTA3 or PTB6/PTB7 may already be claimed by a motor, ADC, or transceiver
signal once the full map is resolved. Resolving the **whole** 64-pin map is the
correct next step and is now unblocked. Tracked in `TODO.md` 1.11(a).

---

## 7. Open items

Every `OPEN` finding above is carried into `TODO.md` §12.3. Summary:

| ID | Item | Severity |
| --- | --- | --- |
| C-03 | Freshness/anti-replay scheme undefined | High |
| C-06 | Shielded Connection + platform binding secret not provisioned | High |
| O-04 | MAC-failure fail-behaviour undefined (safety-critical) | High |
| C-04 | `MAC_LENGTH` truncation and failure rate-limit undecided | Medium |
| C-05 | Control-loop clock budget vs CSEc/HSRUN exclusion | Medium |
| O-05 | No key revocation / fleet lifecycle design | Medium |
| C-02 | No PQC path; identity key immutable (accepted limitation) | Medium |
| C-07 | Pin the ECC curve in the provisioning profile | Low |
| 1.11(a) | Resolve the full S32K144 pin map from the now-located source | — |

---

## 8. References

Cited by tag; full IEEE entries in `REFERENCES.md`.

- **[2]** Infineon SLB9672 TPM 2.0 datasheet — dropped part, cited for history.
- **[6]** ISO 11898-1:2015, CAN data link layer and physical signalling.
- **[31]** NXP *S32K1xx Data Sheet* (Rev. 15) and *S32K1xx Series Reference
  Manual* (Rev. 14) — CSEc, LPI2C, clocking, and the embedded IO signal
  description attachments.
- **[45]** Infineon *OPTIGA™ Trust M Datasheet*, Rev. 3.70, 2024-10-09 — the
  secure element.

---

*Authored by Claude Opus 5 (`claude-opus-5`) under human direction, 2026-08-10.
Cryptographic and OT/ICS findings in §4–§5 are AI-generated analysis of cited
primary sources; they are engineering opinion, not a certified security
assessment, and the `OPEN` items require human decision before fabrication.*
