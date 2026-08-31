# Single-End Wire Egress Variant — design plan

Governed by [`AGENTS.md`](../AGENTS.md). Tracked as `TODO.md` §15.
Decision-matrix axis: **Wire Egress**, value `Same-end, opposite faces`.

**Status: PLAN — not implemented, not vetted for fabrication.** Nothing in
this document has been placed, routed, or DRC-checked. Every quantitative
claim below is either (a) read directly out of the as-built
`builds/6s/50A/CAN_485_faraday/kicad/*.kicad_pcb`, (b) produced by a repo tool
named at the point of use, (c) arithmetic shown in full at the point of use,
or (d) explicitly marked `UNVERIFIED — needs primary source (see TODO.md)`
per `AGENTS.md` §3.

**Authorship.** Drafted by **Claude Opus 5** (Anthropic), 2026-08-31, at the
direction of the repository owner (GitHub: `Stab-Rabbit-coding`). Revised the
same day after the owner confirmed the opposite-**faces** reading. No portion
was authored by another model. Reviewed by: *nobody yet — this plan has not
been through human review.*

**Units.** Human-facing dimensions are imperial-primary with metric in
parentheses, per the project-wide convention. KiCad-native coordinates are
quoted in millimetres exactly as they appear in the board file, because they
are literal file values rather than measurements — converting them would
break traceability back to the `.kicad_pcb`.

---

## 1. The requirement

The ESC is installed in a **pocket** — a blind cavity in a structure — where
all five power conductors must leave through the **same open end**.

**Resolved 2026-08-31 by the repository owner: "opposite sides" means
opposite *faces* — front and back copper — in order to keep separation
between the two conductor groups.** The earlier long-edge reading is
withdrawn; it is retained only as rejected alternative §9.2.

| Conductor | Net | Count | Face |
| --- | --- | --- | --- |
| Motor phases | `PH_A` / `PH_B` / `PH_C` | 3 | **F.Cu** (unchanged) |
| Pack positive | `VM` (VBATT+) | 1 | **B.Cu** |
| Pack return | `GND` (VBATT−) | 1 | **B.Cu** |

§3 derives that face assignment rather than assuming it.

---

## 2. The as-built baseline

Read from
`builds/6s/50A/CAN_485_faraday/kicad/open_secure_esc_6s_50a_can485_faraday.kicad_pcb`
on 2026-08-31.

| Item | Value |
| --- | --- |
| Board outline | 1.260 in × 2.602 in (32.00 mm × 66.10 mm) |
| Outline extents | X 19.95–51.95 mm, Y 19.95–86.05 mm |
| Copper layers | 4 — F.Cu, In1.Cu, In2.Cu, B.Cu |
| Pack terminals `J5A`/`J5B` | Y = 29.00 mm, F.Cu |
| Phase terminals `J4A`/`J4B`/`J4C` | Y = 80.50 mm, F.Cu |
| MCU `U1` (MSPM0G3518-Q1, LQFP-64) | Y = 78.50 mm, **B.Cu** |
| Secure element `U2` (OPTIGA Trust M) | Y = 81.50 mm, **B.Cu** |
| Probe pads `J1` | Y = 81.00 mm, **B.Cu** |
| Gate driver `U5` | Y = 60.00 mm, B.Cu |
| FET bridge `Q1`–`Q6` | Y = 53.50 and 66.00 mm, F.Cu |

### 2.1 Copper pour assignment — the fact that decides this variant

| Layer | Net | Extent |
| --- | --- | --- |
| F.Cu | `PH_A` | X 20.4–28.1, Y 55.2–85.5 mm |
| F.Cu | `PH_B` | X 28.6–43.0, Y 54.5–85.5 mm |
| F.Cu | `PH_C` | X 43.5–51.5, Y 55.2–85.5 mm |
| F.Cu | `VM` | X 20.4–51.5, **Y 20.5–60.3 mm** |
| F.Cu + B.Cu | `GND` | X 20.4–51.4, Y 20.5–85.5 mm |
| **In1.Cu** | **`GND`** | X 20.4–51.4, **Y 20.5–85.5 mm (full board)** |
| In2.Cu | `VM` | X 20.4–51.4, Y 20.5–60.5 mm |
| **In2.Cu** | **`GND`** | X 20.4–51.4, **Y 60.5–85.5 mm** |

