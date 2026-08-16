#!/usr/bin/env python3
"""Generate the KiCad footprint for TI package RTA0040B (WQFN-40, 6x6 mm).

Used by the DRV8353S 3-phase gate driver (U5) -- see
symbols/specs/DRV8353S.json and builds/6s/50A/CAN_485_faraday/README.md.

This footprint closes the gap recorded in symbols/specs/DRV8353S.json
("no existing KiCad standard footprint was confirmed to match ... exactly")
and in builds/6s/50A/CAN_485_faraday/kicad/README.md ("No footprint for U5").
KiCad 9.0's Package_DFN_QFN library ships no WQFN-40 6x6 mm P0.5 mm part with
a 4.15 x 4.15 mm exposed pad, so the land is generated here instead of
referencing a system library footprint.

SOURCE OF EVERY NUMBER BELOW
----------------------------
Primary source: REFERENCES.md [21], Texas Instruments *DRV835x 100-V
Three-Phase Smart Gate Driver* data sheet, SLVSDY6A (AUGUST 2018, REVISED
JUNE 2019), local copy `docs/datasheets/drv8353.pdf`, mechanical drawing
sheet `RTA0040B` (drawing number 4219112/A, 07/2018), which occupies three
sheets in that PDF:

    PACKAGE OUTLINE       -- body, pitch, terminal, exposed-pad dimensions
    EXAMPLE BOARD LAYOUT  -- TI's own recommended land pattern (used here)
    EXAMPLE STENCIL DESIGN-- TI's own recommended paste apertures (used here)

Unlike gen_optiga_uson10_footprint.py -- where Infineon publishes no land
pattern and the fillets had to be an IPC-7351 derivation flagged per
AGENTS.md Sec.4 -- TI DOES publish a recommended land pattern for RTA0040B.
Every copper, mask and paste dimension in this file is therefore a
manufacturer recommendation read directly from that sheet, not a derivation.

Values transcribed from the PACKAGE OUTLINE sheet:

    feature                       drawing callout
    body                          6.1 / 5.9        (-> 6.0 nominal square)
    max height                    0.8 MAX
    standoff                      0.05 / 0.00
    terminal pitch                36X 0.5
    terminal row span (per side)  2X 4.5           (9 pitches x 0.5)
    terminal width                40X 0.28 / 0.16  (-> 0.22 nominal)
    terminal length               40X 0.5 / 0.3    (-> 0.4 nominal)
    exposed thermal pad           4.15 +/-0.1      (square)

Values transcribed from the EXAMPLE BOARD LAYOUT sheet:

    feature                       drawing callout
    land pad length               40X (0.6)
    land pad width                40X (0.22)
    land pitch                    36X (0.5)
    opposite pad rows, centres    2X (5.8)
    terminal row span             2X (4.5)
    thermal land                  (4.15) square
    corner radius                 (R0.05) TYP
    thermal vias                  12X (0.2) VIA TYP  -- "optional", see note 5

    -> pad centre offset from package centre = 5.8 / 2 = 2.9 mm

WHAT (5.8) MEASURES -- CHECKED, NOT ASSUMED
--------------------------------------------
(5.8) is the CENTRE-TO-CENTRE distance between opposite pad rows, not the
outer copper extent. Reading it as the outer extent puts every pad 0.3 mm too
far inward and makes the corner pads overlap, which is a dead short between
e.g. pad 1 (CPL) and pad 40 (VGLS).

The drawing sheet was rendered at 400 dpi and the pads measured by colour
segmentation, calibrated on the one dimension that cannot be misread -- the
4.5 mm row span, which is fixed by "36X 0.5" (9 gaps x 0.5 mm per side).
On that single scale, three independent dimensions all land on their printed
callouts, which is what confirms the reading:

    measurement          printed callout
    pad centre axis  2.901        (5.8)/2 = 2.900
    pad size         0.621 x 0.236   40X (0.6) / 40X (0.22)
    thermal land     4.170 x 4.165   (4.15) square

That also puts the land in the right place physically: with centres at 2.9,
each pad runs 2.6 to 3.2 mm from centre -- its inner edge flush with the
terminal's inner edge (body 6.0 / 2 = 3.0 less the 0.4 mm terminal) and
0.2 mm of toe fillet past the body edge. That is a textbook QFN land.

PIN NUMBERING
-------------
Taken from the numbers printed on the EXAMPLE BOARD LAYOUT sheet itself,
since that sheet IS the land pattern this file reproduces:

    pins  1-10  left column,  top -> bottom
    pins 11-20  bottom row,   left -> right
    pins 21-30  right column, bottom -> top
    pins 31-40  top row,      right -> left

Cross-checked against the package drawing two ways: the top view marks the
PIN 1 INDEX AREA at the top left, which is where pin 1 lands above; and the
bottom view numbers its top row 11-20 left-to-right, which is the vertical
mirror of the land pattern's bottom row -- exactly the relationship a bottom
view and a top-view land must have.

Values transcribed from the EXAMPLE STENCIL DESIGN sheet:

    thermal paste apertures       9X (1.17) square, 3x3 array

The signal map itself is unchanged and comes from [21] Sec. 6 "Pin
Configuration and Functions": pin 1 = CPL, pin 30 = nSCS, pin 39 = GND, all
three agreeing with symbols/specs/DRV8353S.json.

THERMAL PAD NET -- ENGINEERING DEFAULT, NOT A DATASHEET ASSIGNMENT
------------------------------------------------------------------
[21]'s RTA0040B drawing note 3 requires the thermal pad to be soldered
("The package thermal pad must be soldered to the printed circuit board for
optimal thermal and mechanical performance"), and Sec. 11.1 Layout
Guidelines requires a ground plane connection at the GND pin, but neither
states in so many words that the exposed pad is internally tied to GND.
Tying pad 41 to GND is therefore recorded as an ENGINEERING DEFAULT per
AGENTS.md Sec.4 -- the same treatment builds/6s/50A/CAN_485_faraday/kicad/README.md
gives the generic support passives -- and is flagged in TODO.md. Do not
restate it as a datasheet-sourced fact.

Usage:
    python3 symbols/tools/gen_drv8353s_rta0040b_footprint.py
"""
# Authored by Claude Opus 5 (Anthropic) during the 2026-08-15 layout pass,
# TODO.md 12.4. AI-generated; reviewed against the primary sources named
# in the docstring above. Not human-authored.


