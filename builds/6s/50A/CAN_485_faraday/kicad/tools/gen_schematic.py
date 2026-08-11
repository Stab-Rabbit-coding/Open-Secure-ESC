#!/usr/bin/env python3
"""Generate the populated 6S/50A CAN+RS485/Faraday schematic.

Builds the .kicad_sch programmatically via kiutils so every wire/label is
derived from the same verified pin data in symbols/specs/*.json that
generated symbols/*.kicad_sym (see symbols/tools/gen_kicad_symbol.py).

!! DIVERGENCE WARNING -- READ BEFORE RUNNING (2026-08-10) !!

    This script is NO LONGER the sole author of the committed
    open_secure_esc_6s_50a_can485_faraday.kicad_sch. Running it as-is will
    OVERWRITE that file and SILENTLY DROP work that is not reproduced here:

      1. The OPTIGA(TM) Trust M secure element block -- U2, its two 10k I2C
         pull-ups, its 100 nF decoupling cap, the no-connect flags on contacts
         2/4/5/6/7, the SE_I2C_SDA / SE_I2C_SCL / SE_RST nets, and the three
         matching pins (28/29/30) on the embedded S32K144 symbol.
         Added by tools/inject_optiga_secure_element.py.
         Circuit source: REFERENCES.md [45] p.12 Sec.3 Figure 2.

      2. Any edit made in the KiCad GUI since the last generation. The sheet
         has been opened and saved by KiCad (see the -backups/ directory),
         so the committed file is already ahead of this generator.

    The secure-element placement has deliberately NOT been ported into
    place_all()/wire_all() yet. `kiutils` is not installed on the machine where
    that work was done and cannot be installed there, so any such code could
    not have been executed or verified even once -- and shipping unverified
    generator code that silently replaces a verified schematic is exactly the
    failure mode AGENTS.md Sec.1.3 exists to prevent. Porting it is tracked in
    TODO.md and must be done on a machine with kiutils, then diffed against the
    committed sheet before the result is trusted.

    Until then: extend the schematic with a targeted injection script (see
    tools/inject_optiga_secure_element.py for the pattern), not by regenerating.
"""

import json
import re
import sys
import uuid
from itertools import pairwise
from pathlib import Path
from typing import ClassVar

SCRATCH = Path(__file__).parent
sys.path.insert(0, str(SCRATCH))
from genlib import GENERIC_SPECS, GRID, REPO, _layout, build_symbol
from kiutils.items.common import (
    Effects,
    Font,
    Justify,
    PageSettings,
    Position,
    Property,
    Stroke,
    TitleBlock,
)
from kiutils.items.schitems import (
    Connection,
    GlobalLabel,
    HierarchicalSheetInstance,
    Junction,
    NoConnect,
    SchematicSymbol,
    Text,
)
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib

SPECDIR = REPO / "symbols" / "specs"
SYMDIR = REPO / "symbols"
BUILD_KICAD_DIR = REPO / "builds/6s/50A/CAN_485_faraday/kicad"
PROJECT_NAME = "open_secure_esc_6s_50a_can485_faraday"


def U():
    return str(uuid.uuid4())


