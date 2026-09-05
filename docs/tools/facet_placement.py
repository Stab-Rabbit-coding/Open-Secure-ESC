#!/usr/bin/env python3
"""Initial component placement for a faceted (two-panel) 6S/50A board.

Governed by AGENTS.md. Fourth in the form-factor tool chain, after
strip_width.py (facet width budget), hinge_placement.py (fold/cut search on
an EXISTING geometric layout) and partition_panels.py (the FUNCTIONAL
partition that made the joint signal-only).

WHAT THIS SCRIPT DOES
----------------------
Starting from either flat parent board (opposite-end egress or same-end
egress -- both carry the same component set and the same functional
partition), it:

  1. Re-derives the functional panel assignment (same rule as
     partition_panels.py: named power-stage/logic-comms cores, everything
     else by iterated net-majority, fiducials split evenly).
  2. Shelf-packs each panel's footprints into rows that fit the strip width,
     rotating 90 deg any part that is too WIDE but fits the strip when
     rotated (this is how SH1, the 22.75 mm Faraday can, is made to fit a
     23.00 mm strip -- see the SH1 note below).
  3. Writes a NEW two-panel board: one rectangular Edge.Cuts outline per
     panel, side by side with a gap, footprints repositioned into their
     panel. Pad net assignments are preserved untouched, so the ratsnest is
     correct; every pre-existing track, via, zone and rule area is removed,
     because none of them describes valid copper for this geometry.

THIS IS PLACEMENT, NOT A ROUTED BOARD
---------------------------------------
No copper is drawn. TODO.md 15.2 (stackup), the interconnect part (BOM open
item), and routing are unchanged open items. DRC on the output board will
report a large unconnected-item count -- that is the correct, honest state
of an unrouted board, not a defect in this script.

THE SH1 FIT, MADE EXPLICIT
----------------------------
Un-rotated, SH1 (Wurth WE-SHC 3670209, 22.75 x 17.15 mm) is 22.75 mm wide --
against a 23.00 mm strip that leaves 0.25 mm total margin, which is not
workable (TODO.md 16.4e). Rotated 90 deg it presents 17.15 mm across the
strip and 22.75 mm along the panel's length, which fits with real margin.
This script performs that rotation and reports it; it does not silently
assume the can still shields the same nodes after rotating -- that is an
explicit open item in the build README.

WHAT THIS SCRIPT DOES NOT DO
-----------------------------
It does not decide 4-layer vs 6-layer, does not select an interconnect part,
does not draw a single track, and does not re-litigate the CoA (rigid-flex
vs separate boards) -- partition_panels.py already showed the joint is
signal-only, so either is viable and this script is agnostic to which. It
writes the geometry as two independent board outlines because that is the
form both options need in common (a rigid-flex build cuts the same shape
from one continuous flex layer; a separate-boards build fabricates each
outline as its own PCB).

Requires: pcbnew (KiCad 9.x). Do NOT run under KiCad 10 -- it would advance
the file format away from `version 20241229`.

Usage:
    python3 docs/tools/facet_placement.py \\
        --board <flat parent .kicad_pcb> \\
        --output <new two-panel .kicad_pcb> \\
        --strip-width 23.0 --gap 3.0
"""
# Authored by Claude Opus 5 (Anthropic) 2026-09-05. AI-generated. Placement
# is computed geometrically (shelf-packing) from measured courtyards; no
# part values, pin maps or copper rules are invented. Not human-authored.
# Not yet human-reviewed.

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pcbnew

CORE_POWER = re.compile(r"^(Q\d+|U5|U[678]|R[123]|J4[ABC]|J5[AB]|SH1)$")
CORE_LOGIC = re.compile(r"^(U[1234]|J[123]|FB[1-4])$")
FIDUCIAL = re.compile(r"^FID\d+$")

EDGE_MARGIN_MM = 0.5   # footprint courtyard to board edge
ROW_GAP_MM = 0.8       # vertical gap between shelf-pack rows
COL_GAP_MM = 0.8       # horizontal gap between parts in one row


def mm(v):
    return pcbnew.ToMM(v)


def fmm(v):
    return pcbnew.FromMM(v)


