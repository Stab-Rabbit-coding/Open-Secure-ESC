#!/usr/bin/env python3
"""Generate the populated 6S/50A CAN+RS485/Faraday PCB.

Footprints are parametric stand-ins (pad count / package envelope matches the
footprint name already recorded in symbols/specs/*.json) rather than exact
copies of KiCad's system footprint libraries, which aren't available in this
environment. No copper nets are assigned yet (all pads net-less) -- this is a
"footprints placed, board outline defined" checkpoint; netlist import and
routing are the documented next step (see kicad/README.md).
"""
import json
import re
import sys
import uuid
from pathlib import Path

SCRATCH = Path(__file__).parent
sys.path.insert(0, str(SCRATCH))
from genlib import REPO  # noqa: E402

from kiutils.board import Board
from kiutils.footprint import Footprint, Pad, DrillDefinition, Attributes
from kiutils.items.common import Position, Effects, Font, TitleBlock, PageSettings
from kiutils.items.fpitems import FpText, FpRect
from kiutils.items.gritems import GrRect, GrText, GrLine

BUILD_KICAD_DIR = REPO / "builds/6s/50A/CAN_485_faraday/kicad"
PROJECT_NAME = "open_secure_esc_6s_50a_can485_faraday"


def U():
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Parametric footprint builders
# ---------------------------------------------------------------------------

def fp_text_pair(ref_text, val_text, size=1.0, dy=None):
    if dy is None:
        dy = size * 3
    return [
        FpText(type="reference", text=ref_text, position=Position(0, -dy, 0), layer="F.SilkS",
               effects=Effects(font=Font(height=size, width=size)), tstamp=U()),
        FpText(type="value", text=val_text, position=Position(0, dy, 0), layer="F.Fab",
               effects=Effects(font=Font(height=size, width=size)), tstamp=U()),
    ]


def two_pad_smd(lib_id, ref, value, span, pad_w, pad_h):
    fp = Footprint()
    fp.libId = lib_id
    fp.attributes = Attributes(type="smd")
    fp.tstamp = U()
    fp.graphicItems = fp_text_pair(ref, value, size=1.0, dy=pad_h / 2 + 1.5)
    fp.pads = [
        Pad(number="1", type="smd", shape="roundrect", roundrectRatio=0.2,
            position=Position(-span / 2, 0, 0), size=Position(pad_w, pad_h),
            layers=["F.Cu", "F.Paste", "F.Mask"], tstamp=U()),
        Pad(number="2", type="smd", shape="roundrect", roundrectRatio=0.2,
            position=Position(span / 2, 0, 0), size=Position(pad_w, pad_h),
            layers=["F.Cu", "F.Paste", "F.Mask"], tstamp=U()),
    ]
    return fp


def two_pad_tht(lib_id, ref, value, pitch, drill=0.8, pad_d=1.6):
    fp = Footprint()
    fp.libId = lib_id
    fp.attributes = Attributes(type="through_hole")
    fp.tstamp = U()
    fp.graphicItems = fp_text_pair(ref, value, size=1.0, dy=pitch / 2 + 2)
    fp.pads = [
        Pad(number="1", type="thru_hole", shape="rect", position=Position(-pitch / 2, 0, 0),
            size=Position(pad_d, pad_d), drill=DrillDefinition(diameter=drill),
            layers=["*.Cu", "*.Mask"], tstamp=U()),
        Pad(number="2", type="thru_hole", shape="circle", position=Position(pitch / 2, 0, 0),
            size=Position(pad_d, pad_d), drill=DrillDefinition(diameter=drill),
            layers=["*.Cu", "*.Mask"], tstamp=U()),
    ]
    return fp