class Builder:
    def __init__(self):
        self.sch = Schematic()
        self.sch.version = "20211014"
        self.sch.generator = "open_secure_esc_symgen"
        self.sch.uuid = U()
        self.sch.paper = PageSettings(paperSize="A0")
        self.libcache = {}
        self.refcount = {}
        self.bbox = [1e9, 1e9, -1e9, -1e9]
        self.geo_cache = {}
        self.instances = {}  # ref -> pins_abs dict
        self.wire_counter = 0

    # ---- bookkeeping -----------------------------------------------
    def touch(self, x, y):
        self.bbox[0] = min(self.bbox[0], x)
        self.bbox[1] = min(self.bbox[1], y)
        self.bbox[2] = max(self.bbox[2], x)
        self.bbox[3] = max(self.bbox[3], y)

    def geo(self, key, pins):
        if key not in self.geo_cache:
            half_w, half_h, coords = _layout(pins)
            by_num = {p["num"]: (p["name"], x, y, angle) for p, x, y, angle in coords}
            self.geo_cache[key] = (half_w, half_h, by_num)
        return self.geo_cache[key]

    def next_ref(self, prefix):
        n = self.refcount.get(prefix, 0) + 1
        self.refcount[prefix] = n
        return f"{prefix}{n}"

    # ---- symbol library cache --------------------------------------
    def load_custom_symbol(self, name):
        key = (name, name)
        if key not in self.libcache:
            lib = SymbolLib.from_file(str(SYMDIR / f"{name}.kicad_sym"))
            sym = lib.symbols[0]
            sym.libraryNickname = name
            self.libcache[key] = sym
        return self.libcache[key]

    def load_generic_symbol(self, lib_id):
        nick, entry = lib_id.split(":")
        key = (nick, entry)
        if key not in self.libcache:
            spec = GENERIC_SPECS[lib_id]
            lib = build_symbol(spec)
            sym = lib.symbols[0]
            sym.libraryNickname = nick
            sym.entryName = entry
            for unit in sym.units:
                unit.entryName = entry
            if nick == "power":
                # Mark as a real KiCad power symbol (adds the `(power)` token),
                # matching how KiCad's own power:PWR_FLAG/power:GND etc. are
                # authored -- ERC's power-input-pin-not-driven check looks for
                # this, not just a power_out-typed pin on an ordinary symbol.
                sym.isPower = True
            self.libcache[key] = sym
        return self.libcache[key]

    # ---- placement ---------------------------------------------------
    def place(
        self,
        prefix,
        x,
        y,
        spec_json_name=None,
        generic_lib_id=None,
        value=None,
        ref=None,
        note=None,
    ):
        if generic_lib_id:
            nick, entry = generic_lib_id.split(":")
            spec = GENERIC_SPECS[generic_lib_id]
            libsym = self.load_generic_symbol(generic_lib_id)
            geokey = generic_lib_id
        else:
            spec = json.loads((SPECDIR / f"{spec_json_name}.json").read_text())
            nick, entry = spec_json_name, spec_json_name
            libsym = self.load_custom_symbol(spec_json_name)
            geokey = spec_json_name

        half_w, half_h, by_num = self.geo(geokey, spec["pins"])

        if ref:
            r = ref
            m = re.match(r"^[A-Za-z_]+(\d+)$", ref)
            if m:
                self.refcount[prefix] = max(
                    self.refcount.get(prefix, 0), int(m.group(1))
                )
        else:
            r = self.next_ref(prefix)
        inst = SchematicSymbol()
        inst.libId = f"{nick}:{entry}"
        inst.position = Position(x, y, 0)
        inst.unit = 1
        inst.inBom = True
        inst.onBoard = True
        inst.uuid = U()

        propmap = {p.key: p for p in libsym.properties}

        def mkprop(key, val, idx, pos, hide=True):
            return Property(
                key=key,
                value=val,
                id=idx,
                position=Position(pos[0], pos[1], 0),
                effects=Effects(font=Font(height=1.27, width=1.27), hide=hide),
            )

        inst.properties.append(
            mkprop("Reference", r, 0, (x, y - half_h - 2 * GRID), hide=False)
        )
        inst.properties.append(
            mkprop(
                "Value",
                value if value is not None else spec.get("name", entry),
                1,
                (x, y - half_h - GRID),
                hide=False,
            )
        )
        fp = propmap.get("Footprint")
        inst.properties.append(
            mkprop(
                "Footprint", fp.value if fp else spec.get("footprint", ""), 2, (x, y)
            )
        )
        ds = propmap.get("Datasheet")
        inst.properties.append(
            mkprop(
                "Datasheet", ds.value if ds else spec.get("datasheet", ""), 3, (x, y)
            )
        )
        cite = spec.get("citation", "")
        if cite:
            inst.properties.append(mkprop("Citation", cite, 4, (x, y)))
        if note:
            inst.properties.append(mkprop("Note", note, 5, (x, y)))

        for num in by_num:
            inst.pins[num] = U()
        self.sch.schematicSymbols.append(inst)

        pins_abs = {}
        for num, (name, lx, ly, angle) in by_num.items():
            ax, ay = round(x + lx, 3), round(y - ly, 3)
            pins_abs[num] = (ax, ay, name)
            self.touch(ax, ay)
        self.touch(x - half_w, y - half_h)
        self.touch(x + half_w, y + half_h)
        self.instances[r] = pins_abs
        return r, pins_abs

    # ---- wiring -------------------------------------------------------
    def wire(self, p1, p2, bend=None):
        """Route p1->p2 as one or more straight 2-point wire segments.

        KiCad's schematic `(wire (pts ...))` token is a single straight
        segment -- it does not support a multi-point polyline the way a PCB
        graphic line does. A bent route is therefore emitted as several
        separate wire objects sharing bend coordinates, not one N-point
        wire (which real KiCad's parser rejects outright).

        A naive 2-segment L-route reuses the source's native Y (or X) for
        its first leg and the destination's native X (or Y) for its
        second. Both of those are shared by every sibling pin in the same
        stack (e.g. all of DRV8353S's top-row pins share one Y; every
        pin on a component's right edge shares one X). Two unrelated
        wires whose long run then falls on that shared coordinate produce
        collinear, overlapping segments -- which KiCad treats as
        electrically connected, i.e. a short. ERC caught exactly this
        (pin_to_pin "Output and Output are connected" between DRV8353S's
        GHA/GLA/GHB gate-driver outputs, and more) before this fix.

        The fix: every bent route gets a short, per-call-unique lead-in
        off the source's native row/column and a short per-call-unique
        lead-out into the destination's, so only those short legs ever
        touch a "busy" shared coordinate (kept under the 2.54mm pin pitch
        so they can't overlap an adjacent sibling pin's own lead-in/out);
        the long traversal in between runs down a row/column unique to
        this one wire."""
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        if x1 == x2 or y1 == y2:
            legs = [(x1, y1), (x2, y2)]
        else:
            self.wire_counter += 1
            c = self.wire_counter
            # Both offsets stay under the 2.54mm pin pitch (so a lead-in/out
            # leg can't overlap an adjacent sibling pin's own lead-in/out),
            # but use a large, mutually-offset modulus for fine-grained,
            # decorrelated spacing -- reduces the odds of two wires with
            # nearby native coordinates landing on the same middle row/column.
            lead_in = round((c % 229) * 0.01, 3)  # < 2.29mm
            lead_out = round(((c + 113) % 229) * 0.01, 3)  # < 2.29mm, phase-shifted
            if bend == "v":
                xm = x1 + lead_in
                ym = y2 + lead_out
                legs = [(x1, y1), (xm, y1), (xm, ym), (x2, ym), (x2, y2)]
            else:
                ym = y1 + lead_in
                xm = x2 + lead_out
                legs = [(x1, y1), (x1, ym), (xm, ym), (xm, y2), (x2, y2)]
        segments = []
        for a, bpt in pairwise(legs):
            c = Connection(
                type="wire",
                points=[Position(*a), Position(*bpt)],
                stroke=Stroke(width=0, type="default"),
                uuid=U(),
            )
            self.sch.graphicalItems.append(c)
            segments.append(c)
        for p in legs:
            self.touch(p[0], p[1])
        return segments

    def junction(self, p):
        j = Junction(position=Position(p[0], p[1]), diameter=0, uuid=U())
        self.sch.junctions.append(j)

    def no_connect(self, p):
        nc = NoConnect(position=Position(p[0], p[1]), uuid=U())
        self.sch.noConnects.append(nc)
        self.touch(p[0], p[1])

    DIR_VEC: ClassVar[dict] = {
        "right": (1, 0),
        "left": (-1, 0),
        "up": (0, -1),
        "down": (0, 1),
    }
    DIR_ANGLE: ClassVar[dict] = {"right": 0, "left": 180, "up": 90, "down": 270}

    def label_stub(self, p, direction, text, length=5.08, shape="passive"):
        dx, dy = self.DIR_VEC[direction]
        end = (round(p[0] + dx * length, 3), round(p[1] + dy * length, 3))
        self.wire(p, end)
        lbl = GlobalLabel(
            text=text,
            shape=shape,
            position=Position(end[0], end[1], self.DIR_ANGLE[direction]),
            effects=Effects(font=Font(height=1.27, width=1.27), justify=Justify()),
            uuid=U(),
        )
        self.sch.globalLabels.append(lbl)
        self.touch(end[0], end[1])
        return end

    def text(self, p, s, size=1.5):
        t = Text(
            text=s,
            position=Position(p[0], p[1], 0),
            effects=Effects(font=Font(height=size, width=size)),
            uuid=U(),
        )
        self.sch.texts.append(t)
        self.touch(p[0], p[1])


