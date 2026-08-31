#!/usr/bin/env python3
"""Restore the inner copper planes by removing unjustified inner-layer
copper-pour keepouts from the board.

Governed by AGENTS.md.

POLICY
------
An inner copper layer on this board is a *plane* -- In1.Cu is a full-board
GND pour and In2.Cu is VM below y 60.5 mm and GND above it. A rule area that
forbids `copperpour` on an inner layer punches a hole in a plane, and a hole
in a plane is never free: it removes return-current continuity, removes
plane-to-plane overlap, and (on this build) removes the only shielding that
separates the two board faces.

So the default is: **no inner-layer copper-pour keepout unless the reason is
written down and still true.** This script enforces that default. It walks
every rule area, and for each one that forbids copper pour on In1.Cu or
In2.Cu it requires a matching entry in JUSTIFIED below. Anything not
justified has its inner layers stripped; its outer-layer scope is left
untouched, because that is a separate question this script does not decide.

WHY THE ISOLATION RULE AREA IS NOT JUSTIFIED
---------------------------------------------
Rule area 7c9dc61f (x 20.75-51.15, y 76.50-86.55 mm, all four copper layers)
is the isolation keepout. It was authored when the isolated transceivers U3
and U4 sat at that end of the board. They no longer do -- both are now at
y 34.50 mm on B.Cu -- so it guards nothing where it stands. This is already
recorded in TODO.md 12.5.z ("the keepout protects nothing"), 12.5.ae ("not
datasheet-driven and should be replaced, not relocated") and 12.5.an
("Still open: confirm the authored rule area over the phase terminals is
intended").

More than unnecessary, it is backwards. REFERENCES.md [9] p.17 asks for the
OPPOSITE on a 4-layer board:

    "place an embedded stitching capacitor between GND1 and GND2 using
     internal layers of the PCB planes. An embedded PCB capacitor is created
     when two metal planes in a PCB overlap each other and are separated by
     dielectric material. This capacitor provides a return path for high
     frequency common-mode noise currents across the isolation gap."

The full-width inner cut removes exactly the plane overlap [9] asks for. The
only keepout [9] specifies is narrow and conditional -- "there must not be a
GND2 fill on any layer below the L1 and L2 ferrites" -- an ISOLATED-ground
keepout around ferrites this design does not yet carry (TODO.md 12.5.ad).
The constraint that actually binds at the isolation barrier is creepage
(TODO.md 12.5.ac), which is a geometry rule, not a pour rule.

WHAT THIS SCRIPT DOES NOT DO
-----------------------------
It does not touch the outer-layer (F.Cu / B.Cu) scope of any rule area. On
this build that scope is independently suspect -- TODO.md 12.5.an measures
the phase pours stopping at the rule-area edge so that pour meets pad over
1.00 mm of a 10 mm J4 terminal pad -- but changing it alters 50 A current
paths and is a separate, signed-off decision (TODO.md 12.5.ae options a/b).

It does not invent a justification for any keepout. A rule area whose reason
is not in JUSTIFIED is stripped, and the reason it was stripped is printed.

Requires: pcbnew (KiCad 9.x Python bindings)

Usage:
    python3 tools/restore_inner_planes.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-31. AI-generated. The
# datasheet quotation above is transcribed from REFERENCES.md [9]; the
# TODO.md item numbers are this repository's own records. Not human-authored.
# Not yet human-reviewed.

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
BOARD = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"

INNER_LAYERS = (pcbnew.In1_Cu, pcbnew.In2_Cu)

# Rule areas permitted to keep an inner-layer copper-pour keepout, keyed by
# UUID. Each entry must state the reason and the record that carries it.
# Adding an entry here is a design decision, not a formality.
JUSTIFIED = {
    "923717e9-c736-477b-af1e-b493c4e582b8": (
        "VM island under U5's thermal-via ring: a 4.313 sq.mm floating VM "
        "plate on In2.Cu, fenced off by via clearance cutouts on three sides "
        "and the VM zone's own lower boundary on the fourth, with nothing on "
        "net VM inside it -- a floating plate under a switching gate driver. "
        "The zone's island_removal_mode was already ALWAYS and did not "
        "remove it. Scoped to In2.Cu only. TODO.md 12.5.an; created by "
        "tools/remove_vm_island.py."
    ),
}

# Probe points inside the terminal window, in mm, used to prove the inner
# planes actually fill there afterwards. Verifying the edited rule area is
# NOT sufficient -- a zone can be edited and still not fill (stale-fill trap,
# CLAUDE-MEMORY.md). These are checked against the filled polygons.
PROBES_MM = [
    (25.45, 80.50),  # under J4A phase terminal
    (35.95, 80.50),  # under J4B phase terminal
    (46.45, 80.50),  # under J4C phase terminal
    (35.95, 78.50),  # under U1 MCU body
    (28.00, 85.00),  # lower-left of the window
    (48.00, 85.00),  # lower-right of the window
]


def describe(board, zone):
    """Human-readable identity for a rule area."""
    lset = zone.GetLayerSet()
    layers = [board.GetLayerName(layer) for layer in lset.Seq()]
    box = zone.GetBoundingBox()
    return (
        f"{zone.m_Uuid.AsString()}  layers={layers}  "
        f"x {pcbnew.ToMM(box.GetLeft()):.2f}..{pcbnew.ToMM(box.GetRight()):.2f} "
        f"y {pcbnew.ToMM(box.GetTop()):.2f}..{pcbnew.ToMM(box.GetBottom()):.2f}"
    )


def probe_inner_fill(board):
    """Report, per inner layer, how many probe points sit in filled copper."""
    result = {}
    for layer in INNER_LAYERS:
        name = board.GetLayerName(layer)
        hits = []
        for mx, my in PROBES_MM:
            point = pcbnew.VECTOR2I(pcbnew.FromMM(mx), pcbnew.FromMM(my))
            covered = False
            for zone in board.Zones():
                if zone.GetIsRuleArea() or not zone.IsOnLayer(layer):
                    continue
                # Bind the polygon set to a live name before calling into it:
                # chaining off a temporary is the pcbnew SWIG trap that fails
                # open with no exception (CLAUDE-MEMORY.md).
                polys = zone.GetFilledPolysList(layer)
                if polys.Contains(point):
                    covered = True
                    break
            hits.append(covered)
        result[name] = hits
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(BOARD))

    print("=== rule areas found ===")
    to_strip = []
    for zone in board.Zones():
        if not zone.GetIsRuleArea():
            continue
        lset = zone.GetLayerSet()
        inner = [layer for layer in INNER_LAYERS if lset.Contains(layer)]
        if not zone.GetDoNotAllowCopperPour() or not inner:
            print(f"  skip     {describe(board, zone)}")
            continue
        uuid = zone.m_Uuid.AsString()
        if uuid in JUSTIFIED:
            print(f"  KEEP     {describe(board, zone)}")
            print(f"           justified: {JUSTIFIED[uuid]}")
            continue
        print(f"  STRIP    {describe(board, zone)}")
        print("           no justification recorded -- inner layers removed")
        to_strip.append((zone, inner))

    if not to_strip:
        print("\nnothing to do: every inner-layer pour keepout is justified")
        return 0

    print("\n=== inner-plane fill at probe points, BEFORE ===")
    before = probe_inner_fill(board)
    for name, hits in before.items():
        print(f"  {name}: {sum(hits)}/{len(hits)} probes in copper")

    for zone, inner in to_strip:
        lset = zone.GetLayerSet()
        for layer in inner:
            lset.RemoveLayer(layer)
        zone.SetLayerSet(lset)
        print(
            f"\nstripped {[board.GetLayerName(i) for i in inner]} from "
            f"{zone.m_Uuid.AsString()}"
        )
        remaining = [board.GetLayerName(l) for l in zone.GetLayerSet().Seq()]
        print(f"  remaining layers: {remaining}")

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("\nzones refilled")

    print("\n=== inner-plane fill at probe points, AFTER ===")
    after = probe_inner_fill(board)
    for name, hits in after.items():
        print(f"  {name}: {sum(hits)}/{len(hits)} probes in copper")

    gained = sum(
        sum(after[n]) - sum(before[n]) for n in after
    )
    print(f"\nprobe points newly covered by inner-plane copper: {gained}")
    if gained <= 0:
        print("WARNING: no probe point gained copper. The rule area was "
              "edited but the planes did not fill -- do not trust the edit.")

    if args.dry_run:
        print("\ndry run -- nothing written")
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = BOARD.with_suffix(f".kicad_pcb.{stamp}.bak")
    shutil.copy2(BOARD, backup)
    board.Save(str(BOARD))
    print(f"\nbacked up  {backup.name}")
    print(f"wrote      {BOARD.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
