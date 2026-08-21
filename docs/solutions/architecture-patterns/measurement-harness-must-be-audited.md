---
date: 2026-08-19
problem_type: architecture_pattern
category: architecture-patterns
module: builds
component: measurement_harness
severity: high
applies_when:
  - "A script decides whether a layout change is kept or reverted"
  - "A tool reports a metric nobody has cross-checked against the drawing"
  - "Automating placement, alignment, or DRC cleanup on a dense board"
  - "A result looks clean and no one can say which check would have caught it"
tags:
  - measurement
  - kicad
  - drc
  - placement
  - automation
  - verification
related_components:
  - builds/6s/50A/CAN_485_faraday/kicad/tools/score_placement.py
  - builds/6s/50A/CAN_485_faraday/kicad/tools/align_rows_columns.py
  - builds/6s/50A/CAN_485_faraday/kicad/tools/symmetrize.py
---

# The harness is the thing most likely to be wrong

Automated layout work on this project is gated by `score_placement.py`: apply a
change, refill, score, keep or revert on the number. That discipline is sound
and it caught real regressions. But over two sessions **five separate defects
were found in the measuring apparatus itself**, and every one of them had
already produced a confident, wrong conclusion that was acted on.

None was found by reading the harness. Every one was found by a result that
did not match the drawing.

## The five

| # | Defect | What it asserted |
| --- | ------ | ------------------ |
| 1 | Measured pad **centres**, not edges | 7.68 mm where the true gap was 2.51 mm; hid a 77.6 mm perimeter part entirely |
| 2 | `edge_path` ignored along-edge separation | U3 vs Q2 read 7.83 mm; true unfolded path 27.15 mm |
| 3 | Read only kicad-cli's `violations` array | "DRC electrical 0" while the change broke two GND connections |
| 4 | Layer compared by display-name substring | "0 of 59 footprints have courtyards" — all 59 had them |
| 5 | Group centre from the **mean** | Would have centred a column at 15.900 and called it 16.000 |

## What each one teaches

**1 and 2 — geometry, not proxies.** Clearance and creepage are edge-to-edge
across a surface. A centre-to-centre distance is a different quantity that
happens to have the same units. Creepage between opposite faces runs *around
the board edge* as an unfolded path, `sqrt(along_edge² + (insetA + T +
insetB)²)` — not the board thickness plus two insets, which silently assumes
both parts sit at the same point along that edge. They rarely do.

**3 — a tool's output has more than one channel.** `kicad-cli pcb drc` reports
broken connections in `unconnected_items`, a *separate array* from
`violations`. A harness reading one array is structurally blind to the other,
and blind in the worst way: it returns a confident zero. When wrapping a tool,
enumerate what it can report before deciding what to read.

**4 — compare by identity, not by name.** KiCad 9's `GetLayerName()` returns
the display name `"F.Courtyard"`; the canonical string is `F.CrtYd`. Testing
`"CrtYd" in GetLayerName(...)` cannot match, and reports absence rather than
error. Compare against `pcbnew.F_CrtYd` — the ID. The same applies to
`GetBoardEdgesBoundingBox()`, which measures the **outer extent of the
Edge.Cuts stroke** and overstates the board by one line width;
`GetBoardPolygonOutlines()` is the outline. That 0.05 mm has now caused two
separate errors here.

**5 — the summary statistic encodes an assumption.** The mean of a column
whose members include one deliberately offset part is not that column. The
median is. Ask what the number is *for* before picking how to reduce a group
to one value.

## The pattern

Each defect made the harness **more permissive or more alarming than reality**,
and in both directions the failure was silent. A wrong number does not raise;
it gets believed, written into a commit message, and acted on. In this project
one such number was committed under a message asserting DRC results the
committed file did not have.

**So: a harness earns trust by being checked against the artefact, not by
being read.** Before trusting a metric to gate real changes, hand-verify one
case against the drawing — pick the result you would be most embarrassed to
have wrong, and measure it independently.

## Two corollaries for automated placement

**The majority is not automatically the target.** `align_rows_columns.py`
first snapped outliers onto whatever position most of a group shared. On the
high-side FETs that moved Q1 *away* from its gate driver and lengthened the
worst gate loop, so the guard reverted it and the row stayed crooked. The
right move was the opposite — bring the majority to the minority — which
aligned all six FETs *and* shortened the commutation loop. Score every
candidate, not the popular one.

**Cosmetic goals can conflict, and the conflict is arithmetic.** Centring a
mirror pair splits its separation in half, so a pair 8.500 mm apart lands at
±4.250 — symmetric and off a 0.5 mm grid. Symmetry and grid alignment coexist
only when separations are whole millimetres. When resolving it, round in the
direction that is *electrically* safer: this board's pack terminals went
outward, 8.500 → 9.000, gaining clearance rather than losing it.

## Related

- [[isolation-geometry-sets-board-aspect]] — the creepage geometry that
  defects 1 and 2 were mismeasuring.
