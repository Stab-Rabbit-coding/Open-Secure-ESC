#!/usr/bin/env python3
"""Generate the KiCad footprint for Infineon package PG-USON-10-2,-4 (3x3 mm).

Used by the OPTIGA(TM) Trust M secure element (U2) -- see
symbols/specs/OPTIGA_TRUST_M.json and docs/secure-element-architecture.md.

SOURCE OF THE PACKAGE DIMENSIONS
--------------------------------
All *package* numbers below come from the primary source: REFERENCES.md [45],
Infineon *OPTIGA(TM) Trust M Datasheet*, document release reference
Z8F80311641-D, Rev. 3.70 (2024-10-09), local copy
`docs/datasheets/infineon-optiga-trust-m-datasheet-en.pdf`, p.15 Section 4.1
Figure 6 "PG-USON-10-2,-4 Package Outline" and p.16 Figure 7
"PG-USON-10-2,-4 top view".

Figure 6 is an embedded raster drawing, so its callouts were read off the
figure and then independently CHECKED by measuring the drawing's own vector
geometry in pixels and scaling by the body dimension (the body measures
305 x 305 px and is dimensioned "3" x "3" mm, giving 101.67 px/mm). Every
measurement reproduced the printed callout:

    feature                measured        printed callout
    body                   3.000 x 3.000   "3" x "3"
    terminal pitch         0.501           "0.5" (basic, boxed)
    terminal width         0.246           "0.25 +/-0.05"
    terminal length        0.384           "0.4 +/-0.05"
    exposed pad, long      2.508           "2.5 +/-0.1"
    exposed pad, short     1.702           "1.7 +/-0.1"

That six-for-six agreement is the reason these numbers are recorded as
VERIFIED rather than "read off a picture".

SOURCE OF THE LAND PATTERN (a derivation, not a datasheet value)
----------------------------------------------------------------
Infineon publishes NO recommended land pattern for PG-USON-10-2,-4 in [45] --
unlike the TI packages in this repo (cf. gen_rhb0032t_footprint.py, which uses
TI's own "EXAMPLE BOARD LAYOUT" sheet). The toe/heel/side fillets here are
therefore an IPC-7351-style *derivation*, flagged as an engineering judgment
call per AGENTS.md SS4, NOT a manufacturer recommendation.

The specific fillet values are taken from KiCad 9.0's own
`Package_DFN_QFN:DFN-10-1EP_3x3mm_P0.5mm_EP1.7x2.5mm`, which was produced by
`kicad-footprint-generator`'s `ipc_noLead_generator.py` for an identically
dimensioned DFN-10. Using it as the fillet source is deliberate: that
footprint's package geometry (body 3x3 mm, pitch 0.5 mm, terminal width
0.25 mm, exposed pad 1.7 x 2.5 mm, and the pin-1-top-left / 1-5-down-the-left
/ 6-10-up-the-right numbering) independently reproduces every dimension
measured from Figure 6 above, so it is a corroborating second source for the
package and a defensible IPC land for the fillets.

Why this file exists at all rather than just using that KiCad footprint:
  1. Provenance. The KiCad footprint's own `descr` cites a Monolithic Power
     MPQ2483 datasheet. Shipping an Infineon part on a land documented
     against an unrelated vendor's part would be exactly the kind of
     untraceable citation AGENTS.md SS1.2/SS2 exists to prevent.
  2. The 3D model. That footprint references
     `${KICAD9_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/DFN-10-1EP_...step`,
     which is not installed on this system (KiCad's 3D model package is
     absent), so it renders as an empty part. This repo ships its own model,
     built from the Figure 6 dimensions by gen_optiga_uson10_3dmodel.py.

EXPOSED PAD
-----------
[45] p.16 Figure 7 labels the centre pad "n.c.*" with the note "Connect the
exposed pad with the copper area in the PCB to improve thermal dissipation".
It is therefore a thermal/mechanical land that is NOT internally connected to
any signal. Two consequences, both deliberate:
  - The land is emitted WITHOUT a pad number, so it carries no net and cannot
    be mismatched against the 10-pin symbol. This matches the repo-wide
    convention that an exposed pad is a footprint-level feature and not a
    schematic pin (see symbols/specs/DRV8353S.json and OPTIGA_TRUST_M.json).
  - No thermal vias are emitted. At the device's own I_CCAVG of 14 mA typical
    ([45] p.20 Table 11), dissipation is on the order of 50 mW; a via field
    would be cargo-culted, not engineered. Add one only if a thermal analysis
    calls for it.

Per AGENTS.md SS1.3, each constant carries the sheet it came from. Change a
number here and regenerate; never hand-edit the .kicad_mod.

Usage:
    python3 gen_optiga_uson10_footprint.py -o ../footprints/Open_Secure_ESC.pretty
"""