def find(b, ref, name, index=0):
    matches = [(num, v) for num, v in b.instances[ref].items() if v[2] == name]
    return matches[index]


def find_all(b, ref, name):
    return [(num, v) for num, v in b.instances[ref].items() if v[2] == name]


def xy(entry):
    return (entry[1][0], entry[1][1])


def connect(b, ref_a, name_a, ref_b, name_b, bend=None, idx_a=0, idx_b=0):
    pa = find(b, ref_a, name_a, idx_a)
    pb = find(b, ref_b, name_b, idx_b)
    b.wire(xy(pa), xy(pb), bend=bend)


def rail(b, ref, name, direction, label, index=0):
    p = find(b, ref, name, index)
    b.label_stub(xy(p), direction, label)


def rail_all(b, ref, name, direction, label):
    for _, p in find_all(b, ref, name):
        b.label_stub((p[0], p[1]), direction, label)


# Dedicated, otherwise-empty lane near the bottom of the sheet (below all
# placed components -- see build_design()'s bboxes) so PWR_FLAG symbols and
# their routing don't crowd the dense DRV8353S/phase-leg area and collide
# with unrelated wires there.
FLAG_ROW_Y = 780
FLAG_ROW_X0 = 150
FLAG_ROW_DX = 40


def power_flag(b, p, index):
    """Place a PWR_FLAG in the dedicated flag row and wire it back to p, so
    ERC's power-input-pin-not-driven check doesn't fire on a net that's only
    carried by same-name labels (or, for an unlabeled net, only by a direct
    wire) with no regulator/power symbol on this sheet -- see genlib.py's
    power:PWR_FLAG description."""
    fx = FLAG_ROW_X0 + index * FLAG_ROW_DX
    ref, _ = b.place(
        "FLG", fx, FLAG_ROW_Y, generic_lib_id="power:PWR_FLAG", value="PWR_FLAG"
    )
    pin = find(b, ref, "pwr")
    b.wire(xy(pin), p)
    b.junction(p)


