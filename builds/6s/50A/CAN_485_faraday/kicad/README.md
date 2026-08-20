# kicad/ — 6S / 50A / CAN-FD+RS-485 / Faraday

Governed by `AGENTS.md`. Open items are tracked in the repo-root `TODO.md`
§12.4; this file describes what the two design files currently contain.

## Status

**Schematic: ERC-clean (0 errors). PCB: placement and pour work advanced
2026-08-19/20; the board is deliberately committed UNROUTED.** The previous
route was invalidated by the shield-ring part moves and was cleared rather than
committed, because a stale route shorts nets. Regenerate with
`tools/autoroute.py` then `tools/stitch_planes.py`.

Current DRC: **20 violations — 11 `silk_over_copper`, 7 `silk_overlap`,
2 `isolated_copper`. Zero shorts, zero clearance, zero isolation violations.**
151 unconnected (i.e. unrouted). Not fabrication-ready.

| | State |
| --- | --- |
| Schematic | 50 parts, annotated, **0 ERC errors** (`endpoint_off_grid` + `global_label_dangling` warnings remain — see below) |
| PCB | **32.0 × 66.1 mm**, double-sided, 65 footprints, 75 nets, 4 layers, planes poured and stitched, isolation rule area (**stranded — `TODO.md` 12.5.z**). **0 courtyard overlaps, 0 clearance errors, 0 hole-clearance errors** |
| Routing | **Cleared 2026-08-20** — see "Routing" below. Regenerate with `tools/autoroute.py`, then `tools/stitch_planes.py` |
| Gerbers | Not generated. See "Before you fabricate". |

### Placement history

The respin was drawn for a 30 × 60 mm envelope and `tools/build_pcb.py` still
writes that placement. The repo owner then hand-placed the board, after which
it narrowed to **25.4 × 60.1 mm (1 inch wide)** without shrinking any phase
pour — the inch came from dead margin between the FET columns, not from
copper. See the commit "Narrow the board to 25.4 mm" for the full accounting.

`BT1`–`BT6` (the 21700 cells) and `SH2` (the shield cover) are in the BOM but
marked *exclude from board*.

### Respin BOM changes (2026-08-15/16)

| Was | Now | Why |
| --- | --- | --- |
| IRFB4110PBF, TO-220AB THT | **TPHR8504PL**, 2-5W1A SOP Advance(N) | 5.7× lower conduction loss; SMD enables double-sided. Voltage margin drops 3.97× → 1.59× — bound the overshoot before fab |
| WE-SHC 3670375/3671375 | **3670209/3671209** | 812 mm² saved |
| 1 mΩ shunts | **0.5 mΩ** | 2.5 W → 1.25 W against a 3.0 W part |
| C1 10 mm radial | **1210 SMD** | Envelope; holds far less bulk — see its Note |
| J4 3-pin, J5 2-pin | **J4A/B/C, J5A/B** | Terminals fit across the 30 mm width |
| J1–J4 THT headers | **SMD solder pads** | A THT part blocks both sides; 9 of them cost 964 mm² of a 3600 mm² budget |

## Files

| File | What it is |
| --- | --- |
| `*.kicad_sch` | Single sheet, A0. Title block company **Griffing Technology LLC**. |
| `*.kicad_pcb` | 25.4 × 60.1 mm, 4 layers, double-sided, rounded corners. |
| `*.kicad_pro` | Project settings. **Net classes live here**, not in the board. |
| `sym-lib-table`, `fp-lib-table` | Project-relative tables pointing at the shared `symbols/` library. |
| `tools/` | Generators. Re-run these rather than hand-editing the generated files. |

## The board

**4 layers.** Two layers cannot carry this build's currents, and the ground
planes are also the layout half of the Faraday EMI tier — a shield can only
helps if the return currents underneath it are not already radiating.

```text
F.Cu    components, signal routing, per-phase pours over each half-bridge
In1.Cu  GND plane, solid, full board
In2.Cu  VM plane over the power stage, GND under the control section
B.Cu    signal routing, GND pour
```

