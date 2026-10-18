#!/usr/bin/env python3
"""Generate the KiCad footprints for TI PowerPAD packages PWP0016J and DDA0008B.

Used by the nacelle-tilt build `builds/6s/10A/BRUSHED_CAN_485_isolation/`:

  * PWP0016J -- HTSSOP-16 with exposed pad, 1.2 mm max height:
    DRV8874-Q1 (symbols/specs/DRV8874_Q1.json, REFERENCES.md [63]; the
    non-Q1 DRV8874 [62] ships in the same package).
  * DDA0008B -- HSOIC-8 (PowerPAD SOIC), 1.7 mm max height:
    TPS54560B (symbols/specs/TPS54560B.json, REFERENCES.md [65]).

SOURCE OF EVERY NUMBER
----------------------
Both TI datasheets carry the package outline AND TI's own "EXAMPLE BOARD
LAYOUT" sheet (this is where TI keeps land patterns -- see
docs/solutions/architecture-patterns/esc-build-instantiation-workflow.md
Trap 2). The land dimensions below are TI's published values, read from the
local verified copies:

  PWP0016J  [63] docs/datasheets/ti-drv8874-q1-datasheet.pdf, "PACKAGE
            OUTLINE" and "EXAMPLE BOARD LAYOUT" (drawing 4223595/A 03/2017)
  DDA0008B  [65] docs/datasheets/ti-tps54560b-datasheet.pdf, "PACKAGE
            OUTLINE" and "EXAMPLE BOARD LAYOUT" (drawing 4214849/B 09/2025)

PWP0016J (values in mm, parenthesised = reference dimensions on the sheet):
    feature                         value        drawing callout
    signal pads                     16 x 1.5 x 0.45   "16X (1.5)", "16X (0.45)"
    pad pitch                       0.65         "14X (0.65)" (7 gaps per side)
    pad-row centre-to-centre        5.8          "(5.8)"
    thermal metal (F.Cu)            3.4 x 5.0    "(3.4)" NOTE 8, "(5)" NOTE 8
    thermal mask/paste opening      2.46 x 3.55  "(2.46) BY SOLDER MASK", "(3.55)"
    body                            4.4 x 5.0    outline: 4.3-4.5 x 4.9-5.1
    lead span (tip to tip)          6.2-6.6      outline
    exposed pad on package          1.75-2.46 x 2.68-3.55   outline

  Independent check (Trap 1 of the same learning): with the row span read
  as centre-to-centre, a 1.5 mm pad runs from |x| = 2.15 to 3.65 mm, which
  brackets the lead tips at |x| = 3.1-3.3 mm with a 0.35-0.55 mm toe and a
  heel that stops 0.95 mm short of the exposed pad's widest edge (1.23 mm).
  Read instead as tip-to-tip, the pads would END at |x| = 2.9 mm, INSIDE
  the lead tips -- physically impossible -- so the centre-to-centre reading
  is the only consistent one. The 8-per-side pitch check "14X 0.65" gives a
  4.55 mm span, which matches the outline's own "4.55" callout.

DDA0008B:
    feature                         value        drawing callout
    signal pads                     8 x 1.55 x 0.6    "8X (1.55)", "8X (0.6)"
    pad pitch                       1.27         "6X (1.27)"
    pad-row centre-to-centre        5.4          "(5.4)"
    thermal metal (F.Cu)            2.95 x 4.9   "(2.95)" NOTE 9, "(4.9)" NOTE 9
    thermal mask/paste opening      2.71 x 3.4   "(2.71) SOLDER MASK", "(3.4) SOLDER MASK"
    body                            3.9 x 4.9    outline: 3.8-4.0 x 4.8-5.0
    lead span (tip to tip)          5.8-6.2      outline
    exposed pad on package          2.11-2.71 x 2.8-3.4   outline

  Independent check: a 1.55 mm pad centred at |x| = 2.7 runs 1.925-3.475,
  bracketing the lead tips at 2.9-3.1 with a 0.375-0.575 mm toe. The
  mask-opening pair (2.71 x 3.4) equals the outline's maximum exposed-pad
  pair, exactly as on PWP0016J -- two drawings agreeing on the same
  convention is what makes the reading trustworthy.

WHAT IS A JUDGMENT CALL (AGENTS.md Sec.4)
------------------------------------------
  * TI notes 8/9 say the metal-pad size "may vary due to creepage
    requirement"; the values above are TI's example. They are emitted as
    F.Cu + F.Mask metal, with the paste split into four windows (~50 %
    coverage) -- the paste split is this repo's convention for exposed pads
    (cf. gen_optiga_uson10_footprint.py), not a TI value.
  * Thermal vias (TI note 9/10: "optional") are NOT emitted; add them at
    layout time per the build's thermal check (DRV8874 dissipates ~2 W at
    the 20D's stall, see the build README).
  * The exposed pad is emitted as an UNNUMBERED land, consistent with every
    other QFN/USON/HTSSOP part in this repo: it is GND-connected on both
    devices (PWP: "thermal pad" tied to GND/PGND per [63] Sec.5; DDA: "GND
    pin must be electrically connected to the exposed pad" [65] Sec.5) and
    that connection is made by copper at layout, not by a symbol pin.
  * Courtyard: 0.25 mm beyond the pad/body extents (IPC-7351 "nominal").
  * Silkscreen: two body-length lines outside the courtyard-clear zone plus
    a pin-1 tick, drawn 0.12 mm.

Regenerate, never hand-edit:
    python3 symbols/tools/gen_ti_powerpad_footprints.py -o symbols/footprints/Open_Secure_ESC.pretty
"""
# Authored by Claude Opus 5 (Anthropic) 2026-09-17 under the direction of
# Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. AI-generated. Every dimension is
# traced above to a TI drawing callout; the derivations are flagged.

