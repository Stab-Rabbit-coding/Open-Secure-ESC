#!/usr/bin/env python3
"""Score a placement on electrical quality, scriptability and visual order.

Governed by AGENTS.md. Measurement harness for placement work — build this
before moving anything, so a change can be kept or reverted on a number rather
than on impression. Emits JSON on stdout for tooling, plus a human summary on
stderr.

WHY A HARNESS AND NOT AN EYE
-----------------------------
Three times during the 6S/50A build a placement change looked right and was
not: a shift threshold set on a part's exact edge silently skipped the one part
the move was about; zones stretched instead of translating; a connector
followed its transceiver into the pack terminal. Each was caught only after
DRC, and each cost a revert. A change that cannot be scored before and after is
a change made on faith.

WHAT IT MEASURES

electrical
  creepage_min_mm       closest isolated<->non-isolated pad pair on a shared
                        layer, different parts. [9] Table 6 requires 7.5 mm.
  iso_lead_max_mm       furthest isolated support part from the pin it serves.
                        [9] p.17 caps capacitor lead length at 10 mm.
  gate_loop_max_mm      furthest FET gate pad from its gate-driver pin.
  commutation_max_mm    furthest high-side drain from the bulk capacitor.
  drc_electrical        clearance + shorting + courtyard + hole + edge count.

scriptability
  grid_frac_0p5 / _1p0  fraction of footprints whose origin lands exactly on
                        that grid. A generator emits grid coordinates; a board
                        that is already on-grid is one a generator can
                        reproduce.
  distinct_rows / cols  count of shared y / x coordinates. Fewer means more
                        regular — parts sitting in rows and columns rather
                        than scattered.
  row_residual_mm       mean distance from each part to its nearest shared
                        row, counting only parts not already on one.

visual_order
  alignment_frac        fraction of footprints sharing an x or y with at least
                        one other footprint.

rules                   two placement rules for any board carrying an isolated
                        interface, both learned on this build at real cost.
                        Reported pass/fail, not scored, because a violation is
                        a structural mistake rather than a number to optimise.

  iso_ic_perpendicular  every isolating IC's pin rows must run ACROSS the
                        board's long axis, so its isolated side faces a short
                        edge. Creepage to an opposite-face conductor runs
                        around the board edge -- insetA + thickness + insetB --
                        so isolated copper close to a LONG edge poisons that
                        edge for the board's whole length. On this build the
                        support columns sat 0.72-0.82 mm from the side edges
                        and forced a 5.08 mm inset on everything opposite them,
                        anywhere. Rotating the ICs perpendicular put their own
                        bodies outboard at ~2.94 mm and dropped that to
                        2.96 mm -- a 2.1 mm relaxation on both edges, which is
                        what finally let creepage pass.

  pack_layer_separated  the pack (high-current input) terminals must not share
                        a copper layer with the isolated section. A through-
                        hole terminal spans every layer and therefore always
                        shares one; making it SMD on the face opposite the
                        isolated parts removes the in-plane creepage pair
                        entirely, leaving only the (longer) around-edge path.
                        On this build that alone was worth 2.80 -> 4.64 mm.
                        It costs the barrel's free layer transition and its
                        mechanical retention -- both must then be designed in.

The three groups are reported separately and deliberately not collapsed into a
single figure: they trade against each other, and which one binds is a
judgement the operator makes, not the harness.

Usage:
    python3 tools/score_placement.py                    # summary + JSON
    python3 tools/score_placement.py --json             # JSON only
    python3 tools/score_placement.py --baseline b.json  # compare against
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-19. AI-generated; thresholds
# are cited to REFERENCES.md, geometry is measured off the board. The scoring
# weights are an engineering default per AGENTS.md Sec.4. Not human-authored.

import argparse
import collections
import json
import math
import subprocess
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"

CREEPAGE_REQ_MM = 7.5      # [9] Table 6
BOARD_T_MM = 1.6           # F.Cu-to-B.Cu, for the around-the-edge path
ISO_LEAD_MAX_MM = 10.0     # [9] p.17
TOL_MM = 0.02              # coordinates within this are "the same" row/column

ISO_NETS = {
    "CAN_ISO_GND", "CAN_GNDISO", "CAN_VISOIN", "CAN_VISOOUT",
    "RS485_ISO_GND", "RS485_GNDISO", "RS485_VISOIN", "RS485_VISOOUT",
    "RS485_A", "RS485_B", "Net-(J2-Pin_1)", "Net-(J2-Pin_2)",
}
ISO_PARTS = {"U3", "U4"}
ISO_PIN_RANGE = range(11, 21)
ISO_SUPPORT = {"FB1", "FB2", "FB3", "FB4"} | {f"C{n}" for n in range(11, 19)}
# High-current input terminals. Named rather than detected: "which pads are
# the pack input" is a design fact, not something geometry reveals.
PACK_REFS = {"J5A", "J5B"}
ELECTRICAL_DRC = {"clearance", "shorting_items", "courtyards_overlap",
                  "hole_clearance", "copper_edge_clearance", "hole_to_hole",
                  "solder_mask_bridge"}


def load():
    """Board plus its local-mm origin."""
    b = pcbnew.LoadBoard(str(PCB))
    box = b.GetBoardEdgesBoundingBox()
    return b, box.GetLeft(), box.GetTop()


def pads(board, ox, oy):
    """Every netted pad as (ref, pin, x, y, layerset, net, bbox).

    The bbox is carried because creepage is an EDGE-to-edge measure, not a
    centre-to-centre one. An earlier version of this file compared pad centres
    and reported 7.68 mm where the true conductor gap was 6.79 -- optimistic by
    roughly half a pad on each side, which is the whole margin on a 7.5 mm
    requirement.
    """
    out = []
    for f in board.Footprints():
        for p in f.Pads():
            if not p.GetNetname():
                continue
            bx = p.GetBoundingBox()
            out.append((f.GetReference(), p.GetNumber(),
                        pcbnew.ToMM(p.GetPosition().x - ox),
                        pcbnew.ToMM(p.GetPosition().y - oy),
                        set(p.GetLayerSet().Seq()), p.GetNetname(),
                        (pcbnew.ToMM(bx.GetLeft() - ox),
                         pcbnew.ToMM(bx.GetRight() - ox),
                         pcbnew.ToMM(bx.GetTop() - oy),
                         pcbnew.ToMM(bx.GetBottom() - oy))))
    return out


def gap(a, b):
    """Edge-to-edge distance between two axis-aligned pad bounding boxes."""
    ax1, ax2, ay1, ay2 = a[6]
    bx1, bx2, by1, by2 = b[6]
    dx = max(0.0, ax1 - bx2, bx1 - ax2)
    dy = max(0.0, ay1 - by2, by1 - ay2)
    return math.hypot(dx, dy)


def split_isolated(all_pads):
    """Partition pads into isolated and non-isolated.

    Classified by PIN NUMBER on the isolators themselves and by an explicit net
    list elsewhere -- never by substring. `GD_SPI_MISO` contains `ISO`, and a
    substring check scored a SPI signal as an isolated conductor.
    """
    iso, non = [], []
    for rec in all_pads:
        ref, pin, net = rec[0], rec[1], rec[5]
        if ref in ISO_PARTS and pin.isdigit():
            (iso if int(pin) in ISO_PIN_RANGE else non).append(rec)
        elif net in ISO_NETS:
            iso.append(rec)
        else:
            non.append(rec)
    return iso, non


def edge_path(a, c, box):
    """Creepage between conductors on OPPOSITE faces, around the board edge.

    The path is the UNFOLDED surface distance: travel across this face to an
    edge, over the edge, then across the other face. For a rectangular outline
    and a given edge that is

        sqrt( along_edge_separation^2 + (insetA + thickness + insetB)^2 )

    minimised over the four edges.

    The along-edge term matters enormously and an earlier version of this
    function omitted it, effectively assuming both parts sat at the same
    position along the edge. That made every opposite-face pair look like its
    insets alone: U3 against Q2, 26 mm apart in y, measured 7.83 mm when the
    real path is 27.15 mm. The result was a board reported as scraping past
    7.5 mm when it was never close to failing -- conservative, but conservative
    enough to drive real placement decisions the wrong way.
    """
    ax1, ax2, ay1, ay2 = a[6]
    bx1, bx2, by1, by2 = c[6]
    x0, x1, y0, y1 = box

    def unfold(ia, ib, sep):
        return math.hypot(max(0.0, sep), max(0.0, ia) + BOARD_T_MM + max(0.0, ib))

    dy = max(0.0, ay1 - by2, by1 - ay2)     # separation along a side edge
    dx = max(0.0, ax1 - bx2, bx1 - ax2)     # separation along a top/bottom edge
    return min(unfold(ax1 - x0, bx1 - x0, dy),      # left
               unfold(x1 - ax2, x1 - bx2, dy),      # right
               unfold(ay1 - y0, by1 - y0, dx),      # top
               unfold(y1 - ay2, y1 - by2, dx))      # bottom


def nearest(a, group, box=None):
    """Closest member of `group` to pad `a`, or None.

    Same-layer pairs use the in-plane edge-to-edge gap. Pairs sharing no
    layer use the around-the-edge path when `box` is supplied; without it
    they are skipped, which is the pre-2026-08-19 behaviour.
    """
    best = None
    for c in group:
        if c[0] == a[0]:
            continue
        if a[4] & c[4]:
            d = gap(a, c)
        elif box is not None:
            d = edge_path(a, c, box)
        else:
            continue
        if best is None or d < best[0]:
            best = (d, c)
    return best


def net_pairs(all_pads, refs, targets):
    """Max distance from any pad of `refs` to the nearest same-net target."""
    by_net = collections.defaultdict(list)
    for rec in all_pads:
        by_net[rec[5]].append((rec[0], rec[1], rec[2], rec[3]))
    worst = (0.0, None)
    for rec in all_pads:
        ref, pin, x, y, net = rec[0], rec[1], rec[2], rec[3], rec[5]
        if ref not in refs:
            continue
        cands = [(math.hypot(x - tx, y - ty), tr, tp)
                 for tr, tp, tx, ty in by_net[net] if tr in targets]
        if not cands:
            continue
        d, tr, tp = min(cands)
        if d > worst[0]:
            worst = (d, f"{ref}.{pin} -> {tr}.{tp}")
    return worst


def drc_electrical():
    """Count DRC violations that are electrical rather than cosmetic."""
    out = Path("/tmp/claude-1000/score_drc.json")
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all",
                    "--format", "json", "-o", str(out), str(PCB)],
                   capture_output=True, check=False)
    if not out.is_file():
        return -1
    d = json.loads(out.read_text())
    return sum(1 for v in d.get("violations", [])
               if v["type"] in ELECTRICAL_DRC)


def check_rules(board, ox, oy, iso, non):
    """The two structural rules for a board carrying an isolated interface.

    Both are pass/fail rather than scored: a violation is not a number to
    improve, it is an arrangement that cannot be made to pass creepage by
    nudging. See the module docstring for what each cost to learn.
    """
    box = board.GetBoardEdgesBoundingBox()
    long_axis = "y" if box.GetHeight() >= box.GetWidth() else "x"

    perp, detail = True, []
    for ref in sorted({a[0] for a in iso} & {c[0] for c in non}):
        f = next((q for q in board.Footprints()
                  if q.GetReference() == ref), None)
        if f is None:
            continue
        pins = [p for p in f.Pads() if p.GetNetname()]
        if len(pins) < 8:
            continue                      # not a multi-pin isolator
        xs = {round(pcbnew.ToMM(p.GetPosition().x - ox), 2) for p in pins}
        ys = {round(pcbnew.ToMM(p.GetPosition().y - oy), 2) for p in pins}
        rows_along = "x" if len(xs) > len(ys) else "y"
        ok = rows_along != long_axis      # rows must run ACROSS the long axis
        perp &= ok
        detail.append(f"{ref}: rows along {rows_along}, "
                      f"board long axis {long_axis} -> "
                      f"{'ok' if ok else 'PARALLEL, rotate 90'}")

    iso_layers = set()
    for a in iso:
        iso_layers |= a[4]
    shared = [c[0] for c in non
              if c[0] in PACK_REFS and (c[4] & iso_layers)]
    return {
        "board_long_axis": long_axis,
        "iso_ic_perpendicular": perp,
        "iso_ic_detail": detail,
        "pack_layer_separated": not shared,
        "pack_sharing_layers": sorted(set(shared)),
    }


def regularity(board, ox, oy):
    """Grid alignment, shared row/column counts, and off-row residual."""
    xs, ys, on = [], [], collections.Counter()
    for f in board.Footprints():
        p = f.GetPosition()
        xs.append(pcbnew.ToMM(p.x - ox))
        ys.append(pcbnew.ToMM(p.y - oy))
        for step in (0.5, 1.0):
            n = pcbnew.FromMM(step)
            if p.x % n == 0 and p.y % n == 0:
                on[step] += 1
    total = len(xs)

    def cluster(vals):
        """Group coordinates that agree within TOL_MM."""
        groups = []
        for v in sorted(vals):
            if groups and abs(v - groups[-1][-1]) <= TOL_MM:
                groups[-1].append(v)
            else:
                groups.append([v])
        return groups

    rows, cols = cluster(ys), cluster(xs)
    shared_rows = [g for g in rows if len(g) > 1]
    resid = []
    for y in ys:
        if any(abs(y - g[0]) <= TOL_MM for g in shared_rows):
            continue
        if shared_rows:
            resid.append(min(abs(y - g[0]) for g in shared_rows))
    aligned = sum(1 for v in ys if sum(1 for w in ys if abs(v - w) <= TOL_MM) > 1)
    aligned += sum(1 for v in xs
                   if sum(1 for w in xs if abs(v - w) <= TOL_MM) > 1)
    return {
        "grid_frac_0p5": round(on[0.5] / total, 3),
        "grid_frac_1p0": round(on[1.0] / total, 3),
        "distinct_rows": len(rows),
        "distinct_cols": len(cols),
        "row_residual_mm": round(sum(resid) / len(resid), 3) if resid else 0.0,
        "alignment_frac": round(min(aligned / (2 * total), 1.0), 3),
        "footprints": total,
    }


def main() -> int:
    """Measure and report."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="JSON only")
    ap.add_argument("--baseline", help="compare against a saved JSON score")
    a = ap.parse_args()

    board, ox, oy = load()
    ap_ = pads(board, ox, oy)
    iso, non = split_isolated(ap_)

    ob = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(ob)
    obb = ob.BBox()
    box = (pcbnew.ToMM(obb.GetLeft() - ox), pcbnew.ToMM(obb.GetRight() - ox),
           pcbnew.ToMM(obb.GetTop() - oy), pcbnew.ToMM(obb.GetBottom() - oy))
    creep = min((nearest(x, non, box)[0] for x in iso
                 if nearest(x, non, box) is not None), default=999.0)
    iso_lead, iso_who = net_pairs(ap_, ISO_SUPPORT, ISO_PARTS)
    gate, gate_who = net_pairs(ap_, {f"Q{n}" for n in range(1, 7)}, {"U5"})
    comm, comm_who = net_pairs(ap_, {"Q1", "Q3", "Q5"}, {"C1"})

    score = {
        "electrical": {
            "creepage_min_mm": round(creep, 2),
            "creepage_ok": creep >= CREEPAGE_REQ_MM,
            "iso_lead_max_mm": round(iso_lead, 2),
            "iso_lead_ok": iso_lead <= ISO_LEAD_MAX_MM,
            "iso_lead_worst": iso_who,
            "gate_loop_max_mm": round(gate, 2),
            "gate_loop_worst": gate_who,
            "commutation_max_mm": round(comm, 2),
            "commutation_worst": comm_who,
            "drc_electrical": drc_electrical(),
        },
        "regularity": regularity(board, ox, oy),
        "rules": check_rules(board, ox, oy, iso, non),
    }

    if not a.json:
        e, r = score["electrical"], score["regularity"]
        print("ELECTRICAL", file=sys.stderr)
        print(f"   creepage min       {e['creepage_min_mm']:6.2f} mm  "
              f"(need {CREEPAGE_REQ_MM}) {'OK' if e['creepage_ok'] else 'FAIL'}",
              file=sys.stderr)
        print(f"   isolated lead max  {e['iso_lead_max_mm']:6.2f} mm  "
              f"(need <={ISO_LEAD_MAX_MM}) "
              f"{'OK' if e['iso_lead_ok'] else 'FAIL'}  {e['iso_lead_worst']}",
              file=sys.stderr)
        print(f"   gate loop max      {e['gate_loop_max_mm']:6.2f} mm  "
              f"{e['gate_loop_worst']}", file=sys.stderr)
        print(f"   commutation max    {e['commutation_max_mm']:6.2f} mm  "
              f"{e['commutation_worst']}", file=sys.stderr)
        print(f"   DRC electrical     {e['drc_electrical']:6d}", file=sys.stderr)
        print("REGULARITY", file=sys.stderr)
        print(f"   on 0.5 mm grid     {r['grid_frac_0p5']:6.1%}", file=sys.stderr)
        print(f"   on 1.0 mm grid     {r['grid_frac_1p0']:6.1%}", file=sys.stderr)
        print(f"   distinct rows/cols {r['distinct_rows']:3d} / "
              f"{r['distinct_cols']:3d}  of {r['footprints']} parts",
              file=sys.stderr)
        print(f"   off-row residual   {r['row_residual_mm']:6.3f} mm",
              file=sys.stderr)
        print(f"   sharing a row/col  {r['alignment_frac']:6.1%}",
              file=sys.stderr)
        k = score["rules"]
        print("RULES (isolated-interface boards)", file=sys.stderr)
        print(f"   isolator perpendicular to the long axis: "
              f"{'PASS' if k['iso_ic_perpendicular'] else 'FAIL'}",
              file=sys.stderr)
        for d in k["iso_ic_detail"]:
            print(f"      {d}", file=sys.stderr)
        print(f"   pack terminals off the isolated layer:   "
              f"{'PASS' if k['pack_layer_separated'] else 'FAIL'}"
              + (f"  shares with {k['pack_sharing_layers']}"
                 if k["pack_sharing_layers"] else ""), file=sys.stderr)

    if a.baseline and Path(a.baseline).is_file():
        base = json.loads(Path(a.baseline).read_text())
        print("\nDELTA vs baseline", file=sys.stderr)
        for grp in ("electrical", "regularity"):
            for k, v in score[grp].items():
                bv = base.get(grp, {}).get(k)
                if isinstance(v, (int, float)) and isinstance(bv, (int, float)):
                    d = v - bv
                    if abs(d) > 1e-9:
                        print(f"   {k:20s} {bv:8.3f} -> {v:8.3f} "
                              f"({d:+.3f})", file=sys.stderr)
    print(json.dumps(score, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