def assign_panels(board):
    """Same rule as partition_panels.py: named cores, then net-majority."""
    refs = [f.GetReference() for f in board.GetFootprints()]
    panel = {}
    for r in refs:
        if CORE_POWER.match(r):
            panel[r] = "P"
        elif CORE_LOGIC.match(r):
            panel[r] = "L"
        else:
            panel[r] = None

    net_members, part_nets = {}, {r: set() for r in refs}
    for f in board.GetFootprints():
        for pad in f.Pads():
            n = pad.GetNetname()
            if not n:
                continue
            net_members.setdefault(n, set()).add(f.GetReference())
            part_nets[f.GetReference()].add(n)
    uninformative = {n for n, m in net_members.items() if len(m) > len(refs) / 3}

    for _ in range(12):
        changed = False
        for ref in refs:
            if CORE_POWER.match(ref) or CORE_LOGIC.match(ref) or FIDUCIAL.match(ref):
                continue
            score = {"P": 0, "L": 0}
            for n in part_nets[ref] - uninformative:
                for other in net_members[n]:
                    if other == ref or panel.get(other) is None:
                        continue
                    score[panel[other]] += 1
            new = "P" if score["P"] > score["L"] else "L"
            if panel[ref] != new:
                panel[ref] = new
                changed = True
        if not changed:
            break

    fids = sorted(r for r in refs if FIDUCIAL.match(r))
    for i, ref in enumerate(fids):
        panel[ref] = "P" if i < len(fids) / 2 else "L"
    for ref in refs:
        if panel[ref] is None:
            panel[ref] = "L"
    return panel


def footprint_size(fp):
    """(width, height) of the current courtyard bounding box, in mm."""
    box = fp.GetBoundingBox(False, False)
    return mm(box.GetWidth()), mm(box.GetHeight())


def shelf_pack(footprints, strip_width_mm):
    """Greedy row packer. Returns (placements, panel_length_mm, rotated_refs).

    placements: list of (footprint, cx_mm, cy_mm) -- CENTRE position within
    the panel's own local frame (origin at the panel's top-left inside
    corner, i.e. after the edge margin).
    """
    usable = strip_width_mm - 2 * EDGE_MARGIN_MM
    sized = []
    rotated = []
    for fp in footprints:
        w, h = footprint_size(fp)
        if w > usable and h <= usable:
            fp.SetOrientationDegrees((fp.GetOrientationDegrees() + 90.0) % 360.0)
            w, h = footprint_size(fp)
            rotated.append(fp.GetReference())
        sized.append((fp, w, h))
    # Largest area first -- gives the packer its hardest constraints early.
    sized.sort(key=lambda t: -(t[1] * t[2]))

    placements = []
    y = EDGE_MARGIN_MM
    row, row_w, row_h = [], 0.0, 0.0
    for fp, w, h in sized:
        needed = w if not row else row_w + COL_GAP_MM + w
        if row and needed > usable:
            # close the row
            x = EDGE_MARGIN_MM
            for rfp, rw, rh in row:
                placements.append((rfp, x + rw / 2.0, y + row_h / 2.0))
                x += rw + COL_GAP_MM
            y += row_h + ROW_GAP_MM
            row, row_w, row_h = [], 0.0, 0.0
        row.append((fp, w, h))
        row_w = row_w + (COL_GAP_MM if len(row) > 1 else 0) + w
        row_h = max(row_h, h)
    if row:
        x = EDGE_MARGIN_MM
        for rfp, rw, rh in row:
            placements.append((rfp, x + rw / 2.0, y + row_h / 2.0))
            x += rw + COL_GAP_MM
        y += row_h + ROW_GAP_MM
    panel_length = y + EDGE_MARGIN_MM
    return placements, panel_length, rotated


