---
date: 2026-08-18
problem_type: architecture_pattern
category: architecture-patterns
module: builds
component: board_geometry
severity: high
applies_when:
  - "A build carries a galvanically isolated interface (CAN, RS-485, Ethernet)"
  - "Choosing a board envelope before placement starts"
  - "Placement keeps failing creepage no matter how parts are shuffled"
  - "Deciding whether to grow a board's length or its width"
tags:
  - isolation
  - creepage
  - board-geometry
  - placement
  - kicad
  - design-rules
related_components:
  - REFERENCES.md
  - docs/tools/isolation_envelope.py
  - builds/6s/50A/CAN_485_faraday
---

# Isolation creepage sets the board's aspect ratio — compute it before placing

## Context

On `builds/6s/50A/CAN_485_faraday/` the creepage requirement was treated as
something DRC would catch. It is not a check; it is a geometry constraint that
decides the board's shape. Treating it as a check cost several complete
re-placements, a board-growth attempt, and two reverts — all of which a single
line of trigonometry, run before any footprint moved, would have avoided.

The build carries two isolated transceivers (ADM3055E CAN-FD, ADM2582E
RS-485). REFERENCES.md [9] Table 6 requires **7.5 mm external clearance and
7.5 mm creepage, input terminals to output terminals**, with the explicit
footnote that "Consideration must be given to pad layout to ensure the minimum
required distance for clearance is maintained."

That number does not merely forbid certain placements. It partitions the
board.

## Guidance

**Ask one question before placing anything: can the widest non-isolated part
sit BETWEEN the two isolated rows?**

With both isolated rows facing opposite board edges (the arrangement that lets
planes cross the middle), the answer is arithmetic:

```
minimum board width = widest_part + 2 x (creepage + pin_inset) + 2 x edge_margin
```

Run `docs/tools/isolation_envelope.py` — it answers this and prices the
alternative. For this build:

```
12.90 + 2 x (7.5 + 1.43) + 2 x 0.55 = 31.86 mm

at 25.40 mm -> dx = 4.27 mm  FAILS
at 32.00 mm -> dx = 7.57 mm  OK
```

**If it fits, control sits alongside comms and there is no creepage band in
the vertical stack. If it does not, the part must clear the isolated section
in Y instead**, which costs the creepage offset *plus* the part's own height:

```
6.17 mm (gap) + 12.90 mm (its own height) = 19.07 mm of length
```

So on this build, **6.46 mm of width buys back 19.07 mm of length — a 3.0x
trade at essentially constant area** (25.40 x 78 = 1981 mm²; 32 x 59.5 =
1904 mm²). It is an aspect-ratio decision, not a size one, and the narrow
option is almost never the right one.

## Why This Matters

Three failure modes follow from discovering this during placement instead of
before it:

**Placement thrashes without converging.** Every arrangement fails creepage,
because no arrangement can succeed — the board is too narrow for any of them.
Time goes into shuffling parts when the answer is that the envelope is wrong.

**"Grow the board" looks like the fix and is only half of one.** Lengthening
the board resolves the widest part's clearance, then the *next* non-isolated
thing fails — on this build the 50 A pack terminals, which shared the top end
with the isolated section and overlapped it in x. Creepage is a property of
every isolated/non-isolated pair, so fixing one pair just promotes the next.

**The cheaper lever is invisible.** Width and length trade at roughly 3:1
here. Nothing in a DRC report says that; it only says "3.49 mm, needs 7.5."

There is also a temptation worth naming and refusing. The 7.5 mm figure is the
component's rating for full reinforced isolation, and IEC 60664-1 would permit
far less at a lower system working voltage — so "just relax the creepage"
presents itself as the cheap fix. On this build the repo owner rejected it,
and the reasoning generalises: the isolation exists because the board must
survive harsh EMI environments, which is the same reason it carries a Faraday
shield and two redundant control paths. Weakening it to save a few millimetres
defeats the thing it was specified for. Decide that question deliberately and
record the decision; do not let it be decided implicitly by a tight envelope.

## When to Apply

Before placement, on any build whose decision-matrix Protocol axis selects an
isolated interface. Specifically:

- Instantiating a new `builds/<voltage>/<amperage>/<variant>/` with CAN,
  RS-485, or isolated Ethernet
- Any time an envelope is proposed or changed
- Before accepting a width constraint from the vehicle side — check what it
  costs in length first, and quote the trade back

Also apply it when the mechanical envelope turns out to be less binding than
assumed. On this build the ESC mounts in a nacelle annulus around a 55 mm EDF
casing; the usable radial gap is 4.00–11.65 mm and the duct is 185.2 mm long,
so **both 25.4 mm and 32 mm widths fit with 7–9 mm to spare**. The width was
never mechanically forced — it had been chosen early and then defended long
after the constraint that motivated it had gone. Re-derive envelope
constraints from the actual mounting geometry rather than inheriting them.

## Examples

**The arrangement that makes the middle usable.** Rotate both isolated parts
so their isolated pin rows face opposite board edges and their non-isolated
rows face inboard:

```
U3 isolated x= 1.98   non-isolated x=11.28   (rot 180)
U4 isolated x=23.75   non-isolated x=14.45
```

This is what lets a VM plane cross the middle of the board, and it turns the
isolation keepout from one full-width rectangle into two narrow edge bands.
Getting there took two rotations on this build; the target arrangement was
only obvious in hindsight.

**Check the connectors too, not just the ICs.** After rotating a transceiver,
its connector is on the wrong side of the barrier until it follows:

```
before rotation:  RS485_A  U4.13 -> J3   3.12 mm
after rotation:   RS485_A  U4.13 -> J3  13.61 mm
```

An isolated conductor running 13.6 mm back across its own package, past its
own non-isolated row, defeats the barrier as surely as a short pad gap. Rotate
the part and move its connector and support components in the same step.

**Measure creepage by an explicit net list, never a substring.** The first
checker written for this build classified nets by substring, and
`GD_SPI_MISO` contains `ISO` — so a SPI signal was scored as an isolated
conductor and produced confident, wrong minimum distances. Classify by pin
number for the isolator itself (pins 11–20 are the isolated side on both these
20-pin parts) and by an explicit net set for everything else.

## Related

- `docs/solutions/architecture-patterns/esc-build-instantiation-workflow.md` —
  the surrounding build procedure; this document is the geometry decision that
  should precede its placement step
- `docs/tools/isolation_envelope.py` — the calculation, runnable
- `docs/tools/conductor_sizing.py` — the other pre-placement calculation
  (copper cross-section), same spirit: derive it before drawing, not after
