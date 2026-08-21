#!/usr/bin/env python3
"""Generate the KiCad footprint for Toshiba package 2-5W1A, "SOP Advance(N)".

Used by the TPHR8504PL power MOSFET (Q1..Q6) -- see
symbols/specs/TPHR8504PL.json.

PACKAGE VARIANT -- THIS MATTERS
--------------------------------
The TPHR8504PL datasheet offers TWO packages under one part number and says
"The package can be selected according to your preference. For details,
please contact your TOSHIBA sales representative":

    p.8  2-5Q1S  "SOP Advance"     5.00 x 6.00 mm, 0.95 mm tall, 0.087 g
    p.9  2-5W1A  "SOP Advance(N)"  5.15 x 6.10 mm, 1.00 mm tall, 0.111 g

They are pin-compatible (same pinout, same 1.27 mm pitch) but NOT
copper-compatible: the body is 0.75 mm taller on the (N), the lead frame is
thicker (0.28 vs 0.166 mm), and the drain pad differs (4.21 x 3.69 against
4.25 x 3.50). This file implements **2-5W1A, SOP Advance(N)**, per the repo
owner's decision of 2026-08-15. Do not order 2-5Q1S against this land without
re-deriving it.

THE LAND PATTERN IS TOSHIBA'S OWN -- NOT A DERIVATION
------------------------------------------------------
Source: REFERENCES.md [50], Toshiba *MOSFET Product Catalog*, ALQ00024,
2026-07-06, local copy
`docs/datasheets/TPHR8504PL_catalog_20260706_ALQ00024.pdf`, p.46 "Surface
Mount Type", cell "SOP Advance(N) (4.9 x 6.1)", sub-panel "Land pattern
example, unit: mm".

The part datasheet [49] itself carries no land pattern -- all 10 pages were
searched and the words "land", "mounting" and "recommend" do not appear --
so an earlier revision of this file derived one IPC-7351-style. That
derivation has been REPLACED by Toshiba's published figures, which are
materially larger:

    feature        earlier derivation      Toshiba [50] p.46
    drain land     4.21 x 3.69  (15.5)     4.70 x 4.80  (22.6 mm^2, +46%)
    lead pad       0.60 x 1.10  (0.66)     0.85 x 1.45  (1.23 mm^2, +86%)

More land is more copper into the terminal, which is lower resistance and a
better thermal path -- the reason to prefer the manufacturer's figure here is
provenance, but the engineering moves the right way too.

The catalog is the reference to use for ANY Toshiba MOSFET package in this
repo; p.46 tabulates package dimensions and land patterns side by side for
the whole surface-mount family (DSOP Advance(WF)L/M, SOP Advance, SOP
Advance(N)/(E)/(EWF)).

LAND PATTERN, from [50] p.46, SOP Advance(N):

    feature                        drawing callout
    overall land width             4.7
    lead / tab pad width           0.85
    pad pitch                      1.27
    drain land, total height       4.8
    drain land, castellated depth  1.05
    drain land, solid height       3.75      (4.8 - 1.05, and dimensioned)
    gap, drain land to lead pads   0.7
    lead pad height                1.45

    -> total land height = 4.8 + 0.7 + 1.45 = 6.95 mm

The drain land is a single connected shape: a 4.7 x 3.75 body whose top
1.05 mm is castellated into four 0.85 mm tabs on the 1.27 mm pitch, one per
drain lead. It is emitted here as the solid body plus four tab pads, all
numbered so they merge onto the drain net.

PACKAGE TERMINAL GEOMETRY, from [49] p.9 (2-5W1A) top and bottom views,
retained for the body outline and the courtyard:

    feature                        drawing callout
    overall, lead tip to lead tip  5.15 +/-0.15  x  6.10 +/-0.15
    body                           4.90 +/-0.10  x  5.75 +/-0.10
    lead pitch                     1.27
    lead width                     0.4 +/-0.1
    lead thickness                 0.28 +/-0.05
    seated height                  1.0 +/-0.1
    top lead contact length        0.56 +/-0.1
    top edge to drain pad          (1.2)  reference
    drain pad                      4.21 +/-0.15  x  3.69 +/-0.15
    bottom lead contact length     0.65 +/-0.15

CROSS-CHECK THAT THE READING IS RIGHT
--------------------------------------
The four vertical dimensions on the bottom view sum to the overall height:

    0.56 + 1.2 + 3.69 + 0.65 = 6.10  ==  overall 6.10 +/-0.15

and that places the drain pad symmetrically: 1.2 mm from the top edge and
6.10 - 1.2 - 3.69 = 1.21 mm from the bottom edge. So the drain pad is centred
on the package, with ~0.64 mm of clearance to the drain lead row above it and
~0.56 mm to the source/gate lead row below. A misread of any one dimension
would break both the sum and the symmetry.

PIN NUMBERING
-------------
From [49] p.9 TOP VIEW, which labels pin 8 at the top left, 5 at the top
right, 1 at the bottom left and 4 at the bottom right; and Sec. 3 "Packaging
and Internal Circuit", which gives the functions:

    top row,    left to right:  8, 7, 6, 5   -- all DRAIN
    bottom row, left to right:  1, 2, 3, 4   -- 1/2/3 SOURCE, 4 GATE

The central drain pad is electrically the same node as pins 5-8, so it is
emitted as a second pad numbered "5". KiCad merges same-numbered pads onto one
net, which is how a thermal pad that is also a pin should be modelled -- and
it means all four drain symbol pins find a pad instead of three reporting as
missing.

Usage:
    python3 symbols/tools/gen_tphr8504pl_footprint.py
"""
# Authored by Claude Opus 5 (Anthropic) during the 2026-08-15 layout pass,
# TODO.md 12.5. AI-generated; reviewed against the primary source named in the
# docstring above. Not human-authored.