**Placement** follows the signal flow, and the power stage follows
REFERENCES.md [21] §11.1 "Layout Guidelines" — bulk capacitance positioned to
minimise the high-current loop through the external MOSFETs, and minimised
high-side and low-side gate loops:

- **Top band** — pack input (`J5`), bulk cap (`C1`), the three half-bridges
  (`Q1`/`Q2`, `Q3`/`Q4`, `Q5`/`Q6`), the three low-side shunts (`R1`–`R3`),
  and the phase terminal (`J4`) at the right edge.
- **Below the shunts** — the three INA240 current-sense amplifiers
  (`U6`–`U8`), each directly under its own shunt.
- **Middle** — `U5` (gate driver) and its five support capacitors, all
  *inside* the WE-SHC shield frame (`SH1`). The frame's courtyard is an
  annulus, so enclosing parts is not a DRC error.
- **Bottom left** — `U1` (MCU), `U2` (OPTIGA Trust M), decoupling, pull-ups,
  and `J1` (SWD), furthest from the switching node.
- **Bottom right** — the two isolated transceivers (`U3` CAN-FD, `U4`
  RS-485), each rotated so its **isolated pin row faces the board edge**, with
  `J2`/`J3` beyond them. A **copper keepout** removes every plane and pour
  from that band: without it the GND plane runs straight under the isolation
  barrier, which defeats the isolator.

## What the 2026-08-15 pass fixed

This folder previously held a schematic with no reference designators and a
PCB where, in the words of this file's earlier revision, "every PCB pad is
net-less (`net 0`); footprints are placed for board-planning legibility only."
Four of the fixes were real electrical defects, not tidying:

1. **The gate driver's SPI read path had no pull-up.** REFERENCES.md [21]
   lists `SDO` (pin 27) as type **OD** and states "This pin requires an
   external pullup resistor." There was none, so no SPI register read from the
   DRV8353S could have worked. `R14` (10 kΩ to 3V3) added, mirroring `R11` on
   `nFAULT`, the other open-drain pin.
2. **The board had no battery input.** `VM` reached `C1`, `C6`, `R8`, `U5` and
   three MOSFET drains — and no connector. The previous PCB had a `J5`
   footprint with *no schematic counterpart*, i.e. two netless pads. `J5` is
   now a real schematic part on `VM`/`GND`.
3. **Four isolated-side power flags never reached their rails.** `#FLG04`–
   `#FLG07` were wired with long L-routes whose vertical legs stopped at the
   right Y but at x = 381.5 while the target pins sit at x = 380.01 — so not
   one of the four connected. That was 4 `power_pin_not_driven` errors on the
   transceivers' isolated supplies.
4. **The gate driver's exposed thermal pad had no electrical existence.** The
   symbol had no pin 41, so the footprint's thermal pad would have imported
   with no net — an isolated copper island directly under the power stage.

Also: all 57 symbols annotated; the 8 `PWR_FLAG`s made virtual (they had been
ordinary in-BOM parts); `U5`'s footprint authored from TI's own land pattern;
`SH1`'s authored from Würth's; the phase connector moved off a 2.54 mm pin
header; and the 32 `lib_symbol_mismatch` warnings cleared.

## Warnings that remain, and why

**350 × `endpoint_off_grid` (schematic).** `tools/genlib.py` lays the sheet out
on a 10 mm grid, which is not a multiple of KiCad's 1.27 mm connection grid.
Nothing is electrically wrong — KiCad connects by exact coordinate match — but
hand-editing the sheet in Eeschema is awkward because a wire drawn on-grid
will not land on a pin.

**Do not "fix" this with a coordinate snap.** It was tried and reverted:
`genlib.py` separates parallel routes by 0.01–0.02 mm lane offsets, and
snapping to 1.27 mm merges them. The attempt shorted VM to GND, merged all six
PWM lines into one net, shorted `CPH` to `CPL` across the charge-pump
capacitor, and collapsed 73 nets to 63. `tools/snap_to_grid.py` now refuses to
run without `--force` and documents the whole result. A real fix means
re-laying out the drawing with ≥ 1.27 mm lane spacing.