import argparse
import sys
from pathlib import Path

from kiutils.footprint import Attributes, Footprint, Model, Pad
from kiutils.items.common import Coordinate, Position
from kiutils.items.fpitems import FpLine, FpText

# ---------------------------------------------------------------------------
# PACKAGE -- [45] p.15 Figure 6 / p.16 Figure 7 (see module docstring).
# ---------------------------------------------------------------------------
BODY = 3.00  # "3" x "3", square
BODY_H = 0.60  # "0.6 Max." overall height
PITCH = 0.50  # "0.5" basic
TERM_WID = 0.25  # "0.25 +/-0.05", tangential
TERM_LEN = 0.40  # "0.4 +/-0.05", radial (flush to the body edge)
EP_X = 1.70  # "1.7 +/-0.1"  (across the rows)
EP_Y = 2.50  # "2.5 +/-0.1"  (along the rows)
PINS_PER_SIDE = 5

# ---------------------------------------------------------------------------
# LAND -- IPC-7351-style derivation, values from KiCad 9.0's
# Package_DFN_QFN:DFN-10-1EP_3x3mm_P0.5mm_EP1.7x2.5mm (see module docstring).
# ---------------------------------------------------------------------------
PAD_LEN = 0.825  # radial; = 0.05 heel (inward) + 0.40 terminal + 0.375 toe
PAD_WID = 0.25  # tangential; equals the terminal width (no side fillet,
#                       the IPC no-lead convention -- leaves a 0.25 mm gap at
#                       0.5 mm pitch)
PAD_CX = 1.4625  # pad centre, radial

# EP paste is split into 4 apertures rather than one big opening, so the part
# cannot float or tombstone on a single large solder volume.
EP_PASTE_X = 0.690
EP_PASTE_Y = 1.010
EP_PASTE_OFF_X = 0.425
EP_PASTE_OFF_Y = 0.625
# -> 4 x 0.690 x 1.010 / (1.70 x 2.50) = 65.6% paste coverage by area.

# KiCad house style (drawing/DRC conventions, not datasheet values):
CRTYD_CLEARANCE = 0.25
LINE_FAB = 0.10
LINE_SILK = 0.12
LINE_CRTYD = 0.05

NAME = "Infineon_PG-USON-10-2-4_3x3mm_P0.5mm_EP1.7x2.5mm"
MODEL_3D = (
    f"${{KIPRJMOD}}/../../symbols/footprints/Open_Secure_ESC.3dshapes/{NAME}.step"
)


def _line(start, end, layer, width):
    return FpLine(
        start=Position(round(start[0], 4), round(start[1], 4)),
        end=Position(round(end[0], 4), round(end[1], 4)),
        layer=layer,
        width=width,
    )


