#!/usr/bin/env python3
"""HINGE PLACEMENT -- where a faceted rigid-flex board is allowed to fold.

Governed by AGENTS.md. Third of the form-factor trio, after
strip_width.py (how wide a facet may be) and isolation_envelope.py (how wide
the board must be).

WHY MAX STRIP WIDTH IS THE WRONG PLACE TO FOLD
-----------------------------------------------
strip_width.py answers "how wide a flat facet fits the bore". Folding AT that
width is almost always wrong, because the fold line is a physical constraint
on the layout, not just a dimension:

  * **Nothing rigid may straddle a hinge.** A package bridging the fold is
    not a tight fit, it is an unbuildable board.
  * **A hinge is a wiring bottleneck.** Every net crossing it becomes a flex
    conductor, and flex copper is thin. Folding where few nets cross is worth
    more than folding at the widest legal facet.
  * **High-current pours should not cross.** On a 3-phase stage the natural
    fold is a phase boundary -- e.g. two phases on one panel and the third on
    the other -- so no 50 A pour has to survive a bend.

So the optimiser searches the free corridors between components for the fold
that satisfies the width budget AND minimises crossings, rather than folding
at the maximum.

WHAT IT REPORTS
---------------
  * every corridor along the fold axis wide enough to host a hinge;
  * for a proposed fold, the exact parts that block it, if any;
  * for each candidate partition: per-panel width, sagitta and arc, the fold
    angle at each hinge, and the nets and pours that cross it.

HINGE WIDTH IS NOT A REPOSITORY FACT
-------------------------------------
The minimum corridor a flex hinge needs depends on bend radius, flex-zone
layer count and copper weight. **No flex or rigid-flex standard is catalogued
in REFERENCES.md** -- neither IPC-2223 nor IPC-6013 has been obtained -- so
--hinge-width is an INPUT with no defensible default. The 1.0 mm used when
the flag is omitted is a placeholder for arithmetic only and is marked
UNVERIFIED wherever it appears. Do not quote it as a design value.
(TODO.md 16.2.)

Usage:
    python3 docs/tools/hinge_placement.py --board <file.kicad_pcb>
    python3 docs/tools/hinge_placement.py --board <f> --propose 43.25
    python3 docs/tools/hinge_placement.py --board <f> --radius 30 --depth 2.5
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-31. AI-generated. Geometry is
# derivable by inspection; component extents are measured from the board file
# at run time. The hinge-width placeholder is explicitly not a design value.
# Not human-authored. Not yet human-reviewed.

import argparse
import fnmatch
import json
import math
from pathlib import Path

import pcbnew

PLACEHOLDER_HINGE_MM = 1.0
# Minimum width a panel needs if it holds BOTH sides of an isolation barrier.
# From docs/tools/isolation_envelope.py on this design's geometry, which is
# built on the 7.5 mm creepage of REFERENCES.md [9] Table 6.
ISOLATION_MIN_WIDTH_MM = 31.86
POWER_CLASSES = ("Power",)
DEFAULT_RADIUS_MM = 30.0
DEFAULT_DEPTH_MM = 2.5


def mm(value):
    return pcbnew.ToMM(value)


def sagitta(radius_mm, width_mm):
    half = width_mm / 2.0
    if half >= radius_mm:
        return float("nan")
    return radius_mm - math.sqrt(radius_mm**2 - half**2)


def arc_deg(radius_mm, width_mm):
    half = width_mm / 2.0
    if half >= radius_mm:
        return float("nan")
    return 2.0 * math.degrees(math.asin(half / radius_mm))


def load_extents(board):
    """Every footprint's span along X, as (lo, hi, reference)."""
    spans = []
    for footprint in board.GetFootprints():
        box = footprint.GetBoundingBox(False, False)
        spans.append((mm(box.GetLeft()), mm(box.GetRight()),
                      footprint.GetReference()))
    return sorted(spans)


def free_corridors(spans, x_lo, x_hi, min_width):
    """X intervals crossed by no footprint, wide enough for a hinge."""
    merged = []
    for lo, hi, _ in spans:
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    corridors, cursor = [], x_lo
    for lo, hi in merged:
        if lo - cursor >= min_width:
            corridors.append((cursor, lo))
        cursor = max(cursor, hi)
    if x_hi - cursor >= min_width:
        corridors.append((cursor, x_hi))
    return corridors


