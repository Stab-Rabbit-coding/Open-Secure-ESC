# Design Decision: Waterproofing a Faceted / Hinged ESC, Without Defeating Its Cooling Path

Status: DRAFT (authoring complete, several items open — see "Open Items")
Applies to: Form Factor = Faceted rigid-flex, and any variant with a hinged
or otherwise serviceable access cover. The Flat/single-PCB baseline is
covered only for contrast (see §1).
Governing rules: AGENTS.md §1–§3 — every technical claim that requires a
primary source is verified and added to REFERENCES.md; anything not yet
verified is marked `UNVERIFIED — needs primary source` per §3, not guessed.

Supersedes the placeholder reference in README.md ("Ingress & environmental
protection") and TODO.md §2.6, both of which pointed at
`docs/design-submersible-cooling.md` — a file that was never authored. This
document replaces that pointer and that name: "submersible" describes only
one of the two variants this decision produces (§5), and is the wrong frame
for the actual threat model on most builds (§2).

## 1. Why the industry-standard answer stops working here

For a single flat rigid PCB, the standard low-cost ESC waterproofing is heat
shrink tube: slide a tube over the populated board, shrink it down, and the
board's two flat faces plus its perimeter are covered in one operation, with
wire leads exiting through the tube ends (which then usually get their own
smaller boots or a bead of hot-melt). This works because a flat rectangular
board is topologically a cylinder's worth of surface — one tube, one shrink
pass, done.

Two things this repository's Faceted rigid-flex form factor breaks, and one
thing any hinged-access build breaks, regardless of board form factor:

1. **A faceted board is not a single flat plane.** `docs/tools/strip_width.py`
   exists precisely because this form factor is a board folded into chords of
   a curved bore (nacelle, boom, tube). A shrink tube conforms to a
   constant-radius surface; it does not conform to a polygon of flat facets
   with reflex fold lines between them without wrinkling, tenting away from
   the board at each fold, or splitting at the fold under shrink tension. The
   folds are exactly where a wrap-based seal is weakest and least inspectable.
2. **A folded board has re-entrant geometry a tube cannot reach uniformly.**
   Depending on fold angle, the inside of a fold is compressed while the
   outside is stretched; component height differences between panels (e.g. a
   shunt on one facet, a shorter passive on the neighboring one) create air
   gaps under the tube that are invisible until the board is opened again —
   which leads to point 3.
3. **A hinged access cover is a standing requirement for repeated service,
   and heat shrink (like potting, §4.3) is a one-shot process.** Serenity-UAV's
   nacelle ESC bays are explicitly hinged with flush access covers for
   service access (sibling repository, `Serenity-UAV` — see §6). Any
   waterproofing method that must be destroyed to inspect or replace the
   board is incompatible with a design that already committed to opening
   that bay again.

**Consequence:** waterproofing this board is not "pick a better tube." The
sealing boundary has to move from the board's own surface to the
bay/cover assembly that already exists for mechanical access — i.e., the
ESC becomes a component *inside* an enclosure, not its own enclosure. That
reframing is what the rest of this document works out, including the point
where it collides with the cooling analysis already done in the sibling
repository (§6).

## 2. What "splash or spray" actually requires — and what it doesn't

The README/TODO currently ask for one variant to cover "IP ratings up to
IP68 and NEMA equivalents up to NEMA 6P" in the same breath as "Faceted
rigid-flex." IEC 60529 [56] does not treat these as points on one ladder;
Table 3's own clause 6 note separates the **jet family** (numerals 5/6) from
the **immersion family** (numerals 7/8) — a product is rated for one, the
other, or both explicitly (e.g. "IPX6/IPX7"), never implied by the higher
number alone [56].

| Numeral | IEC 60529 [56] definition (Table 3) | Test | Threat it matches |
|---|---|---|---|
| IPX4 | "Water splashed against the enclosure from any direction shall have no harmful effects" | Clause 14.2.4 | Rotor wash, rain, road spray on a ground vehicle, rotor-downwash spray on an aircraft |
| IPX6 | "Water projected in powerful jets ... from any direction shall have no harmful effects" | Clause 14.2.6 | Pressure-washing, heavy following-sea spray |
| IPX7 | "Ingress of water in quantities causing harmful effects shall not be possible ... temporarily immersed ... under standardized conditions of pressure and time" | Clause 14.2.7 | A ground vehicle fording a stream crossing |
| IPX8 | As IPX7 but "conditions ... agreed between manufacturer and user ... more severe than for numeral 7" | Clause 14.2.8 | Sustained submersion (the stated USV/marine case) |

**The aircraft and most ground-vehicle nacelle/bay case described in this
task is IPX4–IPX6: splash and spray, not immersion.** That distinction
matters enormously for this design, because it is the difference between "the
enclosure can still breathe and be actively air-cooled" (IPX4/6 — water is
excluded from a boundary that air still crosses, §4) and "the enclosure is a
closed pressure vessel with no air exchange at all" (IPX7/8 — §5.2). Treating
every build as if it must hit IPX8 forecloses air-cooling on builds that never
needed to give it up.

