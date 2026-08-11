# HANDOFF — MCU swap: S32K144 → MSPM0G3518-Q1

**Written:** 2026-08-10 · **Status:** NOT STARTED — verification done, no files changed yet
**Branch to work on:** `feat/optiga-trust-m-secure-element` (or a new branch off it)
**Governing rules:** [`AGENTS.md`](../AGENTS.md) — every claim below already traces
to a primary source, or is explicitly marked `UNVERIFIED`. Do not re-derive
what is marked VERIFIED here; do not treat anything marked UNVERIFIED as settled.

---

## 1. Why

**Decision (user, 2026-08-10):** replace the NXP S32K144 with the TI
**MSPM0G3518-Q1** — the same MCU family already specified for the sister
LibreServo v4 design — because *"I'd rather have AES-256 than be limited to
128."*

That rationale is sound and verified. It directly retires finding **C-01** in
[`secure-element-architecture.md`](secure-element-architecture.md): the S32K144's
CSEc is SHE-compliant and therefore **AES-128 only**, which capped the strength
of the authenticated hot path regardless of what the OPTIGA™ Trust M could do.

---

## 2. What is already VERIFIED (do not redo)

All read from local PDFs already in `docs/datasheets/`.

| Fact | Source |
| --- | --- |
| "AES-128/**256** accelerator with support for GCM/…" | [44] SLASFA6B p.1 "Features" |
| "Secure key storage for up to **four** AES keys"; TRNG | [44] p.1 |
| §8.20 `AESADV`, §8.21 `Keystore` exist as device sections | [44] p.5 TOC |
| Crypto/secure-boot enabler architecture (CSC, BCR, BSL, secure storage) | [40] SLAAE29A — *Cybersecurity Enablers in MSPM0 MCUs* |
| Packages: PZ LQFP-100, PN LQFP-80, **PM LQFP-64 (12 × 12 mm)**, PT LQFP-48, RGZ VQFN-48, RHB VQFN-32 | [44] p.3 "Device Information" |
| Orderable for LQFP-64: **`M0G3518QPMRQ1`** | [44] p.3 |
| 7 × UART, 3 × I²C (FM+), 3 × SPI, CAN 2.0 A/B + CAN-FD, up to 94 GPIO, 512 KB flash, 128 KB SRAM, Cortex-M0+ | [44] p.1 |
| Real pin names: `VDD`, `VSS`, `VCORE`, `NRST`, `SWCLK`, `SWDIO`, `VREF+`, `VREF-` | [44] p.4 functional block diagram; p.22; p.49 |
| A capacitor between `VCORE` and `VSS` is **required**, ±20 % tolerance or better | [44] p.51 "Recommended Operating Conditions"; p.52 notes |

**Citations are already in `REFERENCES.md`.** `[40]` = SLAAE29A,
`[44]` = SLASFA6B. Neither needs creating. Add "Cited in:" lines as you go.

### Package choice

Use **PM (LQFP-64)**. The outgoing S32K144 is 64-LQFP, so the pin budget is a
direct match and the existing signal set fits with room to spare. Note the body
size differs (MSPM0 PM is 12 × 12 mm / 0.472 in; the S32K144 64-LQFP is
SOT1699-1, whose body dimensions this repo has never obtained — see `[31]`
p.89). This matters only at layout, and `U1` is not placed on the PCB yet.

---

## 3. The one real hazard — `VCORE` is NOT `VDDA`

**Read this before touching the schematic.**

All 30 of `U1`'s pins are currently wired. The two devices' power pin sets are
*not* slot-for-slot equivalent:

| S32K144 pin | Currently wired to | MSPM0G3518-Q1 equivalent |
| --- | --- | --- |
| `VDD` | 3V3 | `VDD` — same |
| `VSS` | GND | `VSS` — same |
| `VREFH` | rail | `VREF+` |
| `VREFL_VSSA_VSS` | rail | `VREF-` |
| `VDDA` | **3V3** | **none — see below** |
| `RESET_B` | reset net | `NRST` |
| `SWD_CLK` / `SWD_DIO` | debug header | `SWCLK` / `SWDIO` |
| — | — | **`VCORE` (new pin, must be added)** |