def blockers(spans, x_at):
    return [(lo, hi, ref) for lo, hi, ref in spans if lo < x_at < hi]


def crossing_nets(board, x_at):
    """Nets with pads on both sides of the fold -- these become flex."""
    left, right = {}, {}
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            net = pad.GetNetname()
            if not net:
                continue
            (left if mm(pad.GetCenter().x) < x_at else right)[net] = True
    return sorted(set(left) & set(right))


def crossing_pours(board, x_at):
    out = []
    for zone in board.Zones():
        if zone.GetIsRuleArea():
            continue
        box = zone.GetBoundingBox()
        if mm(box.GetLeft()) < x_at < mm(box.GetRight()):
            out.append(zone.GetNetname())
    return sorted(set(out))


def net_class_map(board_path):
    """net name -> netclass, resolved from the .kicad_pro patterns."""
    pro = Path(board_path).with_suffix(".kicad_pro")
    if not pro.exists():
        return {}
    settings = json.loads(pro.read_text()).get("net_settings", {})
    patterns = settings.get("netclass_patterns", [])
    return {p["pattern"]: p["netclass"] for p in patterns if "pattern" in p}


def classify(net, patterns):
    """Netclass for a net, honouring the pattern globs KiCad stores."""
    if net in patterns:
        return patterns[net]
    for pattern, cls in patterns.items():
        if fnmatch.fnmatch(net, pattern):
            return cls
    return "Default"


def shield_refs(board):
    """Rigid shielding cans -- these can never straddle a fold or a cut."""
    out = []
    for footprint in board.GetFootprints():
        fid = footprint.GetFPIDAsString()
        if "SHC" in fid or "Shield" in fid or "Frame" in fid:
            box = footprint.GetBoundingBox(False, False)
            out.append((mm(box.GetLeft()), mm(box.GetRight()),
                        footprint.GetReference(), mm(box.GetWidth())))
    return out


def isolation_report(board, x_at, patterns, panel_widths):
    """Does either panel hold both sides of an isolation barrier?"""
    sides = [{"iso": False, "non": False}, {"iso": False, "non": False}]
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            net = pad.GetNetname()
            if not net:
                continue
            index = 0 if mm(pad.GetCenter().x) < x_at else 1
            key = "iso" if classify(net, patterns) == "Isolated" else "non"
            sides[index][key] = True
    findings = []
    for index, side in enumerate(sides):
        if side["iso"] and side["non"]:
            width = panel_widths[index]
            ok = width >= ISOLATION_MIN_WIDTH_MM
            findings.append((index + 1, width, ok))
    return findings