**Design rule adopted here:** resolve Ingress Protection and Form Factor as
one joint axis in the decision matrix, the same way
`docs/solutions/architecture-patterns/esc-build-instantiation-workflow.md`
already requires for Motor × Shaft-Sensor. A "Faceted rigid-flex, hinged
access, IPX4–6" build and a "Flat, sealed, IPX7–8" build are two different
mechanical designs sharing a schematic, not one design with a rating dial.
§5 below makes that split explicit as two named variants.

## 3. The layered boundary: separate "keeps water out" from "keeps air moving"

The mistake this section exists to head off: treating the bay's hinged cover
as if gasketing it shut is the whole answer. A fully gasket-sealed bay is
airtight to the level the gasket achieves, which directly removes the
aspirated-cooling air path the sibling repository's thermal analysis found
to be the only cooling path that actually works for this geometry (§6). The
fix is to put the ingress boundary and the airflow boundary at *different*
places, each doing one job:

```
 outside air/spray                                          duct interior
        |                                                          |
        v                                                          v
  [ baffled / labyrinth louvre, NOT gasketed ]  <-- IPX4/6 by GEOMETRY, not seal
        |
        v
  [ bay cavity — open to air, NOT a sealed volume ]
        |
        v
  [ conformally coated board, IPC-CC-830C [57] ]  <-- IPX4-equivalent AT THE BOARD
        |
        v
  [ drainage: low-point weep to outside, below the board ]
        |
        v
  [ wire egress: sealed gland / potted boot ]      <-- the one true gasketed joint
```

### 3.1 Board level — conformal coating, not a wrap

IPC-CC-830C [57] qualifies conformal coatings by chemistry family (Type AR
acrylic, ER epoxy, SR silicone, UR polyurethane, XY Parylene, UT ultra-thin,
SC styrene block co-polymer) and includes Flexibility (§3.5.5) and Thermal
Shock (§3.7.2) as qualification tests [57] — this is the property that
matters here: a coating has to survive the facet fold lines flexing (during
assembly, and on any variant where the "rigid-flex" is not fully rigidized
after forming) without cracking, which a dip-and-cure rigid coating on a flat
board is never asked to do. **Which coating type is selected, and its
qualified flex/thermal-shock performance, is `UNVERIFIED — needs primary
source`** (TODO §2.6) — [57]'s Table of Contents confirms the test exists;
the pass/fail numbers are on pages of the standard not held locally (see
[57]'s caveat).

This gets the board itself to roughly IPX4-equivalent protection (moisture,
condensation, incidental splash reaching the board through the vent path)
without touching serviceability — a coated board un-hinges, gets inspected,
and re-installs exactly as an uncoated one would; nothing about coating is a
one-shot process the way potting is.

### 3.2 Enclosure level — baffle the vent, don't gasket it

An IPX4 test sprays water "from any direction" [56]; it does not force water
through a right-angle turn against its own momentum and gravity. The louvre
already exists in the sibling repository's nacelle cover for the aspirated
cooling path (`tools/nacelle_esc_thermal.py`'s `ESC_LOUVRE_N/W/L` and the FOD
screen sweep, §6) — the fix here is geometric, not material: offset the
louvre's outer opening from its inner (bay-side) opening by a baffle rib, so
a straight line from outside to the board interior does not exist. This is
the same principle NEMA 3R enclosures and automotive engine-bay louvres use
to breathe while shedding driving rain; it is a judgment call recorded as
such (AGENTS.md §4), not a cited numeric standard, because no primary source
in this repository's catalog gives a baffle-geometry IPX4 pass criterion —
the criterion is the IEC 60529 [56] test itself, applied to the finished
geometry, not derived analytically here.

**The FOD mesh already in `tools/nacelle_esc_thermal.py`'s `SCREENS` table
does not by itself buy splash resistance.** Its apertures (0.4–1.2 mm) are
sized against particle ingress, and a woven screen at that aperture does not
exclude liquid water — water at that pore scale is not held back by surface
tension the way it is in an ePTFE membrane (§3.3). Do not treat "has a FOD
screen" as "is splash-rated" — they are two different filters passing through
the same opening, and only the baffle geometry (this section) or a membrane
(§3.3) does the water job.

### 3.3 Pressure equalization, not cooling flow

A gasketed joint anywhere in the design (the wire-egress gland, §3.4, or a
hinge seal if the cover itself is gasketed on the sealed/immersion variant,
§5.2) will pressure-cycle with altitude and with the ESC's own thermal
cycling. A joint that is pushed outward on the way up and pulled inward on
the way down draws water in past a marginal seal on the down-stroke even
when the seal excludes it on a static soak test. GORE Protective Vents [58]
and similar ePTFE-membrane vents exist to equalize that pressure through a
membrane that "allows air to pass through while preventing the ingress of
liquids and particles" [58] — add one wherever a gasketed volume exists on
this design (i.e., on the §5.2 sealed variant; the §5.1 vented variant has no
sealed volume to equalize).

**This is not a cooling path.** [58]'s own highest-airflow model is quoted at
7600 ml/min at 70 mbar — call it under 0.01 g/s of air — against the
aspirated circuit's mass flow of tens of grams per second at throttle in the
sibling repository's analysis (`aspirated_flow()` in
`tools/nacelle_esc_thermal.py`, §6). A pressure-equalization vent is sized to
prevent seal damage over an altitude/thermal cycle, not to carry heat. Do not
size one against the thermal budget; size it against the enclosed volume and
expected pressure-altitude excursion (`UNVERIFIED — needs primary source`,
no sizing method for this is catalogued yet — TODO §2.6).