**2 × `global_label_dangling`** on `CAN_VISOOUT` and `RS485_VISOOUT`. These are
deliberate: the transceivers' isolated-supply sourcing depends on the
still-open ADM3055E-vs-ADM3057E and ADM2582E-vs-ADM2587E variant choices
(see `../README.md`), so the nets are labelled and left open rather than
resolved by the layout.

**`silk_over_copper` and `starved_thermal` (PCB).** Cosmetic and
fab-preference respectively; neither is electrical.

## Placement guide (25.4 × 60.1 mm, hand-placed)

The board is placed. This section is the record of **why** it is placed the
way it is, so a later edit does not undo a constraint by accident.

**Re-running `tools/build_pcb.py` discards the hand placement.** It rebuilds
the board from the netlist every time, from a `PLACEMENT` table that still
describes the old 30 × 60 layout. Do not run it against the committed board
without folding the current positions back into it first.

### RESOLVED — the `U5` thermal-via short

Earlier revisions of this file recorded a **verified GND-to-VM short**:
`U5`'s 12 GND thermal vias landed inside `Q3`'s `VM`, `PH_B` and gate pads.
The hand placement cleared it. Re-verified against the board 2026-08-16 —
**no `U5` thermal via intersects any pad of any other footprint**, and DRC
reports 0 clearance and 0 hole-clearance errors.

This remains the trap to re-check after **any** move of `U5` or of a `Q`.
`U5` sits on the bottom directly beneath the top-side FETs, so its via field
is always one small move away from a FET drain pad. [21]'s RTA0040B sheet
note 5 makes the vias optional ("vias are optional depending on application"),
so deleting them is a legitimate fallback if a future move re-creates the
conflict.

### Copper weight: 2 oz outer minimum, decided by calculation

`docs/tools/conductor_sizing.py` derives this from copper's resistivity --
run it, it prints the table. At 50 A through a 7.5 x 22 mm phase pour:

| Copper | R per phase | Drop | Dissipation, all 3 phases |
| --- | --- | --- | --- |
| 1 oz | 1.78 mΩ | 89 mV | **13.3 W** |
| 2 oz | 0.89 mΩ | 44 mV | 6.7 W |
| 3 oz | 0.59 mΩ | 30 mV | 4.4 W |

The six TPHR8504PL FETs dissipate 10.5 W of conduction loss between them. **At
1 oz the phase pours alone dissipate more than the FETs do** -- the copper
becomes the dominant heat source, which is indefensible on a board whose
reference design [47] already measures 103 °C at this current. 2 oz outer is
the floor; 2 oz inner as well if the budget allows, since In1/In2 carry the
GND and VM planes.

This is an engineering derivation from material constants, flagged per
`AGENTS.md` §4 -- **not** an IPC-2152 [46] result. It gives watts, not degrees.

### Keep each phase terminal on the SAME side as its pour

A phase changing layers needs **~23 × 0.3 mm vias** to present as much copper
as the 2 oz pour it continues (2.2 A per via at that count). Keeping `J4A/B/C`
on the top side, with the phase pours, costs zero vias and zero extra
dissipation. The current placement has them on the bottom -- move them up, or
budget the via field.

### Commutation loop inductance -- the number that decides the FET choice

The TPHR8504PL is a 40 V part on a 25.2 V pack. Overshoot is
`V_DS = 25.2 + L_loop x dI/dt`, and dI/dt follows the DRV8353S IDRIVE setting
(SPI-programmable 50-1000 mA, [21]; TPHR8504PL Q_SW = 23 nC, [49]):

| IDRIVE | dI/dt | L=2 nH | L=5 nH | L=10 nH | L=20 nH |
| --- | --- | --- | --- | --- | --- |
| 150 mA | 326 A/µs | 25.9 V | 26.8 V | 28.5 V | 31.7 V |
| 300 mA | 652 A/µs | 26.5 V | 28.5 V | 31.7 V | 38.2 V |
| 600 mA | 1304 A/µs | 27.8 V | 31.7 V | 38.2 V | **51.3 V** |
| 1000 mA | 2174 A/µs | 29.5 V | 36.1 V | **46.9 V** | **68.7 V** |

