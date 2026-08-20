---
date: 2026-08-19
problem_type: architecture_pattern
category: architecture-patterns
module: builds
component: routing_handoff
severity: high
applies_when:
  - "Auto-routing a KiCad board through Specctra DSN and FreeRouting"
  - "A router reports connections unrouted and it looks like congestion"
  - "A board has poured plane layers, a power net, or an isolation barrier"
  - "Placement has moved since the pours and rule areas were drawn"
  - "Deciding whether a routed board is ready to fabricate"
tags:
  - routing
  - freerouting
  - specctra
  - kicad
  - netclasses
  - ground-plane
  - automation
  - verification
related_components:
  - builds/6s/50A/CAN_485_faraday/kicad/tools/autoroute.py
  - builds/6s/50A/CAN_485_faraday/kicad/tools/set_netclasses.py
  - builds/6s/50A/CAN_485_faraday/kicad/tools/stitch_planes.py
  - builds/6s/50A/CAN_485_faraday/kicad/tools/fix_phase_pours.py
  - builds/6s/50A/CAN_485_faraday/kicad/open_secure_esc_6s_50a_can485_faraday.kicad_dru
---

# What the auto-router is never told

## Context

Routing `builds/6s/50A/CAN_485_faraday` was expected to be one command against
a placement-converged board: run the build's `tools/autoroute.py`, wait, read
the unrouted count. It took four router runs and ten fixes, and **not one of
the ten was a routing problem**. Every one was something true about the board
that never reached the router, something the router was told that was not
true, or a defect in the tooling that carried the message.

The board is a good stress case for this: 4 layers, 65 parts on 32 x 66 mm,
a 50 A pack net, three motor phases, four poured plane layers, a galvanically
isolated CAN/RS-485 section, and a 0.5 mm-pitch WQFN-40 gate driver. Any board
with two of those has the same exposure.

The failure mode is consistent and it is what makes this worth writing down:
**every one of these defects made the route look BETTER, not worse.** A missing
net class routes fine at 0.2 mm. A router allowed into the ground plane finds
more paths. Filled zones make orphaned pads look connected. The route quality
metric moves the wrong way, so the score cannot catch any of it.

## Guidance

Before handing a board to FreeRouting, verify each of the following. The
measured values are from this board as it stood during the 2026-08-19 routing
pass. Tool paths below are relative to
`builds/6s/50A/CAN_485_faraday/kicad/`.

### 1. Confirm the net classes are actually in effect

Net classes live in the `.kicad_pro`, not in the `.kicad_pcb`. Any tool that
rewrites the project JSON can drop them. This board was found with **only
`Default` defined** — the classes the build's `tools/set_netclasses.py` writes
were gone, so VM, GND and all three motor phases would have exported at the
0.2 mm signal default.

Assert it, do not assume it. `tools/autoroute.py` now refuses to run if a
sampled net does not resolve to its expected width:

```python
got = board.FindNet(name).GetNetClassSlow().GetTrackWidth() / MM
if abs(got - want) > 1e-6:
    raise SystemExit("net classes are not in effect")
```

### 2. Check the class net names still exist

A net-class assignment naming a net the board does not have is **silent** —
the class is written, nothing matches it, and the conductor quietly routes at
`Default`. `set_netclasses.py` still named `CAN_VISOIN_OPEN` and
`RS485_VISOIN_OPEN`, renamed out of existence when the isolated-supply
ferrites split each rail into a `_GNDISO`/`_ISO_GND` and `_VISOIN`/`_VISOOUT`
pair. It now checks every name against the board's net table and refuses.

### 3. Re-test workarounds after a KiCad upgrade

`autoroute.py` carried a hand-written DSN class-injection step, added because
older KiCad put every net in one `kicad_default` class at 0.2 mm. Re-checked
against KiCad 9.0.2 (`pcbnew 9.0.2+dfsg-1`): `LoadBoard()` now resolves the
project net classes and `ExportSpecctraDSN` writes real `(class Power ...)`
blocks with the project widths. The workaround was obsolete; the failure it
guarded against was not, it had just moved upstream to item 1.

### 4. Rule areas export as total no-route zones