`VDDA` on the S32K144 is an **analog supply input** and is tied to 3V3.
`VCORE` on the MSPM0 is a **regulator output**. [44] p.52 states plainly:

> "The `VCORE` pin must only be connected to C_VCORE. **Do not supply any
> voltage or apply any external load to the `VCORE` pin.**"

A naive `VDDA → VCORE` mapping therefore ties `VCORE` to 3V3, which the
datasheet explicitly forbids. **Do not do the slot-for-slot swap.**

### Decision (user, 2026-08-10): give `VCORE` a proper dedicated cap

- Remove `VDDA`'s 3V3 connection entirely — the pin does not exist on the new
  device.
- Add `VCORE` as its own pin with a **dedicated capacitor to `VSS`**, and
  nothing else on that net. No rail, no load.
- Place the cap close to the pin at layout time.

**`UNVERIFIED` — the capacitance value.** It lives in the [44] p.51
"Recommended Operating Conditions" table, whose column structure does not
survive `pdftotext` extraction (the same failure mode as the MSPM0 pin-mux
Table 6-2). **Do not guess it.** Either read that table by another means, or
enter the part as `C_VCORE = UNVERIFIED — needs primary source (see TODO.md)`
per `AGENTS.md` §3 and log it. The ±20 % tolerance requirement *is* verified
and should be stated on the BOM line either way.

---

## 4. Work plan

1. **Symbol + spec.** Author `symbols/specs/MSPM0G3518_Q1_PM.json` and its
   `.kicad_sym`. Mirror the S32K144's functional signal-role names exactly
   (`CAN_TX`, `RS485_TXD`, `GD_SPI_*`, `ADC_*`, `PWM_*`, `SE_I2C_*`, `SE_RST`)
   so the existing schematic wiring survives the swap untouched. Only the
   power/reset/debug pin *names* change, per the table in §3, plus the new
   `VCORE`.
   - Pin **numbers** will again be an `UNVERIFIED PLACEHOLDER PIN MAP`: the
     MSPM0 pin-attribute Table 6-2 ([44] pp. 14–34) has the same
     column-collapse extraction problem. Carry the same caveat wording the
     S32K144 spec uses.
   - There is already a `symbols/MSPM0G3518_Q1_RHB.kicad_sym` in this repo for
     the **VQFN-32** package. It is a different package with a different pin
     count — do not reuse it for the PM part, and do not delete it.
2. **Schematic.** Swap the `U1` lib_symbol and instance. Because the signal
   names are preserved, only the power block needs rework: drop `VDDA`, add
   `VCORE` + its cap. Use a targeted injection script — see §6.
3. **Rewrite the affected findings** in
   [`secure-element-architecture.md`](secure-element-architecture.md):
   - **C-01** (AES-128 ceiling) → **RESOLVED.** Record that the ceiling lifts to
     AES-256 and say why the finding existed.
   - **C-05** (CSEc cannot run in HSRUN at 112 MHz) → **no longer applies**;
     it was S32K144-specific. Delete or mark superseded; check whether the
     MSPM0 has its own equivalent clock/crypto interaction before claiming
     there is none.
   - §1.1 "The gap CSEc cannot close" → rewrite for the MSPM0's AES engine.
     **The conclusion does not change:** the MSPM0's AES is still symmetric, so
     the Trust M is still required for asymmetric identity and key agreement.
     The whole Trust M rationale survives this MCU swap intact.
   - New consideration: the MSPM0 keystore holds **4** AES keys ([44] p.1)
     against CSEc's 17 ([31] Table 36-75). That is a reduction — check it
     against the intended key hierarchy before calling the swap complete.
   - §2 division-of-labour table, and every "CSEc" mention throughout.