Bold exceeds the 40 V rating. **Loop inductance decides this, not IDRIVE.**
A 2-5 nH loop survives the fastest gate drive; a 20 nH loop breaches 40 V at
almost any useful setting. So while placing:

- Put the high-side and low-side FET of each phase **as close as the package
  allows**, drain-to-source, in the same column.
- Get the bulk capacitor into that loop, not off beside the pack terminals --
  the loop is C1 -> Q(high) -> Q(low) -> shunt -> back to C1.
- Use the In1 GND plane as the return directly beneath the loop; every mm of
  detour is inductance.
- Add local high-frequency ceramics right at each half-bridge if the bulk cap
  cannot be close to all three.

Then set IDRIVE as fast as a **bench measurement** of V_DS allows. Do not pick
it from this table -- the table shows which loop inductances are survivable,
not what your loop actually is.

### Do not move these -- they are the reason the layout works

| Group | Constraint | Why |
| --- | --- | --- |
| `Q1`/`Q2`, `Q3`/`Q4`, `Q5`/`Q6` | Keep each half-bridge in its own column, high-side above low-side | Each column is a phase pour; splitting a bridge across columns breaks the pour and lengthens the switching loop |
| `SH1` + `U5` + `C5`-`C9` | Keep the shield block on the BOTTOM, directly under the FETs | Shortest GHx->gate->SHx loop ([21] Sec. 11.1). A top-side column measured 64.7 mm against a 60 mm board -- the shield is the 17.2 mm that did not fit |
| `U6`/`U7`/`U8` | Keep each sense amp under its own shunt | Keeps the differential shunt taps short and matched between phases |
| `U3`, `U4`, `J2`, `J3` | Keep together, past the isolation keepout, away from `U1` | The keepout removes all plane copper under the barrier; parts must stay on their correct side of it |
| `C1` | Keep in the FET loop, not off by the pack pads | [21] Sec. 11.1 asks for bulk positioned to minimise the high-current loop through the MOSFETs |
| Phase pours | One per column, higher priority than the GND pour | The phase nets have no plane; the pour is their conductor |

## Routing

### 2026-08-19 routing pass — read this before re-running the router

The board reached this pass **fully unrouted**: 0 track segments, 0 vias, 157
ratsnest connections. Getting it to route surfaced ten defects, none of them
routing defects. The full write-up is
`docs/solutions/architecture-patterns/what-the-autorouter-is-never-told.md`;
the WBS is `TODO.md` 12.5.av–az. The short version:

- The project net classes had gone missing, so the 50 A pack and all three
  phases would have routed at the 0.2 mm signal default. `autoroute.py` now
  hard-stops rather than routing a board whose classes are not in effect.
- KiCad exports every rule area as a **total** Specctra keepout, losing
  `tracks allowed`. That put U1, U2 and J1 inside a no-route band; the MCU was
  unroutable and it read as congestion.
- KiCad exports In1.Cu and In2.Cu as `(type signal)`. The first run cut
  **415 mm of signal through the GND and VM planes.** They are now marked
  `(type power)`; verified 0 segments on both.
- The board had **zero vias** — all four poured planes were floating.
  `tools/stitch_planes.py` now ties them.
- The PH_A and PH_C pours had been left 3.04 mm short of the high-side FET
  source pads by an earlier alignment pass, splitting each half-bridge switch
  node. `tools/fix_phase_pours.py` re-derives them.
- **Do not turn on `--inset-boundary`.** It hung the router twice for a full
  time limit each; the pours reach the board edge and cannot live outside an
  inset boundary. See `TODO.md` 12.5.av(h).

Current state: **423 segments (287 B.Cu, 136 F.Cu, 0 on the inner planes),
125 vias, 66 open connections.** Routed track on the plane nets totals 1.3 mm
on GND and 2.0 mm on VM — that audit exists because the Power class is relaxed
to 0.5 mm in the DSN so the router can reach U5's 0.25 mm WQFN pads, and it
confirms nothing signal-width ended up in series with a 50 A conductor.

