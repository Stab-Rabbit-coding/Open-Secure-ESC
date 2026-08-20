#!/usr/bin/env python3
"""Move the support passives that can leave SH1's shield ring outside it.

Repo owner's instruction, 2026-08-19: "move some of the support resistors and
caps from inside sh1 to outside it to allow the required vias, minimize
movement".

WHY THE RING MATTERS
--------------------
SH1 (Wurth WE-SHC 3670209) solders to a **closed rectangular land on B.Cu**,
x 24.85..47.05, y 51.70..68.30, 1.5 mm wide. U5's pads sit entirely inside it
(x 32.75..39.15, y 56.80..63.20). **No B.Cu trace of any width leaves that
ring** -- which is why 27 of U5's pad connections are unrouted, and why the
0.10 mm / 0.09 mm "Fine" escape class bought only 3 connections before it was
withdrawn. Trace width was never the constraint.

The land is **B.Cu only**, so F.Cu is free to cross the ring. Every U5 escape
therefore has to be: pad -> short B.Cu stub -> via -> F.Cu -> over the ring.
That via needs annulus space between U5's pads and the shield land, and the
annulus is where the support passives currently sit.

WHICH PARTS MAY LEAVE, AND WHY THESE ONES
-----------------------------------------
A part can leave the ring only if doing so adds NO new B.Cu crossing. Tested
by asking, for each of its nets, whether that net already has pads outside the
ring (so a crossing is already required) or is GND (which the shield land
itself carries).

    CAN LEAVE          nets
    R6                 3V3, NRST                   both already cross
    C2                 3V3, GND                    GND is the shield land
    R14                3V3, GD_SPI_MISO            both already cross
    R4                 3V3, VREF_MID               both already cross
    R13                3V3, SE_I2C_SCL             both already cross
    R5                 VREF_MID, GND               both satisfied
    R10                VBUS_SENSE, GND             both satisfied

    MUST STAY          nets that exist ONLY inside the ring
    R9   U5-ENABLE       R11  U5-nFAULT       C5   U5-CPH / U5-CPL
    C6   U5-VCP          C8   U5-DVDD         C9   U5-VGLS
    C7   U5-VREF

The split falls out of the topology rather than being chosen: everything that
may leave is a pull-up or divider referencing 3V3/GND, and everything that must
stay is U5's own charge-pump and supply decoupling -- which belongs within a
few millimetres of the chip regardless. [9] p.17 caps isolated-supply lead
length at 10 mm; the same reasoning applies to a gate driver's charge pump,
and `tools/score_placement.py` scores that distance.

HOW THE NEW POSITION IS CHOSEN
------------------------------
Minimum Euclidean displacement, subject to:
  - clear of SH1's land rectangle plus SHIELD_MARGIN_MM (the can body sits on
    that land -- a part tucked against it does not fit under the shield);
  - no courtyard overlap with any other part on the same copper layer;
  - inside the board outline by EDGE_MARGIN_MM.
The search is a grid, so the result is reproducible; the displacement of each
part is printed so the cost is auditable.

Orientation and layer are preserved. x is NOT pinned: the project values
row/column regularity (`score_placement.py`), but forcing a pure-y move would
often cost more displacement than the diagonal, and regularity is re-scored
afterwards rather than assumed.

RUN ORDER: after this, re-run `tools/autoroute.py` then
`tools/stitch_planes.py`. Moving parts invalidates the existing route.

Usage:
    python3 tools/move_out_of_shield.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic), 2026-08-19, on the repo owner's
# instruction. AI-generated; the movable/immovable split is derived from the
# board's own netlist, not chosen by hand.

import argparse
import math
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-shieldmove.bak")

# SH1's land rectangle, measured off the board 2026-08-19.
SHIELD = (24.85, 47.05, 51.70, 68.30)  # x0, x1, y0, y1
SHIELD_MARGIN_MM = 0.50
EDGE_MARGIN_MM = 0.50
STEP_MM = 0.05
SEARCH_MM = 14.0

MOVABLE = ("R6", "C2", "R14", "R4", "R13", "R5", "R10")


def courtyard_box(fp, mm):
    """Courtyard bounding box in mm, falling back to the pad extent."""
    bb = fp.GetCourtyard(fp.GetLayer()).BBox()
    if bb.GetWidth() <= 0 or bb.GetHeight() <= 0:
        bb = fp.GetBoundingBox(False, False)
    return (
        bb.GetLeft() / mm,
        bb.GetRight() / mm,
        bb.GetTop() / mm,
        bb.GetBottom() / mm,
    )


def overlaps(a, b) -> bool:
    """True if two (x0, x1, y0, y1) boxes intersect."""
    return not (a[1] <= b[0] or b[1] <= a[0] or a[3] <= b[2] or b[3] <= a[2])


def main() -> int:
    """Relocate the movable passives clear of the shield land."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    mm = pcbnew.pcbIUScale.IU_PER_MM
    edge = board.GetBoardEdgesBoundingBox()
    board_box = (
        edge.GetLeft() / mm + EDGE_MARGIN_MM,
        edge.GetRight() / mm - EDGE_MARGIN_MM,
        edge.GetTop() / mm + EDGE_MARGIN_MM,
        edge.GetBottom() / mm - EDGE_MARGIN_MM,
    )

    sx0, sx1, sy0, sy1 = SHIELD
    keepout = (
        sx0 - SHIELD_MARGIN_MM,
        sx1 + SHIELD_MARGIN_MM,
        sy0 - SHIELD_MARGIN_MM,
        sy1 + SHIELD_MARGIN_MM,
    )

    fps = {f.GetReference(): f for f in board.GetFootprints()}
    missing = [r for r in MOVABLE if r not in fps]
    if missing:
        raise SystemExit(f"not on the board: {missing}")

    # Static obstacles: every part that is not being moved, same layer only.
    placed = {}
    for ref, fp in fps.items():
        if ref in MOVABLE:
            continue
        placed[ref] = (fp.GetLayer(), courtyard_box(fp, mm))

    total = 0.0
    for ref in MOVABLE:
        fp = fps[ref]
        layer = fp.GetLayer()
        x0, x1, y0, y1 = courtyard_box(fp, mm)
        cx, cy = fp.GetX() / mm, fp.GetY() / mm
        half_w, half_h = (x1 - x0) / 2.0, (y1 - y0) / 2.0

        best = None
        steps = int(SEARCH_MM / STEP_MM)
        for iy in range(-steps, steps + 1):
            for ix in range(-steps, steps + 1):
                nx, ny = cx + ix * STEP_MM, cy + iy * STEP_MM
                d = math.hypot(nx - cx, ny - cy)
                if best is not None and d >= best[0]:
                    continue
                box = (nx - half_w, nx + half_w, ny - half_h, ny + half_h)
                if overlaps(box, keepout):
                    continue
                if (
                    box[0] < board_box[0]
                    or box[1] > board_box[1]
                    or box[2] < board_box[2]
                    or box[3] > board_box[3]
                ):
                    continue
                if any(l == layer and overlaps(box, ob) for l, ob in placed.values()):
                    continue
                best = (d, nx, ny)
        if best is None:
            raise SystemExit(f"{ref}: no legal position within {SEARCH_MM} mm")

        d, nx, ny = best
        fp.SetPosition(pcbnew.VECTOR2I(int(nx * mm), int(ny * mm)))
        placed[ref] = (layer, (nx - half_w, nx + half_w, ny - half_h, ny + half_h))
        total += d
        print(
            f"  {ref:4} ({cx:6.2f},{cy:6.2f}) -> ({nx:6.2f},{ny:6.2f})  "
            f"moved {d:5.2f} mm"
        )

    print(
        f"  total displacement {total:.2f} mm over {len(MOVABLE)} parts "
        f"(mean {total / len(MOVABLE):.2f} mm)"
    )

    if args.dry_run:
        print("dry run -- not written")
        return 0

    shutil.copy2(PCB, BACKUP)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.BuildConnectivity()
    board.Save(str(PCB))
    print(f"backed up -> {BACKUP.name}; re-poured and saved")
    print("NEXT: tools/autoroute.py, then tools/stitch_planes.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