def place_all(b):
    r = {}

    # ---- Battery pack (6S, series) -------------------------------------
    bt = []
    for i in range(6):
        ref, _ = b.place(
            "BT",
            30,
            30 + i * 50,
            spec_json_name="INR21700_P42A",
            value="INR-21700-P42A",
        )
        bt.append(ref)
    r["bt"] = bt
    r["c_bulk"], _ = b.place(
        "C",
        100,
        30,
        generic_lib_id="Device:C_Polarized",
        value="100uF/50V",
        note="Generic bulk input cap, V>=25.2V (~2x margin -> >=50V rated); "
        "size per final layout -- see ../README.md BOM. Not independently sourced.",
    )

    # ---- Connectors ------------------------------------------------------
    r["j_swd"], _ = b.place(
        "J", 150, 60, generic_lib_id="Connector_Generic:Conn_01x04", value="J_SWD"
    )
    r["j_can"], _ = b.place(
        "J", 150, 210, generic_lib_id="Connector_Generic:Conn_01x02", value="J_CAN"
    )
    r["j_rs485"], _ = b.place(
        "J", 150, 430, generic_lib_id="Connector_Generic:Conn_01x02", value="J_RS485"
    )
    r["j_motor"], _ = b.place(
        "J", 1010, 430, generic_lib_id="Connector_Generic:Conn_01x03", value="J_MOTOR"
    )

    # ---- Protocol transceivers -------------------------------------------
    r["u3"], _ = b.place(
        "U",
        300,
        210,
        spec_json_name="ADM3055E_ADM3057E",
        value="ADM3055E/ADM3057E",
        ref="U3",
    )
    r["u4"], _ = b.place(
        "U",
        300,
        430,
        spec_json_name="ADM2582E_ADM2587E",
        value="ADM2582E/ADM2587E",
        ref="U4",
    )

    # ---- MCU + its local support passives ---------------------------------
    r["u1"], _ = b.place(
        "U", 460, 290, spec_json_name="S32K144", value="S32K144", ref="U1"
    )
    r["r_nrst"], _ = b.place(
        "R",
        400,
        160,
        generic_lib_id="Device:R",
        value="10k",
        note="Generic RESET_B pull-up, engineering default -- not datasheet-sourced.",
    )
    r["c_mcuvdd"], _ = b.place(
        "C",
        480,
        160,
        generic_lib_id="Device:C",
        value="100nF",
        note="MCU VDD decoupling, generic value. 3V3 regulator selection is an open item -- see ../README.md.",
    )
    r["c_vdda"], _ = b.place(
        "C",
        520,
        160,
        generic_lib_id="Device:C",
        value="100nF",
        note="MCU VDDA decoupling, generic value. Datasheet [31] p.13 requires VDD and VDDA "
        "shorted to a common source on PCB -- both rails carry the 3V3 label here per that "
        "requirement, not an independent design choice.",
    )

    # ---- Gate driver -------------------------------------------------------
    r["u5"], _ = b.place(
        "U", 650, 470, spec_json_name="DRV8353S", value="DRV8353S", ref="U5"
    )

    r["r_en"], _ = b.place(
        "R",
        560,
        430,
        generic_lib_id="Device:R",
        value="10k",
        note="DRV8353S ENABLE pull-up (default-enabled), generic value -- engineering default.",
    )
    r["r_flt"], _ = b.place(
        "R",
        560,
        470,
        generic_lib_id="Device:R",
        value="10k",
        note="DRV8353S nFAULT pull-up only; not wired to an MCU input in this build "
        "-- open item, see ../README.md Open items.",
    )

    r["c_cp"], _ = b.place(
        "C",
        590,
        400,
        generic_lib_id="Device:C",
        value="2.2nF",
        note="DRV8353S charge-pump cap (CPH-CPL), generic/typical value per TI application section, not independently sourced.",
    )
    r["c_vcp"], _ = b.place(
        "C",
        630,
        400,
        generic_lib_id="Device:C",
        value="1uF",
        note="DRV8353S charge-pump reservoir cap (VCP-VM), generic/typical value, not independently sourced.",
    )
    r["c_vref"], _ = b.place(
        "C",
        670,
        400,
        generic_lib_id="Device:C",
        value="100nF",
        note="DRV8353S VREF decoupling, generic value.",
    )
    r["c_dvdd"], _ = b.place(
        "C",
        710,
        400,
        generic_lib_id="Device:C",
        value="1uF",
        note="DRV8353S DVDD decoupling, generic value.",
    )
    r["c_vgls"], _ = b.place(
        "C",
        750,
        400,
        generic_lib_id="Device:C",
        value="1uF",
        note="DRV8353S VGLS decoupling, generic value.",
    )

    # ---- Power stage: 3 phase legs (FET pair + shunt + current-sense amp) ----
    phase_y = {"A": 180, "B": 390, "C": 600}
    q = {}
    sh = {}
    ina = {}
    for ph, cy in phase_y.items():
        qh, _ = b.place(
            "Q", 830, cy - 40, spec_json_name="IRFB4110PBF", value="IRFB4110PBF"
        )
        ql, _ = b.place("Q", 830, cy, spec_json_name="IRFB4110PBF", value="IRFB4110PBF")
        rs, _ = b.place("R", 830, cy + 40, spec_json_name="WSLP2512", value="1mOhm")
        ic, _ = b.place("U", 940, cy, spec_json_name="INA240", value="INA240")
        q[ph] = (qh, ql)
        sh[ph] = rs
        ina[ph] = ic
    r["q"] = q
    r["shunt"] = sh
    r["ina"] = ina

    r["r_vref1"], _ = b.place(
        "R",
        1030,
        60,
        generic_lib_id="Device:R",
        value="10k",
        note="INA240 common-mode bias divider (3V3->VREF_MID->GND), generic engineering default.",
    )
    r["r_vref2"], _ = b.place("R", 1030, 100, generic_lib_id="Device:R", value="10k")

    r["r_vbus1"], _ = b.place(
        "R",
        400,
        400,
        generic_lib_id="Device:R",
        value="90k",
        note="ADC_VBUS sense divider (VM max 25.2V -> ~2.52V at MCU ADC), generic engineering default, not datasheet-sourced.",
    )
    r["r_vbus2"], _ = b.place("R", 400, 440, generic_lib_id="Device:R", value="10k")

    r["sh1"], _ = b.place(
        "SH", 830, 700, spec_json_name="WE_SHC_3671375", value="WE-SHC 3671375 (cover)"
    )
    r["sh2"], _ = b.place(
        "SH", 900, 700, spec_json_name="WE_SHC_3670375", value="WE-SHC 3670375 (frame)"
    )

    return r