import argparse
import sys
from pathlib import Path


def _f(v: float) -> str:
    """Format a millimetre value the way the committed footprints do."""
    v = round(v, 4)
    return str(int(v)) if float(v).is_integer() else repr(v)


def _line(a, b, layer, width):
    return (
        f"  (fp_line (start {_f(a[0])} {_f(a[1])}) (end {_f(b[0])} {_f(b[1])}) "
        f'(layer "{layer}") (width {width}))'
    )


def _rect(x0, y0, x1, y1, layer, width):
    return [
        _line((x0, y0), (x1, y0), layer, width),
        _line((x1, y0), (x1, y1), layer, width),
        _line((x1, y1), (x0, y1), layer, width),
        _line((x0, y1), (x0, y0), layer, width),
    ]


def build(spec: dict) -> str:
    """Emit one dual-row PowerPAD footprint as KiCad S-expression text."""
    n = spec["pins"]
    per_side = n // 2
    pitch = spec["pitch"]
    px, py = spec["pad"]  # pad length (x, toward the body) and width (y)
    row = spec["row_span"] / 2  # pad-row centre |x|
    bw, bl = spec["body"]  # body width (x) and length (y)
    mw, ml = spec["metal"]  # thermal metal (x, y)
    ow, ol = spec["opening"]  # mask/paste opening (x, y)
    name = spec["name"]

    out = [
        (
            f'(footprint "Open_Secure_ESC:{name}" (version 20211014) '
            "(generator open_secure_esc_fpgen)"
        ),
        '  (layer "F.Cu")',
        "  (tedit 6a78f704)",
        f'  (descr "{spec["descr"]}")',
        f'  (tags "{spec["tags"]}")',
        "  (attr smd)",
        f'  (fp_text reference "REF**" (at 0 {_f(-(bl / 2 + 1.2))} 0) (layer "F.SilkS")',
        "    (effects (font (size 1.0 1.0)))",
        "  )",
        f'  (fp_text value "{name}" (at 0 {_f(bl / 2 + 1.2)} 0) (layer "F.Fab")',
        "    (effects (font (size 1.0 1.0)))",
        "  )",
    ]

    # Fabrication outline: body rectangle with a chamfered pin-1 corner.
    hx, hy = bw / 2, bl / 2
    c = 0.5
    out += [
        _line((-hx + c, -hy), (hx, -hy), "F.Fab", 0.1),
        _line((hx, -hy), (hx, hy), "F.Fab", 0.1),
        _line((hx, hy), (-hx, hy), "F.Fab", 0.1),
        _line((-hx, hy), (-hx, -hy + c), "F.Fab", 0.1),
        _line((-hx, -hy + c), (-hx + c, -hy), "F.Fab", 0.1),
    ]

    # Silkscreen: body-length lines clear of the pad rows, plus a pin-1 tick.
    pad_top = -((per_side - 1) / 2) * pitch - py / 2
    sy = hy + 0.11
    inner_x = row - px / 2 - 0.2  # stay clear of the pad heel
    out += [
        _line((-inner_x, -sy), (inner_x, -sy), "F.SilkS", 0.12),
        _line((-inner_x, sy), (inner_x, sy), "F.SilkS", 0.12),
        _line(
            (-(row + px / 2 + 0.3), pad_top - 0.3),
            (-(row + px / 2 + 0.3), pad_top + 0.3),
            "F.SilkS",
            0.12,
        ),
    ]

    # Courtyard: 0.25 mm beyond the outermost pad / body extents.
    cx = row + px / 2 + 0.25
    cy = max(hy, ((per_side - 1) / 2) * pitch + py / 2) + 0.25
    out += _rect(-cx, -cy, cx, cy, "F.CrtYd", 0.05)

    # Signal pads: pin 1 top-left, counting down the left, up the right.
    for i in range(per_side):
        y = (i - (per_side - 1) / 2) * pitch
        left = i + 1
        right = n - i
        for num, x in ((left, -row), (right, row)):
            out.append(
                f'  (pad "{num}" smd roundrect (at {_f(x)} {_f(y)}) (size {_f(px)} {_f(py)}) '
                '(layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25))'
            )

    # Exposed pad: metal on F.Cu with the mask opening TI shows; paste split
    # into four windows sized to ~50 % of the opening.
    out.append(f'  (pad "" smd rect (at 0 0) (size {_f(mw)} {_f(ml)}) (layers "F.Cu"))')
    out.append(
        f'  (pad "" smd rect (at 0 0) (size {_f(ow)} {_f(ol)}) (layers "F.Mask"))'
    )
    wx, wy = ow / 2 * 0.72, ol / 2 * 0.72
    for sx in (-1, 1):
        for sy_ in (-1, 1):
            out.append(
                f'  (pad "" smd rect (at {_f(sx * ow / 4)} {_f(sy_ * ol / 4)}) '
                f'(size {_f(wx)} {_f(wy)}) (layers "F.Paste"))'
            )
    out.append(")")
    return "\n".join(out) + "\n"