import itertools
import uuid
from pathlib import Path

FOOTPRINT_NAME = "Toshiba_2-5W1A_SOP-Advance-N_5.15x6.1mm_P1.27mm"

# ---- Terminal geometry, [49] p.9 (2-5W1A) --------------------------------
OVERALL_W = 5.15
OVERALL_H = 6.10
BODY_W = 4.90
BODY_H = 5.75
PITCH = 1.27
LEAD_W = 0.40  # lead width, 0.4 +/-0.1
LEAD_TOP_L = 0.56  # top (drain) lead contact length
LEAD_BOT_L = 0.65  # bottom (source/gate) lead contact length
DRAIN_W = 4.21
DRAIN_H = 3.69

# ---- Land pattern, Toshiba [50] p.46 SOP Advance(N) ----------------------
LAND_W = 4.70  # overall land width
PAD_W = 0.85  # lead and tab pad width
DRAIN_TOTAL_H = 4.80  # drain land, castellations included
DRAIN_TAB_H = 1.05  # castellated depth at the top
DRAIN_BODY_H = 3.75  # solid part below the castellations
GAP = 0.70  # drain land to lead pads
LEAD_PAD_H = 1.45  # lead pad height
LAND_H = DRAIN_TOTAL_H + GAP + LEAD_PAD_H  # 6.95

# Land-centred coordinates, y down.
DRAIN_TAB_CY = -LAND_H / 2 + DRAIN_TAB_H / 2  # -2.950
DRAIN_BODY_CY = -LAND_H / 2 + DRAIN_TAB_H + DRAIN_BODY_H / 2  # -0.550
LEAD_CY = LAND_H / 2 - LEAD_PAD_H / 2  # +2.750

# Paste over the large drain land is split so the aperture does not float the
# part or trap voids. Coverage ~60%, a stencil convention, not a [50] value.
PASTE_COLS, PASTE_ROWS = 3, 2
PASTE_COVERAGE = 0.60

SILK_W = 0.12
FAB_W = 0.10
CRTYD_W = 0.05
CRTYD_CLR = 0.25

