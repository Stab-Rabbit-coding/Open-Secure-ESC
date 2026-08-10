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
| `S32K144.kicad_sym` | [31] | Feature-level facts VERIFIED; pin **numbers** UNVERIFIED PLACEHOLDER (local datasheet defers physical pinout to the S32K1xx Reference Manual, not obtained — see spec `verification` field, `TODO.md`) |
| `OPTIGA_TRUST_M.kicad_sym` | [45] | VERIFIED (full 10-pin PG-USON-10-2,-4 map, local datasheet p.17 Table 6). **Footprint deliberately blank** — no KiCad 9 standard footprint matches this 3×3 mm / 0.5 mm-pitch package; size one from p.15 Fig. 6 before layout |
| `ADM2582E_ADM2587E.kicad_sym` | [4], [9] | VERIFIED (full 20-pin); part selection itself still "Candidate" in `docs/decision-matrix.xlsx` |
| `ADM3055E_ADM3057E.kicad_sym` | [6], [10] | VERIFIED (full 20-pin); part selection itself still "Candidate" |
| `DRV8353S.kicad_sym` | [21] | VERIFIED (full 40-pin, RTA/WQFN package; local datasheet) |
| `INA240.kicad_sym` | [22] | VERIFIED (full 8-pin, D/SOIC-8 package; local datasheet) |
| `IRFB4110PBF.kicad_sym` | [20] | Standard TO-220AB G/D/S pinout convention; ratings VERIFIED (local datasheet) |
| `WSLP2512.kicad_sym` | [23] | Generic 2-terminal chip pinout; values VERIFIED (local datasheet) |
| `INR21700_P42A.kicad_sym` | [14] | Generic 2-terminal cell pinout; values VERIFIED (local datasheet) |
| `WE_SHC_3671375.kicad_sym` | [15], [19] | Mechanical shield **cover** — no functional schematic pins (placeholder GND-bond pin only); dimensions VERIFIED (local datasheet); pairs with the frame below |
| `WE_SHC_3670375.kicad_sym` | [15], [19], [30] | Mechanical shield **frame** — same treatment as the cover above; dimensions VERIFIED (local datasheet) |

"UNVERIFIED PLACEHOLDER" pin maps must not be sent to fab — see each
`specs/*.json` `verification` field and `TODO.md` 1.10 for what would need to
be resolved first (a working fetch path or a manually obtained primary PDF).

**2026-08-03: MCU/TPM swap.** `MSPM0G3507.kicad_sym`/`specs/MSPM0G3507.json`
(project MCU, REFERENCES.md [1]) and `SLB9672.kicad_sym`/`specs/SLB9672.json`
(external TPM, REFERENCES.md [2]) were removed from this folder. The project
MCU changed to the NXP S32K144 (`S32K144.kicad_sym`, [31] above), whose
on-chip CSEc security module now provides message authentication in place of
the discrete SLB9672 TPM — see root `README.md` and
`builds/6s/50A/CAN_485_faraday/README.md`. Both REFERENCES.md entries [1]
and [2] are retained (never repurposed, per `AGENTS.md` §2.5) and marked
superseded/dropped there; their local datasheet PDFs under
`docs/datasheets/` are also kept so those citation records stay resolvable.

**2026-08-09: secure element added (not a TPM reinstatement).**
`OPTIGA_TRUST_M.kicad_sym`/`specs/OPTIGA_TRUST_M.json` ([45], Infineon
OPTIGA™ Trust M V3, sales code SLS 32AIA010ML) joins this library. It is an
**I2C secure element, a different device class from the dropped SLB9672
TPM 2.0** ([2]) — it is adopted for the asymmetric PKI capability the
S32K144's symmetric-only CSEc structurally cannot provide, and it runs
*alongside* CSEc rather than replacing it. The 2026-08-03 decision above
stands: CSEc still owns per-frame message authentication. See
`docs/secure-element-architecture.md`.

Housekeeping done in the same pass: `SLB9672_TPM.kicad_sym` was deleted.
That file was an orphan — the 2026-08-03 note above already declared the
SLB9672 symbol removed, and no `specs/SLB9672.json` exists, so the file
could not be regenerated, was referenced by nothing, and contradicted both
this README and `REFERENCES.md` [2]. Removing it makes the tree match what
those two documents already said.

## Using this library from a build

Add a project-relative library table entry (see
`builds/6s/50A/CAN_485_faraday/kicad/sym-lib-table` for a working example)
pointing at this shared folder. `${KIPRJMOD}` is the folder containing the
`.kicad_pro`/`.kicad_sch`; for a build at
`builds/<voltage>/<amperage>/<variant>/kicad/`, that is 5 levels above
`symbols/`:

```text
(lib (name "open_secure_esc")(type "KiCad")(uri "${KIPRJMOD}/../../../../../symbols/S32K144.kicad_sym")(options "")(descr ""))
```

One `(lib ...)` line per `.kicad_sym` file needed by that build — do not copy
symbol files into a build folder; reference the shared copy so a pin-map
correction only has to happen once.