def dual_row_smd(lib_id, ref, value, npins, row_span, pitch, pad_w, pad_h):
    """SOIC/SO style: pins 1..n/2 down the left row (top to bottom),
    n/2+1..n up the right row (bottom to top) -- standard IC numbering."""
    fp = Footprint()
    fp.libId = lib_id
    fp.attributes = Attributes(type="smd")
    fp.tstamp = U()
    n_side = npins // 2
    y0 = -(n_side - 1) * pitch / 2
    fp.graphicItems = fp_text_pair(ref, value, size=1.0, dy=(n_side - 1) * pitch / 2 + 2)
    pads = []
    for i in range(n_side):
        pads.append(Pad(number=str(i + 1), type="smd", shape="rect",
                         position=Position(-row_span / 2, y0 + i * pitch, 0),
                         size=Position(pad_w, pad_h), layers=["F.Cu", "F.Paste", "F.Mask"], tstamp=U()))
    for i in range(n_side):
        num = n_side + i + 1
        y = y0 + (n_side - 1 - i) * pitch
        pads.append(Pad(number=str(num), type="smd", shape="rect",
                         position=Position(row_span / 2, y, 0),
                         size=Position(pad_w, pad_h), layers=["F.Cu", "F.Paste", "F.Mask"], tstamp=U()))
    fp.pads = pads
    return fp


def perimeter_qfp(lib_id, ref, value, npins, body_w, body_h, pitch, pad_w, pad_h):
    """4-side perimeter package, counter-clockwise from pin 1 at top-left of
    the left edge -- standard QFP/QFN numbering direction."""
    fp = Footprint()
    fp.libId = lib_id
    fp.attributes = Attributes(type="smd")
    fp.tstamp = U()
    n_side = npins // 4
    fp.graphicItems = fp_text_pair(ref, value, size=1.0, dy=body_h / 2 + pad_h + 2)
    pads = []
    num = 1
    y0 = -(n_side - 1) * pitch / 2
    x_edge = body_w / 2 + pad_h / 2 - 0.2
    for i in range(n_side):
        pads.append(Pad(number=str(num), type="smd", shape="rect",
                         position=Position(-x_edge, y0 + i * pitch, 0),
                         size=Position(pad_h, pad_w), layers=["F.Cu", "F.Paste", "F.Mask"], tstamp=U()))
        num += 1
    x0 = -(n_side - 1) * pitch / 2
    y_edge = body_h / 2 + pad_h / 2 - 0.2
    for i in range(n_side):
        pads.append(Pad(number=str(num), type="smd", shape="rect",
                         position=Position(x0 + i * pitch, y_edge, 0),
                         size=Position(pad_w, pad_h), layers=["F.Cu", "F.Paste", "F.Mask"], tstamp=U()))
        num += 1
    for i in range(n_side):
        pads.append(Pad(number=str(num), type="smd", shape="rect",
                         position=Position(x_edge, -y0 - i * pitch, 0),
                         size=Position(pad_h, pad_w), layers=["F.Cu", "F.Paste", "F.Mask"], tstamp=U()))
        num += 1
    for i in range(n_side):
        pads.append(Pad(number=str(num), type="smd", shape="rect",
                         position=Position(-x0 - i * pitch, -y_edge, 0),
                         size=Position(pad_w, pad_h), layers=["F.Cu", "F.Paste", "F.Mask"], tstamp=U()))
        num += 1
    fp.pads = pads
    return fp


def row_tht(lib_id, ref, value, npins, pitch, drill=1.0, pad_d=1.7):
    fp = Footprint()
    fp.libId = lib_id
    fp.attributes = Attributes(type="through_hole")
    fp.tstamp = U()
    fp.graphicItems = fp_text_pair(ref, value, size=1.0, dy=(npins - 1) * pitch / 2 + 2.5)
    pads = []
    for i in range(npins):
        shape = "rect" if i == 0 else "circle"
        pads.append(Pad(number=str(i + 1), type="thru_hole", shape=shape,
                         position=Position(0, i * pitch, 0), size=Position(pad_d, pad_d),
                         drill=DrillDefinition(diameter=drill), layers=["*.Cu", "*.Mask"], tstamp=U()))
    fp.pads = pads
    return fp