DATASHEET = "docs/datasheets/TPHR8504PL_datasheet_en_20191024.pdf"
DESCR = (
    "Toshiba 2-5W1A SOP Advance(N), 8 lead, 1.27 mm pitch, 5.15x6.10 mm "
    "package. Land pattern is TOSHIBA'S OWN, from REFERENCES.md [50] "
    "(MOSFET Product Catalog ALQ00024) p.46 -- 4.7 mm wide, castellated "
    "4.7x4.8 mm drain land, 0.85x1.45 mm lead pads, 0.7 mm gap. Pads 1/2/3 "
    "source, 4 gate, 5-8 drain; the drain land carries the same numbers as "
    "the drain leads so they merge onto one net. NOT interchangeable with the "
    "2-5Q1S SOP Advance variant. Generated by "
    "symbols/tools/gen_tphr8504pl_footprint.py"
)
TAGS = "Toshiba 2-5W1A SOP Advance N MOSFET TPHR8504PL power 5x6"


def u() -> str:
    """Fresh UUID for a footprint element."""
    return str(uuid.uuid4())


def pad_columns() -> list[float]:
    """The four pad x centres, on the 1.27 mm pitch."""
    return [-1.5 * PITCH + i * PITCH for i in range(4)]  # -1.905 .. +1.905


