---
date: 2026-09-07
problem_type: architecture_pattern
category: architecture-patterns
module: builds
component: pcb_editing
severity: high
applies_when:
  - "Adding, removing, or swapping a footprint on a .kicad_pcb without the KiCad GUI available"
  - "pcbnew Python scripting is unavailable or known to segfault in this environment"
  - "A board file might be open in someone else's live KiCad session"
  - "Any raw S-expression edit to a .kicad_sch or .kicad_pcb that isn't immediately visually inspectable"
tags:
  - kicad
  - pcb
  - footprint
  - automation
  - datasheet-verification
  - safety
related_components:
  - docs/tools/isolation_envelope.py
  - docs/solutions/architecture-patterns/schematic-pin-y-sign-when-hand-wiring.md
  - docs/solutions/architecture-patterns/pcbnew-bulk-removal-segfault.md
  - builds/6s/50A/CAN_485_faraday
---

# Editing a .kicad_pcb by hand: check the lock first, verify by DRC after, never trust the diff

## Context

Swapping `U1`'s footprint (PM LQFP-64 -> RHB VQFN-32) across four board variants could not go through KiCad's own "Update PCB from Schematic" — that requires the GUI, and `pcbnew` Python scripting in this environment has a known segfault on footprint removal (`docs/solutions/architecture-patterns/pcbnew-bulk-removal-segfault.md`). The only path left was hand-editing the `.kicad_pcb` S-expression directly: delete the old `(footprint "LQFP-64_10x10mm_P0.5mm" ...)` block, insert a new one built from the real system footprint file (`Package_DFN_QFN.pretty/Texas_RHB0032E_...kicad_mod`), with every pad wired to the correct net.

Two failure modes are easy to hit doing this, one before the edit and one after:

1. **The file might already be open in someone's live KiCad session.** One of this repository's own PCBs (`CAN_485_faraday_faceted`) was mid-edit in a running `kicad` process while this work was happening on a sibling board. Writing to a file KiCad already has loaded in memory is invisible at write time — no lock error, no warning — but the next GUI save from that session overwrites the disk file with whatever was in memory, silently discarding the change just made.
2. **A "successful" edit that parses fine can still be electrically wrong**, and a huge textual diff (KiCad rewrites the *entire* file's formatting on its own next save, so even an untouched board can show a multi-thousand-line diff) makes visual review useless as a correctness check.

## Guidance

**Before writing to any `.kicad_sch` or `.kicad_pcb`:**

```bash
find <repo> -iname "*.lck"                       # KiCad's own lock file, if the GUI has it open
ps aux | grep -i kicad | grep -v grep            # a running process on that exact path
```

If either turns up a hit on the target file, do not write to it. Wait for the lock/process to clear, or ask whoever has it open to close/save first. This is a five-second check against a class of data loss that has no error message.

**Building the replacement footprint block:**

1. Get the real land pattern from the actual KiCad system footprint (`.pretty` library), not from redrawing it by hand — pad positions, sizes, and layers all come from there verbatim.
2. Assign every pad's `(net N "Name")` by cross-referencing the board's own existing `(net N "Name")` table (near the top of the file) — never invent a net ID. If a pad's correct net assignment is genuinely unverified (e.g., an exposed thermal pad with no confirmed primary-source guidance on what it should tie to), leave it with no net and say so in the footprint's own `Description` property, rather than guessing GND by convention.
3. **Stage new/replacement parts off-board** (placed at fixed coordinates clearly outside the board's own `Edge.Cuts` bounding box) rather than guessing a final position or auto-placing. Final placement is a real engineering decision (creepage, thermal, EMI) that belongs to whoever is doing layout, not to whoever is doing the swap.

**After writing:**

- `python3 -c "s=open(path).read(); assert s.count('(')==s.count(')')"` — confirms the S-expression is at least structurally closed before any KiCad tool touches it.
- Run `kicad-cli pcb drc` (or `sch erc`) **before and after**, and diff the violation/unconnected *counts and categories*, not the raw report text (report ordering/uuids will differ run to run). Identical counts before and after is the actual proof nothing broke — not "the file loaded without error," and not visual inspection of a multi-thousand-line diff. A DRC/ERC report is the only artifact in this workflow that reflects electrical truth rather than textual form.
- If the count changes, don't assume the new part caused it — the *existing* violations on file (from an in-progress manual layout, for example) are not your concern to fix, only to not add to.

## Why This Matters

`kicad-cli` makes both halves of this workflow possible without ever opening the GUI: it can validate structural/electrical correctness (`sch erc`, `pcb drc`, `sch export netlist --format kicadxml`) as fast as it can be invoked, which means "I edited a KiCad file by hand" no longer has to mean "and I have no way to check it except loading it and looking." The check is what makes hand-editing S-expressions a legitimate technique in this repository rather than something to avoid — the same discipline `schematic-pin-y-sign-when-hand-wiring.md` already established for wires (verify the specific pin/net pairing via netlist re-export, because a wrong coordinate fails silently) applies identically to footprints and nets.

The live-file check exists because this failure mode is asymmetric: it costs nothing to check, and the cost of skipping it — a colleague's in-progress manual layout work silently overwritten by their own next save — is not recoverable from the edit side at all.

## When to Apply

- Any programmatic edit to a `.kicad_sch` or `.kicad_pcb` in this repository, whenever the KiCad GUI ("Update PCB from Schematic," manual placement) is not the tool doing it.
- Before running any script that opens a board/schematic file for writing, even read-mostly tooling — the lock/process check costs nothing and the alternative is unrecoverable.
- Whenever a "the file loaded fine" result is being treated as sufficient verification — it isn't; DRC/ERC violation-count parity is.

## Related

- `docs/solutions/architecture-patterns/schematic-pin-y-sign-when-hand-wiring.md` — the matching discipline for hand-authored wires/labels (verify via netlist, not by eye)
- `docs/solutions/architecture-patterns/pcbnew-bulk-removal-segfault.md` — why `pcbnew` Python scripting isn't the alternative to this technique in this environment
- `TODO.md` §12.5.bg — the MCU package swap this pattern was developed for, across four board variants