KiCad's Specctra exporter writes **every** rule area as a bare Specctra
`(keepout ...)`, which to FreeRouting means no wire and no via. It does not
carry KiCad's per-item flags across. This board's isolation rule area is
`copperpour not_allowed` but `tracks allowed` / `vias allowed`; exported
verbatim it declared y 76.50..86.55 off limits on all four layers — the band
containing **U1 (the LQFP-64 MCU), U2 (the secure element) and J1**. The
router could not have connected the MCU at all, and the result would have read
as congestion.

Strip the keepouts whose source rule area allows tracks and vias; leave a
genuine no-route area alone.

### 5. Plane layers export as `(type signal)`

This is the one with the largest consequence. A 4-layer SIG/GND/PWR/SIG stack
has two layers that are not routing space, and the DSN says they are. The
first run put **59 segments / 196.7 mm of signal through the In1.Cu ground
plane and 29 segments / 218.3 mm through the In2.Cu VM plane** — 415 mm of
slots cut in the reference planes of a 50 A inverter whose entire premise is
surviving EMI. Return current under a signal crossing a slot detours around
it, and the detour is the loop antenna.

Rewriting those layers to Specctra `(type power)` excludes them from routing
while keeping them readable as copper. Verified after the fix: **0 segments on
In1.Cu and In2.Cu.**

The cost is honest and should be expected — two fewer routable layers left
more connections unrouted than the four-layer run did. That is the correct
trade, and it is exactly the trade an unaudited "completion percentage" would
push the wrong way.

### 6. The DSN boundary has no clearance margin — and insetting it is a trap

KiCad writes the Edge.Cuts outline as the routing boundary and nothing else.
`min_copper_edge_clearance` is a board setup constraint that never reaches the
DSN, so the router lays copper right up to the edge — 11 violations, 6 of them
on the isolated comms nets, where edge copper matters most.

**The obvious fix does not work, and it fails expensively.** Insetting the
boundary cost two full router runs on this board: both hung until their time
limit (2700 s and 3000 s), produced no `.ses` file, and FreeRouting reported
no error either time. The diagnosis took two attempts because the first cause
masked the second:

- A flat 0.75 mm inset put J4A/J4B/J4C — the phase terminals, 5 x 10 mm
  solder-wire pads reaching y 85.50 — 0.20 mm outside the boundary. Clamping
  the inset to the pads fixed that, and the router hung again anyway.
- The real blocker is the **pours**. GND, VM and the three phase pours are
  exported as `(plane ...)` polygons that reach the board edge at
  x 20.45..51.45, y 20.50..85.50. Any boundary inset from the outline leaves
  conductor area outside the region the router is allowed to work in, and
  pours cannot be clamped away — reaching the edge is their job.

So: on a board with edge-to-edge pours, do not move the boundary. Express the
requirement as clearance **to** the boundary instead — Specctra has
`wire_area` / `via_area` clearance types for exactly this. That is the
candidate fix and it is **untested here**; the inset code is left in place,
disabled behind a flag, with the failure recorded in its docstring so the next
person does not spend two more runs rediscovering it.

Two process points fall out of this and both generalise past FreeRouting:

- **A hang is a failure mode you must plan for.** The router did not reject
  the contradictory input; it accepted it and worked forever. Give any
  external solver a wall-clock limit and treat "no output" as a first-class
  result, not an impossible one.
- **Never destroy the input before you have the output.** `autoroute.py`
  cleared the board and *saved it* before exporting the DSN, so each hang left
  the real board with 548 segments deleted and nothing to replace them. It now
  writes the cleared board to scratch and only touches the project file once
  a routed result exists. Two runs' worth of work was recovered from backups;
  it should not have needed recovering.

### 7. Net-class clearance is a floor that includes IC pins

A KiCad net-class clearance applies to every copper item on the net, including
two adjacent pins of the same package. `Power` at 0.4 mm is wider than the
0.28 mm pin-to-pin gap of U5's 0.5 mm-pitch WQFN-40, so it was unsatisfiable
by construction: **24 clearance violations** between VM, PH_* and ISENSE pins
and their own neighbours on U5, U1, U2 and J1.

This repo had already learned this once — `set_netclasses.py` records the
`Isolated` class producing 346 violations the same way, and the note says why.
The lesson had not been carried across to `Power` and `Sense`. The wide
spacing a power net wants is between **routed copper**, not inside an IC, and
in KiCad 9 that is a scoped custom rule:

```lisp
(rule "power_conductor_spacing"
    (constraint clearance (min 0.4mm))
    (condition "A.NetClass == 'Power' && B.NetClass == 'Power'
                && A.Type != 'Pad' && B.Type != 'Pad'"))
```

Net-class clearance 0.4 -> 0.2 mm plus that rule: 59 -> 35 violations, with no
loss of the constraint that was actually wanted.

### 8. One net class cannot describe a power net's two ends

VM, GND and each phase land on a 7 mm pack terminal **and** on a 0.25 mm WQFN
pad. At the 3.0 mm `Power` width the router cannot leave the QFN pad at all;
it reports the connection unrouted and it reads as congestion again.

Resolve it by making the pour carry the wide conductor and relaxing the class
**in the DSN only** for stub routing, so the `.kicad_pro` keeps stating the
truth about the conductor — then audit total routed length per plane net
afterwards, so a signal-width trace cannot end up in series with 50 A.

### 9. Filled zones hide missing connectivity — check the vias

The board carried **zero vias**. Nine zones were filled, and not one plane was
tied to any other: In1.Cu (solid GND) and In2.Cu (VM) were floating copper,
poured and DRC-quiet and carrying nothing.

Nothing in the flow catches this, because a zone fill makes every same-net pad
on its own layer look connected and the ratsnest goes quiet. The board reads
as "mostly routed" while the inner planes do no work.

Three tests are worth running explicitly, and the third is the one that
actually settles it:

- Count vias. Zero vias on a 4-layer board with plane layers is always a bug.
- Test plane-net pads against their own net's **filled polygon**, using the
  **pad's shape**, not its centre.
- **Then ignore both and ask the connectivity engine.** Geometry tests answer
  "is there copper here", which is not the same question as "is this net one
  electrical node". On this board a shape test said the three phase terminals
  J4A/B/C were connected — their pads genuinely do sit under 1.0 mm of phase
  pour — while KiCad's own connectivity reported all three unconnected. Both
  were right: the pour reaches the pad, and the strip that reaches it had been
  **severed from the main pour body by the routing pass**. Union-find over
  pads, tracks, vias and zone fills (the PCB analyzer's `connectivity_graph`
  with `--full`) is the test that sees that; a proximity test never will.

What that test found is the real state of this board after routing, and it is
much worse than the ratsnest count suggests:

| net | islands | largest island |
| --- | ------- | -------------- |
| GND | 25 | 30 of 85 pads |
| VM | 9 | 28 of 54 pads |
| PH_A / PH_C | 4 each | 4 of 9 pads |
| PH_B | 3 | 7 of 9 pads |
| 3V3 | 3 | 18 of 32 pads |

Every one of those pours was continuous before routing. **Routing the signals
fragmented the power pours**, because each track carves its clearance out of
every pour it crosses, and nothing in the flow re-checks pour continuity
afterwards. On a board where the pours *are* the high-current conductors, that
is the most consequential thing the router did — and it is invisible in the
unrouted count, which went down.

### 10. Pours are derived from placement, and nothing re-derives them

Every placement pass on this board — widen, lengthen, align, symmetrize —
silently invalidated pour geometry drawn from the previous placement. Measured
after the 2026-08-19 alignment pass:

```text
PH_A pour outline   y 60.02 .. 85.50
Q1 source pads 1-3  y 55.52 .. 56.98   <- 3.04 mm ABOVE the pour
```

Each phase pour reached its low-side FET drain and stopped short of its
high-side FET source, so the half-bridge switch node — the conductor carrying
the full 50 A between the two FETs — was split in two with no copper joining
the halves. `PH_B` happened to be correct, so the defect was not even
symmetric and could not be spotted by eye against its neighbours.

Fix it as a pour change, not a routed track: the switch node is the highest
di/dt conductor on the board and a track there adds both resistance and loop
area. Re-derive the pour edge from the pads it must reach, and have the tool
refuse to act if the premise no longer holds.

### 11. A via defeats a layer-separation barrier, and no checker knows