### 3.4 Wire egress — the actual weak point

Every option above still has to get phase and pack conductors, and any sense
lines, out of the bay. This is the one joint on the §5.1 (vented) variant
that legitimately needs a gasketed seal, because it is the one boundary
crossing that is not also an airflow path. No connector series is currently
selected in this repository with a stated IP rating (`grep` of README.md and
TODO.md turns up none), so this is tracked as an open item rather than a
part number invented here: select a connector or cable-gland series with a
manufacturer-stated IP rating at the *mated, installed* condition (not the
unmated pin), and hold its datasheet locally per AGENTS.md §1.3 before it
enters a BOM. Until then, a drip loop — routing the cable to a local low
point below the gland before it rises to the connector, standard practice in
marine and aviation wiring so that water running down the cable drips off
before it reaches the seal — is a no-cost, zero-BOM-impact mitigation worth
building into the harness routing regardless of which connector is chosen.

### 3.5 Drainage — assume the boundary above will someday be beaten

Every layer above reduces the rate of ingress; none of them, on the vented
variant, claims to be absolute (that is what distinguishes IPX4/6 from
IPX7/8, §2). The bay floor should have a low point below the board with a
path to the outside — even a single small weep hole works, since the goal is
to let the small amount of water that gets past the baffle (§3.2) leave
before it pools against the coated board (§3.1) rather than to keep the bay
bone-dry. This costs nothing but placement discipline in the CF-PETG bay
geometry and should be checked the same way `nacelle_esc_thermal.py` checks
the cooling path: as a real geometric flow path, not "a hole exists."

## 4. Thermal and waterproofing are not separable on this geometry

This is the section that makes the whole document necessary rather than a
restatement of "use a gasket": the sibling repository's
`tools/nacelle_esc_thermal.py` already established, for the closely related
Serenity-UAV nacelle ESC bay, that:

- A sealed bay relying on conduction through CF-PETG walls fails at every
  plausible thermal conductivity in the material's plausible band (`Option A`
  in that tool) — the pod's own plastic is not a working heat path.
- An aluminum conduction path to the stator sleeve heat sink works, at a
  measured mass cost (`Option B`), but requires the sink to be a fixed metal
  part reachable by a solid conduction chain — i.e., no hinge or air gap in
  that path.
- The only path with margin at forced-air hover current is **aspirated
  cooling**: air drawn from the duct's inter-stage suction, through the bay,
  carrying the board's heat out as it goes (`Option C`).

Option C is only available on a bay that stays *open to airflow*. That is
the vented variant this document has been building toward in §3: keep the
ingress boundary at the board (coating) and the baffle (geometry), and keep
the airflow boundary open, rather than collapsing both boundaries onto one
gasketed lid. **A gasketed, gore-vented sealed bay — the obvious-looking
"just make it an IP67 box" answer — would reproduce Option A's failure by
removing the only cooling path that passes**, on any build dissipating
ESC-class power without an independent metal path to a heat sink.

## 5. Two variants, not one dial

Per the joint-axis rule in §2, this document's answer to "how do we
waterproof and cool a faceted, hinged ESC" is: it depends which of two
mechanical designs the build actually needs, and both should exist as named
Form-Factor × Ingress combinations in `docs/decision-matrix.xlsx` rather than
one "IP rating" field applied uniformly.

### 5.1 Splash/spray, air-cooled (target IPX4–IPX6)