def wire_all(b, r):
    u1, u3, u4, u5 = r["u1"], r["u3"], r["u4"], r["u5"]
    bt = r["bt"]

    # ---- Battery pack series chain + rails --------------------------------
    for i in range(5):
        b.wire(xy(find(b, bt[i], "-")), xy(find(b, bt[i + 1], "+")))
    rail(b, bt[0], "+", "up", "VM")
    rail(b, bt[-1], "-", "down", "GND")
    rail(b, r["c_bulk"], "+", "up", "VM")
    rail(b, r["c_bulk"], "-", "down", "GND")
    b.text(
        (15, 10),
        "Battery pack -- 6S (Molicel INR-21700-P42A x6 series), REFERENCES.md [14]",
        size=2.0,
    )

    # ---- Debug header ------------------------------------------------------
    connect(b, r["j_swd"], "Pin_1", u1, "SWD_DIO")
    connect(b, r["j_swd"], "Pin_2", u1, "SWD_CLK")
    rail(b, r["j_swd"], "Pin_3", "left", "3V3")
    rail(b, r["j_swd"], "Pin_4", "left", "GND")

    # ---- CAN transceiver (U3) ----------------------------------------------
    connect(b, r["j_can"], "Pin_1", u3, "CANH")
    connect(b, r["j_can"], "Pin_2", u3, "CANL")
    rail_all(b, u3, "GND1", "left", "GND")
    rail(b, u3, "VCC", "left", "3V3")
    rail(b, u3, "VIO", "left", "3V3")
    b.no_connect(xy(find(b, u3, "AUXIN")))
    b.no_connect(xy(find(b, u3, "AUXOUT")))
    rail(b, u3, "SILENT", "left", "GND")
    rail(b, u3, "STBY", "left", "GND")
    connect(b, u1, "CAN_TX", u3, "TXD")
    connect(b, u3, "RXD", u1, "CAN_RX")
    rail(b, u3, "RS", "right", "CAN_ISO_GND")
    rail_all(b, u3, "GND2", "right", "CAN_ISO_GND")
    rail_all(b, u3, "GNDISO", "right", "CAN_ISO_GND")
    rail(b, u3, "VISOOUT", "right", "CAN_VISOOUT")
    rail(b, u3, "VISOIN", "right", "CAN_VISOIN_OPEN")

    # ---- RS-485 transceiver (U4) --------------------------------------------
    # Y-A and Z-B are both on U4's right edge (shared X); Y/A and Z/B are
    # interleaved in that pin stack (Y, Z, B, A in stacking order) so a
    # straight tie between each pair overlaps the *other* pair's span on
    # that same column. Jog each pair out to its own clear column instead.
    for name_a, name_b, jog in (("Y", "A", 15), ("Z", "B", 25)):
        pa = xy(find(b, u4, name_a))
        pb = xy(find(b, u4, name_b))
        out_x = pa[0] + jog
        b.wire(pa, (out_x, pa[1]))
        b.wire((out_x, pa[1]), (out_x, pb[1]))
        b.wire((out_x, pb[1]), pb)
    rail(b, u4, "A", "right", "RS485_A")
    rail(b, u4, "B", "right", "RS485_B")
    rail(b, r["j_rs485"], "Pin_1", "left", "RS485_A")
    rail(b, r["j_rs485"], "Pin_2", "left", "RS485_B")
    rail_all(b, u4, "GND1", "left", "GND")
    rail_all(b, u4, "VCC", "left", "3V3")
    connect(b, u1, "RS485_TXD", u4, "TxD")
    connect(b, u4, "RxD", u1, "RS485_RXD")
    rail(b, u1, "RS485_DE_RE", "left", "RS485_DE_RE")
    rail(b, u4, "DE", "left", "RS485_DE_RE")
    rail(b, u4, "RE", "left", "RS485_DE_RE")
    rail_all(b, u4, "GND2", "right", "RS485_ISO_GND")
    rail(b, u4, "VISOOUT", "right", "RS485_VISOOUT")
    rail(b, u4, "VISOIN", "right", "RS485_VISOIN_OPEN")

    # ---- MCU power / reset / debug -------------------------------------------
    rail(b, u1, "VDD", "up", "3V3")
    rail(b, u1, "VSS", "down", "GND")
    rail(b, u1, "VDDA", "up", "3V3")
    rail(b, u1, "VREFH", "up", "3V3")
    rail(b, u1, "VREFL_VSSA_VSS", "down", "GND")
    connect(b, u1, "RESET_B", r["r_nrst"], "~", idx_b=1)
    rail(b, r["r_nrst"], "~", "up", "3V3", index=0)
    rail(b, r["c_mcuvdd"], "~", "up", "3V3", index=0)
    rail(b, r["c_mcuvdd"], "~", "down", "GND", index=1)
    rail(b, r["c_vdda"], "~", "up", "3V3", index=0)
    rail(b, r["c_vdda"], "~", "down", "GND", index=1)
    b.text(
        (460, 130),
        "No external TPM: message authentication is provided by the S32K144's own on-chip "
        "CSEc security module (internal peripheral, no dedicated pins) -- see ../README.md",
        size=1.2,
    )

    # ---- DRV8353S (U5) ---------------------------------------------------------
    rail(b, u5, "VM", "up", "VM")
    rail(b, u5, "VDRAIN", "up", "VM")
    connect(b, u5, "VCP", r["c_vcp"], "~", idx_b=0)
    rail(b, r["c_vcp"], "~", "up", "VM", index=1)
    connect(b, u5, "CPH", r["c_cp"], "~", idx_b=0)
    connect(b, u5, "CPL", r["c_cp"], "~", idx_b=1)
    connect(b, u5, "VREF", r["c_vref"], "~", idx_b=0)
    rail(b, r["c_vref"], "~", "down", "GND", index=1)
    rail(b, u5, "AGND", "up", "GND")
    connect(b, u5, "DVDD", r["c_dvdd"], "~", idx_b=0)
    rail(b, r["c_dvdd"], "~", "down", "GND", index=1)
    rail(b, u5, "GND", "up", "GND")
    connect(b, u5, "VGLS", r["c_vgls"], "~", idx_b=0)
    rail(b, r["c_vgls"], "~", "down", "GND", index=1)

    connect(b, u1, "GD_SPI_CS", u5, "nSCS")
    connect(b, u1, "GD_SPI_SCK", u5, "SCLK")
    connect(b, u1, "GD_SPI_MOSI", u5, "SDI")
    connect(b, u5, "SDO", u1, "GD_SPI_MISO")
    connect(b, u5, "ENABLE", r["r_en"], "~", idx_b=1)
    rail(b, r["r_en"], "~", "up", "3V3", index=0)
    connect(b, u5, "nFAULT", r["r_flt"], "~", idx_b=1)
    rail(b, r["r_flt"], "~", "up", "3V3", index=0)
    b.text(
        (560, 500),
        "nFAULT: pulled up only, not wired to MCU in this build -- open item, see ../README.md",
        size=1.2,
    )

    connect(b, u1, "PWM_AH", u5, "INHA")
    connect(b, u1, "PWM_AL", u5, "INLA")
    connect(b, u1, "PWM_BH", u5, "INHB")
    connect(b, u1, "PWM_BL", u5, "INLB")
    connect(b, u1, "PWM_CH", u5, "INHC")
    connect(b, u1, "PWM_CL", u5, "INLC")

    # ---- Phase legs (A/B/C): FETs, shunt, current sense -------------------------
    adc_pin = {"A": "ADC_IU", "B": "ADC_IV", "C": "ADC_IW"}
    drv_gh = {"A": "GHA", "B": "GHB", "C": "GHC"}
    drv_gl = {"A": "GLA", "B": "GLB", "C": "GLC"}
    drv_sh = {"A": "SHA", "B": "SHB", "C": "SHC"}
    drv_sp = {"A": "SPA", "B": "SPB", "C": "SPC"}
    drv_sn = {"A": "SNA", "B": "SNB", "C": "SNC"}

    for ph in ("A", "B", "C"):
        qh, ql = r["q"][ph]
        rs = r["shunt"][ph]
        ic = r["ina"][ph]
        ph_net = f"PH_{ph}"
        hi_net = f"ISENSE_{ph}_HI"

        connect(b, u5, drv_gh[ph], qh, "G")
        rail(b, qh, "D", "up", "VM")
        rail(b, qh, "S", "right", ph_net)

        connect(b, u5, drv_gl[ph], ql, "G")
        rail(b, ql, "D", "up", ph_net)
        rail(b, ql, "S", "down", hi_net)

        rail(b, u5, drv_sh[ph], "right", ph_net)
        rail(b, u5, drv_sp[ph], "down", hi_net)
        rail(b, u5, drv_sn[ph], "down", "GND")

        rail(b, rs, "~", "up", hi_net, index=0)
        rail(b, rs, "~", "down", "GND", index=1)

        rail(b, ic, "IN+", "left", hi_net)
        rail(b, ic, "IN-", "left", "GND")
        rail(b, ic, "GND", "down", "GND")
        rail(b, ic, "VS", "up", "3V3")
        rail(b, ic, "REF1", "right", "VREF_MID")
        rail(b, ic, "REF2", "right", "VREF_MID")
        rail(b, ic, "OUT", "right", adc_pin[ph])
        b.no_connect(xy(find(b, ic, "NC")))

        motor_pin = {"A": "Pin_1", "B": "Pin_2", "C": "Pin_3"}[ph]
        rail(b, r["j_motor"], motor_pin, "left", ph_net)

    rail(b, u1, "ADC_IU", "down", "ADC_IU")
    rail(b, u1, "ADC_IV", "down", "ADC_IV")
    rail(b, u1, "ADC_IW", "down", "ADC_IW")

    # ---- VREF_MID bias divider (shared by all 3 INA240) -------------------------
    rail(b, r["r_vref1"], "~", "up", "3V3", index=0)
    rail(b, r["r_vref1"], "~", "down", "VREF_MID", index=1)
    rail(b, r["r_vref2"], "~", "up", "VREF_MID", index=0)
    rail(b, r["r_vref2"], "~", "down", "GND", index=1)

    # ---- VBUS sense divider -----------------------------------------------------
    rail(b, r["r_vbus1"], "~", "up", "VM", index=0)
    rail(b, r["r_vbus1"], "~", "down", "VBUS_SENSE", index=1)
    rail(b, r["r_vbus2"], "~", "up", "VBUS_SENSE", index=0)
    rail(b, r["r_vbus2"], "~", "down", "GND", index=1)
    rail(b, u1, "ADC_VBUS", "down", "VBUS_SENSE")

    # ---- EMI shield (mechanical, Faraday tier) -----------------------------------
    rail(b, r["sh1"], "SHIELD_GND", "down", "GND")
    rail(b, r["sh2"], "SHIELD_GND", "down", "GND")
    b.text(
        (830, 675),
        "Faraday shield (WE-SHC 3671375 cover + 3670375 frame) over gate-drive / "
        "high-di/dt switching-node area -- see ../README.md EMI Hardening tier",
        size=1.2,
    )

    # ---- DRV8353S SOA/SOB/SOC: open design question, not wired -------------------
    for name in ("SOA", "SOB", "SOC"):
        b.no_connect(xy(find(b, u5, name)))
    b.text(
        (650, 705),
        "SOA/SOB/SOC (DRV8353S integrated per-phase CSA outputs) intentionally left unconnected: "
        "this build routes ADC_IU/IV/IW from external INA240 devices instead -- DRV8353S-vs-INA240 "
        "current-sense sourcing is an open design question, see ../README.md Open items.",
        size=1.2,
    )

    # ---- Power-flag markers -------------------------------------------------------
    # ERC requires every net with a power-input pin to have a declared driver
    # (a power-output pin or a PWR_FLAG). GND/3V3/VM/the two isolated grounds/
    # the two open isolated-supply nets carry only same-name labels with no
    # regulator or source symbol on this sheet; DRV8353S.VREF is wired only to
    # its own decoupling cap with no label at all. None of that changes with a
    # PWR_FLAG -- it just tells ERC the omission is intentional, not a
    # dangling input. See genlib.py power:PWR_FLAG and kicad/README.md.
    power_flag(b, xy(find(b, bt[-1], "-")), 0)  # GND
    power_flag(b, xy(find(b, r["r_nrst"], "~", 0)), 1)  # 3V3
    power_flag(b, xy(find(b, bt[0], "+")), 2)  # VM
    power_flag(b, xy(find(b, u3, "RS")), 3)  # CAN_ISO_GND
    power_flag(b, xy(find(b, u4, "GND2", 0)), 4)  # RS485_ISO_GND
    power_flag(b, xy(find(b, u3, "VISOIN")), 5)  # CAN_VISOIN_OPEN
    power_flag(b, xy(find(b, u4, "VISOIN")), 6)  # RS485_VISOIN_OPEN
    power_flag(b, xy(find(b, u5, "VREF")), 7)  # DRV8353S.VREF local net (no label)


