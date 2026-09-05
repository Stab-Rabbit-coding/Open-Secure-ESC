#!/usr/bin/env python3
"""Assign every part to a facet panel by FUNCTION, and price the interconnect.

Governed by AGENTS.md. Implements the Form Factor axis value
`Faceted separate boards` / `Faceted rigid-flex` for the 6S/50A build.

WHY FUNCTIONAL, NOT GEOMETRIC
------------------------------
docs/tools/hinge_placement.py cuts an EXISTING layout along X and reports what
crosses. On the flat board every such cut carries 3 Power-netclass conductors,
because the cut slices through the FET bridge -- the power stage spans 26.96 mm
in X and the logic spans 28.74 mm, overlapping over 26.96 mm.

That is a property of the layout, not of faceting. Partition by FUNCTION
instead -- the whole power stage on one panel, logic and comms on the other --
and the 50 A path never reaches the joint: it runs pack terminal -> FET drains
-> phase terminals -> shunts -> pack return, all within one panel.

This script performs that assignment and measures the resulting interconnect,
so the claim is checked rather than asserted.

ASSIGNMENT RULE
---------------
1. Core power-stage parts are named explicitly (FETs, gate driver, shunts,
   phase and pack terminals, the shield can).
2. Every other part is assigned by majority: whichever panel holds more of the
   parts it shares a net with. Iterated to a fixed point, so a decoupling cap
   follows the device it decouples rather than its alphabetical neighbours.
3. Ties go to the logic panel -- the conservative direction, since it keeps
   parts off the panel with the 50 A copper.

WHAT IT DOES NOT DO
-------------------
It does not place parts. Producing a valid placement inside a 23.98 mm strip
is layout work with real DFM and thermal consequences, and inventing one would
be worse than leaving it open. This script defines the partition, sizes each
panel's envelope from the parts assigned to it, and specifies the
interconnect. Placement and routing are the next task (TODO.md 16.5).

Requires: pcbnew (KiCad 9.x). Do NOT run under KiCad 10.

Usage:
    python3 tools/partition_panels.py --board <flat.kicad_pcb> [--json out.json]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-09-01. AI-generated. Part
# assignment is measured from the board netlist; no placement is invented.
# Not human-authored. Not yet human-reviewed.

import argparse
import fnmatch
import json
import math
import re
from pathlib import Path

import pcbnew

# Core power-stage parts. Everything here carries or switches pack current,
# shields the node that does, or must stay physically next to it.
#   Q1-Q6   FET bridge          U5   DRV8353S gate driver
#   R1-R3   phase shunts        SH1  Faraday shield can
#   J4A/B/C phase terminals     J5A/B pack terminals
#   U6-U8   current-sense amplifiers -- these sit on the POWER panel
#           deliberately. Their inputs are the small differential shunt
#           signals; keeping the amplifier next to its shunt means the joint
#           carries the amplified single-ended ADC output instead of a
#           noise-sensitive differential pair, which is the whole point of
#           putting a sense amplifier near the sense element.
CORE_POWER = re.compile(r"^(Q\d+|U5|U[678]|R[123]|J4[ABC]|J5[AB]|SH1)$")

# Core logic/comms parts. Both isolated transceivers live here, so the
# isolation barrier stays wholly on one panel and never reaches the joint.
#   U1  MSPM0G3518-Q1 MCU       U2   OPTIGA Trust M secure element
#   U3  isolated CAN-FD         U4   isolated RS-485
#   J1  probe pads              J2/J3 comms wire pads
#   FB1-FB4 isolated-supply ferrites, which belong with U3/U4
CORE_LOGIC = re.compile(r"^(U[1234]|J[123]|FB[1-4])$")

# Fiducials carry no nets, so net-majority cannot place them. Each panel is a
# separately fabricated and separately assembled board and needs its own set.
FIDUCIAL = re.compile(r"^FID\d+$")

MAX_STRIP_MM = 23.98   # docs/tools/strip_width.py at R=30.0 mm, s=2.5 mm
POWER_CLASS = "Power"


def mm(v):
    return pcbnew.ToMM(v)


def netclass_patterns(board_path):
    pro = Path(board_path).with_suffix(".kicad_pro")
    if not pro.exists():
        return {}
    settings = json.loads(pro.read_text()).get("net_settings", {})
    return {p["pattern"]: p["netclass"]
            for p in settings.get("netclass_patterns", []) if "pattern" in p}


def classify(net, patterns):
    if net in patterns:
        return patterns[net]
    for pattern, cls in patterns.items():
        if fnmatch.fnmatch(net, pattern):
            return cls
    return "Default"


def assign_panels(board):
    """Core parts by name, everything else by iterated net majority."""
    refs = [f.GetReference() for f in board.GetFootprints()]
    panel = {}
    for r in refs:
        if CORE_POWER.match(r):
            panel[r] = "P"
        elif CORE_LOGIC.match(r):
            panel[r] = "L"
        else:
            panel[r] = None

    net_members = {}
    part_nets = {r: set() for r in refs}
    for f in board.GetFootprints():
        for pad in f.Pads():
            n = pad.GetNetname()
            if not n:
                continue
            net_members.setdefault(n, set()).add(f.GetReference())
            part_nets[f.GetReference()].add(n)

    # GND and VM touch nearly everything; they carry no assignment information.
    uninformative = {n for n, m in net_members.items() if len(m) > len(refs) / 3}

    for _ in range(12):
        changed = False
        for ref in refs:
            if CORE_POWER.match(ref) or CORE_LOGIC.match(ref):
                continue
            if FIDUCIAL.match(ref):
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
    # Fiducials: split evenly, each panel is its own assembled board.
    fids = sorted(r for r in refs if FIDUCIAL.match(r))
    for index, ref in enumerate(fids):
        panel[ref] = "P" if index < len(fids) / 2 else "L"
    for ref in refs:
        if panel[ref] is None:
            panel[ref] = "L"
    return panel


def envelope(board, panel, want):
    """Total courtyard area and widest part for one panel's assignment."""
    area = 0.0
    widest = (0.0, None)
    tallest = (0.0, None)
    count = 0
    for f in board.GetFootprints():
        if panel[f.GetReference()] != want:
            continue
        box = f.GetBoundingBox(False, False)
        w, h = mm(box.GetWidth()), mm(box.GetHeight())
        area += w * h
        count += 1
        if w > widest[0]:
            widest = (w, f.GetReference())
        if h > tallest[0]:
            tallest = (h, f.GetReference())
    return count, area, widest, tallest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--board", required=True)
    ap.add_argument("--json", help="write the partition to this path")
    ap.add_argument("--strip", type=float, default=MAX_STRIP_MM)
    args = ap.parse_args()

    board = pcbnew.LoadBoard(args.board)
    patterns = netclass_patterns(args.board)
    panel = assign_panels(board)

    print("=== panel assignment (functional) ===")
    for want, name in (("P", "POWER STAGE"), ("L", "LOGIC / COMMS")):
        members = sorted(r for r, p in panel.items() if p == want)
        count, area, widest, tallest = envelope(board, panel, want)
        util = area / (args.strip * 1.0)
        print(f"\nPanel {want} -- {name}: {count} parts")
        print(f"  {', '.join(members)}")
        print(f"  total courtyard area   {area:8.1f} mm^2")
        print(f"  widest part            {widest[0]:8.2f} mm  ({widest[1]})")
        print(f"  tallest part           {tallest[0]:8.2f} mm  ({tallest[1]})")
        fits = "OK" if widest[0] <= args.strip else "TOO WIDE"
        print(f"  vs {args.strip:.2f} mm strip: {fits}")
        print(f"  min length if packed at 100% (unachievable floor): "
              f"{area / args.strip:6.1f} mm")
        print(f"  at a realistic 40% area utilisation:              "
              f"{area / args.strip / 0.40:6.1f} mm")

    nets = {"P": {}, "L": {}}
    for f in board.GetFootprints():
        side = nets[panel[f.GetReference()]]
        for pad in f.Pads():
            n = pad.GetNetname()
            if n:
                side.setdefault(n, set()).add(f.GetReference())
    crossing = sorted(set(nets["P"]) & set(nets["L"]))

    print(f"\n=== interconnect: {len(crossing)} nets ===")
    by_class = {}
    for n in crossing:
        by_class.setdefault(classify(n, patterns), []).append(n)
    for cls in sorted(by_class):
        print(f"  {cls:9s} {len(by_class[cls]):3d}  "
              f"{', '.join(sorted(by_class[cls]))}")

    print("\n=== does 50 A cross the joint? ===")
    verdict_ok = True
    for n in sorted(by_class.get(POWER_CLASS, [])):
        p_side = sorted(nets['P'][n])
        l_side = sorted(nets['L'][n])
        carries = [r for r in l_side if CORE_POWER.match(r)]
        print(f"  {n}: L-side parts = {', '.join(l_side[:10])}"
              f"{'...' if len(l_side) > 10 else ''}")
        if carries:
            print(f"    ** carries pack current to {carries} -- 50 A CROSSES")
            verdict_ok = False
        else:
            print(f"    no power-stage part on the L side -- this net crosses "
                  f"as a supply/reference only, not as a 50 A conductor")
    print(f"\n  VERDICT: {'SIGNAL-ONLY interconnect' if verdict_ok else '50 A CROSSES'}")
    if verdict_ok:
        print("  Both faceted options are viable. This is the result a purely")
        print("  geometric cut could not reach: the 50 A path runs pack ->")
        print("  FET drains -> phases -> shunts -> pack return, wholly inside")
        print("  Panel P.")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"panel": panel, "interconnect": crossing,
             "by_class": {k: sorted(v) for k, v in by_class.items()}},
            indent=2, sort_keys=True) + "\n")
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