This board's isolation barrier is held **geometrically**, by keeping the pack
terminals as single-layer SMD islands on the face *opposite* the isolated
section — worth 2.80 → 4.64 mm of creepage when it was adopted. A through via
punches every layer, so a via anywhere near the isolated section destroys the
thing the barrier is made of.

The plane stitcher, written without that rule, placed **48 vias inside the
isolated band** — several directly over the isolators' isolated pin rows and
the isolated supply capacitors. Worst measured clearance from a via to
isolated copper: **0.340 mm, against a 7.5 mm requirement.**

**Nothing in the flow caught it, and the reason generalises.** KiCad's DRC has
no rule for "isolation barrier". The project's own placement scorer has a
creepage metric — but it measures *pads on a shared layer*, so a via is
invisible to it twice over: a via is not a pad, and it is on every layer. Both
exclusions are individually correct and deliberate; together they leave a hole
exactly the shape of this defect. It surfaced only because someone audited via
positions against the isolated nets directly.

So: when a design rule is enforced by *geometry the tools do not model*, every
tool that places copper unattended must carry the rule itself. Write it into
the placer, not just the reviewer — and prefer a check that measures **all
copper items** against the constraint, not the one class of item the original
metric happened to compare.

### 12. A checker that matches nothing reads exactly like a checker passing

Two of this board's custom DRC rules had never fired, and the discovery came
only from deliberately testing them against a board known to be broken.

**A multi-line `(condition "...")` in a `.kicad_dru` silently invalidates the
entire file** — every rule in it, including rules above the offending line. No
error, no warning, exit 0. A rule that fires 154 times on its own fires zero
times with a multi-line condition anywhere else in the file. Two conductor-
spacing rules on this board had been written that way, so the DRC improvement
attributed to them came *entirely* from a net-class change made at the same
time. With them actually running, 79 previously-hidden violations appeared.

**And clause order in a two-item condition is not commutative.** Measured
against a board with 48 known violations:

| condition | hits |
| --------- | ---- |
| `A.Type == 'Via'` | 502 |
| `B.NetClass == 'Isolated'` | 499 |
| `A.Type == 'Via' && B.NetClass == 'Isolated'` | **0** |
| `(A && B) \|\| (B && A)` | **0** |
| `A.NetClass == 'Isolated' && B.Type == 'Via'` | **154** |

Both halves match alone. The obvious conjunction matches nothing. An OR
*containing* the working clause matches nothing. Only one ordering fires.

The general rule this forces: **every checker needs a negative control** — an
input known to violate it, on which it must be *seen* to fire. This applies to
DRC rules, lint configs, assertions, and CI gates equally. Silence from a
checker is not evidence; it is the absence of evidence, and the two are
indistinguishable from the outside. On this board a full day of DRC runs were
quoted as evidence of compliance while the rules producing that silence were
inert.

Corollary for the router: **one plane per net per layer in the exported DSN.**
Adding a second, overlapping same-net zone is electrically fine and
catastrophic for FreeRouting — the router failed to complete a single pass in
53 minutes on a board it had routed in 23. Diffing the DSN's plane inventory
against the last board that routed normally found it in one step; nothing else
would have.

### 13. Stitch after routing, not before

Placing the stitching vias first looks tidier and routes worse: 223 vias on a
32 x 66 mm board are 223 obstacles the router solves around, and it will leave
connections unrouted rather than displace copper it was told is fixed. Placed
afterwards, the stitching takes the space the router did not want.

Related: a rigid stitching lattice is the wrong pattern on a dense board. At
2.5 mm pitch it placed 32 GND vias and **zero** VM vias — not because the VM
plane had nowhere to tie, but because no lattice point happened to land on
free copper; a 0.5 mm scan of the same board found 116 legal VM sites. Scan
finely, take any legal site, and enforce the pitch as a **minimum spacing**
between placed vias rather than as a grid. Same board, same rules: 46 GND +
35 VM.

## Why This Matters

Two reasons, and the second is the one that generalises.

**The router's report is not a measure of the board.** Six of the eleven items
above make the unrouted count go *down* when they are wrong. A board routed
with plane layers open, an isolation keepout that does not exist, and a pack
net at signal width will report a better completion percentage than the
correct board does. Any workflow that gates on "how much routed" is being
steered by the defects.