def title_block():
    tb = TitleBlock(
        title="Open-Secure-ESC -- 6S / 50A / CAN-FD+RS-485 / Faraday",
        date="2026-08-02",
        revision="0.2-populated",
        company="Griffing Technology LLC",
    )
    tb.comments[1] = "Build spec: builds/6s/50A/CAN_485_faraday/README.md"
    tb.comments[2] = "BOM/citations: docs/decision-matrix.xlsx, REFERENCES.md"
    tb.comments[3] = (
        "Symbols: ../../../../symbols/ (see symbols/README.md) via kicad/sym-lib-table"
    )
    tb.comments[4] = (
        "Populated schematic: components placed & wired per verified pin maps; "
        "generic support passives are engineering defaults, not datasheet-sourced -- "
        "see kicad/README.md"
    )
    return tb


def center_drawing(b):
    """Translate the whole drawing so its bounding box is centered within the
    usable drawing area of the sheet (full page minus outer margin and the
    KiCad title-block band along the bottom)."""
    paper = b.sch.paper.paperSize
    sizes = {
        "A4": (297, 210),
        "A3": (420, 297),
        "A2": (594, 420),
        "A1": (841, 594),
        "A0": (1189, 841),
    }
    pw, ph = sizes[paper]
    margin = 10
    title_h = 40
    area_x0, area_y0 = margin, margin
    area_x1, area_y1 = pw - margin, ph - margin - title_h

    x0, y0, x1, y1 = b.bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    tx = round(((area_x0 + area_x1) / 2 - cx) / 1.27) * 1.27
    ty = round(((area_y0 + area_y1) / 2 - cy) / 1.27) * 1.27
    return tx, ty, pw, ph, (x1 - x0), (y1 - y0)


