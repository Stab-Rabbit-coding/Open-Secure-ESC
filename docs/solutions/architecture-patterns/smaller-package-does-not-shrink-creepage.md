---
date: 2026-09-06
problem_type: architecture_pattern
category: architecture-patterns
module: builds
component: board_geometry
severity: high
applies_when:
  - "Proposing to swap an isolated transceiver for a smaller-package part to save board width"
  - "Considering a discrete isolator + dc-dc + transformer stack in place of an integrated isolated transceiver"
  - "A faceted or narrow board is short of its width target and an isolated part is a suspect"
  - "Comparing two isolator/transceiver parts by package size alone"
tags:
  - isolation
  - creepage
  - board-geometry
  - can
  - rs-485
  - datasheet-verification
related_components:
  - REFERENCES.md
  - docs/tools/isolation_envelope.py
  - docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md
  - builds/6s/50A/CAN_485_faraday
---

# A smaller isolator package does not buy back creepage — working voltage does that math, not pin count

## Context

The question that triggered this: would swapping the CAN transceiver
(ADM3055E/ADM3057E [10], 20-lead wide-body SOIC) for TI's ISO1042 [59] on
its smaller SOIC-8 (DWV) package, plus swapping the RS-485 transceiver
(ADM2582E/ADM2587E [9]) for a discrete "digital isolator + isolated dc-dc
chip + isolation transformer" stack, get the `CAN_485_faraday` board's
faceted-strip width under 24 mm (the chord width `docs/tools/strip_width.py`
allows inside a 25 mm radius EDF bore)?

Two things had to be checked before that question could even be answered,
and both corrected the premise:

1. **ADM3055E is already the CAN chip, and ISO1042 is also a CAN chip.**
   ADM3055E/ADM3057E's own datasheet title is "... CAN Transceivers for CAN
   FD" [10]; RS-485 in this build is the separate ADM2582E/ADM2587E [9].
   ISO1042 [59] is TI's isolated CAN transceiver — a same-function swap
   candidate for ADM3055E, not for the RS-485 part. TI's actual RS-485
   equivalent to ADM2582E is ISOW1412 [60], a single integrated package
   (isolator + isolated dc-dc + transceiver, exactly like ADM2582E's own
   architecture) — not the "isolator + separate dc-dc chip + separate
   transformer" three-part stack the question proposed. No primary source
   for that specific discrete architecture (a bare digital isolator paired
   with a named external isolated dc-dc IC and a named isolation
   transformer, for an RS-485 channel) is catalogued in this repository,
   and none is invented here.

2. **The smaller package needs MORE creepage, not less.** Both TI
   candidates were pulled from primary datasheets [59][60] and checked
   against the two Analog Devices parts they'd replace [9][10]:

   | Part | Function | Package (nominal body) | External creepage/clearance | Working voltage (VIOWM) |
   |---|---|---|---|---|
   | ADM2582E/ADM2587E [9] | RS-485, integrated | 20-lead wide SOIC | **7.5 mm** | 396 V rms |
   | ISOW1412 [60] | RS-485, integrated | 20-lead wide SOIC (12.83 × 7.5 mm) | **>8 mm** | 1000 V rms |
   | ADM3057E [10] | CAN, integrated | 20-lead wide SOIC (RW-20) | **7.8 mm** | 420 V rms |
   | ADM3055E [10] | CAN, integrated | 20-lead increased-creepage SOIC (RI-20-1) | **8.3 mm** | 420 V rms |
   | ISO1042 [59] | CAN, isolator only (needs external bus-side supply) | **SOIC-8** (DWV, 5.85 × 7.5 mm) | **>8.5 mm** | 1060 V rms |

   The SOIC-8 ISO1042 has under a third of the body width of the wide
   20-lead packages, and still needs the *largest* creepage figure in the
   table. Both TI parts are rated to roughly 2.5× the working voltage of the
   Analog Devices parts they'd replace, and IEC 60664-1's creepage/clearance
   tables (cited by name in every one of [9], [10], [59], [60]'s own
   insulation-specification sections) step up with working voltage — a
   package being physically smaller does not exempt it from that table.

