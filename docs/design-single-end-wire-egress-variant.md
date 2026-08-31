# Single-End Wire Egress Variant — design plan

Governed by [`AGENTS.md`](../AGENTS.md). Tracked as `TODO.md` §15.

**Status: PLAN — not implemented, not vetted for fabrication.** Nothing in
this document has been placed, routed, or DRC-checked. Every quantitative
claim below is either (a) read directly out of the as-built
`builds/6s/50A/CAN_485_faraday/kicad/*.kicad_pcb`, (b) produced by a repo tool
named at the point of use, or (c) explicitly marked
`UNVERIFIED — needs primary source (see TODO.md)` per `AGENTS.md` §3.

**Authorship.** Drafted by **Claude Opus 5** (Anthropic), 2026-08-31, at the
direction of the repository owner (GitHub: `Stab-Rabbit-coding`). No portion
was authored by another model. Reviewed by: *nobody yet — this plan has not
been through human review.*

**Units.** Human-facing dimensions are imperial-primary with metric in
parentheses, per the project-wide convention. KiCad-native coordinates are
quoted in millimetres exactly as they appear in the board file, because they
are literal file values rather than measurements — converting them would
break traceability back to the `.kicad_pcb`.

---

## 1. The requirement

The ESC is to be installed in a **pocket** — a blind cavity in a structure —
where the board is inserted from one face and all five power conductors must
leave through the **same open end**. There is no access to the opposite end
of the board once installed.

Specifically: **the pack conductors and the phase conductors both terminate
at one end of the board, on opposite sides of it.**

That is five conductors at 50 A:

| Conductor | Net | Count |
| --- | --- | --- |
| Pack positive | `VM` (VBATT+) | 1 |
| Pack return | `GND` (VBATT−) | 1 |
| Motor phases | `PHASE_A/B/C` | 3 |

### 1.1 What "opposite sides" resolves to

Two readings are possible, and the arithmetic settles it rather than
preference. See §3.1 — a single row of five terminals across one board end is
not buildable at this board width, so the two terminal groups must be split
onto the **two long edges near the chosen end**. The "opposite faces"
(F.Cu / B.Cu) reading is recorded and rejected in §7.1.

**This is the one item requiring the owner's confirmation before §5.1
starts.** If "opposite sides" was meant as top face / bottom face, §3 through
§6 change materially.

---

## 2. The as-built baseline this variant departs from

Read from
`builds/6s/50A/CAN_485_faraday/kicad/open_secure_esc_6s_50a_can485_faraday.kicad_pcb`
on 2026-08-31.

| Item | Value |
| --- | --- |
| Board outline | 1.260 in × 2.602 in (32.00 mm × 66.10 mm) |
| Outline extents | X 19.95–51.95 mm, Y 19.95–86.05 mm |
| Pack terminals `J5A`/`J5B` | Y = 29.00 mm, F.Cu |
| Phase terminals `J4A`/`J4B`/`J4C` | Y = 80.50 mm, F.Cu |
| Isolated CAN-FD / RS-485 `U3`/`U4` | Y = 34.50 mm, B.Cu |
| Comms wire pads `J2`/`J3` | Y = 26.50 mm, B.Cu |
| Gate driver `U5` | Y = 60.00 mm, B.Cu |
| FET bridge `Q1`–`Q6` | Y = 53.50 and 66.00 mm, F.Cu |
| MCU `U1` (MSPM0G3518-Q1, LQFP-64) | Y = 78.50 mm, B.Cu |
| Secure element `U2` (OPTIGA Trust M) | Y = 81.50 mm, B.Cu |
| Phase-terminal rule area | X 20.8–51.1 mm, Y 76.5–86.5 mm |

The baseline is therefore **pack in at one end, phases out at the other**,
with the logic cluster (`U1`, `U2`, `J1`) sharing the phase end and the
isolated comms cluster sharing the pack end.

### 2.1 Board width is locked and this variant must not touch it

`docs/tools/isolation_envelope.py`, run 2026-08-31, reproduces the width the
board already has:

```text
creepage required          7.50 mm
isolated pin inset         1.43 mm from the board edge
widest non-isolated part  12.90 mm

MINIMUM BOARD WIDTH:
   12.90 + 2 x (7.5 + 1.43) + 2 x 0.55 = 31.86 mm
```

The 7.5 mm (0.295 in) figure is the ADM2582E/ADM2587E minimum external
clearance and creepage, Table 6 of [9] — a **verified** primary-source value.
The as-built 32.00 mm (1.260 in) width clears the 31.86 mm (1.254 in) minimum
by 0.14 mm (0.006 in).