def apply_translate(b, tx, ty):
    for inst in b.sch.schematicSymbols:
        inst.position.X = round(inst.position.X + tx, 3)
        inst.position.Y = round(inst.position.Y + ty, 3)
        for p in inst.properties:
            p.position.X = round(p.position.X + tx, 3)
            p.position.Y = round(p.position.Y + ty, 3)
    for item in b.sch.graphicalItems:
        for p in item.points:
            p.X = round(p.X + tx, 3)
            p.Y = round(p.Y + ty, 3)
    for j in b.sch.junctions:
        j.position.X = round(j.position.X + tx, 3)
        j.position.Y = round(j.position.Y + ty, 3)
    for nc in b.sch.noConnects:
        nc.position.X = round(nc.position.X + tx, 3)
        nc.position.Y = round(nc.position.Y + ty, 3)
    for lbl in b.sch.globalLabels:
        lbl.position.X = round(lbl.position.X + tx, 3)
        lbl.position.Y = round(lbl.position.Y + ty, 3)
    for t in b.sch.texts:
        t.position.X = round(t.position.X + tx, 3)
        t.position.Y = round(t.position.Y + ty, 3)
    b.bbox = [b.bbox[0] + tx, b.bbox[1] + ty, b.bbox[2] + tx, b.bbox[3] + ty]