Almost every one of the 66 open connections terminates on U1 (LQFP-64) or U5
(WQFN-40). Those need a staggered dogbone fanout before another router run
will help — `TODO.md` 12.5.ay.

### Historical: the 2026-08-16 pass

`tools/autoroute.py` was run 2026-08-16 (FreeRouting 2.2.4, 100 passes,
15 min 26 s). It took the board from 124 unrouted connections to 56, laying
381 segments and 48 vias.

**Then 29 of those segments were deleted on purpose.** The router had closed
`VM` with 3.0 mm track from the "power" net class — the 5.2 W outcome
described below. `tools/strip_high_current_tracks.py` removed them and refilled
the zones, and `tools/add_vm_top_pour.py` replaced them with copper. The
router did **not** attempt the three phase nets; those connections were left
open and still are.

State at the end of that pass (superseded by the 2026-08-19 pass above):
**352 segments, 48 vias, 57 open connections.** Of those 57:

| | Count | Status |
| --- | --- | --- |
| Phase nets to their terminals | 3 | **Blocked** — needs a placement decision, see below |
| Phase nets to `U5` sense pins | 3 | Low current; routable |
| `VM` bottom-side taps (`U5`, `R8`, `C6`) | 4 | Low current (gate-driver supply, sense divider, decoupling); routable |
| `GND` stitches | 9 | Short pour-to-pad; routable |
| Ordinary signal nets | 38 | Router did not converge; re-run with more passes or route by hand |

DRC at the end of that pass: 32 `silk_over_copper`, 21 `silk_overlap`,
12 `starved_thermal`, 5 `isolated_copper`, 2 `silk_edge_clearance`.

**Current DRC (2026-08-19, after routing and stitching): 31 violations —
11 `copper_edge_clearance`, 8 `silk_over_copper`, 7 `silk_overlap`,
5 `starved_thermal`. Zero shorts, zero clearance, zero hole-clearance, zero
schematic-parity errors.** `isolated_copper` cleared when the planes were
stitched. Edge clearance is `TODO.md` 12.5.az; silkscreen is deferred
(`TODO.md` 12.5.u).

**Fab-capability note:** `U5`'s 12 thermal vias are **0.20 mm** drill. That
matches this board's own minimum (`m_MinThroughDrill` = 0.2 mm) so it is not a
rule violation, but it is below the 0.3 mm many fabs treat as standard and
will be an upcharge or a redesign at some vendors. Confirm before ordering.

### THE HIGH-CURRENT GAPS — the open electrical problem in the layout

Of the 124 unrouted connections KiCad reports, **14 are on the 50 A nets**
(`VM` 8, `PH_A`/`PH_B`/`PH_C` 2 each). Those 14 are the ones an autorouter
must not be allowed to close, because `tools/autoroute.py` puts them in a
3.0 mm "power" class — a sane width for a signal-class power net, not for
50 A. The other 110 are ordinary signal nets and are the router's job.

#### Gap 1 — `VM` has no top-side copper at all

The `VM` plane is on **In2.Cu only**. Every part that actually carries pack
current sits on **F.Cu**: `J5A` (pack +), `C1` (bulk), and the three
high-side drains `Q1`/`Q3`/`Q5`. Nothing joins them — not to each other, and
not down to the plane. KiCad's own connectivity confirms it:

```text
PTH pad 1 [VM] of J5A   <-> Pad 6 [VM] of Q1 on F.Cu
Pad 5  [VM] of Q1 on F.Cu <-> Pad 8 [VM] of Q3 on F.Cu
Pad 5  [VM] of Q3 on F.Cu <-> Pad 8 [VM] of Q5 on F.Cu
Pad 8  [VM] of Q3 on F.Cu <-> Pad 1 [VM] of C1 on F.Cu
```