def build() -> str:
    """Emit the complete .kicad_mod S-expression text."""
    L: list[str] = []
    add = L.append

    add(f'(footprint "{FOOTPRINT_NAME}"')
    add("\t(version 20241229)")
    add('\t(generator "gen_tphr8504pl_footprint.py")')
    add('\t(generator_version "9.0")')
    add('\t(layer "F.Cu")')
    add(f'\t(descr "{DESCR}")')
    add(f'\t(tags "{TAGS}")')
    add("\t(attr smd)")

    add('\t(property "Reference" "Q**"')
    add(f"\t\t(at 0 {-(OVERALL_H / 2 + 1.2):.3f} 0)")
    add('\t\t(layer "F.SilkS")')
    add(f'\t\t(uuid "{u()}")')
    add("\t\t(effects (font (size 1 1) (thickness 0.15)))")
    add("\t)")
    add(f'\t(property "Value" "{FOOTPRINT_NAME}"')
    add(f"\t\t(at 0 {OVERALL_H / 2 + 1.2:.3f} 0)")
    add('\t\t(layer "F.Fab")')
    add(f'\t\t(uuid "{u()}")')
    add("\t\t(effects (font (size 1 1) (thickness 0.15)))")
    add("\t)")
    add(f'\t(property "Datasheet" "{DATASHEET}" (at 0 0 0) (layer "F.Fab") (hide yes)')
    add(f'\t\t(uuid "{u()}")')
    add("\t\t(effects (font (size 1 1) (thickness 0.15)))")
    add("\t)")
    add('\t(fp_text user "${REFERENCE}"')
    add("\t\t(at 0 0 0)")
    add('\t\t(layer "F.Fab")')
    add(f'\t\t(uuid "{u()}")')
    add("\t\t(effects (font (size 0.8 0.8) (thickness 0.12)))")
    add("\t)")

    # ---- F.Fab: package body, with a pin-1 chamfer ----------------------
    bx, by, ch = BODY_W / 2, BODY_H / 2, 0.6
    fab = [
        (-bx, by - ch),
        (-bx + ch, by),
        (bx, by),
        (bx, -by),
        (-bx, -by),
        (-bx, by - ch),
    ]
    for (x1, y1), (x2, y2) in itertools.pairwise(fab):
        add(
            f"\t(fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) "
            f'(stroke (width {FAB_W}) (type solid)) (layer "F.Fab") (uuid "{u()}"))'
        )

    # ---- F.CrtYd --------------------------------------------------------
    cx = max(OVERALL_W, LAND_W) / 2 + CRTYD_CLR
    cy = max(OVERALL_H, LAND_H) / 2 + CRTYD_CLR
    cyd = [(-cx, -cy), (cx, -cy), (cx, cy), (-cx, cy), (-cx, -cy)]
    for (x1, y1), (x2, y2) in itertools.pairwise(cyd):
        add(
            f"\t(fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) "
            f'(stroke (width {CRTYD_W}) (type solid)) (layer "F.CrtYd") (uuid "{u()}"))'
        )

    # ---- F.SilkS: pin-1 dot, clear of copper ----------------------------
    add(
        f"\t(fp_circle (center {-(LAND_W / 2 + 0.55):.4f} {LEAD_CY:.4f}) "
        f"(end {-(LAND_W / 2 + 0.55) + 0.15:.4f} {LEAD_CY:.4f}) "
        f"(stroke (width {SILK_W}) (type solid)) (fill solid) "
        f'(layer "F.SilkS") (uuid "{u()}"))'
    )

    # ---- Lead pads 1-4, bottom row, left to right ------------------------
    for num, x in zip(("1", "2", "3", "4"), pad_columns()):
        add(f'\t(pad "{num}" smd roundrect')
        add(f"\t\t(at {x:.4f} {LEAD_CY:.4f})")
        add(f"\t\t(size {PAD_W:.4f} {LEAD_PAD_H:.4f})")
        add('\t\t(layers "F.Cu" "F.Paste" "F.Mask")')
        add("\t\t(roundrect_rratio 0.058824)")
        add(f'\t\t(uuid "{u()}")')
        add("\t)")

    # ---- Drain land: solid body plus the four castellated tabs -----------
    # One connected shape in copper. The tabs take the drain lead numbers so
    # every drain symbol pin resolves to a pad; the body repeats number 5 so
    # KiCad merges it onto the same net.
    add('\t(pad "5" smd rect')
    add(f"\t\t(at 0 {DRAIN_BODY_CY:.4f})")
    add(f"\t\t(size {LAND_W:.4f} {DRAIN_BODY_H:.4f})")
    add('\t\t(layers "F.Cu" "F.Mask")')
    add(f'\t\t(uuid "{u()}")')
    add("\t)")
    for num, x in zip(("8", "7", "6", "5"), pad_columns()):
        add(f'\t(pad "{num}" smd rect')
        add(f"\t\t(at {x:.4f} {DRAIN_TAB_CY:.4f})")
        add(f"\t\t(size {PAD_W:.4f} {DRAIN_TAB_H:.4f})")
        add('\t\t(layers "F.Cu" "F.Mask")')
        add(f'\t\t(uuid "{u()}")')
        add("\t)")

    # Segmented paste over the solid part of the drain land.
    ap_w = LAND_W / PASTE_COLS * (PASTE_COVERAGE**0.5)
    ap_h = DRAIN_BODY_H / PASTE_ROWS * (PASTE_COVERAGE**0.5)
    for i in range(PASTE_COLS):
        for j in range(PASTE_ROWS):
            px = (i - (PASTE_COLS - 1) / 2) * (LAND_W / PASTE_COLS)
            py = DRAIN_BODY_CY + (j - (PASTE_ROWS - 1) / 2) * (
                DRAIN_BODY_H / PASTE_ROWS
            )
            add('\t(pad "5" smd rect')
            add(f"\t\t(at {px:.4f} {py:.4f})")
            add(f"\t\t(size {ap_w:.4f} {ap_h:.4f})")
            add('\t\t(layers "F.Paste")')
            add(f'\t\t(uuid "{u()}")')
            add("\t)")
    # Paste on the tabs too, matching their copper.
    for x in pad_columns():
        add('\t(pad "5" smd rect')
        add(f"\t\t(at {x:.4f} {DRAIN_TAB_CY:.4f})")
        add(f"\t\t(size {PAD_W:.4f} {DRAIN_TAB_H:.4f})")
        add('\t\t(layers "F.Paste")')
        add(f'\t\t(uuid "{u()}")')
        add("\t)")

    add("\t(embedded_fonts no)")
    add(")")
    return "\n".join(L) + "\n"


def main() -> None:
    """Write the footprint into this repo's own .pretty library."""
    repo = Path(__file__).resolve().parents[2]
    out = repo / "symbols" / "footprints" / "Open_Secure_ESC.pretty"
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{FOOTPRINT_NAME}.kicad_mod"
    target.write_text(build(), encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