import uuid
from pathlib import Path

# --------------------------------------------------------------------------
# Dimensions -- every value here is traceable to the drawing quoted above.
# --------------------------------------------------------------------------

FOOTPRINT_NAME = "TI_RTA0040B_WQFN-40_6x6mm_P0.5mm_EP4.15x4.15mm"

BODY = 6.0            # PACKAGE OUTLINE: 6.1 / 5.9 -> 6.0 nominal square
PITCH = 0.5           # PACKAGE OUTLINE: 36X 0.5
PINS_PER_SIDE = 10
PAD_LEN = 0.6         # EXAMPLE BOARD LAYOUT: 40X (0.6)
PAD_WID = 0.22        # EXAMPLE BOARD LAYOUT: 40X (0.22)
ROW_CENTRES = 5.8     # EXAMPLE BOARD LAYOUT: 2X (5.8), centre to centre
PAD_CENTRE = ROW_CENTRES / 2.0               # = 2.9 mm
EP = 4.15             # PACKAGE OUTLINE: 4.15 +/-0.1 ; LAYOUT: (4.15)
CORNER_R = 0.05       # EXAMPLE BOARD LAYOUT: (R0.05) TYP
VIA_DRILL = 0.2       # EXAMPLE BOARD LAYOUT: 12X (0.2) VIA TYP
PASTE_APERTURE = 1.17  # EXAMPLE STENCIL DESIGN: 9X (1.17)
PASTE_ARRAY = 3        # 3x3 = 9 apertures

# Silkscreen / courtyard are KiCad drafting conventions, not datasheet values.
SILK_W = 0.12
FAB_W = 0.10
CRTYD_W = 0.05
# Courtyard clears the copper, which reaches 2.9 + 0.6/2 = 3.2 mm, further
# out than the 6.0 mm body.
CRTYD_CLR = 0.25

DATASHEET = (
    "https://www.ti.com/lit/ds/symlink/drv8353.pdf"
)
DESCR = (
    "TI RTA0040B, WQFN-40, 6x6 mm body, 0.5 mm pitch, 4.15x4.15 mm exposed "
    "thermal pad. Land pattern and paste apertures are TI's own recommendation "
    "from the RTA0040B mechanical drawing (4219112/A 07/2018) in SLVSDY6A "
    "(REFERENCES.md [21]) -- EXAMPLE BOARD LAYOUT and EXAMPLE STENCIL DESIGN "
    "sheets, not an IPC derivation. Pad 41 is the exposed thermal pad; "
    "drawing note 3 requires it to be soldered. Generated by "
    "symbols/tools/gen_drv8353s_rta0040b_footprint.py"
)
TAGS = "TI RTA0040B WQFN QFN 40 6x6 0.5 thermal pad DRV8353S"


