# Build: 6S / 50A / CAN-FD + RS-485 / Faraday / Opposite-end egress / Faceted

Governed by [`AGENTS.md`](../../../../AGENTS.md). Per-build instantiation of
the axis options in the repo-root [`README.md`](../../../../README.md).

**Parent build:** [`../CAN_485_faraday/`](../CAN_485_faraday/) — the original
build, **opposite-end** wire egress (pack in at one board end, phases out at
the other; this is the `Wire Egress = Opposite-end` default, carrying no
suffix in the parent's own name). This variant differs on the **Form
Factor** axis and inherits the parent's entire BOM and schematic. The BOM is
deliberately **not** duplicated here.

**Sibling build:**
[`../CAN_485_faraday_sameend_faceted/`](../CAN_485_faraday_sameend_faceted/)
— the same Form Factor value applied to the **same-end** egress parent
instead. Both faceted builds share an identical component set and an
identical functional partition (below), because both parent boards are
instantiated from the same schematic and differ only in where the five power
conductors terminate — a fact this build's placement run confirms rather
than assumes.

**Status: INITIAL PLACEMENT DONE. Not routed. Not fabricable.** Every
footprint is placed inside a 23.00 mm strip with zero courtyard overlaps and
zero DRC errors. No copper, no stackup, no interconnect part. AI-generated
by **Claude Opus 5** (Anthropic), 2026-09-05. Not human-reviewed.

## Requested build parameters

| Axis | Selection | Same as parent? |
| --- | --- | --- |
| Voltage / Amperage | 6S / 50A | yes |
| Protocol | CAN-FD **and** RS-485 | yes |
| EMI Hardening | Faraday | yes |
| Wire Egress | Opposite-end (default) | yes |
| **Form Factor** | **Faceted** (two panels, placed) | **NO — this variant** |

## 1. Functional partition and placement, run fresh against this parent

[`docs/tools/facet_placement.py`](../../../../docs/tools/facet_placement.py)
re-derives the functional partition from **this** board's own netlist —
it does not assume the sibling build's assignment — and produces:

```text
Panel P (power stage): 30 parts, 23.00 x 89.51 mm
  rotated 90 deg to fit strip width: SH1
Panel L (logic/comms):  35 parts, 23.00 x 61.68 mm
```

**Identical to the same-end sibling build's numbers**, part-for-part and
millimetre-for-millimetre. That is not a coincidence to wave past: it is the
expected result, because Wire Egress only relocates the five terminal
footprints and their local copper — it changes nothing about which
components exist, which nets connect them, or the functional partition rule
(named power-stage/logic-comms cores, then net-majority propagation).
Confirming the two runs agree is what makes it safe to say the Form Factor
axis and the Wire Egress axis are **independent** on this design: choosing
one does not silently constrain the other.

## 2. Panel envelopes, as placed

| | Panel P | Panel L |
| --- | --- | --- |
| Parts | 30 | 35 |
| Strip width | 23.00 mm | 23.00 mm |
| Length (component-driven) | 89.51 mm | 61.68 mm |
| Combined envelope (side by side, 3 mm gap) | 49.00 × 89.51 mm | |

See the sameend-faceted sibling's README §2 for the placement-floor caveat
(this is a greedy shelf-pack, not a routing-aware layout) and the SH1
rotation rationale (§1 there) — both apply here unchanged.

## 3. Verification performed

Toolchain: KiCad **9.0.2** throughout. Output board remains
`version 20241229` / `generator_version "9.0"` — not advanced to KiCad 10.

| Check | Result |
| --- | --- |
| Courtyard overlaps (all 65 parts, both panels) | **0** |
| DRC errors | **0** |
| DRC warnings | 43 (`silk_edge_clearance` 7, `silk_over_copper` 23, `silk_overlap` 13 — all silkscreen, expected) |
| Unconnected items | 184 (expected — no copper exists yet) |
| Board format after write | `version 20241229` / `"9.0"` — unchanged |

## 4. What is not done

Same open list as the same-end sibling build (§4 there): no routing, no
stackup (`TODO.md` 15.2), SH1's rotated shielding geometry unverified against
the gate-drive loop, no interconnect part selected, panel length not
routing-aware, host envelope unconfirmed (`TODO.md` 16.3), and no mounting
scheme (`TODO.md` 16.4h).

**One item specific to this egress variant:** the opposite-end parent's
terminal geometry (pack and phase conductors at opposite board ends, per the
original build) has not been re-examined for whether it changes anything
about where the functional partition's panel boundary should physically fall
relative to the terminals once real placement — not just the functional
grouping — is considered. §1 confirms the *grouping* is identical; it does
not by itself confirm the *panel boundary location relative to each
terminal* is equally sensible for both egress variants.

## 5. Reproducing this placement

```bash
python3 docs/tools/facet_placement.py \
    --board builds/6s/50A/CAN_485_faraday/kicad/open_secure_esc_6s_50a_can485_faraday.kicad_pcb \
    --output kicad/open_secure_esc_6s_50a_can485_faraday_faceted.kicad_pcb \
    --strip-width 23.0 --gap 3.0 \
    --json kicad/placement.json
```

KiCad **9.0.2** only — see
[`docs/solutions/architecture-patterns/pcbnew-bulk-removal-segfault.md`](../../../../docs/solutions/architecture-patterns/pcbnew-bulk-removal-segfault.md)
for a pcbnew scripting trap this tool works around.