def build() -> Footprint:
    fp = Footprint(
        libraryNickname="Open_Secure_ESC",
        entryName=NAME,
        version="20211014",
        generator="open_secure_esc_fpgen",
        layer="F.Cu",
        description=(
            "Infineon PG-USON-10-2,-4, 10-pin USON with exposed thermal pad, "
            "0.5 mm pitch, body 3x3 mm, 0.6 mm max height, EP 1.7x2.5 mm. "
            "Package dimensions per REFERENCES.md [45] p.15 Fig.6 / p.16 "
            "Fig.7 (Infineon OPTIGA Trust M datasheet, Rev 3.70); land "
            "pattern is an IPC-7351-style derivation, NOT an Infineon "
            "recommendation (Infineon publishes none) -- see AGENTS.md SS4. "
            "Exposed pad is emitted unnumbered: it is n.c. internally and is "
            "not a schematic pin. Generated by "
            "symbols/tools/gen_optiga_uson10_footprint.py -- do not hand-edit."
        ),
        tags="USON DFN PG-USON-10 OPTIGA TrustM Infineon SMD thermal-pad",
        attributes=Attributes(type="smd"),
    )

    text_y = BODY / 2 + 1.0
    fp.graphicItems.append(
        FpText(
            type="reference",
            text="REF**",
            position=Position(0, -text_y, 0),
            layer="F.SilkS",
        )
    )
    fp.graphicItems.append(
        FpText(type="value", text=NAME, position=Position(0, text_y, 0), layer="F.Fab")
    )

    # --- Signal pads -------------------------------------------------------
    # Numbering per [45] p.16 Figure 7 (the datasheet's own top view): pin 1
    # top-left, 1..5 down the LEFT side, 6..10 up the RIGHT side.
    # (KiCad's +Y axis points down, so "down the left side" is +Y.)
    t0 = -PITCH * (PINS_PER_SIDE - 1) / 2
    for i in range(PINS_PER_SIDE):
        t = t0 + i * PITCH
        for number, x in ((1 + i, -PAD_CX), (2 * PINS_PER_SIDE - i, PAD_CX)):
            fp.pads.append(
                Pad(
                    number=str(number),
                    type="smd",
                    shape="roundrect",
                    roundrectRatio=0.25,
                    position=Position(round(x, 4), round(t, 4)),
                    size=Position(PAD_LEN, PAD_WID),
                    layers=["F.Cu", "F.Mask", "F.Paste"],
                )
            )

    # --- Exposed thermal pad (unnumbered -- see module docstring) ----------
    fp.pads.append(
        Pad(
            number="",
            type="smd",
            shape="rect",
            position=Position(0, 0),
            size=Position(EP_X, EP_Y),
            layers=["F.Cu", "F.Mask"],
        )
    )
    for sx in (-1, 1):
        for sy in (-1, 1):
            fp.pads.append(
                Pad(
                    number="",
                    type="smd",
                    shape="rect",
                    position=Position(
                        round(sx * EP_PASTE_OFF_X, 4), round(sy * EP_PASTE_OFF_Y, 4)
                    ),
                    size=Position(EP_PASTE_X, EP_PASTE_Y),
                    layers=["F.Paste"],
                )
            )

    # --- F.Fab: body outline with a pin-1 chamfer --------------------------
    h = BODY / 2
    ch = 0.5
    for s, e in (
        ((-h + ch, -h), (h, -h)),
        ((h, -h), (h, h)),
        ((h, h), (-h, h)),
        ((-h, h), (-h, -h + ch)),
        ((-h, -h + ch), (-h + ch, -h)),
    ):
        fp.graphicItems.append(_line(s, e, "F.Fab", LINE_FAB))

    # --- F.SilkS: top/bottom edges only ------------------------------------
    # The left/right body edges are fully occupied by pads, so silk there
    # would sit on copper. The pads span +/-(2.0/2 + 0.25/2) = +/-1.125 in Y,
    # which is inside the 1.5 body half-height, so short horizontal runs at
    # the top and bottom edges stay clear.
    silk_x = h + LINE_SILK / 2
    for sy in (-1, 1):
        fp.graphicItems.append(
            _line(
                (-silk_x, sy * (h + LINE_SILK)),
                (silk_x, sy * (h + LINE_SILK)),
                "F.SilkS",
                LINE_SILK,
            )
        )

    # --- F.SilkS: pin-1 dot, outboard of pin 1's land ----------------------
    p1x = PAD_CX + PAD_LEN / 2 + 0.25
    p1y = t0
    fp.graphicItems.append(
        _line((-p1x, p1y - 0.15), (-p1x, p1y + 0.15), "F.SilkS", LINE_SILK)
    )
    fp.graphicItems.append(
        _line((-p1x - 0.15, p1y), (-p1x + 0.15, p1y), "F.SilkS", LINE_SILK)
    )

    # --- F.CrtYd -----------------------------------------------------------
    cx = PAD_CX + PAD_LEN / 2 + CRTYD_CLEARANCE
    cy = BODY / 2 + CRTYD_CLEARANCE
    corners = [(-cx, -cy), (cx, -cy), (cx, cy), (-cx, cy)]
    for i in range(4):
        fp.graphicItems.append(
            _line(corners[i], corners[(i + 1) % 4], "F.CrtYd", LINE_CRTYD)
        )

    # --- 3D model ----------------------------------------------------------
    fp.models.append(
        Model(
            path=MODEL_3D,
            pos=Coordinate(0, 0, 0),
            scale=Coordinate(1, 1, 1),
            rotate=Coordinate(0, 0, 0),
        )
    )

    return fp


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--outdir", default=".", help="Output .pretty directory")
    args = ap.parse_args(argv)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"{NAME}.kicad_mod"
    out.write_text(build().to_sexpr())
    print(f"wrote {out} (10 signal pads + unnumbered EP + 4 paste apertures)")


if __name__ == "__main__":
    sys.exit(main())