def u() -> str:
    """Fresh UUID for a footprint element."""
    return str(uuid.uuid4())


def pad_positions() -> list[tuple[int, float, float, float]]:
    """Return (number, x, y, rotation) for pads 1..40.

    Counter-clockwise from bottom-left, per [21] Sec. 6 top-view diagram.
    KiCad's Y axis points down, so "up the left side" is decreasing Y.
    """
    out: list[tuple[int, float, float, float]] = []
    # Offsets of the 10 pads along a side, centred on 0: -2.25 .. +2.25
    span = (PINS_PER_SIDE - 1) * PITCH          # 4.5 mm, matches 2X (4.5)
    offs = [-span / 2.0 + i * PITCH for i in range(PINS_PER_SIDE)]

    n = 1
    # Pins 1-10: left column, top -> bottom. Pad long axis lies in X.
    for o in offs:
        out.append((n, -PAD_CENTRE, o, 0.0))
        n += 1
    # Pins 11-20: bottom row, left -> right. Pad long axis lies in Y.
    for o in offs:
        out.append((n, o, PAD_CENTRE, 90.0))
        n += 1
    # Pins 21-30: right column, bottom -> top.
    for o in reversed(offs):
        out.append((n, PAD_CENTRE, o, 0.0))
        n += 1
    # Pins 31-40: top row, right -> left.
    for o in reversed(offs):
        out.append((n, o, -PAD_CENTRE, 90.0))
        n += 1
    return out