At the terminal end (Y > 60.5 mm) **both inner layers are solid GND**. That
is the shield this variant needs, and it already exists. §4 is about
protecting it, not creating it.

### 2.2 There is no stackup — and that is the real gap

The board file contains **no `(stackup ...)` block**. It declares four copper
layers and `(thickness 1.6)` in its `general` block, which is KiCad's default
value, not a recorded design decision. Consequently the repository specifies
**none** of:

- dielectric height between F.Cu and In1.Cu, or between In2.Cu and B.Cu;
- copper weight on any layer (`conductor_sizing.py` prices 1/2/3 oz as
  options; nothing has been chosen);
- laminate relative permittivity or `Tg`;
- surface finish.

Every question in this document about separation, coupling and cost lands on
that gap. **Defining the stackup is task 15.2 and it gates the rest.**

### 2.3 Board width is locked

`docs/tools/isolation_envelope.py`, run 2026-08-31:

```text
creepage required          7.50 mm
isolated pin inset         1.43 mm from the board edge
widest non-isolated part  12.90 mm

MINIMUM BOARD WIDTH:
   12.90 + 2 x (7.5 + 1.43) + 2 x 0.55 = 31.86 mm
```

The 7.5 mm (0.295 in) figure is the ADM2582E/ADM2587E minimum external
clearance and creepage, Table 6 of [9] — a **verified** primary-source value.
The as-built 32.00 mm (1.260 in) clears the 31.86 mm (1.254 in) minimum by
0.14 mm (0.006 in). Width is not a free parameter in this variant.

---

## 3. Deriving the face assignment

Two assignments are possible. The pours in §2.1 decide it.

### 3.1 Phases must stay on F.Cu

All three phase pours are on F.Cu, spanning Y 55.2–85.5 mm — they already
reach the terminal end, and `J4A`/`J4B`/`J4C` at Y = 80.50 mm already sit
directly on them. `conductor_sizing.py`'s standing conclusion is that a
terminal must sit on its own pour or the connecting gap must itself be pour;
a 0.118 in (3.0 mm) track across that gap costs more power than all six FETs'
conduction loss combined (§7).

Moving the phases to B.Cu would take three 50 A terminals off their pour
layer and force a via field through both inner GND planes — perforating the
shield in exactly the window where it is needed. **Rejected.**

### 3.2 Therefore the pack moves to B.Cu

`J5A`/`J5B` move to B.Cu at the terminal end, opposite the phase pads.

- `GND` (VBATT−) is trivial: B.Cu already carries a GND pour there.
- `VM` (VBATT+) is the real work. The VM pour stops at Y 60.3 mm (F.Cu) and
  Y 60.5 mm (In2.Cu). VM must be carried roughly 0.79 in (20 mm) further to
  reach a B.Cu pad at Y ≈ 80 mm, on a face where GND currently pours. B.Cu at
  the terminal end must be re-partitioned into a VM region and a GND region.

### 3.3 What has to move, and what does not

| Item | Baseline | Variant |
| --- | --- | --- |
| `J4A`/`J4B`/`J4C` phases | F.Cu, Y 80.50 | **unchanged** |
| Phase pours `PH_A/B/C` | F.Cu | **unchanged** |
| FET bridge `Q1`–`Q6` | F.Cu | **unchanged** |
| Gate driver `U5` | B.Cu, Y 60.00 | **unchanged** |
| `J5A`/`J5B` pack | F.Cu, Y 29.00 | → **B.Cu, Y ≈ 76–86** |
| `U1` MCU | B.Cu, Y 78.50 | → B.Cu, logic end (Y ≈ 25–45) |
| `U2` secure element | B.Cu, Y 81.50 | → B.Cu, logic end |
| `J1` probe pads | B.Cu, Y 81.00 | → B.Cu, logic end |
| `VM` distribution | ends Y ≈ 60.4 | extended to B.Cu terminal end |
| Terminal-end rule area | all 4 layers | → outer layers only (§4.2) |