def mechanical_outline(lib_id, ref, value, outer_w, outer_h, note):
    """Placeholder for a mechanical, no-copper-net part (Faraday shield can) --
    outline + a single GND bond pad, sized to the verified datasheet dimensions."""
    fp = Footprint()
    fp.libId = lib_id
    fp.attributes = Attributes(type="other", excludeFromPosFiles=True, excludeFromBom=False)
    fp.tstamp = U()
    fp.graphicItems = fp_text_pair(ref, value, size=1.0, dy=outer_h / 2 + 2)
    fp.graphicItems.append(FpRect(start=Position(-outer_w / 2, -outer_h / 2),
                                   end=Position(outer_w / 2, outer_h / 2),
                                   layer="Cmts.User", width=0.15, tstamp=U()))
    fp.graphicItems.append(FpText(type="user", text=note, position=Position(0, 0, 0),
                                   layer="Cmts.User",
                                   effects=Effects(font=Font(height=0.8, width=0.8)), tstamp=U()))
    fp.pads = [Pad(number="1", type="smd", shape="rect", position=Position(0, outer_h / 2 - 1.5, 0),
                   size=Position(3, 2), layers=["F.Cu", "F.Paste", "F.Mask"], tstamp=U())]
    return fp


def reserved_area(x, y, w, h, text):
    """Board-level (not a footprint) reserved-area marker for parts with no
    confirmed footprint yet -- see AGENTS.md SS1.3 (no fabricated footprint claim)."""
    items = [
        GrRect(start=Position(x - w / 2, y - h / 2), end=Position(x + w / 2, y + h / 2),
               layer="Cmts.User", width=0.15, tstamp=U()),
        GrText(text=text, position=Position(x, y + h / 2 + 3, 0), layer="Cmts.User",
               effects=Effects(font=Font(height=1.2, width=1.2)), tstamp=U()),
    ]
    return items
from kiutils.board import Board
from kiutils.schematic import Schematic
from kiutils.items.common import Position, TitleBlock, PageSettings
from kiutils.items.brditems import SetupData
from kiutils.items.gritems import GrRect, GrText, GrLine

BUILD_KICAD_DIR = REPO / "builds/6s/50A/CAN_485_faraday/kicad"
PROJECT_NAME = "open_secure_esc_6s_50a_can485_faraday"
SPECDIR = REPO / "symbols" / "specs"


def build_footprint(ref, lib_id, value, footprint):
    if footprint == "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm":
        fp = two_pad_tht(footprint, ref, value, pitch=5.0, drill=0.8, pad_d=1.8)
    elif footprint.startswith("Connector_PinHeader_2.54mm:PinHeader_1x0"):
        n = int(re.search(r"PinHeader_1x0(\d)", footprint).group(1))
        fp = row_tht(footprint, ref, value, npins=n, pitch=2.54, drill=1.0, pad_d=1.7)
    elif footprint == "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm":
        fp = dual_row_smd(footprint, ref, value, npins=20, row_span=9.4, pitch=1.27, pad_w=2.1, pad_h=0.6)
    elif footprint == "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm":
        fp = dual_row_smd(footprint, ref, value, npins=8, row_span=5.4, pitch=1.27, pad_w=1.55, pad_h=0.6)
    elif footprint == "Package_QFP:LQFP-64_10x10mm_P0.5mm":
        fp = perimeter_qfp(footprint, ref, value, npins=64, body_w=10, body_h=10, pitch=0.5, pad_w=0.3, pad_h=1.5)
    elif footprint == "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm":
        fp = perimeter_qfp(footprint, ref, value, npins=32, body_w=5, body_h=5, pitch=0.5, pad_w=0.25, pad_h=0.55)
    elif footprint == "Resistor_SMD:R_0805_2012Metric" or footprint == "Capacitor_SMD:C_0805_2012Metric":
        fp = two_pad_smd(footprint, ref, value, span=1.5, pad_w=1.0, pad_h=1.2)
    elif footprint == "Resistor_SMD:R_2512_6332Metric":
        fp = two_pad_smd(footprint, ref, value, span=5.7, pad_w=1.8, pad_h=3.3)
    elif footprint == "Package_TO_SOT_THT:TO-220-3_Vertical":
        fp = row_tht(footprint, ref, value, npins=3, pitch=2.54, drill=1.1, pad_d=2.0)
    else:
        raise ValueError(f"no footprint generator for {footprint!r} (ref {ref})")
    fp.properties["Reference"] = ref
    return fp