4. **Docs.** `README.md` (MCU line), `builds/6s/50A/CAN_485_faraday/README.md`
   (BOM row + the 2026-08-03 CSEc note, which becomes historical),
   `docs/security-mcu-comparison.md` (34 SLB9672 mentions and the whole
   S32K144-vs-alternatives argument now reads differently), `TODO.md`,
   and "Cited in:" lines for `[40]`/`[44]`.
5. **Validate.** `kicad-cli sch erc --severity-all` and `sch export netlist`.
   Record before/after counts. Current baseline on this branch: **431
   violations, 8 errors, 423 warnings.**

---

## 5. What must NOT regress

- The OPTIGA™ Trust M block (`U2`, its two 10 kΩ pull-ups, its 100 nF cap, the
  five no-connect flags) and the `SE_I2C_SDA` / `SE_I2C_SCL` / `SE_RST` nets.
  Netlist-verified as `U1.28↔U2.8` (SCL), `U1.29↔U2.3` (SDA), `U1.30↔U2.9`
  (RST). The new symbol must keep those three pins or the secure element
  silently disconnects.
- The Trust M's own justification. It is unaffected by the MCU change.
- The open safety item **O-04** (behaviour on MAC verification failure is
  undefined) and the other `OPEN` items in `TODO.md` §12.3. They are
  MCU-independent.

---

## 6. Environment constraints (learned the hard way)

- **`kiutils` is not installed and pip is not permitted.** Every generator in
  this repo (`symbols/tools/gen_kicad_symbol.py`,
  `builds/.../kicad/tools/gen_schematic.py`, `gen_pcb.py`, `genlib.py`) imports
  it and dies at module load. You cannot regenerate. Extend by targeted
  S-expression injection instead — working patterns:
  `builds/6s/50A/CAN_485_faraday/kicad/tools/inject_optiga_secure_element.py`
  and `LibreServo_v4/PCB/kicad/tools/swap_slb9672_for_optiga.py`. Commit
  whatever script you write, so the edit stays auditable.
- `gen_schematic.py` carries a divergence warning at the top saying the
  committed `.kicad_sch` is ahead of it. Keep that true; do not "fix" it by
  writing placement code you cannot execute.
- **Parser trap:** do not find the end of an embedded `lib_symbol` by matching
  `\t\t\t)\n\t\t)` — there is an `(embedded_fonts no)` line before the close,
  so the pattern silently matches an unrelated node far down the file and you
  get "Failed to load schematic" with balanced parens. Walk the parens.
- `openpyxl` is not installed either; parse `.xlsx` with stdlib `zipfile` +
  `xml.etree`.
- Validate with `kicad-cli` 9.0.2. Render checks: `sch export svg` →
  `inkscape --export-width` → `magick -crop`.
- The sheet is **fully unannotated** (`U?`/`R?`/`C?`). A netlist export
  therefore collapses same-prefix passives, so it is reliable for *net
  membership* but not for counting individual passives. Tracked as
  `TODO.md` 12.3.i.

---

## 7. Useful precedent

The S32K144 pin map was blocked for months on a document this repo believed it
did not have. It does: the pinout spreadsheets are **embedded files inside
`docs/datasheets/S32K-RM.pdf`**, extractable with `pdfdetach` — see
`TODO.md` 1.11(a). **Try the same trick on the MSPM0 datasheet** before
concluding its Table 6-2 is unreadable; if `mspm0g3518-q1.pdf` carries embedded
attachments, the MSPM0 pin map may be immediately resolvable and the
placeholder caveat avoidable entirely:

```bash
pdfdetach -list docs/datasheets/mspm0g3518-q1.pdf
```

---

*Prepared by Claude Opus 5 (`claude-opus-5`) under human direction, 2026-08-10,
at the end of the session that completed the OPTIGA™ Trust M integration. No
MCU-swap code or schematic changes have been made — this file is the starting
point, not a progress report.*