The top-side `VM` pads span **x 2.20 → 22.81, y 4.60 → 13.05 mm**, so a single
F.Cu `VM` pour of roughly **22.6 × 10.5 mm** reaches all of them, and stitches
to the In2 plane wherever there is room. Worst-case lateral run is `J5A` to
the far `Q5` drain, ≈ 20.6 mm; at 2 oz:

| Conductor | R | Dissipation |
| --- | --- | --- |
| 3.0 mm track (what the router draws) | 2.08 mΩ | **5.2 W** |
| 6.0 mm | 1.04 mΩ | 2.6 W |
| 10.0 mm | 0.62 mΩ | 1.6 W |
| Full 22.6 mm pour | 0.28 mΩ | 0.7 W |

**Fix: pour `VM` on F.Cu across the top band.** It costs nothing in area — the
band is already reserved for the pack input and the high-side drains — and it
takes the run from 5.2 W to 0.7 W.

#### Gap 2 — the phase nets do not reach their own terminals

Measured off the board 2026-08-16:

| | Layer | Extent |
| --- | --- | --- |
| `PH_A`/`PH_B`/`PH_C` pours | **F.Cu** | y 11.10 → **33.10** mm |
| `J4A`/`J4B`/`J4C` pads | **B.Cu** | y **48.10** → 58.10 mm |