# Board layout, keyed by schematic reference designator. (x, y) = footprint
# center in mm, chosen for functional-block legibility, not yet DRC-checked
# spacing -- see kicad/README.md PCB status.
REF_POS = {
    "J1": (15, 20), "J2": (15, 45), "J3": (15, 70), "J5": (15, 100), "C1": (30, 100),
    "U3": (45, 45), "U4": (45, 70),
    "U1": (90, 55),
    "R1": (75, 25), "C2": (90, 25), "C3": (105, 25),
    "R9": (78, 88), "R10": (90, 88),
    "U2": (140, 25),
    "R2": (160, 45), "R3": (166, 45), "C4": (172, 45), "C5": (178, 45),
    "C6": (184, 45), "C7": (190, 45), "C8": (196, 45),
    "Q1": (220, 20), "Q2": (220, 30), "R4": (220, 40), "U6": (245, 30),
    "Q3": (220, 60), "Q4": (220, 70), "R5": (220, 80), "U7": (245, 70),
    "Q5": (220, 100), "Q6": (220, 110), "R6": (220, 120), "U8": (245, 110),
    "R7": (270, 20), "R8": (270, 26),
    "J4": (270, 70),
    "SH1": (140, 112), "SH2": (176, 112),
}

BATT_JSON = json.loads((SPECDIR / "WE_SHC_3671375.json").read_text())
FRAME_JSON = json.loads((SPECDIR / "WE_SHC_3670375.json").read_text())


def title_block():
    tb = TitleBlock(
        title="Open-Secure-ESC -- 6S / 50A / CAN-FD+RS-485 / Faraday",
        date="2026-08-02",
        revision="0.2-populated",
        company="Griffing Technology LLC",
    )
    tb.comments[1] = "Build spec: builds/6s/50A/CAN_485_faraday/README.md"
    tb.comments[2] = "BOM/citations: docs/decision-matrix.xlsx, REFERENCES.md"
    tb.comments[3] = "Footprints placed from the populated schematic BOM; not yet netlisted or routed"
    tb.comments[4] = ("U5 (DRV8353S) has no confirmed footprint (custom WQFN, size before fab) -- "
                       "reserved area only, see kicad/README.md")
    return tb


