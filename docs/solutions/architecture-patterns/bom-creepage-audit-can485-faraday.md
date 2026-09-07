---
date: 2026-09-06
problem_type: architecture_pattern
category: architecture-patterns
module: builds
component: board_geometry
severity: high
applies_when:
  - "Auditing a BOM for creepage/clearance reduction opportunities"
  - "Working voltage and current rating are both fixed and cannot be reduced"
  - "Trying to shrink a board carrying isolated CAN and/or RS-485 interfaces"
  - "Deciding between two isolator part variants that differ only in package"
tags:
  - isolation
  - creepage
  - bom-audit
  - can
  - rs-485
  - board-geometry
  - datasheet-verification
related_components:
  - REFERENCES.md
  - docs/tools/isolation_envelope.py
  - docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md
  - docs/solutions/architecture-patterns/smaller-package-does-not-shrink-creepage.md
  - builds/6s/50A/CAN_485_faraday
---

# BOM-wide creepage audit, with 50A/6S and working voltage held fixed

## Context

Two prior findings on this build established that (1) board width is set by
isolation creepage geometry, not placement luck
(`isolation-geometry-sets-board-aspect.md`), and (2) swapping an isolated
transceiver for a smaller-package part does not reduce the required creepage,
because creepage is set by the barrier's working-voltage/insulation class per
IEC 60664-1, not by package size or chip count
(`smaller-package-does-not-shrink-creepage.md`). This document is the
follow-on: with 50 A / 6S and the resulting working-voltage class both held
fixed as hard constraints (per the build's own protocol/battery requirements,
not a preference), what is left in the BOM and layout that genuinely reduces
creepage or board area — audited part by part, not guessed.

## Findings, ranked by verified impact

### 1. MCU package: PM (LQFP-64) → RHB (VQFN-32) — the largest lever found

`docs/tools/isolation_envelope.py`'s "widest non-isolated part" figure
(12.90 mm) is `U1`'s current PM package body/courtyard. TI's own MSPM0G3518-Q1
datasheet [44] lists an RHB (VQFN-32, 5×5 mm nominal body) package option for
the *identical part number* — same die, same AES-128/256 + keystore + TRNG.
Every signal this build's schematic assigns to specific PM pins was checked,
pad by pad, against RHB's Table 6-2 IOMUX options (RHB exposes only PA0–PA27,
no Port B/C at all) and a fully conflict-free assignment exists with 4 GPIOs
to spare — CAN0_TX/RX, UART0 TX/RX/RTS(RS-485 DE), SPI1 CS0/SCK/POCI/PICO
(gate driver), all three TIMA0 complementary PWM pairs, I2C1 SCL/SDA (secure
element), SWCLK/SWDIO, and all four ADC channels. Re-running
`isolation_envelope.py` with the RHB footprint:

```
PM  (12.90 mm widest part):  needs 31.86 mm width to sit inboard of both isolated rows
RHB (~6.5 mm w/ courtyard):  needs 25.46 mm — closes 82% of the gap to a 24 mm target
```

This is the only change examined across this whole audit that reduces the
*non-isolated* side of the geometry rather than fighting the isolated side,
and it is a package-option change on a part already in the BOM, not a new
part number.

### 2. CAN transceiver variant: close the "left open" ADM3055E/ADM3057E decision — free 0.5 mm

REFERENCES.md [10]'s Table 2 "Timing Characteristics" is a single table
covering **both** ADM3055E and ADM3057E — 12 Mbps maximum data rate for
either, no per-variant split anywhere in it. The only differences are
package and UL rating:

| | Package | CLR/CRP | UL 1577 VISO | VIORM/VIOWM |
|---|---|---|---|---|
| ADM3055E | RI-20-1 "increased creepage" | 8.3 mm | 5000 V rms | 595 Vpk / 420 Vrms |
| ADM3057E | RW-20 "wide body" | **7.8 mm** | 3750 V rms | 595 Vpk / 420 Vrms (identical) |