This is materially smaller than the long-edge reading would have been: the
entire phase side is untouched. The cost is concentrated in two places — the
`U1`/`U2`/`J1` relocation, and getting VM to the back face.

---

## 4. The shield between front and back copper

This section answers the direct question: *what shielding can or should be
put between the front and back copper?*

### 4.1 The shield already exists

Per §2.1, at the terminal end (Y > 60.5 mm) **In1.Cu is solid GND and In2.Cu
is solid GND**. Two grounded planes lie between the phase pads on F.Cu and
the pack pads on B.Cu. Nothing needs to be added. A grounded plane between
two conductors does not attenuate their mutual field — it **terminates** it:
field lines from the phase pad end on the plane instead of continuing to the
pack pad. The residual is aperture and edge coupling, not bulk coupling.

**So the correct answer to "what shielding should go between the faces" is:
the shielding you already have, kept intact.** The work is protective, not
additive.

### 4.2 It is currently broken — this is the headline finding

The board carries an unnamed rule area:

```text
bbox      x 20.75..51.15 mm,  y 76.50..86.55 mm
layers    "F.Cu" "B.Cu" "In1.Cu" "In2.Cu"
keepout   (tracks allowed) (vias allowed) (pads allowed)
          (copperpour not_allowed) (footprints allowed)
```

It spans **all four copper layers** and forbids copper pour on every one of
them, across X 20.75–51.15 mm of a 19.95–51.95 mm outline — essentially the
full width — for Y 76.50–86.55 mm.

That is the exact window where the two terminal groups would face each other.
**As the board stands, the inner GND planes are cut away precisely where this
variant needs them to shield.** The rule area's evident purpose — keeping
pour off the outer-layer phase terminals — is fully served by scoping it to
F.Cu and B.Cu. Extending it to In1.Cu and In2.Cu buys nothing and removes the
shield.

**Fix:** restrict the rule area to the outer layers and let In1.Cu and In2.Cu
pour solid through the terminal window. This costs nothing and is the single
highest-value change in the whole variant.

### 4.3 Keep phase via transitions out of the window

A via through the inner planes needs an antipad — a hole in the shield. The
phase pads sit on their F.Cu pours and need no layer change, so no phase via
*has* to enter the terminal window. Make that a placement rule: **no phase or
VM via inside X 20.75–51.15, Y 76.50–86.55 mm**, so the shield stays
unperforated where the pads overlap.

### 4.4 Stitch the two planes into one cage

Tie In1.Cu and In2.Cu together with a GND via fence around the terminal
window perimeter so they behave as a single enclosure rather than two
independent sheets.

Stitch pitch is chosen against the highest frequency of interest. In a
laminate of relative permittivity `εr`, the wavelength is
`λ = c / (f · √εr)`. Taking `εr = 4.3` (a **nominal FR-4 value — this
repository has verified no permittivity for its laminate**, so this is marked
`UNVERIFIED — needs primary source (see TODO.md)`), `√4.3 = 2.074`:

| Frequency | λ in laminate | λ/20 stitch pitch |
| --- | --- | --- |
| 100 MHz | 56.9 in (1447 mm) | 2.83 in (72 mm) |
| 500 MHz | 11.4 in (289 mm) | 0.57 in (14 mm) |
| 1 GHz | 5.70 in (145 mm) | 0.28 in (7.2 mm) |

A 0.28 in (7.2 mm) pitch covers to 1 GHz. On a 1.260 in (32.00 mm) wide
window that is roughly five vias per side — trivially achievable. **Stitching
is not the hard part of this variant.** The λ/20 criterion is a common
engineering rule of thumb, not a standards requirement; no standard is cited
for it because none has been read in this repository.

### 4.5 What this shield is *not*

The `Faraday` EMI-hardening tier already carries a candidate board-level
shielding can, the Würth WE-SHC 3671375 [19], sized to cover the gate-drive
and switching-node area. That is a **surface** shield against radiated
emissions from the top of the board. It does not sit between the faces and
does not do this job. The two are complementary, not alternatives — do not
let one be quoted as satisfying the other.

---

## 5. Can the substrate be thickened to improve separation?

It can be thickened, but it is close to the wrong lever, for two reasons.