SPECS = [
    {
        "name": "TI_PWP0016J_HTSSOP-16_4.4x5mm_P0.65mm_EP2.46x3.55mm",
        "pins": 16,
        "pitch": 0.65,
        "pad": (1.5, 0.45),
        "row_span": 5.8,
        "body": (4.4, 5.0),
        "metal": (3.4, 5.0),
        "opening": (2.46, 3.55),
        "descr": (
            "TI PWP0016J PowerPAD HTSSOP-16, 0.65 mm pitch, body 4.4x5.0 mm, "
            "1.2 mm max height, thermal metal 3.4x5.0 mm with a 2.46x3.55 mm "
            "solder-mask opening. Land pattern is TI's own EXAMPLE BOARD "
            "LAYOUT (drawing 4223595/A) from REFERENCES.md [63] (DRV8874-Q1 "
            "datasheet SLVSF67B); exposed pad emitted unnumbered (GND by "
            "copper at layout). Generated by "
            "symbols/tools/gen_ti_powerpad_footprints.py -- do not hand-edit."
        ),
        "tags": "HTSSOP PowerPAD TI-PWP0016J DRV8874 SMD thermal-pad",
    },
    {
        "name": "TI_DDA0008B_HSOIC-8_3.9x4.9mm_P1.27mm_EP2.71x3.4mm",
        "pins": 8,
        "pitch": 1.27,
        "pad": (1.55, 0.6),
        "row_span": 5.4,
        "body": (3.9, 4.9),
        "metal": (2.95, 4.9),
        "opening": (2.71, 3.4),
        "descr": (
            "TI DDA0008B PowerPAD SOIC-8 (HSOIC), 1.27 mm pitch, body "
            "3.9x4.9 mm, 1.7 mm max height, thermal metal 2.95x4.9 mm with a "
            "2.71x3.4 mm solder-mask opening. Land pattern is TI's own "
            "EXAMPLE BOARD LAYOUT (drawing 4214849/B) from REFERENCES.md [65] "
            "(TPS54560B datasheet SLVSF00); exposed pad emitted unnumbered "
            "(GND by copper at layout, required by [65] Sec.5). Generated by "
            "symbols/tools/gen_ti_powerpad_footprints.py -- do not hand-edit."
        ),
        "tags": "HSOIC SOIC PowerPAD TI-DDA0008B TPS54560B SMD thermal-pad",
    },
]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--outdir", default=".", help="Output .pretty directory")
    args = ap.parse_args(argv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for spec in SPECS:
        out = outdir / f"{spec['name']}.kicad_mod"
        out.write_text(build(spec))
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