def draw_rectangle(board, x0_mm, y0_mm, x1_mm, y1_mm, layer):
    corners = [(x0_mm, y0_mm), (x1_mm, y0_mm), (x1_mm, y1_mm), (x0_mm, y1_mm)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(layer)
        a, b = corners[i], corners[(i + 1) % 4]
        seg.SetStart(pcbnew.VECTOR2I(fmm(a[0]), fmm(a[1])))
        seg.SetEnd(pcbnew.VECTOR2I(fmm(b[0]), fmm(b[1])))
        board.Add(seg)


def strip_old_geometry(board):
    """Remove everything that described copper/outline for the OLD layout.

    Two pcbnew 9.0.2 (Debian package) SWIG binding traps, found by bisection
    while writing this script -- both are silent or delayed, neither raises
    at the point of the actual mistake:

    1. `board.GetDrawings()` (== `list(board.Drawings())`) becomes unusable
       -- raises `TypeError: 'SwigPyObject' object is not iterable` -- if
       called AFTER zones have been removed from the same live BOARD. The
       container accessor's return-type typemap does not survive a prior
       bulk zone removal. Fix: capture the Edge.Cuts drawings list BEFORE
       removing anything else.
    2. `board.Remove(item)` sets the C++ item's `thisown` flag so the SWIG
       Python wrapper now owns it -- but no destructor is wrapped for
       ZONE/PCB_SHAPE/PCB_TRACK, so when Python's GC later tries to free it
       (at latest, at interpreter exit) it corrupts the heap. This does NOT
       raise a Python exception and does NOT stop `board.Save()` from
       writing a fully correct file -- the crash (SIGSEGV, exit 139) lands
       after the file is safely on disk, during process teardown. But it
       still fails the shell command, and relying on "the crash is harmless"
       without proof would be exactly the kind of claim AGENTS.md Sec.1.3
       forbids. Fix: immediately after `board.Remove(item)`, set
       `item.thisown = False` so SWIG never attempts to destroy it.

    Verified by reload: `pcbnew.LoadBoard()` on the output of this function
    (post-fix) reports 0 zones, 0 tracks, and only non-Edge.Cuts drawings
    remaining, with a clean process exit.
    """
    edge_cuts = [d for d in board.GetDrawings()
                 if board.GetLayerName(d.GetLayer()) == "Edge.Cuts"]
    for zone in list(board.Zones()):
        board.Remove(zone)
        zone.thisown = False
    for track in list(board.Tracks()):
        board.Remove(track)
        track.thisown = False
    for drawing in edge_cuts:
        board.Remove(drawing)
        drawing.thisown = False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--board", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--strip-width", type=float, default=23.0)
    ap.add_argument("--gap", type=float, default=3.0,
                    help="gap between the two panel outlines, mm")
    ap.add_argument("--json", help="write placement report to this path")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(args.board)
    panel = assign_panels(board)

    by_panel = {"P": [], "L": []}
    for f in board.GetFootprints():
        by_panel[panel[f.GetReference()]].append(f)

    report = {"strip_width_mm": args.strip_width, "panels": {}}
    panel_origin_x = {}
    cursor_x = 0.0
    for want, name in (("P", "power stage"), ("L", "logic/comms")):
        placements, length, rotated = shelf_pack(by_panel[want], args.strip_width)
        panel_origin_x[want] = cursor_x
        for fp, cx, cy in placements:
            fp.SetPosition(pcbnew.VECTOR2I(
                fmm(cursor_x + cx), fmm(cy)))
        report["panels"][want] = {
            "name": name,
            "count": len(placements),
            "width_mm": round(args.strip_width, 3),
            "length_mm": round(length, 3),
            "rotated_to_fit": rotated,
            "x_origin_mm": round(cursor_x, 3),
        }
        print(f"Panel {want} ({name}): {len(placements)} parts, "
              f"{args.strip_width:.2f} x {length:.2f} mm")
        if rotated:
            print(f"  rotated 90 deg to fit strip width: {', '.join(rotated)}")
        cursor_x += args.strip_width + args.gap

    max_length = max(p["length_mm"] for p in report["panels"].values())

    strip_old_geometry(board)
    for want in ("P", "L"):
        x0 = panel_origin_x[want]
        draw_rectangle(board, x0, 0.0, x0 + args.strip_width, max_length,
                        pcbnew.Edge_Cuts)

    board.Save(args.output)
    print(f"\nwrote {args.output}")
    print(f"combined envelope (two panels + gap): "
          f"{cursor_x - args.gap:.2f} x {max_length:.2f} mm "
          f"(panels are independent boards; this is footprint only, not "
          f"real panel bounding stock)")

    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2) + "\n")
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
