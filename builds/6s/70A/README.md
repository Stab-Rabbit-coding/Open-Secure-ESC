# Builds: 6S / 70A (Serenity-UAV 64 mm nacelle, issue 23)

Governed by [`AGENTS.md`](../../../AGENTS.md). Plan:
[`docs/plans/2026-11-22-001-feat-70a-nacelle64-esc-sprint-plan.md`](../../../docs/plans/2026-11-22-001-feat-70a-nacelle64-esc-sprint-plan.md).
Index: `TODO.md` §19.

**Status: no board exists.** This folder holds the cross-repo baseline only.
The two build folders are created in U3 (plan KTD5):

| ESC | Folder | Wire egress |
| --- | --- | --- |
| A (forward motor) | `CAN_485_faraday_sameend_faceted/` | all leads forward |
| B (aft motor) | `CAN_485_faraday_faceted/` | pack and signal forward, phases aft |

> **WARNING** — The G1 envelope in issue 23 is invalid (Serenity-UAV
> `3d23e68`, WBS NAC-64-ESC-SKIN-RAY). Do not place or route a board here
> before Gate E (a corrected envelope posted on issue 23).

## Cross-repo baseline (U1, 2026-11-22)

The Serenity-UAV harness was pinned and its own regression tests were run.

| Item | Value |
| --- | --- |
| Repository / branch | `Stab-Rabbit-coding/Serenity-UAV`, `Theme-N-S2-S6` |
| Pinned commit | `3d23e68` ("Fix ESC bay skin ray cast: it read the far side of the pod") |
| Files used | `tools/esc70_design.json`, `tools/esc80_cooptimize.py`, `tools/nacelle_esc_bay_fit.py`, `tools/esc_f1_pivot_iter.py`, `airframe/stls/nacelles/eng_left_shell24_50mm_repaired.stl` |
| Harness tests | `tools/tests/test_esc80_cooptimize.py`: 15 passed, including `test_model1_golden_unchanged` (−60.51) and `test_skin64_reads_the_near_side` |
| Python deps beyond the Build environment | `trimesh`, `rtree`, `shapely`, `pytest` (Serenity-UAV `requirements-dev.txt`) |

Issue 23's per-bay areas and "today" figures, including the 154.6 °F
(68.1 °C) channel temperature, predate `3d23e68`. They are not used as
goldens.

## Harness bend radius

Serenity-UAV cites "NASA-STD-8739.4A Chg 3 Table 7-1, 3× OD minimum". The
3 × OD minimum was confirmed in the current Change 4 copy [69] (Table 7-1,
p. 30) for an overall harness of AWG 10 or smaller without coaxial cable.

> **CAUTION** — Table 7-1 sets the minimum bend radius to 10 × OD for
> polyimide (Kapton) insulated wire, or for any harness that includes it
> [69]. For a Kapton-insulated lead, a 3 × OD loop is below that minimum.
>
> U9 shall check the insulation of every lead against Table 7-1.