So each phase has a **15 mm gap and a layer change** between the pour that
carries it and the terminal that leaves the board. The x-alignment is already
right (each terminal sits under its own pour's column); only the run down the
board and the side change are missing.

Run `docs/tools/conductor_sizing.py`, which models this gap; at 2 oz:

| Track width | R per phase | Dissipation, all 3 |
| --- | --- | --- |
| 3.0 mm (what the router will draw) | 1.52 mΩ | **11.4 W** |
| 5.0 mm | 0.91 mΩ | 6.8 W |
| 7.5 mm (full pour width) | 0.61 mΩ | 4.6 W |

At 3.0 mm this gap alone dissipates **more than all six FETs' conduction loss
combined** (10.5 W), and it is *in series with* the pours' own 6.7 W. That is
indefensible on a board whose reference design [47] already measures 103 °C at
this current.

Three ways to close it, in order of electrical cost:

1. **Move `J4A`/`J4B`/`J4C` to F.Cu and extend each phase pour down to its
   terminal.** Zero vias, zero added dissipation — the pour simply gets
   longer. Cost: the top side at y ≈ 48–58 currently holds `J2` (x 6.0) and
   `J3` (x 18.5), so those two solder-pad strips have to go somewhere else.
   This is a **placement** decision and therefore the repo owner's call.
2. **Keep the terminals on B.Cu, add a B.Cu phase pour per column, and stitch
   with a via field.** Needs **23 × 0.3 mm vias per phase** (2.2 A each) to
   present as much copper as the 2 oz pour — 69 vias total, in a region that
   also has to clear `U1`/`U2` and the resistor columns.
3. **Widen to full 7.5 mm pour on B.Cu without a matching via count.** Cheapest
   to draw and the easiest to get wrong: the via field, not the pour, becomes
   the narrowest point in the conductor.

Option 1 is the recommendation. Options 2 and 3 both pay for a layer change
the geometry does not actually require.

### Getting back into the flow after placing

```bash
kicad-cli pcb drc --severity-all <board>.kicad_pcb   # expect 0 errors first
python3 tools/autoroute.py --passes 60               # injects the net classes
kicad-cli pcb drc --severity-all <board>.kicad_pcb   # again, after routing
```

Then the fab outputs. Conductor sizing is still the blocking gap -- see below.

## Before you fabricate

**Conductor sizing is the blocking gap.** No conductor width on this board is
a computed value. IPC-2152 [46] is the governing standard; it is paywalled,
and only its Table of Contents has been read, so under `AGENTS.md` §1.3 no
width may be derived from it yet. `VM` and `GND` are poured planes and do not
depend on track width, but the three **phase** nets reach the motor connector
partly as routed track, and that is load-bearing at 50 A. See `TODO.md`
§12.4.k.

Also open before fab (all in `TODO.md` §12.4):

- **Real power connectors.** `J4` and `J5` are KiCad 6 mm² (~10 AWG)
  solder-wire pads — the largest in the stock library, chosen because the
  previous `J4` was a 2.54 mm pin header. No part has been selected and no
  current rating verified.
- **The isolation barrier width** follows from the transceiver variant, which
  is still open. The keepout is sized to clear the isolated pin rows, not to a
  creepage table.
- **Three engineering defaults need confirming**: the DRV8353S thermal pad
  tied to GND, the WE-SHC frame's locating holes plated, and the 10 kΩ
  pull-up values.
- **Placement is a starting point, not a solved layout.** It is DRC-clean and
  respects [21] §11.1's loop constraints, but thermal, EMI and
  manufacturability review of the power stage is a human task.
- **The MCU symbol maps 28 of the LQFP-64's 64 pins**, so 36 pads import with
  no net. Fine electrically (unused GPIO), but the symbol does not describe
  the whole package.

## tools/

Re-run these rather than hand-editing the generated `.kicad_sch`/`.kicad_pcb`.
Requires `kiutils` (schematic scripts) and KiCad's `pcbnew` Python module
(board scripts).

| Script | Purpose |
| --- | --- |
| `build_pcb.py` | Builds the PCB from the exported netlist: real footprints, every pad netted, outline, 4-layer stack, planes, phase pours, isolation keepout. |
| `autoroute.py` | FreeRouting round trip. Injects the power/sense net classes into the DSN — net classes live in the `.kicad_pro`, which `pcbnew.LoadBoard()` does not read, so without this every net routes at the 0.2 mm default. |
| `set_netclasses.py` | Writes the Power / Sense / Isolated classes into the project file. |
| `finish_annotate_and_footprints.py` | Annotation, footprint assignment, off-board flags. |
| `finish_erc_fixes.py` | The `R14` pull-up, the thermal-pad pin, the four power flags. |
| `add_power_connectors.py` | `J5` battery input; both power connectors off 2.54 mm headers. |
| `fix_generic_symbol_libs.py` | Moves the generic stand-ins into `Open_Secure_ESC_Generic.kicad_sym`. |
| `snap_to_grid.py` | Refuses to run without `--force`; documents why the snap shorts this sheet. |
| `check_shorts.py` | Finds collinear overlapping wire segments on different nets — a short KiCad's ERC reads as one net. |
| `gen_schematic.py` | **Carries a divergence warning.** No longer the sole author of the committed sheet; running it drops later work. |
| `gen_pcb.py` | Superseded by `build_pcb.py`. |

## Libraries (`sym-lib-table`)

| Nickname | Symbol | Pin-map status |
| --- | --- | --- |
| `MSPM0G3518_Q1_PM` | MCU, LQFP-64 | **VERIFIED** against [44] — real pin numbers, not placeholders |
| `OPTIGA_TRUST_M` | Secure element | VERIFIED, [45] p.17 Table 6 |
| `ADM3055E_ADM3057E` | CAN-FD transceiver | VERIFIED, full 20-pin |
| `ADM2582E_ADM2587E` | RS-485 transceiver | VERIFIED, full 20-pin |
| `DRV8353S` | Gate driver | VERIFIED, full 40-pin + thermal pad as pin 41 |
| `INA240` | Current-sense amp | VERIFIED |
| `IRFB4110PBF` | Power MOSFET | Standard TO-220AB pinout |
| `WSLP2512` | Shunt | Generic 2-terminal |
| `INR21700_P42A` | Cell (×6) | Generic 2-terminal; off-board |
| `WE_SHC_3670375` / `_3671375` | Shield frame / cover | Mechanical; cover is off-board |
| `Open_Secure_ESC_Generic` | R, C, C_Polarized, Conn_01x02/03/04, PWR_FLAG | This repo's own parts — **not** KiCad's `Device:`/`Connector_Generic:`/`power:` symbols; the pin geometry differs |
| `S32K144` | Superseded MCU | Retained so the old design history stays loadable; unused |
