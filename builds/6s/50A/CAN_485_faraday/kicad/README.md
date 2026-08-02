# kicad/ — 6S / 50A / CAN-FD+RS-485 / Faraday

## Status

Project **skeleton**, not a captured schematic. What exists:

- `open_secure_esc_6s_50a_can485_faraday.kicad_sch` — a valid, empty root
  schematic sheet (KiCad 6/7/8 format, generated with `kiutils` and
  round-trip-validated) with a title block pointing back at the build spec,
  BOM/citation sources, and the shared symbol library. No components are
  placed and no nets are drawn yet.
- `sym-lib-table` — wires this project to every component symbol this build
  needs, from the shared `symbols/` library at the repo root (see
  `symbols/README.md`). Opening the schematic in KiCad and adding a symbol
  should show all ten libraries listed below already available, with no
  manual library setup.

What does **not** exist yet: a `.kicad_pro` project file, placed components,
routed nets, or a PCB layout (`.kicad_pcb`). `.kicad_pro` is intentionally
omitted rather than hand-authored — its JSON schema has many
version-sensitive required keys that could not be validated in this session
(no local KiCad install to round-trip against); open the `.kicad_sch`
directly in KiCad and let it generate a matching `.kicad_pro` on first save,
rather than trusting a hand-built one.

Schematic capture is blocked on the same thing the BOM is blocked on: most
candidate parts in `../README.md`'s BOM table are still `Candidate
(unverified)` in `docs/decision-matrix.xlsx` (no primary datasheet reachable
this session for DRV8353S, INA240, IRFB4110PBF, WSLP2512, the Molicel cell,
or the WE-SHC shield can — see each part's citation in REFERENCES.md). Per
`AGENTS.md` §1.3, an unverified part is not fabricated into a "final" BOM
line; wiring a schematic around parts whose pin maps are themselves
placeholders (see `symbols/README.md` "Per-component status") would just be
guessing twice. Tracked in `TODO.md` 1.10, 3-7.

## Libraries available (`sym-lib-table`)

| Library nickname | Symbol | Verified? |
| --- | --- | --- |
| `MSPM0G3507` | MCU | pin subset VERIFIED |
| `SLB9672` | TPM | VERIFIED, full 32-pin |
| `ADM2582E_ADM2587E` | RS-485 transceiver | VERIFIED, full 20-pin |
| `ADM3055E_ADM3057E` | CAN-FD transceiver | VERIFIED, full 20-pin |
| `DRV8353S` | gate driver | UNVERIFIED placeholder pins |
| `INA240` | current-sense amp | UNVERIFIED placeholder pins |
| `IRFB4110PBF` | power MOSFET | standard TO-220 pinout |
| `WSLP2512` | shunt resistor | generic pinout |
| `INR21700_P42A` | cell (×6 for this pack) | generic pinout |
| `WE_SHC_3671375` | Faraday shield can | mechanical, no signal pins |

## Next steps (tracked in TODO.md)

1. Resolve TODO.md 1.10 (primary datasheets for the still-candidate parts)
   or accept the placeholder pin maps with an explicit design-review
   sign-off before wiring them into a schematic.
2. Place symbols, wire the MCU pin assignment already fixed in
   `symbols/specs/MSPM0G3507.json` (CAN-FD, RS-485 UART+DE, dual SPI, FOC
   ADC, 3-phase PWM) to the transceivers/gate-driver/TPM.
3. Add power-stage passives (bulk input cap, decoupling) using KiCad's
   standard `Device:C` / `Device:C_Polarized` / `Device:R` library symbols
   — not reinvented here, since those are generic parts with no
   part-specific pinout to source.
4. Open the sheet in KiCad, let it create `.kicad_pro`, then start a
   `.kicad_pcb` for the `../gerbers/` output.
