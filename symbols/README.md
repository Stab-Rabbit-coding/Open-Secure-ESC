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
| `DRV8353S.kicad_sym` | [21] | VERIFIED (full 40-pin, RTA/WQFN package; local datasheet). **2026-08-15: pin 41 `PAD` added** for the exposed thermal pad, tied to GND — without it the footprint's pad 41 imported with no net, i.e. an isolated copper island under the power stage. The GND assignment is an engineering default, not a datasheet value. Footprint now `Open_Secure_ESC:TI_RTA0040B_WQFN-40_6x6mm_P0.5mm_EP4.15x4.15mm` |
| `INA240.kicad_sym` | [22] | VERIFIED (full 8-pin, D/SOIC-8 package; local datasheet) |
| `IRFB4110PBF.kicad_sym` | [20] | Standard TO-220AB G/D/S pinout convention; ratings VERIFIED (local datasheet) |
| `WSLP2512.kicad_sym` | [23] | Generic 2-terminal chip pinout; values VERIFIED (local datasheet) |
| `INR21700_P42A.kicad_sym` | [14] | Generic 2-terminal cell pinout; values VERIFIED (local datasheet) |
| `WE_SHC_3671375.kicad_sym` | [15], [19] | Mechanical shield **cover** — no functional schematic pins (placeholder GND-bond pin only); dimensions VERIFIED (local datasheet); pairs with the frame below. **Intentionally has NO footprint**: the cover clips onto the frame and is not soldered, so its datasheet publishes no land pattern. Placed on schematics as BOM-only, excluded from the board |
| `WE_SHC_3670375.kicad_sym` | [15], [19], [30] | Mechanical shield **frame** — the piece actually soldered; dimensions VERIFIED (local datasheet). Footprint `Open_Secure_ESC:Wurth_WE-SHC_3670375_Frame_29.3x37.5mm` reproduces Wurth's own Recommended Land Pattern |

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

## footprints/ — this repo's own land patterns

`footprints/Open_Secure_ESC.pretty/` holds footprints for packages KiCad 9.0
does not ship. Each one is generated by a script in `tools/`, and each
script's docstring records exactly which drawing every dimension came from
and which numbers are derivations rather than manufacturer values — the same
standard `specs/*.json` applies to pin maps.

| Footprint | For | Source of the land pattern |
| --- | --- | --- |
| `Infineon_PG-USON-10-2-4_3x3mm_P0.5mm_EP1.7x2.5mm` | OPTIGA Trust M (U2) | Package dimensions from [45] p.15 Fig. 6. Infineon publishes **no** land pattern, so the fillets are an **IPC-7351-style derivation** — an engineering judgment call per `AGENTS.md` §4 |
| `Texas_DGS0028A_VSSOP-28_3x7.1mm_P0.5mm` | superseded MCU package | TI package drawing |
| `TI_RTA0040B_WQFN-40_6x6mm_P0.5mm_EP4.15x4.15mm` | DRV8353S gate driver (U5) | **TI's own** EXAMPLE BOARD LAYOUT and EXAMPLE STENCIL DESIGN sheets, drawing 4219112/A in [21] — manufacturer values, not a derivation |
| `Wurth_WE-SHC_3670375_Frame_29.3x37.5mm` | Faraday shield frame (SH1) | **Wurth's own** Recommended Land Pattern, [30] p.1 rev. ViM 002.000 — manufacturer values. Hole *plating* is the one engineering default |

Two of these land patterns are printed as vector drawings whose callouts do
not survive `pdftotext`. Where that happened the sheet was rendered at
300–400 dpi and measured, and the reading was then **cross-checked against an
independent dimension on the same drawing** rather than trusted on its own —
see each generator's docstring for the specific checks. That cross-check is
what separates a measured value from a guessed one under `AGENTS.md` §1.3.

**Toshiba land patterns live in the CATALOG, not the datasheet.** The
TPHR8504PL part datasheet has no land pattern -- all 10 pages were searched
and the words "land", "mounting" and "recommend" do not appear. Toshiba
publishes them in the *MOSFET Product Catalog* (REFERENCES.md [50], local
copy `docs/datasheets/TPHR8504PL_catalog_20260706_ALQ00024.pdf`), whose
**p.46 "Surface Mount Type"** tabulates package dimensions and land patterns
side by side for the whole surface-mount family -- DSOP Advance(WF)L/M, SOP
Advance, SOP Advance(N), SOP Advance(E), SOP Advance(EWF). Use it for **any**
Toshiba MOSFET package this repo adopts; do not derive one from the package
drawing when the catalog has the real figure. The first pass at
`gen_tphr8504pl_footprint.py` did derive one IPC-7351-style, and it was 46%
short on drain-land area and 86% short on lead-pad area against Toshiba's
published values.

**Watch the reference datum.** TI's RTA0040B sheet dimensions `2X (5.8)` as
the **centre-to-centre** distance between opposite pad rows, not the outer
copper extent. Reading it as the outer extent moves every pad 0.3 mm inward
and overlaps the corner pads — a dead short between pin 1 (CPL) and pin 40
(VGLS). DRC caught it; inspection had not.

## Open_Secure_ESC_Generic.kicad_sym — generic support symbols

R, C, C_Polarized, Conn_01x02/03/04 and PWR_FLAG, as authored by
`builds/*/kicad/tools/genlib.py`. These had previously been stored in
schematics under KiCad's own `Device:`, `Connector_Generic:` and `power:`
library names even though their pin geometry differs from KiCad's parts
(`Device:R` pin 1 sits at y = 6.35 here against y = 3.81 in KiCad 9.0),
which made every placed instance raise a `lib_symbol_mismatch`. They live
here now so that a schematic matches the library it names. Their *values*
remain engineering defaults, not datasheet-sourced.

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
