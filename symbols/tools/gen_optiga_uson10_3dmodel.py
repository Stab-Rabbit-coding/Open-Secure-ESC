#!/usr/bin/env python3
"""Build the 3D model (STEP) for Infineon package PG-USON-10-2,-4 (3x3 mm).

Run with FreeCAD's headless interpreter, NOT plain python3:

    freecadcmd gen_optiga_uson10_3dmodel.py \
        -- -o ../footprints/Open_Secure_ESC.3dshapes

Why this file exists
--------------------
KiCad 9.0 ships a dimensionally equivalent footprint
(`Package_DFN_QFN:DFN-10-1EP_3x3mm_P0.5mm_EP1.7x2.5mm`) whose model entry
points at `${KICAD9_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/...step`, but the
KiCad 3D model package is not installed on this system, so that reference
resolves to nothing and the part renders as an empty space in the 3D viewer
and in any STEP board export. This script produces the missing solid from the
package drawing so `symbols/footprints/Open_Secure_ESC.pretty` is
self-contained.

Dimensions
----------
Every dimension is the same verified set used by
gen_optiga_uson10_footprint.py, read from REFERENCES.md [45], Infineon
*OPTIGA(TM) Trust M Datasheet* Rev. 3.70, p.15 Section 4.1 Figure 6
"PG-USON-10-2,-4 Package Outline" and p.16 Figure 7 (top view). See that
script's docstring for the pixel-measurement cross-check that confirms each
printed callout.

This is a dimensionally faithful *mechanical envelope* for clearance, height
and MCAD checks -- body, terminals and exposed pad -- not a cosmetic render of
the moulding's exact fillets, and not a model of the die inside. That is the
purpose a footprint 3D model serves in this repo.

Coordinate convention
---------------------
KiCad places a footprint's 3D model with the footprint origin at (0,0,0), the
board's top surface at Z = 0, and the part extending towards +Z. KiCad's
footprint editor has +Y pointing DOWN while the 3D model space has +Y
pointing UP, so a footprint feature at (fx, fy) is modelled here at
(fx, -fy, z). The only asymmetric feature is the pin-1 index dimple, so that
sign flip is the one thing that has to be right: footprint pin 1 sits at
(-1.4625, -1.0), i.e. top-left on screen, so the dimple is modelled in the
(-X, +Y) quadrant.
"""

import argparse
import sys
from pathlib import Path

import FreeCAD as App
import Part

# --- [45] p.15 Figure 6 -----------------------------------------------------
BODY = 3.00           # "3" x "3" body, square
BODY_H = 0.60         # "0.6 Max." overall height
STANDOFF = 0.05       # "0.05 Max. Standoff" -> terminal/EP metal thickness
PITCH = 0.50          # "0.5" basic
TERM_WID = 0.25       # "0.25 +/-0.05" tangential
TERM_LEN = 0.40       # "0.4 +/-0.05" radial, flush to the body edge
EP_X = 1.70           # "1.7 +/-0.1" across the rows
EP_Y = 2.50           # "2.5 +/-0.1" along the rows
PINS_PER_SIDE = 5

# Cosmetic only (not datasheet values): pin-1 dimple and top-edge break.
DIMPLE_R = 0.18
DIMPLE_DEPTH = 0.06
EDGE_CHAMFER = 0.05

NAME = "Infineon_PG-USON-10-2-4_3x3mm_P0.5mm_EP1.7x2.5mm"


def _box(dx, dy, dz, cx, cy, z0):
    """Axis-aligned box of size (dx,dy,dz) centred on (cx,cy), base at z0."""
    b = Part.makeBox(dx, dy, dz)
    b.translate(App.Vector(cx - dx / 2.0, cy - dy / 2.0, z0))
    return b


def build():
    solids = []

    # --- Moulded body, sitting on the standoff --------------------------
    body = _box(BODY, BODY, BODY_H - STANDOFF, 0, 0, STANDOFF)
    try:
        body = body.makeChamfer(
            EDGE_CHAMFER,
            [e for e in body.Edges
             if abs(e.BoundBox.ZMin - BODY_H) < 1e-6
             and abs(e.BoundBox.ZMax - BODY_H) < 1e-6],
        )
    except Exception as exc:  # chamfering is cosmetic; never fail the build
        print(f"  note: top-edge chamfer skipped ({exc})")

    # Pin-1 index dimple. Footprint pin 1 is at (-1.4625, -1.0) with +Y down,
    # so in model space (+Y up) it belongs in the (-X, +Y) quadrant.
    d_off = BODY / 2.0 - 0.45
    dimple = Part.makeCylinder(
        DIMPLE_R, DIMPLE_DEPTH + 0.01,
        App.Vector(-d_off, d_off, BODY_H - DIMPLE_DEPTH),
    )
    body = body.cut(dimple)
    solids.append(body)

    # --- Terminals ------------------------------------------------------
    # 5 per side, on the left (-X) and right (+X) body edges, flush with the
    # edge and extending TERM_LEN inward.
    t0 = -PITCH * (PINS_PER_SIDE - 1) / 2.0
    cx = BODY / 2.0 - TERM_LEN / 2.0
    for i in range(PINS_PER_SIDE):
        ty = t0 + i * PITCH
        for sx in (-1, 1):
            solids.append(
                _box(TERM_LEN, TERM_WID, STANDOFF, sx * cx, ty, 0.0))

    # --- Exposed thermal pad --------------------------------------------
    solids.append(_box(EP_X, EP_Y, STANDOFF, 0, 0, 0.0))

    return Part.makeCompound(solids)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--outdir", default=".",
                    help="Output .3dshapes directory")
    args = ap.parse_args(argv)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    shape = build()
    bb = shape.BoundBox
    print(f"  bounding box: X {bb.XMin:.3f}..{bb.XMax:.3f}  "
          f"Y {bb.YMin:.3f}..{bb.YMax:.3f}  Z {bb.ZMin:.3f}..{bb.ZMax:.3f} mm")
    assert abs(bb.XLength - BODY) < 1e-6, "body X must be 3.0 mm"
    assert abs(bb.YLength - BODY) < 1e-6, "body Y must be 3.0 mm"
    assert abs(bb.ZMax - BODY_H) < 1e-6, "overall height must be 0.6 mm"
    assert abs(bb.ZMin) < 1e-9, "model must sit on Z = 0 (board surface)"

    out = outdir / f"{NAME}.step"
    shape.exportStep(str(out))
    print(f"wrote {out}")


# NOTE: freecadcmd imports this file as a module rather than running it as
# __main__, so a `if __name__ == "__main__":` guard would never fire and the
# script would silently do nothing. Dispatch unconditionally instead, and
# default the output directory relative to this file so the no-argument
# invocation still writes to the right place.
_argv = sys.argv[1:]
if "--" in _argv:
    _argv = _argv[_argv.index("--") + 1:]
else:
    _argv = [a for a in _argv if not a.endswith(".py")]
if not _argv:
    _argv = ["-o", str(Path(__file__).resolve().parent.parent
                       / "footprints" / "Open_Secure_ESC.3dshapes")]
main(_argv)