def build_and_write(out_path):
    sch = Schematic.from_file(str(BUILD_KICAD_DIR / f"{PROJECT_NAME}.kicad_sch"))

    board = Board.create_new()
    board.generator = "open_secure_esc_pcbgen"
    board.paper = PageSettings(paperSize="A3")

    bbox = [1e9, 1e9, -1e9, -1e9]

    def touch(x, y, half=0):
        bbox[0] = min(bbox[0], x - half)
        bbox[1] = min(bbox[1], y - half)
        bbox[2] = max(bbox[2], x + half)
        bbox[3] = max(bbox[3], y + half)

    placed, skipped = [], []
    for sym in sch.schematicSymbols:
        props = {p.key: p.value for p in sym.properties}
        ref = props["Reference"]
        if ref.startswith("BT"):
            skipped.append((ref, "off-board pack -- see J5 BATT_IN + ../README.md"))
            continue
        if ref == "U5":
            x, y = 140, 70
            board.graphicItems.extend(reserved_area(
                x, y, 8, 8,
                "U5 DRV8353S -- reserved area, no confirmed footprint (custom WQFN 40-RTA0040B), "
                "see symbols/specs/DRV8353S.json + kicad/README.md"))
            touch(x, y, 5)
            skipped.append((ref, "reserved area only, no footprint fabricated -- see kicad/README.md"))
            continue
        if ref in ("SH1", "SH2"):
            spec = BATT_JSON if ref == "SH1" else FRAME_JSON
            desc = spec["description"].split(" -- ")[0]
            outer_w, outer_h = (30.1, 38.3) if ref == "SH1" else (29.3, 37.5)
            x, y = REF_POS[ref]
            fp = mechanical_outline(sym.libId, ref, props["Value"], outer_w, outer_h,
                                           f"{desc} -- verified dims per REFERENCES.md [15]/[19]/[30]")
            fp.position = Position(x, y, 0)
            fp.tstamp = U()
            fp.properties["Reference"] = ref
            board.footprints.append(fp)
            touch(x, y, max(outer_w, outer_h) / 2 + 3)
            placed.append(ref)
            continue

        footprint = props.get("Footprint", "")
        if not footprint:
            skipped.append((ref, "no footprint on this instance"))
            continue
        x, y = REF_POS[ref]
        fp = build_footprint(ref, sym.libId, props.get("Value", ""), footprint)
        fp.position = Position(x, y, 0)
        fp.tstamp = U()
        board.footprints.append(fp)
        touch(x, y, 12)
        placed.append(ref)

    # PCB-only battery pack input terminal (6S pack is off-board, see README)
    x, y = REF_POS["J5"]
    fp = two_pad_tht("Connector_Wire:SolderWirePad_1x02_P5.08mm_Drill1.3mm", "J5", "BATT_IN",
                            pitch=5.08, drill=1.3, pad_d=2.5)
    fp.position = Position(x, y, 0)
    fp.properties["Reference"] = "J5"
    board.footprints.append(fp)
    board.graphicItems.append(GrText(
        text="J5 BATT_IN: 6S pack (BT1-BT6 in schematic) connects here off-board -- see ../README.md",
        position=Position(x, y + 12, 0), layer="Cmts.User", tstamp=U()))
    touch(x, y, 6)
    placed.append("J5")

    print(f"placed {len(placed)} footprints, skipped {len(skipped)}:")
    for ref, why in skipped:
        print(f"  {ref}: {why}")

    # ---- board outline (Edge.Cuts), sized to bbox + margin -----------------
    margin = 8
    ox0, oy0, ox1, oy1 = bbox[0] - margin, bbox[1] - margin, bbox[2] + margin, bbox[3] + margin
    board.graphicItems.append(GrRect(start=Position(ox0, oy0), end=Position(ox1, oy1),
                                      layer="Edge.Cuts", width=0.15, tstamp=U()))

    board_w, board_h = ox1 - ox0, oy1 - oy0

    # ---- center the board on the drawing page -------------------------------
    pw, ph = 420, 297  # A3 landscape
    title_h = 40
    area_x0, area_y0 = 10, 10
    area_x1, area_y1 = pw - 10, ph - 10 - title_h
    cx, cy = (ox0 + ox1) / 2, (oy0 + oy1) / 2
    tx = round(((area_x0 + area_x1) / 2 - cx) / 0.5) * 0.5
    ty = round(((area_y0 + area_y1) / 2 - cy) / 0.5) * 0.5

    for fp in board.footprints:
        fp.position.X = round(fp.position.X + tx, 3)
        fp.position.Y = round(fp.position.Y + ty, 3)
    for item in board.graphicItems:
        if hasattr(item, "start"):
            item.start.X = round(item.start.X + tx, 3)
            item.start.Y = round(item.start.Y + ty, 3)
            item.end.X = round(item.end.X + tx, 3)
            item.end.Y = round(item.end.Y + ty, 3)
        elif hasattr(item, "position"):
            item.position.X = round(item.position.X + tx, 3)
            item.position.Y = round(item.position.Y + ty, 3)

    print(f"board outline {board_w:.1f}x{board_h:.1f}mm, centered on A3 page (translate {tx:.2f},{ty:.2f})")

    board.titleBlock = title_block()
    board.nets = board.nets[:1]  # net 0 only -- no netlist imported yet

    out_path.write_text(board.to_sexpr())
    print(f"wrote {out_path} ({len(board.footprints)} footprints)")
    return board


if __name__ == "__main__":
    out = BUILD_KICAD_DIR / f"{PROJECT_NAME}.kicad_pcb"
    build_and_write(out)
