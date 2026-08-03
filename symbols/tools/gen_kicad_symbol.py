#!/usr/bin/env python3
"""Generate a KiCad symbol library (.kicad_sym) from a JSON pin spec.

Workflow this exists for (see symbols/README.md):
  1. Source a component's real pin-out from its primary datasheet (or mark it
     UNVERIFIED per AGENTS.md if no primary source is reachable).
  2. Record that pin-out once as symbols/specs/<NAME>.json, citing the
     REFERENCES.md tag and verification status.
  3. Run this script to (re)generate symbols/<NAME>.kicad_sym.
This keeps the citation/verification trail in a diffable JSON file instead of
hand-edited S-expressions, and lets any future build regenerate or tweak a
symbol without re-deriving pin geometry by hand.

Usage:
    python3 gen_kicad_symbol.py specs/FOO.json [specs/BAR.json ...] -o ../
    python3 gen_kicad_symbol.py specs/*.json -o ../   # regenerate everything
"""

import argparse
import json
import math
import sys
from pathlib import Path

from kiutils.items.common import Effects, Font, Position, Property
from kiutils.symbol import Symbol, SymbolLib, SyRect

GRID = 2.54
PIN_LEN = 2.54
FONT_SIZE = 1.27

SIDE_ANGLE = {"left": 0, "right": 180, "top": 270, "bottom": 90}


def _font_effects(hide: bool = False) -> Effects:
    return Effects(font=Font(height=FONT_SIZE, width=FONT_SIZE), hide=hide)


def _layout(pins):
    """Compute a simple rectangular body + pin coordinates for the 4 sides.

    This is a functional layout aid, not a hand-tuned datasheet pin diagram:
    pins are grouped onto the side given in the spec and stacked in the order
    given. Rearrange visually in the KiCad Symbol Editor if a different
    physical arrangement is wanted -- electrical connectivity (pin number <->
    signal) is the authoritative part, not the on-paper position.

    Sizing rule: KiCad draws each pin's name *inward* from its own side, so a
    left-side name runs rightward across the body and a bottom-side name runs
    upward across it. The body therefore has to clear two things at once on
    each axis -- the pins themselves, and the label text arriving from the
    perpendicular pair of sides. Sizing only on pin count (the earlier rule)
    produced a body too small for a part with many pins AND long names, and
    the two label sets overlapped illegibly. Both constraints are applied
    below, and each side's pins are then centred in the band the opposing
    labels leave free.
    """
    sides = {"left": [], "right": [], "top": [], "bottom": []}
    for p in pins:
        sides[p.get("side", "left")].append(p)

    v_count = max(len(sides["left"]), len(sides["right"]), 1)
    h_count = max(len(sides["top"]), len(sides["bottom"]), 1)

    char_w = FONT_SIZE * 0.62
    clr = GRID / 2  # breathing room between a label's far end and a pin row

    def _text(side):
        """Length, in mm, of the longest pin name drawn inward from `side`."""
        return max([len(p["name"]) for p in sides[side]] + [0]) * char_w

    left_t, right_t = _text("left"), _text("right")
    top_t, bottom_t = _text("top"), _text("bottom")

    # Width: fit the top/bottom pin columns, and the left+right label text.
    # Height: fit the left/right pin rows, and the top+bottom label text.
    half_w = max(
        GRID * h_count / 2 + GRID,
        ((h_count - 1) * GRID + left_t + right_t + 2 * clr) / 2,
    )
    half_h = max(
        GRID * v_count / 2 + GRID,
        ((v_count - 1) * GRID + top_t + bottom_t + 2 * clr) / 2,
    )
    # Snap outward to a whole grid step so the body corners land on grid.
    half_w = math.ceil(half_w / GRID) * GRID
    half_h = math.ceil(half_h / GRID) * GRID

    # Centre of the band each axis has left over once the opposing side's
    # label text is reserved; pins are stacked symmetrically about it.
    y_mid = ((half_h - top_t - clr) + (-half_h + bottom_t + clr)) / 2
    x_mid = ((-half_w + left_t + clr) + (half_w - right_t - clr)) / 2
    y_mid = round(y_mid / (GRID / 2)) * (GRID / 2)
    x_mid = round(x_mid / (GRID / 2)) * (GRID / 2)

    coords = []
    for side, plist in sides.items():
        n = len(plist)
        for i, p in enumerate(plist):
            if side in ("left", "right"):
                y = y_mid + ((n - 1) / 2 - i) * GRID
                x = -(half_w + PIN_LEN) if side == "left" else (half_w + PIN_LEN)
            else:
                x = x_mid + (i - (n - 1) / 2) * GRID
                y = half_h + PIN_LEN if side == "top" else -(half_h + PIN_LEN)
            coords.append((p, x, y, SIDE_ANGLE[side]))
    return half_w, half_h, coords


def build_symbol(spec: dict) -> SymbolLib:
    name = spec["name"]
    pins = spec["pins"]
    half_w, half_h, coords = _layout(pins)

    lib = SymbolLib(version="20211014", generator="open_secure_esc_symgen")

    top = Symbol(
        entryName=name,
        inBom=True,
        onBoard=True,
        pinNames=True,
        pinNamesOffset=1.016,
        hidePinNumbers=False,
    )

    props = [
        (
            "Reference",
            spec.get("reference", "U"),
            0,
            Position(0, half_h + 2 * GRID, 0),
            False,
        ),
        ("Value", name, 1, Position(0, half_h + GRID, 0), False),
        ("Footprint", spec.get("footprint", ""), 2, Position(0, 0, 0), True),
        ("Datasheet", spec.get("datasheet", ""), 3, Position(0, 0, 0), True),
        ("Description", spec.get("description", ""), 4, Position(0, 0, 0), True),
        ("Citation", spec.get("citation", ""), 5, Position(0, 0, 0), True),
        ("Verification", spec.get("verification", ""), 6, Position(0, 0, 0), True),
    ]
    for key, value, pid, pos, hide in props:
        prop = Property(
            key=key, value=value, id=pid, position=pos, effects=_font_effects(hide=hide)
        )
        top.properties.append(prop)

    body = Symbol(entryName=name, unitId=0, styleId=1)
    body.graphicItems.append(
        SyRect(
            start=Position(-half_w, half_h),
            end=Position(half_w, -half_h),
        )
    )

    unit = Symbol(entryName=name, unitId=1, styleId=1)
    for p, x, y, angle in coords:
        unit.pins.append(_make_pin(p, x, y, angle))

    top.units.append(body)
    top.units.append(unit)
    lib.symbols.append(top)
    return lib


def _make_pin(p, x, y, angle):
    from kiutils.symbol import SymbolPin

    return SymbolPin(
        electricalType=p["etype"],
        graphicalStyle="line",
        position=Position(round(x, 3), round(y, 3), angle),
        length=PIN_LEN,
        name=p["name"],
        number=str(p["num"]),
        nameEffects=_font_effects(),
        numberEffects=_font_effects(),
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("specs", nargs="+", help="JSON pin-spec file(s)")
    ap.add_argument(
        "-o", "--outdir", default=".", help="Output directory for .kicad_sym files"
    )
    args = ap.parse_args(argv)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for spec_path in args.specs:
        spec = json.loads(Path(spec_path).read_text())
        lib = build_symbol(spec)
        out_path = outdir / f"{spec['name']}.kicad_sym"
        out_path.write_text(lib.to_sexpr())
        print(f"wrote {out_path} ({len(spec['pins'])} pins)")


if __name__ == "__main__":
    sys.exit(main())