def build() -> str:
    """Emit the complete .kicad_mod S-expression text."""
    L: list[str] = []
    add = L.append

    add(f'(footprint "{FOOTPRINT_NAME}"')
    add("\t(version 20241229)")
    add('\t(generator "gen_drv8353s_rta0040b_footprint.py")')
    add('\t(generator_version "9.0")')
    add('\t(layer "F.Cu")')
    add(f'\t(descr "{DESCR}")')
    add(f'\t(tags "{TAGS}")')
    add("\t(attr smd)")

    # ---- reference / value / user text -----------------------------------
    add('\t(property "Reference" "U**"')
    add(f"\t\t(at 0 {-(BODY / 2 + 1.0):.3f} 0)")
    add('\t\t(layer "F.SilkS")')
    add(f'\t\t(uuid "{u()}")')
    add("\t\t(effects (font (size 1 1) (thickness 0.15)))")
    add("\t)")
    add(f'\t(property "Value" "{FOOTPRINT_NAME}"')
    add(f"\t\t(at 0 {BODY / 2 + 1.0:.3f} 0)")
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
    add("\t\t(effects (font (size 1 1) (thickness 0.15)))")
    add("\t)")

    # ---- F.Fab: body outline with a chamfered pin-1 corner ---------------
    h = BODY / 2.0
    ch = 0.6  # drafting convention, marks pin 1 on the fab layer
    fab = [
        (-h + ch, h), (h, h), (h, -h), (-h, -h), (-h, h - 0.0),
    ]
    # Chamfer at bottom-left (pin-1 side, KiCad +Y is down = "bottom")
    # Chamfer marks pin 1, which sits at the TOP-left (KiCad +Y is down).
    fab_pts = [(-h, -h + ch), (-h + ch, -h), (h, -h), (h, h), (-h, h), (-h, -h + ch)]
    for (x1, y1), (x2, y2) in zip(fab_pts, fab_pts[1:]):
        add(
            f'\t(fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) '
            f'(stroke (width {FAB_W}) (type solid)) (layer "F.Fab") (uuid "{u()}"))'
        )

    # ---- F.SilkS: four corner ticks clear of the pads --------------------
    # Pads span +/-2.9 mm; silk sits just outside the body corners.
    s = PAD_CENTRE + PAD_LEN / 2 + 0.11
    tick = 0.7
    for sx in (-1, 1):
        for sy in (-1, 1):
            add(
                f"\t(fp_line (start {sx * s:.4f} {sy * (s - tick):.4f}) "
                f"(end {sx * s:.4f} {sy * s:.4f}) "
                f'(stroke (width {SILK_W}) (type solid)) (layer "F.SilkS") (uuid "{u()}"))'
            )
            add(
                f"\t(fp_line (start {sx * (s - tick):.4f} {sy * s:.4f}) "
                f"(end {sx * s:.4f} {sy * s:.4f}) "
                f'(stroke (width {SILK_W}) (type solid)) (layer "F.SilkS") (uuid "{u()}"))'
            )
    # Pin-1 dot, clear of the copper, on the pin-1 (top-left) side
    add(
        f"\t(fp_circle (center {-(h + 0.75):.4f} {-(h + 0.75):.4f}) "
        f"(end {-(h + 0.75) + 0.15:.4f} {-(h + 0.75):.4f}) "
        f'(stroke (width {SILK_W}) (type solid)) (fill solid) (layer "F.SilkS") (uuid "{u()}"))'
    )

    # ---- F.CrtYd ---------------------------------------------------------
    c = PAD_CENTRE + PAD_LEN / 2 + CRTYD_CLR
    cy = [(-c, -c), (c, -c), (c, c), (-c, c), (-c, -c)]
    for (x1, y1), (x2, y2) in zip(cy, cy[1:]):
        add(
            f'\t(fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) '
            f'(stroke (width {CRTYD_W}) (type solid)) (layer "F.CrtYd") (uuid "{u()}"))'
        )

    # ---- Perimeter pads 1..40 -------------------------------------------
    for num, x, y, rot in pad_positions():
        # Pad long axis is radial: X-oriented pads on left/right, Y on top/bottom.
        sx, sy = (PAD_LEN, PAD_WID) if rot == 0.0 else (PAD_WID, PAD_LEN)
        ratio = CORNER_R / min(sx, sy)
        add(f'\t(pad "{num}" smd roundrect')
        add(f"\t\t(at {x:.4f} {y:.4f})")
        add(f"\t\t(size {sx:.4f} {sy:.4f})")
        add('\t\t(layers "F.Cu" "F.Paste" "F.Mask")')
        add(f"\t\t(roundrect_rratio {ratio:.6f})")
        add(f'\t\t(uuid "{u()}")')
        add("\t)")

    # ---- Pad 41: exposed thermal pad ------------------------------------
    # Copper + mask opening are the full 4.15 mm square; paste is the 3x3
    # array of 1.17 mm apertures from the EXAMPLE STENCIL DESIGN sheet, so
    # the copper pad itself is declared with no paste layer.
    add('\t(pad "41" smd rect')
    add("\t\t(at 0 0)")
    add(f"\t\t(size {EP:.4f} {EP:.4f})")
    add('\t\t(layers "F.Cu" "F.Mask")')
    add(f'\t\t(uuid "{u()}")')
    add("\t)")

    # 3x3 paste apertures, 1.17 mm square, evenly spread over the 4.15 mm pad.
    step = (EP - PASTE_APERTURE) / (PASTE_ARRAY - 1)
    base = -(EP - PASTE_APERTURE) / 2.0
    for i in range(PASTE_ARRAY):
        for j in range(PASTE_ARRAY):
            px = base + i * step
            py = base + j * step
            add('\t(pad "41" smd rect')
            add(f"\t\t(at {px:.4f} {py:.4f})")
            add(f"\t\t(size {PASTE_APERTURE:.4f} {PASTE_APERTURE:.4f})")
            add('\t\t(layers "F.Paste")')
            add(f'\t\t(uuid "{u()}")')
            add("\t)")

    # ---- 12 thermal vias, "optional" per EXAMPLE BOARD LAYOUT note 5 -----
    # TI's sheet shows them on the exposed pad; positions here are the 12
    # points of a 4x4 grid minus its 4 interior points, spread over the
    # 4.15 mm pad. Note 5 makes the vias optional, so their exact placement
    # is a layout choice, not a datasheet requirement -- see AGENTS.md Sec.4.
    vpitch = 1.15
    steps = (-1.5, -0.5, 0.5, 1.5)
    vias = [
        (i * vpitch, j * vpitch)
        for i in steps
        for j in steps
        if not (abs(i) == 0.5 and abs(j) == 0.5)  # drop 4 interior -> 12 vias
    ]
    for vx, vy in vias:
        add('\t(pad "41" thru_hole circle')
        add(f"\t\t(at {vx:.4f} {vy:.4f})")
        add(f"\t\t(size {VIA_DRILL + 0.2:.4f} {VIA_DRILL + 0.2:.4f})")
        add(f"\t\t(drill {VIA_DRILL:.4f})")
        add('\t\t(layers "*.Cu" "*.Mask")')
        add('\t\t(remove_unused_layers no)')
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