### 5.1 Thickening scales the wrong term, linearly

Face-to-face pad coupling is a parallel-plate capacitance,
`C = ε₀ · εr · A / h`. With `ε₀ = 8.854 × 10⁻¹² F/m`, `εr = 4.3`
(UNVERIFIED nominal, §4.4), and a pack pad of 7.0 mm diameter
(`A = π · 3.5² = 38.5 mm²`):

| Total thickness `h` | `C` face-to-face, **unshielded** |
| --- | --- |
| 0.063 in (1.6 mm) | 0.92 pF |
| 0.094 in (2.4 mm) | 0.61 pF |
| 0.126 in (3.2 mm) | 0.46 pF |

Doubling the laminate thickness halves the capacitance — one factor of two,
bought with a doubled board thickness. A grounded plane in between removes
the direct path altogether. **The plane is worth far more than the thickness,
and the plane is already paid for.**

### 5.2 The coupling that actually dominates is not face-to-face

The phase pours on F.Cu total at most 1.43 in² (922 mm²) — sum of the three
bounding boxes in §2.1; actual fill is less. Their capacitance to the In1.Cu
GND plane, at dielectric height `h₁`:

| `h₁` (F.Cu → In1.Cu) | `C` phase pours → GND plane |
| --- | --- |
| 0.004 in (0.10 mm) | 351 pF |
| 0.008 in (0.20 mm) | 176 pF |
| 0.014 in (0.36 mm) | 97 pF |
| 0.020 in (0.51 mm) | 69 pF |

At a typical 0.008 in (0.20 mm) prepreg that is **176 pF — roughly 190× the
0.92 pF face-to-face figure.** Displacement current follows `I = C · dV/dt`,
so this is the dominant common-mode injection path on the board, and it is
governed by a dielectric height the stackup has never specified (§2.2).

*Arithmetic illustration only:* at an edge rate of 1 V/ns, 176 pF passes
176 mA while 0.92 pF passes 0.92 mA. **The 1 V/ns figure is not a design
value** — the actual edge rate is set by the DRV8353S `IDRIVE` setting and
the gate resistors, neither of which is specified in this repository. Marked
`UNVERIFIED — needs primary source (see TODO.md)`. The ratio, not the
absolute number, is the point.

### 5.3 Thickening has its own costs

- **Z-height in the pocket.** Thickness is the one dimension a blind cavity
  most directly constrains. Going 0.063 → 0.126 in (1.6 → 3.2 mm) doubles the
  board's contribution to the pocket depth budget.
- **Via aspect ratio.** A 0.3 mm drill gives 5.3:1 at 1.6 mm, 8.0:1 at
  2.4 mm, 10.7:1 at 3.2 mm. Where a fab's plating limit sits is a vendor
  question, not a repository fact — see task 15.9.
- **Thermal.** A thicker laminate raises through-board thermal resistance on
  a design already dissipating 10.5 W in the FETs alone (§7).

**Recommendation: keep 0.063 in (1.6 mm) nominal, and spend the effort on
§4.2 instead.** If the pocket permits and a quote shows it is cheap, a modest
increase to 0.079 in (2.0 mm) is harmless — but it should be justified by
mechanical stiffness or connector retention, not by inter-face separation.

---

## 6. Would a fifth layer be needed?

**No — and five is not the right question.**

### 6.1 Not needed for shielding

Two solid GND planes already lie between the faces at the terminal end
(§2.1). A fifth plane adds nothing that In1.Cu and In2.Cu, poured solid and
stitched, do not already provide.

### 6.2 Five is not a normal fabrication count

Rigid FR-4 multilayers are laminated from double-sided cores bonded with
prepreg, so copper counts come in even numbers. A five-copper-layer order is
normally built as six with one layer unused, and priced as six. The practical
choice is therefore **4 versus 6**. This is stated as general fabrication
practice; **it must be confirmed with the chosen fab** (task 15.9) rather
than treated as a repository fact.

### 6.3 If six layers are ever justified, it will be for copper, not shielding

