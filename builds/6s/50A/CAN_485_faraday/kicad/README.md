# kicad/ — 6S / 50A / CAN-FD+RS-485 / Faraday

Governed by `AGENTS.md`. Open items are tracked in the repo-root `TODO.md`
§12.4; this file describes what the two design files currently contain.

## Status

**Schematic: ERC-clean (0 errors) on the 30 x 60 mm respin BOM. PCB: placed,
netted and poured, but placement has NOT converged — see the hand-placement
guide below.** Not fabrication-ready.

| | State |
| --- | --- |
| Schematic | 50 parts, annotated, **0 ERC errors** (`endpoint_off_grid` + `global_label_dangling` warnings remain — see below) |
| PCB | 30 × 60 mm, double-sided, 47 footprints, 73 nets, 4 layers, planes poured, isolation keepout. **~11 courtyard overlaps outstanding** |
| Routing | Not run on the respin — placement must converge first |
| Gerbers | Not generated. See "Before you fabricate". |

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
| `*.kicad_pcb` | 30 × 60 mm, 4 layers, double-sided, rounded corners. |
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

## Hand-placement guide (30 x 60 mm respin)

`tools/build_pcb.py` writes a complete, netted, poured board, but its
placement table does **not** converge on 30 x 60 -- roughly 11 courtyard
overlaps remain, all in the bottom-end region where the phase pads and J1
land on U1 and the resistor columns. Placement from here is a manual pass in
the PCB editor.

**Re-running `tools/build_pcb.py` discards hand placement.** It rebuilds the
board from the netlist every time. Once you start placing by hand, either stop
running it or fold your positions back into its `PLACEMENT` table.

### Do not move these -- they are the reason the layout works

| Group | Constraint | Why |
| --- | --- | --- |
| `Q1`/`Q2`, `Q3`/`Q4`, `Q5`/`Q6` | Keep each half-bridge in its own column, high-side above low-side | Each column is a phase pour; splitting a bridge across columns breaks the pour and lengthens the switching loop |
| `SH1` + `U5` + `C5`-`C9` | Keep the shield block on the BOTTOM, directly under the FETs | Shortest GHx->gate->SHx loop ([21] Sec. 11.1). A top-side column measured 64.7 mm against a 60 mm board -- the shield is the 17.2 mm that did not fit |
| `U6`/`U7`/`U8` | Keep each sense amp under its own shunt | Keeps the differential shunt taps short and matched between phases |
| `U3`, `U4`, `J2`, `J3` | Keep together, past the isolation keepout, away from `U1` | The keepout removes all plane copper under the barrier; parts must stay on their correct side of it |
| `C1` | Keep in the FET loop, not off by the pack pads | [21] Sec. 11.1 asks for bulk positioned to minimise the high-current loop through the MOSFETs |
| Phase pours | One per column, higher priority than the GND pour | The phase nets have no plane; the pour is their conductor |

### Known conflicts to resolve

All in the bottom end: `J4A`/`J4B`/`J4C` and `J1` overlap `U1` and the
`R4`/`R5`/`R8`/`R9` columns. `U5`'s thermal via field also overlaps `Q3`/`Q4`
above it -- see the warning below.

### One electrical trap while you place

`U5`'s footprint carries **12 thermal vias on the GND net** (TI's RTA0040B
sheet, note 5, "vias are optional"). `U5` sits on the bottom directly beneath
the top-side FETs. If a via lands under a FET drain pad it shorts **GND to VM
or to a phase**. Either keep the via field clear of the FET drain pads, or
delete the vias from the footprint. Check this specifically after moving
either `U5` or any `Q`.

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
