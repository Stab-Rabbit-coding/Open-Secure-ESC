#!/usr/bin/env python3
"""Generate SMD solder-pad strip footprints for the signal connectors.

Governed by AGENTS.md. These replace the 2.54 mm through-hole pin headers on
J1 (SWD), J2 (CAN) and J3 (RS-485) for the 30 x 60 mm respin.

WHY
---
On a double-sided board this dense, a through-hole part costs its area TWICE:
it blocks the same footprint on both sides. Measured on this build, nine
through-hole parts occupied 482 mm^2 but consumed 964 mm^2 of the 3600 mm^2
two-sided budget -- 27% of the board for 9 parts. That, not total component
area, is what stopped a 30 x 60 layout converging.

Precedent, not invention: the Vimdrones ESC S50 [47] -- a shipping 6S/50A ESC
in 40 x 17 mm -- specifies "CAN Port Connector: Solder PAD" and a "120 Ohm
with Solder PAD switch". It carries no pin headers at all. Wires solder
directly to surface pads.

WHAT THIS IS AND IS NOT
------------------------
This is a bare solder-pad strip: N rectangular SMD pads on a pitch, with a
silkscreen outline and a pin-1 marker. There is no connector body, no
retention, no keying, and no mating part. A wire or a pogo-pin jig lands on
it directly.

That is a deliberate trade and an ENGINEERING DEFAULT per AGENTS.md Sec.4,
not a verified selection:

  * GAINED: no through-hole, so the opposite side of the board stays usable;
    much smaller area; no connector to source.
  * LOST: no mechanical retention. A soldered wire on a surface pad relies on
    the solder joint alone for strain relief. For J1 (SWD) this is fine -- it
    is a bring-up/debug interface, not a flight connection. For J2/J3, which
    carry CAN and RS-485 off-board in service, strain relief must come from
    somewhere else (a cable tie-down, potting, or a real connector chosen
    later). Flagged in TODO.md.

Pad geometry below is a drafting choice sized for hand-soldering 26-30 AWG
wire, NOT a value from any standard or datasheet. No IPC land-pattern rule
governs a bare wire pad.

Usage:
    python3 symbols/tools/gen_smd_solder_pad_footprints.py
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-16, TODO.md 12.5.
# AI-generated; the pad geometry is an engineering default, not a datasheet
# or standards value. Not human-authored.

import uuid
from pathlib import Path

# Drafting choices, not sourced values.
PAD_W = 1.60           # across the strip
PAD_H = 3.20           # along the wire, long enough to hand-solder
PITCH = 2.54           # matches the header pitch it replaces, so a pogo jig
                       # or an existing cable pinout still lines up
SILK_W = 0.12
CRTYD_W = 0.05
CRTYD_CLR = 0.25

VARIANTS = {
    "SolderPad_1x02_SMD_P2.54mm": 2,
    "SolderPad_1x04_SMD_P2.54mm": 4,
}

DESCR_TMPL = (
    "Bare SMD solder-pad strip, {n} pads, {pitch} mm pitch, {pw} x {ph} mm "
    "pads. Replaces a through-hole pin header so the opposite board side stays "
    "usable -- see symbols/tools/gen_smd_solder_pad_footprints.py. No "
    "connector body, no retention, no mating part: a wire solders directly to "
    "the pad. Pad geometry is an ENGINEERING DEFAULT (AGENTS.md Sec.4), not a "
    "datasheet or IPC value. Precedent: Vimdrones ESC S50 [47] 'CAN Port "
    "Connector: Solder PAD'."
)


def u() -> str:
    """Fresh UUID for a footprint element."""
    return str(uuid.uuid4())


def build(name: str, n: int) -> str:
    """Emit one .kicad_mod for an n-pad solder strip."""
    L: list[str] = []
    add = L.append
    span = (n - 1) * PITCH
    half_w = span / 2 + PAD_W / 2
    half_h = PAD_H / 2

    add(f'(footprint "{name}"')
    add("\t(version 20241229)")
    add('\t(generator "gen_smd_solder_pad_footprints.py")')
    add('\t(generator_version "9.0")')
    add('\t(layer "F.Cu")')
    add(f'\t(descr "{DESCR_TMPL.format(n=n, pitch=PITCH, pw=PAD_W, ph=PAD_H)}")')
    add(f'\t(tags "solder pad SMD wire connector 1x{n:02d} {PITCH}mm")')
    add("\t(attr smd)")

    add('\t(property "Reference" "J**"')
    add(f"\t\t(at 0 {-(half_h + 1.0):.3f} 0)")
    add('\t\t(layer "F.SilkS")')
    add(f'\t\t(uuid "{u()}")')
    add("\t\t(effects (font (size 1 1) (thickness 0.15)))")
    add("\t)")
    add(f'\t(property "Value" "{name}"')
    add(f"\t\t(at 0 {half_h + 1.0:.3f} 0)")
    add('\t\t(layer "F.Fab")')
    add(f'\t\t(uuid "{u()}")')
    add("\t\t(effects (font (size 1 1) (thickness 0.15)))")
    add("\t)")
    add('\t(fp_text user "${REFERENCE}"')
    add("\t\t(at 0 0 0)")
    add('\t\t(layer "F.Fab")')
    add(f'\t\t(uuid "{u()}")')
    add("\t\t(effects (font (size 0.8 0.8) (thickness 0.12)))")
    add("\t)")

    # Courtyard and a silk outline that does not sit on copper.
    cx, cy = half_w + CRTYD_CLR, half_h + CRTYD_CLR
    for layer, width in (("F.CrtYd", CRTYD_W), ("F.SilkS", SILK_W)):
        pts = [(-cx, -cy), (cx, -cy), (cx, cy), (-cx, cy), (-cx, -cy)]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            add(
                f"\t(fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) "
                f'(stroke (width {width}) (type solid)) (layer "{layer}") '
                f'(uuid "{u()}"))'
            )
    # Pin-1 marker outside the courtyard.
    add(
        f"\t(fp_circle (center {-(cx + 0.4):.4f} {-half_h + PAD_H / 2:.4f}) "
        f"(end {-(cx + 0.4) + 0.15:.4f} {-half_h + PAD_H / 2:.4f}) "
        f'(stroke (width {SILK_W}) (type solid)) (fill solid) '
        f'(layer "F.SilkS") (uuid "{u()}"))'
    )

    for i in range(n):
        x = -span / 2 + i * PITCH
        add(f'\t(pad "{i + 1}" smd roundrect')
        add(f"\t\t(at {x:.4f} 0)")
        add(f"\t\t(size {PAD_W:.4f} {PAD_H:.4f})")
        add('\t\t(layers "F.Cu" "F.Paste" "F.Mask")')
        add("\t\t(roundrect_rratio 0.125)")
        add(f'\t\t(uuid "{u()}")')
        add("\t)")

    add("\t(embedded_fonts no)")
    add(")")
    return "\n".join(L) + "\n"


def main() -> None:
    """Write every variant into this repo's own .pretty library."""
    repo = Path(__file__).resolve().parents[2]
    out = repo / "symbols" / "footprints" / "Open_Secure_ESC.pretty"
    out.mkdir(parents=True, exist_ok=True)
    for name, n in VARIANTS.items():
        (out / f"{name}.kicad_mod").write_text(build(name, n), encoding="utf-8")
        print(f"wrote {name}.kicad_mod  ({n} pads)")


if __name__ == "__main__":
    main()