The genuine argument for six is cross-section, not isolation. This board
carries 50 A, and `conductor_sizing.py` (§7) shows 1 oz copper on the phase
pours alone dissipates 13.33 W — more than the six FETs' 10.5 W conduction
loss. Extra layers give extra parallel pour area. That is a real trade, but
it belongs to the copper-weight decision in task 15.2 and should be settled
by comparing **6 layers at 1 oz against 4 layers at 2 oz**, which are
different points on a cost curve, not by the shielding question.

---

## 7. Copper sizing

`docs/tools/conductor_sizing.py`, run 2026-08-31. Its own header states it is
a derivation from material constants and **not** an IPC-2152 result — that
distinction is preserved here.

Phase pour, 0.295 in × 0.866 in (7.5 mm × 22.0 mm), at 50 A:

| Copper weight | R (mΩ) | Drop (mV) | W per phase | W all three |
| --- | --- | --- | --- | --- |
| 1 oz | 1.778 | 88.9 | 4.44 | 13.33 |
| 2 oz | 0.889 | 44.4 | 2.22 | 6.67 |
| 3 oz | 0.593 | 29.6 | 1.48 | 4.44 |

The six Toshiba TPHR8504PL FETs [49] dissipate 6 × 1.75 W = 10.5 W of
conduction loss at this current. At 1 oz the phase pours alone exceed that —
the standing argument for 2 oz minimum on this board.

Pour-edge-to-terminal gap, 0.591 in (15 mm) in the baseline, at 2 oz:

| Gap fill width | R (mΩ) | W all three |
| --- | --- | --- |
| 0.118 in (3.0 mm) | 1.515 | 11.36 |
| 0.197 in (5.0 mm) | 0.909 | 6.82 |
| 0.295 in (7.5 mm) | 0.606 | 4.55 |

**Variant-specific consequence.** The phase side is unchanged, so its gap is
unchanged. The pack side creates a *new* gap that does not exist today: VM
must reach a B.Cu pad at Y ≈ 80 mm from a pour that currently stops at
Y ≈ 60.4 mm (§3.2). That run must be pour on B.Cu, not track — the table
above is the reason. Re-run the tool against the new geometry before drawing
copper (task 15.5).

---

## 8. Risks this variant creates

**Single-end egress deletes the physical separation between the pack harness
and the phase harness that the split-end baseline got for free.** Inside the
board the inner planes handle it (§4). Outside the board they do not: both
groups leave the pocket in one bundle, coupled along their whole run.

1. A common-mode choke on the pack input becomes **mandatory** for this
   variant where it is optional in the baseline. No part selected — task 15.7.
2. Build instructions must specify harness dress: phases as a twisted
   triplet, pack pair twisted, stated minimum bundle separation.
3. Conducted-emissions pre-compliance (`TODO.md` §7.3) must be run on *this*
   variant. The baseline result does not transfer.

**No claim is made about how much margin is lost.** That requires
measurement; inventing a figure would violate `AGENTS.md` §1.3.

### 8.1 Second-order consequences

| Consequence | Effect | Handled in |
| --- | --- | --- |
| `U1`/`U2`/`J1` leave the terminal end | **Improvement** — logic no longer sits under the phase rule area, and moves to the logic side of the isolation barrier | 15.4 |
| MCU-to-gate-driver distance grows ≈18.5 → ≈31 mm | Longer DRV8353S SPI and 6× PWM runs beside the switching node | 15.4 |
| Current-sense returns lengthen | Analog runs cross more of the board | 15.4 |
| VM must reach B.Cu at the terminal end | New 50 A pour region on a face that is currently all GND | 15.5 |
| VM pour on B.Cu under the phase pours on F.Cu | Acceptable **only** if §4.2 is fixed first; otherwise unshielded | 15.3 |
| Five terminals concentrated at one end | Wires are a heat path out of the board; the gradient concentrates | 15.8 |
| Rule area must be re-scoped and split | New DRC rules, each needing a negative control | 15.3, 15.6 |

---

## 9. Alternatives considered and rejected

### 9.1 Thicken the laminate instead of fixing the shield

Rejected — §5. One factor of two, bought with doubled thickness, against a
grounded plane that removes the path entirely and is already in the stackup.

### 9.2 Same end, both groups on the outer faces, split onto the two long edges

