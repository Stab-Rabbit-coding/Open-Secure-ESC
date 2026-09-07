#!/usr/bin/env python3
"""STRIP WIDTH -- how wide a flat board fits inside a curved host.

Governed by AGENTS.md. Companion to isolation_envelope.py and
conductor_sizing.py: those decide a board's width from its isolation
requirement and its copper from its current, and this one decides the width a
curved enclosure will physically accept.

WHY THIS EXISTS
---------------
A rigid PCB is flat. Mounting one inside a cylindrical bore -- a nacelle, a
boom, a tube -- means the board is a CHORD of the bore circle, and the gap
between the chord and the arc is the radial depth the board steals from
whatever else lives in that annulus. That gap is the sagitta.

Getting this wrong is not a tolerance problem, it is a "the skin does not
close" problem, so the number belongs in the decision matrix as a build axis
value, not in someone's head during placement.

    s = R - sqrt(R^2 - (w/2)^2)          depth consumed by a strip of width w
    w = 2 * sqrt(2*R*s - s^2)            widest strip that fits depth s

THE COUPLING THIS TOOL EXISTS TO MAKE VISIBLE
----------------------------------------------
Width and length are not independent. A board holds a fixed set of parts, so
pinning one dimension drives the other. Narrowing a board does not shrink it;
it makes it longer, and usually by more than the width saved:

  * The isolated transceivers must clear each other by the creepage of
    REFERENCES.md [9] Table 6. Below isolation_envelope.py's minimum width the
    control section can no longer sit BETWEEN the isolated rows and must stack
    beyond them in Y instead, which that tool prices in millimetres of length.
  * A power stage laid out in N columns across the width may not fit a
    narrower strip at all, forcing fewer columns and more rows -- more length
    again.

So: choose the dimension the enclosure actually constrains, and let the
components drive the other. This tool reports both directions plus the area
consequence, so the trade is explicit rather than discovered during placement.

WHAT IT DOES NOT DO
-------------------
It is pure geometry. It does not know the board's part list, so it cannot tell
you the driven dimension -- only that one exists and roughly what a width
change costs in area. It says nothing about bend radius, flex-zone stackup or
copper limits: **no flex or rigid-flex standard is catalogued in
REFERENCES.md**, so any such value would be fabricated. See the Form Factor
sheet of docs/decision-matrix.xlsx.

Usage:
    python3 docs/tools/strip_width.py                      # reference table
    python3 docs/tools/strip_width.py --radius 30 --depth 2.5
    python3 docs/tools/strip_width.py --radius 30 --width 24
    python3 docs/tools/strip_width.py --radius 30 --width 24 --arc 180
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-31. AI-generated; pure
# geometry, every formula shown above and derivable by inspection. Not
# human-authored. Not yet human-reviewed.

import argparse
import math

DEFAULT_RADIUS_MM = 30.0
WIDTH_SERIES_MM = (16, 18, 20, 22, 24, 25.4, 26, 28, 30, 32)
DEPTH_SERIES_MM = (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0)


def sagitta(radius_mm: float, width_mm: float) -> float:
    """Radial depth consumed by a flat strip of the given width."""
    half = width_mm / 2.0
    if half >= radius_mm:
        raise ValueError(f"strip {width_mm} mm cannot fit radius {radius_mm} mm")
    return radius_mm - math.sqrt(radius_mm**2 - half**2)


def width_for_depth(radius_mm: float, depth_mm: float) -> float:
    """Widest flat strip fitting inside the given radial depth."""
    if depth_mm >= radius_mm:
        raise ValueError("depth must be less than the radius")
    return 2.0 * math.sqrt(2.0 * radius_mm * depth_mm - depth_mm**2)


def facet_angle_deg(radius_mm: float, width_mm: float) -> float:
    """Arc subtended by one flat facet of the given width."""
    return 2.0 * math.degrees(math.asin((width_mm / 2.0) / radius_mm))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radius", type=float, default=DEFAULT_RADIUS_MM,
                    help="host bore radius in mm (default: 30.0)")
    ap.add_argument("--width", type=float, help="strip width in mm")
    ap.add_argument("--depth", type=float, help="radial depth budget in mm")
    ap.add_argument("--arc", type=float,
                    help="total arc to cover in degrees; reports facet count")
    args = ap.parse_args()

    radius = args.radius
    print(f"host bore radius R = {radius:.2f} mm "
          f"({radius / 25.4:.3f} in), circumference "
          f"{2 * math.pi * radius:.2f} mm\n")

    if args.width is not None:
        depth = sagitta(radius, args.width)
        angle = facet_angle_deg(radius, args.width)
        print(f"strip width  w = {args.width:.2f} mm "
              f"({args.width / 25.4:.3f} in)")
        print(f"  sagitta    s = {depth:.3f} mm ({depth / 25.4:.3f} in) "
              f"-- radial depth this strip consumes")
        print(f"  facet arc    = {angle:.2f} deg of the bore")
        if args.arc:
            print(f"  covering {args.arc:.1f} deg needs "
                  f"{math.ceil(args.arc / angle)} facets")
        print()

    if args.depth is not None:
        width = width_for_depth(radius, args.depth)
        print(f"radial depth s = {args.depth:.2f} mm "
              f"({args.depth / 25.4:.3f} in)")
        print(f"  max width  w = {width:.2f} mm ({width / 25.4:.3f} in)")
        print(f"  facet arc    = {facet_angle_deg(radius, width):.2f} deg\n")

    if args.width is None and args.depth is None:
        print(f"{'width mm':>9s} {'width in':>9s} {'sagitta mm':>11s} "
              f"{'sagitta in':>11s} {'facet deg':>10s}")
        for width in WIDTH_SERIES_MM:
            try:
                depth = sagitta(radius, width)
            except ValueError:
                continue
            print(f"{width:9.2f} {width / 25.4:9.3f} {depth:11.3f} "
                  f"{depth / 25.4:11.3f} {facet_angle_deg(radius, width):10.2f}")

        print(f"\n{'depth mm':>9s} {'max width mm':>13s} {'max width in':>13s}")
        for depth in DEPTH_SERIES_MM:
            width = width_for_depth(radius, depth)
            print(f"{depth:9.2f} {width:13.2f} {width / 25.4:13.3f}")

        print("\nWidth is not free: a narrower board is a LONGER board.")
        print("Run docs/tools/isolation_envelope.py --board-width <w> for the")
        print("length that narrowing costs on THIS design's isolation "
              "geometry.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