- Faceted rigid-flex board, IPC-CC-830C [57]-qualified flexible coating.
- Bay stays open to air; access cover hinges normally, no compression gasket
  on the hinge or the vent.
- Baffled/labyrinth louvre geometry at every opening (§3.2); FOD mesh stays,
  understood as a particle filter, not a water seal.
- Gasketed wire-egress gland only (§3.4), with a drip loop.
- Bay-floor drainage to a low-point weep (§3.5).
- Cooling: the sibling repository's aspirated circuit (`Option C`), unchanged
  by anything in this document — this variant is compatible with that
  analysis by construction, since nothing here closes the air path.
- This is the variant that matches the Serenity-UAV nacelle case as
  described (§6): an aircraft ESC subject to rotor-wash spray, not
  submersion.

### 5.2 Sealed / immersion (target IPX7–IPX8)

- Flat or unfolded board (a folded/faceted board complicates a compression
  gasket's sealing plane — this variant is not the faceted one), potted or
  fully gasketed enclosure, no air exchange with the outside.
- Pressure-equalization vent [58] required (§3.3) to protect the seal over
  thermal/altitude cycling, sized against volume and excursion, not thermal
  load.
- Cooling: no aspirated path is available (there is no outside air to draw
  on), so this variant must use the sibling repository's `Option B`-style
  answer — a solid metal conduction path from the board to an external heat
  sink or the vehicle's own structure — sized the same way `Option B` was
  sized there (thermal resistance chain, `k`-swept where the conductor's
  conductivity is not a verified figure). This is the USV/marine submersible
  case the README's "up to IP68" line was actually describing.
- Serviceability is reduced by design (potting) or preserved only if the
  seal is a re-usable compression gasket rather than a pour; which of those
  two this variant uses is `UNVERIFIED — needs primary source` / an open
  design decision (TODO §2.6), since it trades service access against seal
  margin and no requirement in this repository currently forces one answer.

## 6. Relationship to the Serenity-UAV nacelle analysis

`tools/nacelle_esc_thermal.py` in the sibling repository **Serenity-UAV**
(not part of this repository; referenced descriptively, not by in-repo path)
performs the thermal-only half of this problem for that project's specific
nacelle geometry: two Open-Secure-ESC boards per nacelle, in bays cut into a
CF-PETG pod's annulus, with hinged access covers and louvred FOD screens.
Its conclusions (Options A/B/C, and the duct-pressure argument for why a
"bleed" circuit flows backwards while an "aspirated" one works) are treated
here as an already-verified input, not re-derived — this document's
contribution is the ingress-protection layer that has to coexist with that
cooling design (§4) without undoing it, plus the general (not
Serenity-UAV-specific) two-variant framework of §5 for any other host using
a faceted or hinged Open-Secure-ESC build.

## Open Items (tracked in TODO.md §2.6)

- [ ] Select a conformal coating meeting IPC-CC-830C [57] with its
      Flexibility (§3.5.5) and Thermal Shock (§3.7.2) qualification data
      obtained from a primary source (vendor datasheet naming IPC-CC-830C
      compliance), not assumed from the coating "type" alone.
- [ ] Select a wire-egress connector/gland series with a manufacturer-stated
      IP rating at the mated condition; hold its datasheet locally.
- [ ] Size the pressure-equalization vent (§3.3) against bay free volume and
      the design altitude/thermal excursion — no sizing method is catalogued
      yet.
- [ ] Verify whether IEC 60529 Amendments 1/2 changed the IPX4/6/7/8 clause
      numbers or definitions relative to the 2001 text held locally [56].
- [ ] Confirm, for the §5.2 sealed variant, whether service access is
      required (compression gasket) or may be sacrificed (potting) — this is
      a requirements decision, not an engineering one, and is currently open.
- [ ] If a rigid-flex bend radius or flex-endurance standard is ever needed
      for the Faceted form factor's fold lines, note that
      `docs/tools/strip_width.py` already flags that none is catalogued in
      REFERENCES.md — do not fabricate one; add it via the normal citation
      workflow (AGENTS.md §2) when actually needed.

## Related

- `AGENTS.md` §1.3 (no fabrication), §3 (marking unverified content), §4
  (design-decision rationale)
- `REFERENCES.md` [56]–[58]
- `docs/tools/strip_width.py` — the faceted board's own geometry constraint,
  and its existing "no flex/rigid-flex standard catalogued" flag
- `docs/solutions/architecture-patterns/esc-build-instantiation-workflow.md`
  — the joint-axis-resolution pattern this document follows for Form Factor
  × Ingress Protection
- `TODO.md` §2.6 — the open items this document feeds
- Serenity-UAV (sibling repository) `tools/nacelle_esc_thermal.py` — the
  cooling-path analysis this document's §4 builds on without re-deriving