**Consequence for this variant:** width is not a free parameter. Any
temptation to widen the board so five terminals fit across one end is
governed by `docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md`
— width is bought at 3.0× the length it saves, and the current width is
already the minimum that lets the widest non-isolated part sit *between* the
isolated rows. Growing width does not help here anyway; see §3.1.

---

## 3. What the requirement actually forces

### 3.1 A single row of five terminals across one end does not fit

Terminal footprints as built:

| Designator | Footprint | Pad extent along the board edge |
| --- | --- | --- |
| `J5A`, `J5B` | `SolderWire-6sqmm_1x01_D3.5mm_OD7mm` | 0.276 in (7.0 mm) each |
| `J4A`, `J4B`, `J4C` | `SolderWirePad_1x01_SMD_5x10mm` | 0.197 in (5.0 mm) each |

Laid in one row across the 1.260 in (32.00 mm) end:

```text
2 x 7.0 mm  +  3 x 5.0 mm            = 29.0 mm of pad
32.00 - 29.0                         =  3.0 mm left over
3.0 mm  /  (4 inter-pad gaps + 2 edge margins) = 0.50 mm each
```

0.020 in (0.50 mm) of gap between adjacent 50 A terminals. That fails on
mechanics long before it fails electrically: the conductor is 6 mm²
(≈10 AWG), roughly 0.205 in (5.2 mm) bare and 0.24–0.28 in (6–7 mm) over
insulation, and each joint carries a solder fillet and needs strain relief.
Five such joints cannot be dressed side by side on a 1.260 in (32.00 mm)
edge.

