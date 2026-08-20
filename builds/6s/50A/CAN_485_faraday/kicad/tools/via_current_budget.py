#!/usr/bin/env python3
"""How many vias the pack terminals need, and how many actually fit.

READ THE PROVENANCE SECTION BEFORE USING ANY NUMBER THIS PRINTS.

WHY THIS EXISTS
---------------
TODO.md 12.5.aw records that `tools/stitch_planes.py` sizes the pack-terminal
via arrays geometrically -- as many as fit the pad -- and asserts no current
rating, because IPC-2152 and IPC-2221 are not in REFERENCES.md. This script
does the arithmetic that was missing, from the one source currently on this
machine, and shows its working so every number can be re-derived when an
authoritative copy of the standard is obtained.

PROVENANCE -- SECONDARY SOURCES, CORROBORATED, STILL NOT THE STANDARD
--------------------------------------------------------------------
Neither IPC-2152 nor IPC-2221 has been read. Per AGENTS.md Sec.1.1 nothing
below is a primary citation. What IS now available is a second, independent,
publicly accessible source that agrees with the first, which is worth more
than either alone.

Source A (tool documentation, not a standard):
    ~/.claude/skills/pcb-engineer/references/design-rules.md, "Trace Width
    Calculator" -- gives the equation and its constants:
        k = 0.048 external / 0.024 internal, b = 0.44, c = 0.725.
    It labels these "IPC-2152 methodology". They are the IPC-2221 conductor
    equation; IPC-2152 (2009) replaced that closed form with chart data that
    also accounts for board thickness, copper weight and plane proximity.

Source B (vendor educational article, open access, dated and attributed):
    Z. Peterson, "PCB Trace Width vs. Current Table for High Power Designs",
    Altium Resources, updated 2025-06-27.
    https://resources.altium.com/p/pcb-trace-width-vs-current-table-high-voltage-design
    Gives a trace-width table for 1 oz copper at 10 C rise:
        1 A -> 10 mil, 2 A -> 30 mil, 5 A -> 110 mil, 10 A -> 300 mil

CROSS-CHECK, and the reason the constants are trusted here. Source B's table
was recomputed from Source A's equation using the EXTERNAL constants, 1 oz =
1.378 mil, dT = 10 C. Agreement: -1.8 %, +0.7 %, +4.3 % on the 2 A, 5 A and
10 A rows (-11.4 % on the 1 A row, which is a rounded table entry). Two
sources that never cite each other produce the same numbers, so the external
constants are treated as sound.

WHAT IS STILL NOT CORROBORATED -- read this before trusting the via counts:
  - The INTERNAL constant (k = 0.024) comes from Source A alone. Source B's
    table is external-layer data and cannot confirm it.
  - The annulus model for a via barrel below is this file's own construction.
    NO SOURCE CONSULTED STATES IT. Altium's dedicated via article
    ("PCB Via Current-Carrying Capacity: Is My PCB Too Hot?", Z. Peterson,
    updated 2025-09-09,
    https://resources.altium.com/p/pcb-current-carrying-capacity-how-hot-too-hot)
    gives no area formula at all -- it offers a rule of thumb instead, quoted
    in the cross-check printed by this script.

ONE THING THAT HELPS: Altium's IPC-2221 calculator article
(https://resources.altium.com/p/ipc-2221-calculator-pcb-trace-current-and-heating,
updated 2025-06-26) states that "the minimum width value that you calculate
from IPC-2221 is probably an overestimate, thus the IPC-2152 standard
attempted to expand the available set of data." IPC-2221 therefore demands
MORE copper than IPC-2152 would. The via counts below are consequently
conservative, not optimistic -- which is the direction an unverified number
should err in.

THE MODEL
---------
A plated via barrel is treated as a conductor of annular cross-section:

    A = pi/4 * (D_outer^2 - D_inner^2),  D_outer = drill + 2 * plating

and the IPC-2221 conductor equation is inverted to give current for that area:

    I = k * dT^b * A^c        A in mil^2, I in A, dT in C

External vs internal constants is the judgement call. A via barrel sits inside
the laminate like an internal conductor, but it is only as long as the board is
thick and it terminates in copper at both ends, so the usual practice is
somewhere between. Both are printed. **Use the internal column for anything
load-bearing** until the real standard says otherwise.

Barrel plating thickness dominates the result and is a FAB parameter, not a
design one: IPC-6012 Class 2 and Class 3 differ, and budget vendors publish
lower typical values. It is swept rather than assumed.

Usage:
    python3 tools/via_current_budget.py
    python3 tools/via_current_budget.py --current 50 --pad 7.0
"""
# Authored by Claude Opus 5 (Anthropic), 2026-08-19. AI-generated.
# Arithmetic only -- no standard was read in producing this file.

import argparse
import math

MM2_TO_MIL2 = 1550.0031          # 1 mm^2 in mil^2

# Constants. [S-F] is a dedicated via calculator that publishes IPC-2221 and
# IPC-2152 side by side and settles the question this file previously had to
# leave open: for a VIA it uses the OUTER-layer constant, k = 0.048, not the
# internal 0.024. IPC-2152 uses k = 0.064 for the same geometry -- [S-F]:
# "IPC-2152 typically rates vias 25-35% higher for the same geometry because
# it accounts for plane proximity heat-sinking." 0.064/0.048 = 1.333, inside
# that band, and consistent in direction with [S-C]'s statement that IPC-2221
# overestimates the copper IPC-2152 would require.
K_IPC2221 = 0.048
K_IPC2152 = 0.064
B_EXP = 0.44
C_EXP = 0.725