**The handoff is where the design intent is lost.** Every one of these is
information the KiCad project genuinely holds — the net classes, the rule
area's allowed/not-allowed flags, the stackup's plane layers, the edge
clearance constraint — that the Specctra export does not carry, or carries in
a form that means something else. The router is not wrong; it is answering the
question it was actually asked. The work is in making the exported question
match the board.

This extends
[the harness is the thing most likely to be wrong](measurement-harness-must-be-audited.md)
from the placement scorer to the routing handoff: same failure shape, same
reason it survives, one layer further down the toolchain.

## When to Apply

- Before the first auto-route of any board, and again after any KiCad upgrade
  (item 3) or any placement pass (item 10).
- Whenever an auto-router leaves connections unrouted around one package or
  one region — check items 4, 7 and 8 before concluding the placement is too
  tight.
- Before calling any routed board fabrication-ready: items 9 and 10 are both
  invisible to DRC and both leave a board that looks finished.

## Examples

The tooling that implements these checks has its own traps, and two of them
cost a full re-run of the board:

**A chained SWIG call silently reads freed memory.** The stitcher's collision
test was written as valid C++:

```python
# WRONG -- rejects nothing
if pad.GetBoundingBox().Inflate(keep).Contains(point):
```

`GetBoundingBox()` returns a temporary proxy, `Inflate()` returns a reference
*into* that temporary, and the temporary can be collected before `Contains()`
runs. No exception, no warning; the test just returns False for everything. It
placed 60 vias through the FETs' VM and phase pads and took the board from 29
DRC violations to **186, including 41 hard shorts**. Binding the box to a live
name first is the entire fix:

```python
box = pad.GetBoundingBox()
box.Inflate(keep)
if box.Contains(point) and pad.HitTest(point, keep):
```

**DSN coordinates are decimal, not integer.** KiCad writes the board outline
as `50092.9 -19952.4`. An integer-only `-?\d+` regex splits each of those into
two numbers and scrambles the whole coordinate list — the first boundary inset
turned a 32 x 66 mm outline into the rectangle (-85547, -491) .. (51450,
-85550). Nothing errored. The router simply went on hugging the real board
edge, and the fix looked like it had been applied. Match `-?\d+(?:\.\d+)?`.

Both belong with the KiCad scripting traps already earmarked as a separate
capture in TODO.md 14.6(b).

**What this pass could not fix, and why it is worth knowing the shape of it.**
Two findings were referred to the repo owner rather than fixed, and both are
placement questions the router cannot route around:

- The isolation rule area is stranded at the opposite end of the board from
  the isolators (TODO.md 12.5.z), so the actual barrier band y 30.4..38.6
  carries solid VM and GND copper on all four layers while the rule area voids
  the plane under the MCU instead.
- The 50 A pack terminals cannot be stitched to the inner planes at all: the
  pack-terminal via arrays placed **0 of 18 vias**.

The second one is worth the space, because the first answer was wrong and the
way it was wrong is the lesson. J5A and J5B overlap U3's and U4's isolated pin
rows *in plan view*, which a planar pad-to-pad measurement reports as 0.000 mm
of isolation clearance. That reading is wrong, and this repo's own
`score_placement.py` says so: it measures the closest isolated/non-isolated
pad pair **on a shared layer, between different parts**, and reports 7.83 mm
against the 7.5 mm requirement. Both exclusions are deliberate and correct —
the pack terminals are SMD on the face *opposite* the isolated parts, so the
only surface path between them runs around the board edge, and that layer
separation is itself a recorded design decision worth 2.80 -> 4.64 mm of
creepage on this build.

So the barrier holds. What does not hold is the pack return, and the reason is
the same fact seen from the other side: **the isolation strategy depends on
those terminals being single-layer islands, and a via is exactly what would
break it.** A via under J5B punches GND through to B.Cu a fraction of a
millimetre from U4's isolated pins. The stitcher placing 0 of 18 vias was not a
failure to find room — it was the correct refusal, and it surfaced an
architectural constraint that neither the creepage metric nor the ratsnest
could show: *the connection the pack return needs is the connection the
isolation forbids.*

The general form: when a geometric measurement disagrees with a purpose-built
project harness, assume the harness encodes a definition you have not read
yet. Go and read it before reporting the number.
