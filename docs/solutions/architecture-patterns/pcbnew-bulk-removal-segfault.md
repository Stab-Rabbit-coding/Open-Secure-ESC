---
date: 2026-09-05
problem_type: architecture_pattern
category: architecture-patterns
module: builds
component: pcbnew_scripting
severity: high
applies_when:
  - "A pcbnew script bulk-removes zones, tracks, or drawings from a live BOARD"
  - "A script calls board.GetDrawings() / board.Zones() / board.Tracks() more than once in one process"
  - "A pcbnew script exits 139 (SIGSEGV) after its last print statement, with no Python traceback body"
  - "board.Save() appears to have worked but the shell command still reports failure"
tags:
  - pcbnew
  - kicad
  - swig
  - segfault
  - scripting
  - placement
related_components:
  - docs/tools/facet_placement.py
  - CLAUDE-MEMORY.md
---

# pcbnew bulk item removal segfaults at process exit unless `thisown` is cleared

## Context

Writing `docs/tools/facet_placement.py` (initial component placement for the
faceted 6S/50A form factor) required stripping a flat board's tracks, zones,
and Edge.Cuts drawings before redrawing two panel outlines. The obvious
pattern — `for z in list(board.Zones()): board.Remove(z)` — is what every
public pcbnew scripting example shows, and it is not safe on this binding
(KiCad 9.0.2, Debian package, `pcbnew 9.0.2+dfsg-1`).

Two independent traps stacked here, and both are silent or delayed — neither
raises at the point of the actual mistake, which is what made this expensive
to isolate (this took roughly a dozen bisection runs against a real board to
pin down, per `CLAUDE-MEMORY.md`'s own standing note that pcbnew SWIG bugs
"fail open" rather than loudly).

## Guidance

**Trap 1 — a board-level container accessor breaks after a prior bulk
removal, with a misleading error.**

```
File ".../pcbnew.py", line 20244, in GetDrawings
    def GetDrawings(self): return list(self.Drawings())
TypeError: 'SwigPyObject' object is not iterable
```

`board.GetDrawings()` (and independently, `board.Zones()` / `board.Tracks()`
called for introspection rather than removal) can raise this **only if**
zones were removed earlier in the same process. The error reads like a type
mismatch in your own code; it is actually the container accessor's
return-type typemap failing after the board's internal item lists have been
mutated by removal. **Fix: capture every list you will need (e.g. the
Edge.Cuts drawings) BEFORE removing anything, in one pass, and never call
these accessors again afterward for introspection** (`len(...)`, `print`,
etc.) in the same process.

**Trap 2 — `board.Remove(item)` sets `thisown = True`, and no destructor is
wrapped for `ZONE` / `PCB_TRACK` / `PCB_SHAPE`.**

`Remove()`'s own docstring says exactly this: *"set the thisown flag so that
the python wrapper owns the C++ BOARD_ITEM."* Python's GC will eventually try
to free that object — at the latest, at interpreter shutdown — and since no
destructor exists for these types, that free corrupts the heap. This
produces the `swig/python detected a memory leak of type 'ZONE *', no
destructor found` warnings seen on every run (harmless on their own), and
**separately**, a SIGSEGV (exit 139) with no Python traceback body, which
looks like it happened at the very last `print()` but actually happens
during process teardown, well after `board.Save()` already wrote a correct
file. Confirmed by reloading the "crashed" output: it was complete and
correct every time. Relying on "the crash is harmless" without that reload
check would itself violate `AGENTS.md` §1.3 — an unverified claim is not
a fact.

**Fix: immediately after `board.Remove(item)`, set `item.thisown = False`.**
This tells SWIG never to attempt the destructor call, which is exactly what
you want for an object the board no longer owns and nothing else references.

```python
for zone in list(board.Zones()):
    board.Remove(zone)
    zone.thisown = False        # <- prevents the exit-time SIGSEGV
```

**Bisection method that found this**, worth reusing: isolate each suspected
statement into its own one-line `python3 -` invocation, run it 3-4 times
(not once — the corruption is heap-layout-dependent and can pass by luck),
and check the **process exit code**, not just stdout. `print()` output
appearing before a crash does not mean the crash happened where it looks
like it happened; buffering means completed stdout content is not evidence
about ordering relative to a later exit-time process teardown fault.

## Related

`CLAUDE-MEMORY.md`'s `pcbnew-swig-chained-call-trap` entry already documents
a sibling issue in the same binding (`GetBoundingBox().Inflate(k)` collecting
a temporary before `.Contains()` runs). Both traps share the same root cause:
this SWIG binding does not manage C++ object lifetime the way idiomatic
Python code assumes, and both fail in ways that produce no exception at the
point of the actual error.
