---
date: 2026-09-07
problem_type: architecture_pattern
category: architecture-patterns
module: builds
component: schematic_editing
severity: medium
applies_when:
  - "Computing a symbol pin's absolute schematic position from its instance placement, to hand-author a wire or label in raw S-expression"
  - "A guessed wire/label coordinate silently fails to connect, with no parse error"
  - "Verifying a hand-edited .kicad_sch by netlist export rather than by eye"
tags:
  - kicad
  - schematic
  - erc
  - coordinate-transform
  - datasheet-verification
related_components:
  - builds/6s/50A/CAN_485_faraday_sameend
  - symbols/MSPM0G3518_Q1_PM.kicad_sym
---

# A symbol pin's Y offset flips sign going from library to page — verify by netlist, not by formula

## Context

Fixing 18 pre-existing `pin_not_connected` ERC errors on `CAN_485_faraday_sameend`'s power FETs (Q1-Q6, TPHR8504PL) required adding wires that land exactly on each floating pin's true schematic position, computed from the symbol's placement instance plus the pin's local `(at x y angle)` from the library definition — the same kind of hand-authored S-expression editing this repository already uses elsewhere (see `symbols/MSPM0G3518_Q1_PM.kicad_sym`'s own header, hand-written because `kiutils` isn't installed).

The naive transform — `absolute = instance_at + pin_at`, no rotation math needed since the instance itself was unrotated (`angle 0`) — worked perfectly for the FET's gate pin (`angle 0`) and appeared to work for its source pins (`angle 180`), matched exactly against real wire endpoints already in the file. It was then used, with full confidence, to place a label at the computed position of the FET's drain pins (`angle 270`). The label sat in empty space. No error, no warning — `kicad-cli sch erc` and `kicad-cli sch export netlist` both stayed completely silent about it; the pin just kept reporting `unconnected-(Q1-D-Pad5)` as if nothing had been added.

## Why This Matters

**The correct transform is `absolute_y = instance_y − pin_y`, not `instance_y + pin_y`.** The library editor's pin coordinates are authored in a Y-up convention; the schematic page is Y-down. This flip is invisible whenever the pin's local Y happens to be 0 (the gate pin, `y=0`, gave an identical answer either way) or when a pin's identity doesn't matter because it's symmetric with another one on the same net (the source pins, `y=±2.54`, both had real wires at the flipped AND unflipped position — one wire per pin either way — so the check "does a wire exist near my computed point" passed without ever confirming *which* pin it belonged to). The drain pins were the first case where the local Y was both nonzero and where getting it wrong put the guess in a location with nothing else nearby to coincidentally satisfy — which is exactly why it was caught: a rendered SVG crop of the area (`kicad-cli sch export svg`, then a cropped `viewBox` rasterized with ImageMagick) showed the real wire sitting on the *other* side of the pin row from where the formula placed it.

**A second, independent trap compounded the first and is worth keeping separate:** even with the correct coordinate, a single wire segment spanning all four parallel drain pins (5 through 8) connected only its own two *endpoints* — the two interior pins it merely passed through geometrically were not picked up. KiCad's connectivity model does not treat a pin sitting in the middle of a longer wire segment as connected; only wire endpoints (and explicit junctions) are connection nodes. The fix was three short two-point wire segments (5→6, 6→7, 7→8) rather than one long one, giving every pin a real vertex.

**The only check that actually matters is `kicad-cli sch export netlist` (or `sch erc --severity-error`, matching the CI invocation exactly) confirming the specific pin now appears on the intended net — not "does a wire exist near where I expect."** A coordinate that's off by a fixed, wrong sign, or a wire that merely overlaps a pin without terminating on it, produces no parse error and no ERC warning; it just leaves the netlist unchanged, silently.

## When to Apply

- Any time a wire, label, or junction is hand-authored in a `.kicad_sch` by computing a pin's page position from `instance_at + pin_at` (or any other formula) rather than reading it off KiCad's own rendering.
- Immediately after such an edit — before trusting it, before committing it — re-export the netlist (or run ERC at the same severity CI checks) and confirm the specific pin/net pairing, not just "no new errors."
- When bussing more than two pins together with wires: use one segment per adjacent pair, not one long segment across all of them.

## Related

- `TODO.md` §12.5.bg.2 — the fix this trap was found while making
- `symbols/specs/TPHR8504PL.json` — the verified 8-pin spec (1-3 Source, 4 Gate, 5-8 Drain) whose expansion from an older 3-pin stub is what left these pins unwired in the first place
- `docs/HANDOFF-mcu-swap-s32k144-to-mspm0g3518.md` §6 — kiutils unavailability, the reason symbols in this repo are hand-authored at all