# [S-F]: IPC Class 2 minimum average barrel plating 20 um, Class 3 25 um.
PLATING_UM = {"Class 2": 20.0, "Class 3": 25.0}

# [S-F]: "Apply 20-25% safety margin above the IPC-2221 minimum current."
# Stated as advice to the designer; the calculator does not apply it itself.
DESIGN_MARGIN = 0.25


def barrel_area_mm2(drill_mm: float, plating_um: float) -> float:
    """Annular copper cross-section of a plated via barrel.

    Plating grows INWARD from the drilled wall -- the finished hole is
    drill - 2t, and the copper occupies the ring between them:

        A = pi * ((d/2)^2 - (d/2 - t)^2)

    The first version of this file had the plating growing OUTWARD into the
    laminate (A = pi/4 ((d + 2t)^2 - d^2)), which overstates the barrel area
    by about 7 % at 0.60 mm / 20 um. Corrected 2026-08-19 against [S-F].
    """
    r = drill_mm / 2.0
    t = plating_um / 1000.0
    return math.pi * (r ** 2 - (r - t) ** 2)


def current_a(area_mm2: float, delta_t_c: float, k: float) -> float:
    """Conductor equation solved for current. A in mm^2 in, amps out."""
    return k * (delta_t_c ** B_EXP) * ((area_mm2 * MM2_TO_MIL2) ** C_EXP)


def fit_count(pad_mm: float, via_pad_mm: float, clearance_mm: float) -> int:
    """How many vias fit a square pad on a regular grid."""
    pitch = via_pad_mm + clearance_mm
    per_side = int((pad_mm - via_pad_mm) // pitch) + 1
    return max(per_side, 0) ** 2


def main() -> int:
    """Print the via budget for the pack terminals."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--current", type=float, default=50.0,
                    help="terminal current in A (default 50)")
    ap.add_argument("--pad", type=float, default=7.0,
                    help="square terminal pad size in mm (default 7.0)")
    ap.add_argument("--rise", type=float, default=10.0,
                    help="allowed temperature rise in C (default 10)")
    args = ap.parse_args()

    print(f"Terminal: {args.current:.0f} A into a {args.pad:.1f} x "
          f"{args.pad:.1f} mm F.Cu pad, dT = {args.rise:.0f} C\n")

    print("PER-VIA CAPACITY  (barrel annulus, plating inward from the drill)")
    print(f"  {'drill':>6} {'class':>8} {'plating':>8} {'area':>10} "
          f"{'IPC-2221':>9} {'IPC-2152':>9}")
    cap = {}
    for drill in (0.30, 0.40, 0.60):
        for cls, plating in PLATING_UM.items():
            a = barrel_area_mm2(drill, plating)
            i21 = current_a(a, args.rise, K_IPC2221)
            i52 = current_a(a, args.rise, K_IPC2152)
            cap[(drill, cls)] = (i21, i52)
            print(f"  {drill:>6.2f} {cls:>8} {plating:>6.0f}um "
                  f"{a * MM2_TO_MIL2:>7.1f}mil2 {i21:>8.2f}A {i52:>8.2f}A")

    print(f"\nVIA COUNT  (with the {DESIGN_MARGIN:.0%} design margin [S-F] advises)")
    print(f"  {'drill':>6} {'class':>8} {'basis':>9} {'A/via':>7} "
          f"{'bare':>6} {'+margin':>8} {'fits pad':>9} {'verdict':>8}")
    for drill, via_pad in ((0.30, 0.60), (0.40, 0.80), (0.60, 1.00)):
        fits = fit_count(args.pad, via_pad, 0.20)
        for cls in PLATING_UM:
            for label, idx in (("IPC-2221", 0), ("IPC-2152", 1)):
                per = cap[(drill, cls)][idx]
                bare = math.ceil(args.current / per)
                marg = math.ceil(args.current / (per * (1 - DESIGN_MARGIN)))
                print(f"  {drill:>6.2f} {cls:>8} {label:>9} {per:>6.2f}A "
                      f"{bare:>6} {marg:>8} {fits:>9} "
                      f"{'OK' if marg <= fits else 'SHORT':>8}")

    print("""
THE SOURCE DISAGREES WITH ITSELF -- READ BEFORE USING THESE NUMBERS
  [S-F] publishes both the formula above and a reference table. They do not
  agree. Its table gives ~0.65 A (IPC-2221) for a 0.30 mm via at 25 um and
  dT 10 C; the same formula and constants give 1.69 A -- a factor of 2.6.
  Its two table columns ARE self-consistent (0.87 / 0.65 = 1.34, matching
  0.064 / 0.048), so the ratio between the standards is sound and only the
  absolute scale is in doubt.
  This matters because the two readings straddle the answer:
    formula basis  -> 0.60 mm Class 2 needs 28 vias with margin, 36 fit: OK
    table basis    -> the same terminal needs ~61, 36 fit: SHORT
  The figures printed above use the FORMULA, because its constants are
  independently corroborated (see the provenance block) while the table's
  are not reproducible from anything published on the page.""")

    print("\nWHAT THIS DOES NOT DECIDE")
    print("  J5B cannot have vias at any count -- the isolation barrier")
    print("  forbids them there (TODO.md 12.5.ax). This budget applies to")
    print("  J5A, and to wherever the F.Cu GND corridor added by")
    print("  tools/split_top_pour.py hands off to the ground planes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
