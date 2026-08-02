# kicad/ — 6S / 50A / CAN-FD+RS-485 / Faraday

## Status

**Populated**: schematic, project file, and PCB all now exist with every BOM
part from `../README.md` placed and wired (schematic) or footprinted (PCB).
This is a step up from the earlier "empty skeleton" state, but it is still
not a fab-ready design -- see "What's still missing" below before treating
anything here as final.

- `open_secure_esc_6s_50a_can485_faraday.kicad_sch` -- KiCad 6/7/8-format
  (`version 20211014`) schematic, title block company **Griffing Technology
  LLC**, drawn on an A0 sheet (the previous A3 skeleton was too small for a
  legibly-wired single-sheet MCU + power-stage schematic once populated).
  44 symbol instances, every documented MCU pin assignment
  (`symbols/specs/MSPM0G3507.json`) wired point-to-point with real schematic
  wires (`(wire ...)`) to its peer chip; shared rails (GND, VM, 3V3,
  VREF_MID, the two isolated-side grounds, per-phase current-sense/phase
  nodes) are carried by same-name global labels with a short wire stub at
  each participating pin -- standard KiCad practice for multi-drop nets, and
  every one of those stub wires is still a real drawn line, so "use lines to
  connect components" is satisfied both for the direct point-to-point runs
  and for the labeled rails. The drawing is centered on the sheet's usable
  area (full page minus outer margin and the title-block band).
- `open_secure_esc_6s_50a_can485_faraday.kicad_pro` -- hand-authored project
  file (JSON). Earlier revisions of this README deliberately omitted this
  file pending a local KiCad install to round-trip against; that caution
  still applies in spirit -- **open this file in KiCad and let it re-save
  once**, before trusting it for anything beyond opening the project, since
  no KiCad install was available in this session to validate every
  version-sensitive key.
- `open_secure_esc_6s_50a_can485_faraday.kicad_pcb` -- footprints placed for
  every BOM part that has a confirmed footprint string in
  `symbols/specs/*.json`, plus a board outline (`Edge.Cuts`), on an A3 sheet,
  centered the same way as the schematic. **No netlist has been imported and
  nothing is routed** -- see below.
- `sym-lib-table` -- now also lists `WE_SHC_3670375` (the Faraday shield's
  required frame, previously missing from this table even though the part
  was already used in the BOM discussion) and two entries for KiCad's own
  system libraries (`Device`, `Connector_Generic`) used for the generic
  support passives and headers below.
- `tools/` -- the generator scripts used to produce the two files above
  (`gen_schematic.py`, `gen_pcb.py`, `genlib.py`), in the same spirit as
  `symbols/tools/gen_kicad_symbol.py`: re-run them after editing
  `symbols/specs/*.json` or the placement/wiring tables inside these scripts,
  rather than hand-editing the generated `.kicad_sch`/`.kicad_pcb` text.
  Requires `pip install kiutils`.

## What got added beyond the verified BOM

Per `AGENTS.md` §1.3 (no fabrication), every part placed here is either a
BOM line from `../README.md` with a citation, or one of the following two
categories, called out explicitly rather than silently blended in:

1. **Generic support passives/connectors** (decoupling caps, pull-up
   resistors, the VBUS/VREF-MID bias dividers, the debug/CAN/RS-485/motor
   headers): drawn as KiCad's own standard `Device:R` / `Device:C` /
   `Device:C_Polarized` / `Connector_Generic:Conn_01x0N` parts (per this
   file's own earlier "Next steps" note), with generic/typical values
   (e.g. "10k", "100nF") called out in each part's `Note` property as an
   *engineering default, not datasheet-sourced* -- the same treatment
   `../README.md` already gives the bulk input capacitor line.
2. **Genuinely open design questions, left open rather than resolved here**:
   - DRV8353S's integrated per-phase current-sense amplifier outputs
     (`SOA`/`SOB`/`SOC`) are left unconnected (schematic `no_connect` flags
     + an on-sheet text note) because this build routes `ADC_IU/IV/IW` from
     the external INA240 devices instead -- the DRV8353S-vs-INA240 sourcing
     question from `../README.md`'s BOM note is **not** silently decided by
     this schematic; both parts are placed, only one path is wired to the
     MCU.
   - `nFAULT` (DRV8353S) is pulled up but not wired to any MCU pin -- the
     MCU pin map in `symbols/specs/MSPM0G3507.json` doesn't reserve one, and
     inventing a new pin assignment here would itself be a fabricated design
     decision.
   - The isolated-side supply pins on both transceivers
     (`VISOIN`/`AUXIN`/`AUXOUT` on the CAN part) are labeled and left
     unconnected beyond that label -- `../README.md`'s Protocol section
     already flags the transceiver variant choice (and therefore its
     isolated-supply sourcing) as open.
   - The 3V3 logic rail has no regulator on this sheet -- `../README.md`'s
     "Open items" already lists control-loop/regulator selection as
     unresolved; this schematic just carries the net as a label rather than
     inventing a part to source it from.

## Battery pack representation

`BT1`-`BT6` (`INR21700_P42A`, wired in series per `../README.md`'s 6S tier)
are drawn on the **schematic** to document the pack composition against
REFERENCES.md [14], but are **not** placed on the PCB -- a 21700 cell pack is
physically an external assembly, not a board-mounted part. The PCB instead
has a PCB-only 2-pin terminal footprint `J5` (`BATT_IN`, no schematic
counterpart) marking where that external pack connects.

## What's still missing (do not treat this as fab-ready)

- **No footprint for U5 (DRV8353S)**: its own spec
  (`symbols/specs/DRV8353S.json`) explicitly declines to guess a KiCad
  footprint name for its RTA0040B WQFN package ("no existing KiCad standard
  footprint was confirmed to match ... exactly"). The PCB has a labeled
  reserved-area outline at U5's board position instead of a fabricated
  footprint -- size and place a real footprint here before layout continues.
- **No netlist import, no routing, no DRC pass.** Every PCB pad is net-less
  (`net 0`); footprints are placed for board-planning legibility only. Open
  in KiCad, `Tools -> Update PCB from Schematic`, then route and run DRC.
  `PROJECT_NAME` in `tools/gen_pcb.py` assumes the reference designators
  already match between the two files (they do, by construction -- the PCB
  generator reads them straight out of the `.kicad_sch`), but KiCad's own
  netlist importer should still be treated as the source of truth once run.
- **Footprints in the PCB are parametric stand-ins**, not exact copies of
  KiCad's system footprint libraries (which weren't available in this
  session) -- pad count and package envelope match the footprint name
  already recorded in `symbols/specs/*.json`, but exact pad geometry should
  be re-verified against the real library footprint before fab.
- Every open item already listed in `../README.md` ("Open items" section)
  is still open; this schematic documents where each one sits electrically
  (see "What got added" above) without resolving any of them.

## Libraries available (`sym-lib-table`)

| Library nickname | Symbol | Verified? |
| --- | --- | --- |
| `MSPM0G3507` | MCU | pin subset VERIFIED |
| `SLB9672` | TPM | VERIFIED, full 32-pin |
| `ADM2582E_ADM2587E` | RS-485 transceiver | VERIFIED, full 20-pin |
| `ADM3055E_ADM3057E` | CAN-FD transceiver | VERIFIED, full 20-pin |
| `DRV8353S` | gate driver | pin map VERIFIED (footprint still TBD, see above) |
| `INA240` | current-sense amp | pin map VERIFIED |
| `IRFB4110PBF` | power MOSFET | standard TO-220 pinout |
| `WSLP2512` | shunt resistor | generic pinout |
| `INR21700_P42A` | cell (×6 for this pack) | generic pinout |
| `WE_SHC_3671375` | Faraday shield can, cover | mechanical, no signal pins |
| `WE_SHC_3670375` | Faraday shield can, frame (required pair to the cover) | mechanical, no signal pins |
| `Device` | KiCad standard R/C/C_Polarized | KiCad system library |
| `Connector_Generic` | KiCad standard generic headers | KiCad system library |

## Next steps (tracked in TODO.md)

1. Open in KiCad, let it re-save `.kicad_pro`, confirm the schematic and PCB
   both load and ERC/DRC run cleanly; fix anything this session's kiutils
   round-trip validation couldn't catch without a real KiCad install.
2. Size and place a real footprint for U5 (DRV8353S) from its RTA0040B WQFN
   mechanical drawing (`docs/datasheets/drv8353.pdf`).
3. `Update PCB from Schematic` to import the real netlist, then route and
   run DRC -- current copper is entirely unrouted.
4. Resolve the open design questions listed above (or carry them into a
   design-review decision, per `AGENTS.md` §4) before treating the BOM as
   settled per `AGENTS.md` §5.
5. Once routed and DRC-clean, proceed to `../gerbers/` per its own README.
