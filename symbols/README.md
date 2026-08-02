# symbols/ — Shared KiCad Symbol Library

Governed by `AGENTS.md`. One `.kicad_sym` file per component, generated (not
hand-edited) from a citable JSON pin spec. This folder is shared across every
`builds/<voltage>/<amperage>/<variant>/` build — a build's `kicad/` folder
references these files instead of re-deriving or re-drawing pinouts, which is
the token-optimized part of the workflow: sourcing a datasheet pinout once
here is reusable for every future build that needs the same part.

## Layout

```text
symbols/
  <PART>.kicad_sym      generated symbol library, one component per file
  specs/<PART>.json      pin spec the symbol was generated from (source of truth)
  tools/gen_kicad_symbol.py   generator: JSON spec -> .kicad_sym
```

Never hand-edit a `.kicad_sym` file directly (except cosmetic repositioning in
the KiCad Symbol Editor, which does not change pin numbers/names). If a pin
map changes, edit the JSON spec and regenerate:

```bash
cd symbols/tools
python3 gen_kicad_symbol.py ../specs/<PART>.json -o ..
```

Regenerate everything: `python3 gen_kicad_symbol.py ../specs/*.json -o ..`

Requires `kiutils` (`pip install kiutils`; generated and round-trip-validated
against kiutils 1.4.8).

## Adding a new component (the reusable part of this workflow)

1. Locate the component's primary datasheet (manufacturer PDF), per
   `AGENTS.md` SS1.1. If a local copy exists under `docs/datasheets/`, extract
   the pin table from it directly (e.g. with `pypdf`) rather than trusting
   memory or a secondary source.
2. Add/reuse a citation tag in `REFERENCES.md` per `AGENTS.md` SS2.
3. Write `symbols/specs/<PART>.json`:
   - `pins`: list of `{"num", "name", "etype", "side"}`. `etype` is a KiCad
     electrical pin type (`input`, `output`, `bidirectional`, `tri_state`,
     `passive`, `power_in`, `power_out`, `open_collector`, `no_connect`, ...).
     `side` is `left` / `right` / `top` / `bottom` — a layout hint, not a
     datasheet claim (rearrange freely in the KiCad Symbol Editor).
   - `citation`: REFERENCES.md tag(s), e.g. `"[9]"`.
   - `verification`: state plainly whether pin **numbers** came from a
     primary-source pin table (`VERIFIED`, cite page/table) or are
     placeholders because no primary source was reachable
     (`UNVERIFIED PLACEHOLDER PIN MAP`, per `AGENTS.md` SS1.3/SS3 — never
     silently presented as settled).
4. Run the generator, then round-trip-validate:

   ```bash
   python3 -c "from kiutils.symbol import SymbolLib; SymbolLib.from_file('../<PART>.kicad_sym')"
   ```

5. Reference the new file from the build's `kicad/sym-lib-table` (see below).

## Per-component status

| File | Citation | Pin-map status |
| --- | --- | --- |
| `MSPM0G3507.kicad_sym` | [1] | VERIFIED (partial — build-specific pin subset; see spec `verification` field) |
| `SLB9672.kicad_sym` | [2] | VERIFIED (full 32-pin, footprint-complete) |
| `ADM2582E_ADM2587E.kicad_sym` | [4], [9] | VERIFIED (full 20-pin); part selection itself still "Candidate" in `docs/decision-matrix.xlsx` |
| `ADM3055E_ADM3057E.kicad_sym` | [6], [10] | VERIFIED (full 20-pin); part selection itself still "Candidate" |
| `DRV8353S.kicad_sym` | [21] | UNVERIFIED PLACEHOLDER pin numbering (no local datasheet copy) |
| `INA240.kicad_sym` | [22] | VERIFIED (full 8-pin, D/SOIC-8 package; local datasheet) |
| `IRFB4110PBF.kicad_sym` | [20] | Standard TO-220AB G/D/S pinout convention; ratings VERIFIED (local datasheet) |
| `WSLP2512.kicad_sym` | [23] | Generic 2-terminal chip pinout; values VERIFIED (local datasheet) |
| `INR21700_P42A.kicad_sym` | [14] | Generic 2-terminal cell pinout; values VERIFIED (local datasheet) |
| `WE_SHC_3671375.kicad_sym` | [15], [19] | Mechanical shield **cover** — no functional schematic pins (placeholder GND-bond pin only); dimensions VERIFIED (local datasheet), but the paired frame (part 3670375) is not yet in this repo |

"UNVERIFIED PLACEHOLDER" pin maps must not be sent to fab — see each
`specs/*.json` `verification` field and `TODO.md` 1.10 for what would need to
be resolved first (a working fetch path or a manually obtained primary PDF).

## Using this library from a build

Add a project-relative library table entry (see
`builds/6s/50A/CAN_485_faraday/kicad/sym-lib-table` for a working example)
pointing at this shared folder. `${KIPRJMOD}` is the folder containing the
`.kicad_pro`/`.kicad_sch`; for a build at
`builds/<voltage>/<amperage>/<variant>/kicad/`, that is 5 levels above
`symbols/`:

```text
(lib (name "open_secure_esc")(type "KiCad")(uri "${KIPRJMOD}/../../../../../symbols/MSPM0G3507.kicad_sym")(options "")(descr ""))
```

One `(lib ...)` line per `.kicad_sym` file needed by that build — do not copy
symbol files into a build folder; reference the shared copy so a pin-map
correction only has to happen once.