def describe_partition(x_edges, radius, depth_budget):
    """Per-panel geometry for a fold at the given interior edges."""
    print(f"  {'panel':>7s} {'x range':>16s} {'width':>8s} "
          f"{'sagitta':>9s} {'arc deg':>9s}  fits?")
    total_arc = 0.0
    for index in range(len(x_edges) - 1):
        lo, hi = x_edges[index], x_edges[index + 1]
        width = hi - lo
        sag = sagitta(radius, width)
        ang = arc_deg(radius, width)
        total_arc += ang
        ok = "OK" if sag <= depth_budget else "TOO DEEP"
        print(f"  {index + 1:>7d} {lo:7.2f}..{hi:6.2f} {width:8.2f} "
              f"{sag:9.3f} {ang:9.2f}  {ok}")
    print(f"  total arc subtended: {total_arc:.2f} deg")
    for index in range(1, len(x_edges) - 1):
        a = arc_deg(radius, x_edges[index] - x_edges[index - 1])
        b = arc_deg(radius, x_edges[index + 1] - x_edges[index])
        print(f"  fold at x {x_edges[index]:.2f}: bend "
              f"{(a + b) / 2.0:.2f} deg from flat")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--board", required=True, help="path to .kicad_pcb")
    ap.add_argument("--radius", type=float, default=DEFAULT_RADIUS_MM)
    ap.add_argument("--depth", type=float, default=DEFAULT_DEPTH_MM)
    ap.add_argument("--hinge-width", type=float, default=PLACEHOLDER_HINGE_MM,
                    help="corridor a hinge needs (UNVERIFIED placeholder)")
    ap.add_argument("--propose", type=float, action="append", default=None,
                    help="test a fold at this X; repeatable")
    ap.add_argument("--optimize", action="store_true",
                    help="rank fold positions by pour crossings, flex "
                         "conductor count and parts that must move")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(args.board)
    box = board.GetBoardEdgesBoundingBox()
    x_lo, x_hi = mm(box.GetLeft()), mm(box.GetRight())
    max_strip = 2.0 * math.sqrt(2.0 * args.radius * args.depth - args.depth**2)

    print(f"board X {x_lo:.2f}..{x_hi:.2f}  ({x_hi - x_lo:.2f} mm wide)")
    print(f"host radius {args.radius:.2f} mm, depth budget {args.depth:.2f} mm")
    print(f"  -> max flat strip {max_strip:.2f} mm")
    print(f"  -> hinge corridor {args.hinge_width:.2f} mm "
          f"** UNVERIFIED placeholder, no flex standard catalogued "
          f"(TODO.md 16.2) **\n")

    if x_hi - x_lo <= max_strip:
        print("board already fits one facet -- no fold needed")
        return 0

    patterns = net_class_map(args.board)
    shields = shield_refs(board)
    if shields:
        print("rigid shielding cans (may not straddle a fold or joint):")
        for lo, hi, ref, width in shields:
            print(f"  {ref}  {lo:.2f}..{hi:.2f}  ({width:.2f} mm)")
        print()

    spans = load_extents(board)
    corridors = free_corridors(spans, x_lo, x_hi, args.hinge_width)
    print(f"=== free corridors >= {args.hinge_width:.2f} mm ===")
    if not corridors:
        print("  NONE. No fold line exists anywhere on this layout.")
    for lo, hi in corridors:
        interior = lo > x_lo + 0.01 and hi < x_hi - 0.01
        print(f"  x {lo:6.2f}..{hi:6.2f}  ({hi - lo:5.2f} mm)"
              f"{'' if interior else '   [board edge, not a fold site]'}")

    interior = [(lo, hi) for lo, hi in corridors
                if lo > x_lo + 0.01 and hi < x_hi - 0.01]
    if not interior:
        print("\n  No INTERIOR corridor: every candidate fold line is crossed")
        print("  by a component. Folding this board requires a re-layout that")
        print("  reserves a hinge corridor as a placement constraint.")
        print("\n=== what blocks the widest-legal fold ===")
        for ref_x in (x_lo + max_strip, x_hi - max_strip):
            hits = blockers(spans, ref_x)
            print(f"  at x {ref_x:.2f}: " + (", ".join(
                f"{r} ({lo:.2f}..{hi:.2f})" for lo, hi, r in hits) or "clear"))

    if args.optimize:
        print(f"\n=== optimiser: best fold positions ===")
        print("Ranked by what a fold actually costs. A high-current pour "
              "crossing the\nbend is the dominant penalty, then flex "
              "conductor count, then parts to move.\n")
        candidates = []
        step = 0.05
        x_at = x_lo + step
        while x_at < x_hi:
            widths = (x_at - x_lo, x_hi - x_at)
            if max(sagitta(args.radius, w) for w in widths) <= args.depth:
                nets = crossing_nets(board, x_at)
                power = [n for n in nets
                         if classify(n, patterns) in POWER_CLASSES]
                iso = [n for n in nets if classify(n, patterns) == "Isolated"]
                hits = blockers(spans, x_at)
                shield_bad = any(s[0] < x_at < s[1] for s in shields)
                cost = (100.0 * shield_bad + 10.0 * len(power)
                        + 2.0 * len(iso) + len(nets) + 0.5 * len(hits))
                candidates.append((cost, x_at, widths, nets, power, hits,
                                   iso, shield_bad))
            x_at += step
        if not candidates:
            print("  no fold position gives two panels within the depth "
                  "budget")
        else:
            # Collapse runs that score identically into their midpoint, so the
            # report lists distinct options rather than 0.05 mm neighbours.
            best, seen = [], set()
            for entry in sorted(candidates, key=lambda c: (c[0], c[1])):
                key = (round(entry[0], 2), tuple(entry[4]), len(entry[3]))
                if key in seen:
                    continue
                seen.add(key)
                best.append(entry)
                if len(best) >= 6:
                    break
            print(f"  {'x':>7s} {'panels mm':>16s} {'cond':>5s} "
                  f"{'pwr':>4s} {'iso':>4s} {'move':>5s} {'shield':>7s}  "
                  f"interconnect")
            for (cost, x_at, widths, nets, power, hits, iso,
                 shield_bad) in best:
                verdict = "POWER" if power else "signal-only"
                print(f"  {x_at:7.2f} {widths[0]:7.2f} +{widths[1]:7.2f} "
                      f"{len(nets):5d} {len(power):4d} {len(iso):4d} "
                      f"{len(hits):5d} {'STRADDLE' if shield_bad else 'ok':>7s}"
                      f"  {verdict}")
            print("\n  cond = conductors crossing; pwr = of those, Power "
                  "netclass (up to 50 A);")
            print("  iso = Isolated netclass; move = footprints straddling "
                  "the cut today.")
            print("  A 'POWER' interconnect rules out a flex hinge in "
                  "practice and points at")
            print("  separate boards with a busbar/tab joint.")

    for x_at in (args.propose or []):
        print(f"\n=== proposed fold at x {x_at:.2f} ===")
        hits = blockers(spans, x_at)
        if hits:
            print("  BLOCKED by:")
            for lo, hi, ref in hits:
                print(f"    {ref:6s} spans {lo:6.2f}..{hi:6.2f} "
                      f"({hi - lo:5.2f} mm) -- straddles the fold")
        else:
            print("  clear of every footprint")
        describe_partition([x_lo, x_at, x_hi], args.radius, args.depth)
        nets = crossing_nets(board, x_at)
        pours = crossing_pours(board, x_at)
        by_class = {}
        for net in nets:
            by_class.setdefault(classify(net, patterns), []).append(net)
        print(f"  conductors crossing: {len(nets)}")
        for cls in sorted(by_class):
            tag = "  <-- POWER, up to 50 A" if cls in POWER_CLASSES else ""
            if cls == "Isolated":
                tag = "  <-- CROSSES THE ISOLATION BARRIER"
            print(f"    {cls:9s} {len(by_class[cls]):3d}  "
                  f"{', '.join(by_class[cls])[:60]}{tag}")
        print(f"  pours crossing: {', '.join(pours) if pours else 'none'}")

        power_crossing = [n for n in nets
                          if classify(n, patterns) in POWER_CLASSES]
        print("\n  INTERCONNECT VERDICT: ", end="")
        if power_crossing:
            print(f"POWER interconnect required "
                  f"({len(power_crossing)} conductors at up to 50 A)")
            print("    Flex hinge is not advisable here -- flex copper is thin")
            print("    and conductor_sizing.py already needs 2 oz for the")
            print("    pours. Separate boards with a busbar/tab joint can")
            print("    carry this; a flex hinge realistically cannot.")
        else:
            print("SIGNAL-ONLY interconnect")
            print("    Either form factor works. Flex is the lighter answer:")
            print("    no connector on the BOM, self-locating, compliant")
            print("    under vibration.")

        straddling = [s for s in shields if s[0] < x_at < s[1]]
        print("\n  SHIELD CONTAINMENT: ", end="")
        if straddling:
            for lo, hi, ref, width in straddling:
                print(f"INVALID -- {ref} ({width:.2f} mm, {lo:.2f}..{hi:.2f}) "
                      f"straddles the cut.")
            print("    A rigid shielding can cannot fold or span a joint. It")
            print("    must sit wholly on one panel -- and at 22.75 mm it")
            print("    nearly fills a 23.98 mm facet on its own, so that")
            print("    panel has almost no width left for anything else.")
        else:
            print("OK -- no rigid can straddles the cut")

        widths = (x_at - x_lo, x_hi - x_at)
        print("  ISOLATION CONTAINMENT: ", end="")
        findings = isolation_report(board, x_at, patterns, widths)
        if not findings:
            print("OK -- no panel holds both sides of a barrier")
        for position, (panel, width, ok) in enumerate(findings):
            lead = "" if position == 0 else "                         "
            print(f"{lead}{'OK' if ok else 'FAILS'} -- panel {panel} holds isolated "
                  f"AND non-isolated pads")
            print(f"    width {width:.2f} mm vs {ISOLATION_MIN_WIDTH_MM:.2f} "
                  f"mm required by isolation_envelope.py ([9] Table 6)")
            if not ok:
                print("    => that barrier cannot fit on this panel. Either")
                print("       put the isolated section on its OWN panel, or")
                print("       let the barrier fall ON the cut, where the")
                print("       inter-panel gap supplies the separation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