def connectivity_check(b):
    """Sanity check: every placed pin must be touched by at least one wire
    endpoint, label stub, or no-connect flag."""
    touched = set()
    for item in b.sch.graphicalItems:
        for p in item.points:
            touched.add((round(p.X, 2), round(p.Y, 2)))
    for nc in b.sch.noConnects:
        touched.add((round(nc.position.X, 2), round(nc.position.Y, 2)))
    problems = []
    for ref, pins in b.instances.items():
        for num, (x, y, name) in pins.items():
            if (round(x, 2), round(y, 2)) not in touched:
                problems.append((ref, num, name))
    return problems


def build_and_write(out_path):
    b = Builder()
    refs = place_all(b)
    wire_all(b, refs)

    problems = connectivity_check(b)
    if problems:
        print(f"WARNING: {len(problems)} unconnected pins:")
        for ref, num, name in problems:
            print(f"  {ref} pin {num} ({name})")
    else:
        print(
            "connectivity check: OK, every placed pin is wired, labeled, or no-connected"
        )

    tx, ty, pw, ph, w, h = center_drawing(b)
    apply_translate(b, tx, ty)
    print(
        f"paper {pw}x{ph}mm, content {w:.1f}x{h:.1f}mm, centered (translate {tx:.2f},{ty:.2f})"
    )
    print("final bbox:", [round(v, 2) for v in b.bbox])

    b.sch.titleBlock = title_block()
    b.sch.libSymbols = list(b.libcache.values())
    b.sch.sheetInstances = [HierarchicalSheetInstance(instancePath="/", page="1")]

    out_path.write_text(b.sch.to_sexpr())
    print(
        f"wrote {out_path} ({len(b.sch.schematicSymbols)} symbol instances, "
        f"{len(b.sch.graphicalItems)} wires, {len(b.sch.globalLabels)} labels, "
        f"{len(b.sch.noConnects)} no-connects, {len(b.sch.libSymbols)} lib symbols)"
    )
    return b


if __name__ == "__main__":
    out = BUILD_KICAD_DIR / f"{PROJECT_NAME}.kicad_sch"
    build_and_write(out)