Electrically the spacing is not the binding constraint — at a 25.2 V maximum
pack voltage the conductor-spacing requirement is small. The exact figure
would come from IPC-2221 Table 6-1, which **this repository has not obtained
and issues no citation tag for** (see `REFERENCES.md`, "Pending Verification
— IPC-2152 and IPC-2221"). Recording it here as
`UNVERIFIED — needs primary source (see TODO.md)`; it does not change the
conclusion, because mechanics already decides it.

**Therefore: the two terminal groups must occupy the two long edges near the
chosen end.** This is forced, not chosen.

### 3.2 Which end?

The phase end (Y ≈ 80 mm). The FET bridge already sits at Y 53.5–66.0 mm —
closer to the phase end than the pack end — so bringing the pack terminals to
Y ≈ 80 mm *shortens* the DC bus rather than lengthening it. Bringing the
phases to Y ≈ 29 mm instead would drag the switched-node conductors across
the whole board and past the isolation barrier, which is not acceptable.

### 3.3 The real work: the logic cluster and the pack input swap ends

Y 76.5–86.5 mm is currently occupied by `U1` (MCU), `U2` (secure element),
`J1` (probe pads) and the phase terminals. There is no room there for two
more 0.276 in (7.0 mm) pack terminals plus the bulk capacitance that must sit
in the commutation loop beside them.

So the variant is **not a connector move — it is a board re-partition**:

```text
BASELINE                          SINGLE-END VARIANT

Y=20  +------------------+        +------------------+
      | comms J2/J3      |        | comms J2/J3      |
      | PACK J5A/J5B     |        | isolated U3/U4   |
      | isolated U3/U4   |        | U6/U7/U8         |
      | U6/U7/U8         |        | MCU U1 + SE U2   |   <-- moved here
Y=45  |                  |        | probe J1         |
      +------------------+        +------------------+
      | gate driver U5   |        | gate driver U5   |
      | FETs Q1-Q6       |        | FETs Q1-Q6       |
Y=70  | shunts           |        | shunts           |
      +------------------+        +------------------+
      | MCU U1 + SE U2   |        | bulk caps        |
      | probe J1         |        | PACK J5  | PHASE |   <-- opposite
Y=86  | PHASE J4A/B/C    |        |  -X edge | J4 +X |       long edges
      +------------------+        +------------------+
```

This partition is, on its own terms, cleaner than the baseline: all
low-voltage logic ends up on one end behind the isolation barrier, and all
high-current copper on the other. It is worse in exactly one respect, and
that respect is serious — see §4.

---

## 4. The risk this variant creates, stated plainly

**Split-end egress bought physical separation between the pack harness and
the phase harness for free. Single-end egress deletes it.**

The three phase conductors carry the full PWM switching waveform. The pack
conductors are the reference against which conducted emissions are measured.
In the baseline they leave from opposite ends of the board and can be routed
apart. In this variant they leave the pocket in one bundle, capacitively and
inductively coupled along their whole run.

This directly undercuts the point of the `Faraday` EMI-hardening tier this
build carries. It is a **new requirement on the variant**, not an
implementation detail:

1. A common-mode choke on the pack input becomes mandatory for this variant,
   where it is optional in the baseline. Part not yet selected — see §6,
   task 15.6.
2. The build instructions must specify harness dress: phases as a twisted
   triplet, pack pair twisted, and a stated minimum separation between the
   two bundles inside the pocket.
3. Pre-compliance conducted-emissions testing (`TODO.md` §7.3) must be run on
   *this* variant, not inherited from the baseline. The baseline result does
   not transfer.

**No claim is made here about how much margin is lost.** That number requires
measurement, and inventing one would violate `AGENTS.md` §1.3.

### 4.1 Second-order consequences, each with a real cost

| Consequence | Effect | Where it is handled |
| --- | --- | --- |
| MCU-to-gate-driver distance grows from ≈18.5 mm to ≈31 mm | Longer DRV8353 SPI and 6× PWM runs beside the switching node | §6 task 15.4 |
| MCU leaves the phase-terminal high-dV/dt zone | **Improvement** — `U1` and `U2` no longer sit under the phase rule area | — |
| MCU moves adjacent to `U3`/`U4` | **Improvement** — comms runs shorten; logic sits on the logic side of the barrier | — |
| DC bus from pack terminal to bridge shortens | **Improvement** — smaller commutation loop, lower DC-link inductance | §6 task 15.5 |
| Current-sense returns from the shunts to the MCU lengthen | Analog runs get longer and cross more of the board | §6 task 15.4 |
| Five wire terminals concentrated at one end | The wires are a heat path out of the board; concentrating them concentrates the gradient | §6 task 15.8 |
| Phase-terminal rule area must be split in two | New DRC rules, each needing a negative control | §6 task 15.7 |

---

## 5. Copper sizing — what the repo tool already says

`docs/tools/conductor_sizing.py`, run 2026-08-31 against the as-built
geometry, is the governing calculation. Its own header states it is a
derivation from material constants and **not** an IPC-2152 result — that
distinction is preserved here.

Phase pour, 0.295 in × 0.866 in (7.5 mm × 22.0 mm), at 50 A:

| Copper weight | R (mΩ) | Drop (mV) | W per phase | W all three |
| --- | --- | --- | --- | --- |
| 1 oz | 1.778 | 88.9 | 4.44 | 13.33 |
| 2 oz | 0.889 | 44.4 | 2.22 | 6.67 |
| 3 oz | 0.593 | 29.6 | 1.48 | 4.44 |

For scale, the six Toshiba TPHR8504PL FETs [49] dissipate 6 × 1.75 W =
10.5 W of conduction loss at this current. At 1 oz the phase pours alone beat
that, which is the standing argument for 2 oz minimum on this board.

**The number that matters for this variant** is the pour-edge-to-terminal
gap. In the baseline that gap is 0.591 in (15 mm) of copper the pours do not
cover, and at 2 oz:

| Gap fill width | R (mΩ) | W all three |
| --- | --- | --- |
| 0.118 in (3.0 mm) | 1.515 | 11.36 |
| 0.197 in (5.0 mm) | 0.909 | 6.82 |
| 0.295 in (7.5 mm) | 0.606 | 4.55 |

A 3.0 mm track across that gap costs more than all six FETs' conduction loss
combined. The tool's own conclusion applies unchanged: **that gap must be
pour, not track, or the terminals must move onto the pour's layer.**

Moving the phase terminals to the `+X` long edge changes the gap geometry
entirely, and moving the pack terminals to the `−X` long edge creates a
second such gap that does not exist today. **`conductor_sizing.py` must be
re-run against the new geometry before any copper is drawn** — task 15.5.

---

## 6. Work breakdown

Mirrored into `TODO.md` §15. Sequencing: 15.1 → 15.2 → 15.3 → 15.4 → 15.5 →
15.7 → 15.6 → 15.8 → 15.9. Task 15.2 gates everything.

### 15.1 Confirm the egress reading

Confirm with the repository owner that "opposite sides" means the two long
edges near one end (§1.1), not the two board faces (§7.1). **Blocking.**
One-line answer; everything downstream depends on it.

*Done when:* the answer is recorded in this document with a date.

### 15.2 Add the egress axis to the decision matrix

The `builds/<voltage>/<amperage>/<variant>/` layout encodes protocol and EMI
tier in the variant string. Wire egress is a new, mechanical axis and belongs
in the workbook like every other axis.

- Add a **Wire Egress** sheet to `docs/decision-matrix.xlsx` with values
  `split-end` (the as-built default) and `single-end` (this variant).
- Re-run `docs/tools/decision_matrix_to_json.py` and verify with `--check`.
- Add the axis to the root `README.md` "Build Options" list.
- Instantiate `builds/6s/50A/CAN_485_faraday_singleend/` per
  `docs/solutions/architecture-patterns/esc-build-instantiation-workflow.md`.

*Done when:* `decision_matrix_to_json.py --check` passes and the new build
folder exists with a `README.md` naming its parent build.

### 15.3 Select the power connectors — now a gate, not a follow-up

`TODO.md` §12.4.l already records that **no connector has been selected** for
`J4` or `J5`; they are bare solder-wire pads. In the baseline that is a
fab-blocking item that can be resolved late. **In this variant it must be
resolved first**, because single-end egress constrains the connector *body
length along the long edge* — the dimension the baseline never had to budget.

- Determine the available edge length per group after §15.4's placement.
- Select real, retained connectors (or ratify solder-wire terminals with a
  specified strain-relief scheme) rated ≥ 50 A continuous at 25.2 V.
- Add a `REFERENCES.md` entry per `AGENTS.md` §2 before the part is used.

*Done when:* both groups have a cited part or a cited termination method, and
the chosen bodies are shown to fit the edge budget.

### 15.4 Re-place: swap the logic cluster and the pack input

- Move `U1`, `U2`, `J1` from Y ≈ 76–86 mm to the Y ≈ 25–45 mm end, on the
  logic side of the isolation barrier.
- Verify the 7.5 mm creepage of [9] Table 6 still holds with `U1` present in
  that region — the `isolation_envelope.py` "widest non-isolated part" input
  of 12.90 mm may no longer be the widest part once the LQFP-64 (10 × 10 mm
  body) is in that band. **Re-run the tool with the new widest part.** If the
  minimum width rises above 32.00 mm, this variant needs a different
  partition, not a wider board.
- Move `J5A`/`J5B` to the `−X` long edge at the Y ≈ 76–86 mm end.
- Move `J4A`/`J4B`/`J4C` to the `+X` long edge at the same end.
- Re-check the lengthened DRV8353 SPI and PWM runs and the lengthened
  current-sense returns against the DRV8353S datasheet's layout guidance.

*Done when:* placement is complete, `isolation_envelope.py` has been re-run
with the correct widest part, and courtyard/edge-clearance checks pass.

### 15.5 Re-run conductor sizing against the new geometry

Re-run `docs/tools/conductor_sizing.py` for the new pour-to-terminal gaps on
both edges. Apply its standing conclusion: the gap is pour or the terminals
sit on the pour's layer. Record the resulting copper weight decision.

*Done when:* both gaps have a stated width, a stated dissipation, and a
stated copper weight, with no "TBD".

### 15.6 Common-mode choke on the pack input

New for this variant (§4). Select a part, size it against the pack current
and the switching fundamental, cite it in `REFERENCES.md`, and add it to the
schematic. Mark any performance figure that cannot be traced to a datasheet
as `UNVERIFIED`.

*Done when:* the part is cited, placed, and its insertion loss at the
switching fundamental is quoted from its own datasheet — not estimated.

### 15.7 Split the phase-terminal rule area — with negative controls

The existing rule area spans X 20.8–51.1 mm, Y 76.5–86.5 mm — nearly the full
width. Under this variant it must become two: a `VBATT` area on the `−X`
side and a `PHASE` area on the `+X` side, with a defined gap between them.

**Every new rule gets a negative control before it is trusted.** This repo
has already been bitten: a full day of DRC runs was quoted as evidence that
conductor spacing was enforced while the rules producing that silence had
never executed, hiding 79 real violations (`CLAUDE-MEMORY.md`,
*kicad-dru-silent-failure*). Two failure modes to guard against specifically:

- A multi-line `(condition "...")` silently invalidates the **entire**
  `.kicad_dru` file, every rule in it, with no error and exit 0. Keep every
  condition on one line.
- Clause order in a two-item condition is not commutative. Verify the rule
  fires against a board known to violate it.

*Done when:* each new rule has been *seen* to fire on a deliberately
violating scratch board, and that control procedure is written as a comment
beside the rule.

### 15.8 Thermal re-run

Five terminals at one end changes the board's thermal gradient: the wires are
a conduction path out of the board, and the logic end loses the heat sink it
had. Re-run thermal analysis over the new placement.

*Done when:* junction temperatures for `Q1`–`Q6`, `U5` and `U1` are quoted
for the new layout at the stated ambient, with no "TBD".

### 15.9 Conducted-emissions pre-compliance for this variant

Per §4.3, the baseline result does not transfer. Add this variant explicitly
to the `TODO.md` §7.3 pre-compliance test plan, including the harness dress
specified in §4.2 — the test is only meaningful against a defined harness.

*Done when:* the test plan names this variant and its harness dress.

---

## 7. Alternatives considered and rejected

### 7.1 Opposite faces — pack on F.Cu, phases on B.Cu, same end

Rejected. It is mechanically simpler (no lateral pad relocation, and each
group gets the full 1.260 in / 32.00 mm edge), but:

- It stacks `VBATT` copper directly over `PHASE` copper across the board
  thickness — the highest-dV/dt net over the DC reference, on the smallest
  separation available on the board. That is the opposite of what a Faraday
  tier is for.
- It requires the phase terminals to move to B.Cu, where the gate driver
  `U5` and the isolated transceivers already sit.
- It requires the pocket to provide clearance on both faces, which defeats
  the point of a blind cavity.

**If the owner's intent was in fact opposite faces (§15.1), this rejection is
reopened and §3 through §6 are rewritten.**

### 7.2 Widen the board so five terminals fit across one end

Rejected on arithmetic. Fitting five terminals in one row with buildable
0.20 in (5 mm) gaps needs roughly 29.0 + 6 × 5.0 = 59 mm (2.32 in) of edge —
nearly double the current width. Per
`docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md`,
width on this board trades against length at 3.0×, so this is a very large
area penalty to avoid a placement swap that is otherwise beneficial (§4.1).

### 7.3 Keep the baseline and route the pack wire externally along the board

Rejected. Running a 50 A pack conductor back along the outside of the board
to the phase end puts an unshielded, unsupported high-current conductor
inside the pocket alongside the phases, with no strain relief and no defined
separation — every disadvantage of §4 plus a mechanical failure mode, and
none of the §4.1 improvements.

---

## 8. Open items

| # | Item | Blocking? |
| --- | --- | --- |
| 1 | Egress reading confirmation (§15.1) | **Yes** — gates everything |
| 2 | Connector selection (§15.3), inherited from `TODO.md` §12.4.l | **Yes** for layout |
| 3 | Does `U1` become the "widest non-isolated part" at the logic end? (§15.4) | **Yes** — may invalidate the partition |
| 4 | IPC-2221 conductor spacing — no primary copy, no citation tag issued | No — mechanics governs (§3.1) |
| 5 | Common-mode choke part selection (§15.6) | No |
| 6 | Bulk input capacitance is still generic in the baseline BOM | No — but this variant makes its placement load-bearing (§3.3) |

---

## 9. References used

Cited per `AGENTS.md` §1.2 against `REFERENCES.md`:

- **[9]** Analog Devices ADM2582E/ADM2587E data sheet, Rev. H — p. 5,
  "Insulation and Safety-Related Specifications," Table 6: 7.5 mm minimum
  external clearance and creepage. Used in §2.1 and §15.4. **Verified**
  (local copy `docs/datasheets/analog-devices-adm2582e-adm2587e-datasheet.pdf`).
- **[49]** Toshiba TPHR8504PL MOSFET. Used in §5 for the 6 × 1.75 W
  conduction-loss figure.

Deliberately **not** cited, because no primary copy exists in this repository
and `AGENTS.md` §1.3 forbids asserting it:

- IPC-2221 Table 6-1 conductor spacing (§3.1). See `REFERENCES.md`,
  "Pending Verification — IPC-2152 and IPC-2221". Marked
  `UNVERIFIED — needs primary source (see TODO.md)`.

Repo tools whose output is quoted:

- `docs/tools/isolation_envelope.py` — §2.1, run 2026-08-31.
- `docs/tools/conductor_sizing.py` — §5, run 2026-08-31.

Prior learnings applied:

- `docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md`
  — §2.1, §7.2.
- `docs/solutions/architecture-patterns/esc-build-instantiation-workflow.md`
  — §15.2.
- `CLAUDE-MEMORY.md`, *kicad-dru-silent-failure* — §15.7.