Rejected on arithmetic, and superseded by the owner's 2026-08-31 decision.
Five terminals in one row need 2 × 7.0 mm + 3 × 5.0 mm = 29.0 mm of pad on a
32.00 mm edge, leaving 0.020 in (0.50 mm) per gap once four inter-pad gaps
and two edge margins are taken — not dressable with 6 mm² (≈10 AWG)
conductor, its solder fillet and its strain relief. Widening the board to
suit is priced at 3.0× by
`docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md`.

### 9.3 Phases on B.Cu, pack on F.Cu

Rejected — §3.1. Takes three 50 A terminals off their pour layer and forces a
via field through both inner planes, perforating the shield exactly where it
is needed.

### 9.4 Six layers for isolation

Rejected — §6. Six layers may eventually be justified for copper
cross-section, but not for inter-face shielding, which two existing planes
already provide.

---

## 10. Work breakdown

Mirrored into `TODO.md` §15. Sequencing: 15.1 → 15.2 → 15.3 → 15.4 → 15.5 →
15.6 → 15.7 → 15.8 → 15.9.

**15.1 — Instantiate the build tree.** *(done for the matrix half)* The
**Wire Egress** axis is in `docs/decision-matrix.xlsx` and
`docs/decision-matrix.json` as of 2026-08-31, values `Opposite-end` (default)
and `Same-end, opposite faces`, added by
`docs/tools/add_wire_egress_sheet.py`. Remaining: add the axis to the root
`README.md` build-options list, and instantiate
`builds/6s/50A/CAN_485_faraday_sameend/` per
`docs/solutions/architecture-patterns/esc-build-instantiation-workflow.md`.

**15.2 — Define the stackup. Gates everything downstream.** The board has
none (§2.2). Specify layer count, per-layer copper weight, every dielectric
height, laminate and `εr`, and surface finish, and write them into the
`.kicad_pcb` stackup block. Settle 4 layers at 2 oz against 6 at 1 oz (§6.3).
*Done when:* the stackup block exists and no value in it is "TBD".

**15.3 — Re-scope the terminal-end rule area. Highest value, lowest cost.**
Restrict the X 20.75–51.15, Y 76.50–86.55 mm rule area to F.Cu and B.Cu so
In1.Cu and In2.Cu pour solid through the terminal window (§4.2). Add the
placement rule barring phase and VM vias from that window (§4.3).
*Done when:* both inner planes show continuous fill across the window in the
filled-polygon data, not merely an edited rule area.

**15.4 — Re-place `U1`, `U2`, `J1` to the logic end.** Move all three off
B.Cu Y ≈ 76–86 mm to Y ≈ 25–45 mm. **Re-run `isolation_envelope.py` with the
new widest non-isolated part** — the LQFP-64 (10 × 10 mm body) may displace
the 12.90 mm input and push the minimum width past the as-built 32.00 mm. If
it does, this variant needs a different partition, **not** a wider board.
Re-check the lengthened DRV8353S SPI, PWM and current-sense runs against the
DRV8353S datasheet's layout guidance.

**15.5 — Extend VM to a B.Cu pad at the terminal end.** Re-partition B.Cu
Y > 60.5 mm into VM and GND regions; place `J5A`/`J5B`. Re-run
`conductor_sizing.py` for the new pack-side gap and apply its conclusion —
pour, not track (§7). *Done when:* the gap has a stated width, dissipation
and copper weight, with no "TBD".

**15.6 — Stitch In1.Cu to In2.Cu around the terminal window** at a pitch
justified against a stated highest frequency of interest (§4.4). Every new
DRC rule gets a **negative control** before it is trusted: this repo has
already had a full day of DRC runs quoted as evidence while the rules
producing that silence had never executed, hiding 79 real violations
(`CLAUDE-MEMORY.md`, *kicad-dru-silent-failure*). Keep every `(condition …)`
on one line — a multi-line condition silently invalidates the entire
`.kicad_dru` with exit 0 — and verify clause order, which is not commutative.
*Done when:* each rule has been *seen* to fire on a deliberately violating
scratch board, with the control procedure written beside it.