Since the two parts are timing-identical and carry the *same* reinforced
working-voltage rating, ADM3057E is strictly better for this board's purpose
unless something downstream specifically requires the higher UL proof
voltage. **The board's own PCB already has this resolved in practice**: `U3`
in `builds/6s/50A/CAN_485_faraday/kicad/*.kicad_pcb` is placed on footprint
`SOIC-20W_7.5x12.8mm_P1.27mm` — dimensionally the RW-20 (ADM3057E) package,
not RI-20-1. The schematic `Value`/`Description` fields and README still
carry the decision as "left open"; this should be closed to ADM3057E
explicitly (see REFERENCES.md [10] addendum, 2026-09-06) rather than left
ambiguous, and the KiCad footprint should be independently checked against
[10]'s own RW-20 land pattern (Outline Dimensions, p. 27) — that dimensional
check is not yet done and is tracked in TODO.md.

**This is a genuine 0.5 mm creepage reduction at zero functional cost.** It
is small next to item 1, but it costs nothing to take.

### 3. Consolidating CAN + RS-485 onto one shared isolation barrier — promising, NOT yet verified feasible

Today this board pays the creepage-zone overhead (pin inset + edge margin,
not just the raw creepage number) **twice** — once for `U3` (CAN) and once
for `U4` (RS-485) — even though both already sit on one shared island with
one keepout per the existing placement (`README.md` "bottom right... A
copper keepout removes every plane and pour from that band"). The
architectural question worth asking: could ONE multi-channel reinforced
isolator carry both interfaces' signals across a single barrier, with bare
(non-isolated) CAN and RS-485 transceivers living on its isolated side,
powered from its own integrated DC-DC — eliminating a second full component
footprint and its own inset/margin overhead, even though the per-barrier
creepage number itself would not shrink?

TI's ISOW7841 [61] was checked as a concrete candidate: quad-channel
reinforced digital isolator, integrated DC-DC (up to 650 mW, "eliminates the
need for a separate isolated power supply"), SOIC-16 body 10.30 × 7.50 mm,
>8 mm creepage/clearance at 1000 V rms working voltage. **It does not fit as
a drop-in**: CAN needs 2 channels (TX, RX) and this build's RS-485 uses 3
(TXD, RXD, DE/RE) — 5 total against ISOW7841's 4. Two ways to close that gap
exist, neither verified here:

- Tie DE and RE-bar into one shared direction-control line (a single
  transistor inverter on the isolated side recovers the second control
  signal) — brings RS-485 to 2 lines, CAN + RS-485 = 4, fits exactly.
- Select an automatic-direction-sensing RS-485 transceiver (no DE/RE pin at
  all) — same result, no inverter needed.

**Neither a specific automatic-direction RS-485 transceiver nor a verified
current budget (does 650 mW / the achievable output current actually cover a
bare CAN transceiver plus a bare RS-485 transceiver simultaneously at 16 Mbps
and 50 Ω bus loading?) has been checked against a primary datasheet.** There
is also an unrecorded functional-safety trade this repository has not made a
decision on: today a fault on the CAN bus and a fault on the RS-485 bus are
isolated from *each other*, not just from the MCU; merging both onto one
barrier removes that channel-to-channel separation. That is a real design
decision requiring its own justification under `AGENTS.md` §4, not an
incidental side effect to accept by default. **This item is recorded as a
direction worth a follow-up spike, not a recommendation to implement.**

### 4. PCB creepage-extending geometry (grooves/ribs/slots) — real technique, not yet usable here

Every isolator datasheet checked in this audit ([9], [10], [59], [60], [61])
carries the same footnote, verbatim in substance: "Techniques such as
inserting grooves, ribs, or both on a printed circuit board are used to help
increase these specifications." This is a real IEC 60664-1 provision — a
routed slot between two creepage domains lengthens the *surface path* a
tracking failure would have to follow, which can let a design meet a given
creepage figure over a shorter *straight-line* distance than an unbroken
board surface would need, in principle shrinking board width without
changing which parts are used at all.

**This repository does not yet catalog the actual IEC 60664-1 clause that
governs slot width/depth vs. credited creepage distance**, and every
datasheet's footnote stops at naming the technique, not quantifying it. Using
a groove without that clause would mean claiming a creepage credit that
cannot be traced to a verified source — exactly what `AGENTS.md` §1.3
prohibits. **Open item:** obtain and cite the specific IEC 60664-1 clause
(likely in its Annex on grooves/ribs) before this technique is applied to any
layout, and mark it `UNVERIFIED — needs primary source` until then.

### 5. Board edge margin (0.55 mm) — small, unverified, possibly fab-limited rather than safety-limited

`isolation_envelope.py`'s `EDGE_MARGIN_MM = 0.55` is not attributed to a
specific fab's design rules in this repository's citation trail — it reads
as a generic copper-to-board-edge allowance, not a creepage requirement
itself (the 7.5 mm+ creepage figures already account for the isolator's own
safety margin). If the actual fab house's minimum copper-to-edge clearance is
smaller than 0.55 mm, this could be tightened for a small (≤0.5 mm total,
both edges) width reduction. **Open item:** trace this figure to the
target fab's stated design rules before relying on it, per the same
`AGENTS.md` §1.3 discipline as everything else in this audit — it is not
large enough to change any conclusion above, but it should not be asserted
as a hard 0.55 mm floor without a source either.

### 6. Everything else in the BOM checked and found NOT to carry its own creepage boundary

For completeness, the rest of the BOM was checked for hidden isolation
crossings that would each demand their own creepage zone: the gate driver
(`U5`, DRV8353S) and its SPI bus to `U1` share the battery-negative ground
domain with the MCU — no isolation, no creepage boundary. The secure element
(`U2`, OPTIGA Trust M) is on the same non-isolated domain via I2C. The
current-sense amplifiers (`U6`–`U8`, INA240) and shunts are single-domain.
**Only `U3` (CAN) and `U4` (RS-485) carry an isolation barrier on this
board.** There is no third hidden creepage zone to find or consolidate.

## What This Means for "Rearrange for a Smaller Board"

The single most effective *rearrangement* already exists in this design and
should be preserved, not re-litigated: `U3` and `U4` already share one
isolated island with one keepout (`README.md`, "bottom right... A copper
keepout removes every plane and pour from that band"), so the two barriers
are not each paying a separate keepout today. The rearrangement lever that
remains open is the one `isolation_envelope.py` already names as the
alternative to an inboard fit: put the non-isolated control section (`U1`,
`U2`, decoupling) on a **different facet** of the Faceted rigid-flex form
factor than the isolated pair, paying board *length* across a fold rather
than trying to win *width* at the isolation boundary — which is what the
Faceted form factor exists to do, and item 1 above (the RHB MCU package)
makes that facet's own footprint dramatically smaller regardless of which
strategy is chosen.

## When to Apply

- Any BOM audit where working voltage/insulation class cannot move (fixed by
  protocol, battery chemistry, or a certification requirement already made).
- Before proposing a "smaller isolator" swap — check `smaller-package-does-
  not-shrink-creepage.md` first; this document is the audit that follows once
  that avenue is closed off.
- Before treating two isolated interfaces as requiring two independent
  creepage zones by default — check whether they can share one island first
  (already done here) and whether they could share one barrier (item 3,
  still open).

## Related

- `docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md`
- `docs/solutions/architecture-patterns/smaller-package-does-not-shrink-creepage.md`
- `docs/tools/isolation_envelope.py`
- `REFERENCES.md` [9], [10] (with 2026-09-06 addendum), [44], [59], [60], [61]
- `builds/6s/50A/CAN_485_faraday/README.md` — current placement description
- `TODO.md` — tracks the open items in findings 3, 4, and 5