## Why This Matters

**Creepage is not a property of how many chips implement a barrier; it is a
property of the working voltage and insulation class the barrier is rated
to, read off a standards table (IEC 60664-1) that every one of these parts'
own datasheets cites by name.** Two consequences follow that are easy to
miss when the instinct is "smaller package, smaller board":

1. **A same-working-voltage swap to a smaller package saves nothing at the
   isolation boundary**, because the required clearance around the part
   (which `docs/tools/isolation_envelope.py` and
   `isolation-geometry-sets-board-aspect.md` already establish is what
   actually sets the board's minimum width, not the part's own body size)
   is set by the voltage/class table entry, which is unchanged by the
   package shrinking.
2. **Splitting one integrated part into several discrete ones (isolator +
   separate dc-dc + transformer) does not divide the creepage requirement
   between them — it multiplies the places it has to be re-established.**
   Each discrete piece that itself straddles the isolation boundary (the
   isolator IC, and separately the dc-dc transformer's own primary-to-
   secondary spacing) needs its own full creepage clearance at the *same*
   working voltage, and the PCB copper between them still needs the same
   clearance maintained across the gap connecting them. Nothing about using
   three parts instead of one lowers the voltage the barrier has to hold
   off, which is the only number the standard's table cares about.

Running the actual board-width tool on all three creepage values makes the
outcome quantitative, not just qualitative:

```
$ python3 docs/tools/isolation_envelope.py --creepage 7.5 --board-width 24.0   # current, ADM2582E
   ... FAILS by 3.57 mm regardless; MCU needs 31.86 mm width to sit inboard

$ python3 docs/tools/isolation_envelope.py --creepage 8.0 --board-width 24.0   # ISOW1412
   ... FAILS by 3.57 mm; now needs 32.86 mm — WORSE

$ python3 docs/tools/isolation_envelope.py --creepage 8.5 --board-width 24.0   # ISO1042 DWV
   ... FAILS by 3.57 mm; now needs 33.86 mm — WORSE STILL
```

**The 24 mm target fails even at today's parts, by the same 3.57 mm margin,
because the bottleneck is the MCU footprint (12.90 mm) needing to sit
inboard of two 7.5 mm-creepage rows on one flat cross-section — not which
transceiver occupies those rows.** Every swap examined makes the working-
voltage class higher, which makes it worse, not better.

## The Actual Lever, If <24 mm Is a Hard Requirement

`docs/tools/isolation_envelope.py`'s own output states the real trade this
repository already uses: at a width that fails the inboard-fit test, the
control section (MCU) instead clears the isolated rows in **Y** — i.e., it
moves to a different position along the board's length, paying length for
width instead of trying to win width at the isolation boundary. That is
exactly what the Faceted rigid-flex form factor is *for*: folding the board
so the isolated-row cross-section and the MCU's cross-section are not the
same facet. Chasing a smaller transceiver package to fix this is solving
the problem in the wrong axis; the tool already prices the right one.

The one lever that *would* reduce the 7.5–8.5 mm figures directly is
lowering the required working voltage or insulation class (e.g., verifying
whether this application actually needs reinforced isolation at these
voltage margins, versus basic isolation at a lower rated working voltage)
— but that is a systems safety-requirements decision requiring its own
justification and citation (`AGENTS.md` §4), not a component substitution,
and is not resolved here.

## When to Apply

- Any time a part swap is proposed on the grounds of package size, for any
  isolated interface (CAN, RS-485, Ethernet, isolated power).
- Before recommending a "split the integrated part into discretes" redesign
  for board-space reasons.
- Whenever `docs/tools/isolation_envelope.py` reports a failing width — check
  whether the proposed fix changes the working-voltage class before
  assuming it changes the creepage number.

## Related

- `docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md`
  — the board-aspect-ratio consequence this trap feeds into
- `docs/tools/isolation_envelope.py` — the tool used to quantify all three
  cases above
- `REFERENCES.md` [9], [10], [59], [60] — the four datasheets compared
- `docs/tools/strip_width.py` — the 24 mm chord-width constraint this
  question was trying to satisfy