**15.7 — Common-mode choke on the pack input.** New for this variant (§8).
Select, size against pack current and switching fundamental, cite in
`REFERENCES.md` per `AGENTS.md` §2. *Done when:* insertion loss at the
switching fundamental is quoted from the part's own datasheet, not estimated.

**15.8 — Thermal re-run** over the new placement (§8.1). *Done when:*
junction temperatures for `Q1`–`Q6`, `U5`, `U1` are quoted at a stated
ambient, with no "TBD".

**15.9 — Obtain a fabrication quote** covering: 4 vs 6 layers; 1 oz vs 2 oz
outer and inner; 1.6 vs 2.0 vs 3.2 mm thickness; and the maximum via aspect
ratio accepted at each thickness (§5.3, §6.2). **No price appears anywhere in
this repository until it comes from a vendor quotation** — `AGENTS.md` §1.3.
*Done when:* a dated quote is recorded and the §5/§6 recommendations are
either confirmed or revised against it.

**15.10 — Conducted-emissions pre-compliance for this variant.** Add it and
its harness dress to the `TODO.md` §7.3 test plan (§8). *Done when:* the test
plan names this variant and its harness dress.

---

## 11. Open items

| # | Item | Blocking? |
| --- | --- | --- |
| 1 | Stackup undefined — no dielectric height, copper weight or `εr` anywhere (§2.2) | **Yes** — gates 15.3–15.9 |
| 2 | Rule area cuts the inner planes in the terminal window (§4.2) | **Yes** — the variant does not work until fixed |
| 3 | Does `U1` become the "widest non-isolated part" at the logic end? (15.4) | **Yes** — may invalidate the partition |
| 4 | Connector selection, inherited from `TODO.md` §12.4.l | **Yes** for layout |
| 5 | Laminate `εr` — nominal 4.3 used, none verified (§4.4, §5) | No — ratios hold regardless |
| 6 | Switching edge rate unspecified — `IDRIVE` and gate resistors not set (§5.2) | No — but 15.7 needs it |
| 7 | Fabrication cost structure — no quote obtained (15.9) | No |
| 8 | Bulk input capacitance still generic in the baseline BOM | No |

---

## 12. References used

Cited per `AGENTS.md` §1.2 against `REFERENCES.md`:

- **[9]** Analog Devices ADM2582E/ADM2587E data sheet, Rev. H — p. 5,
  "Insulation and Safety-Related Specifications," Table 6: 7.5 mm minimum
  external clearance and creepage. Used in §2.3 and 15.4. **Verified**
  (local copy `docs/datasheets/analog-devices-adm2582e-adm2587e-datasheet.pdf`).
- **[19]** Würth Elektronik WE-SHC 3671375 shielding cabinet — candidate for
  the `Faraday` EMI tier. Referenced in §4.5 to distinguish a surface shield
  from the inter-face shield this variant needs. Candidate status unchanged.
- **[49]** Toshiba TPHR8504PL MOSFET. Used in §7 for the 6 × 1.75 W
  conduction-loss figure.

Deliberately **not** cited, because no primary copy exists in this repository
and `AGENTS.md` §1.3 forbids asserting it:

- IPC-2221 Table 6-1 conductor spacing. See `REFERENCES.md`, "Pending
  Verification — IPC-2152 and IPC-2221".
- Any laminate permittivity, fabrication cost, fab via-aspect-ratio limit, or
  switching edge rate. All marked `UNVERIFIED` at the point of use.
- The λ/20 stitch-pitch criterion (§4.4) — a common engineering rule of
  thumb, presented as such; no standard has been read for it.

Repo tools whose output is quoted:

- `docs/tools/isolation_envelope.py` — §2.3, run 2026-08-31.
- `docs/tools/conductor_sizing.py` — §7, run 2026-08-31.
- `docs/tools/add_wire_egress_sheet.py` — 15.1, run 2026-08-31.

Prior learnings applied:

- `docs/solutions/architecture-patterns/isolation-geometry-sets-board-aspect.md`
  — §2.3, §9.2.
- `docs/solutions/architecture-patterns/esc-build-instantiation-workflow.md`
  — 15.1.
- `CLAUDE-MEMORY.md`, *kicad-dru-silent-failure* — 15.6.
