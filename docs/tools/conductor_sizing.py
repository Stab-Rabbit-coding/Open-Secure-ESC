#!/usr/bin/env python3
"""Size this project's high-current copper from first principles.

Governed by AGENTS.md. This is an INTERIM basis while IPC-2152 [46] remains
unread, not a substitute for it. Read the next two sections before using any
number this prints.

WHAT THIS IS
------------
An engineering derivation from material constants, flagged per AGENTS.md Sec.4
in exactly the way `builds/6s/50A/CAN_485_faraday/README.md` already flags its
Faraday-tier field-strength derivation (E_rms = sqrt(S * eta_0)). The inputs
are two published properties of copper:

    resistivity at 20 C     rho = 1.68e-8 ohm*m
    temperature coefficient alpha = 0.00393 /K

From those, sheet resistance is rho/t, a pour's resistance is sheet resistance
times its aspect ratio in squares, and dissipation is I^2 R. No standard is
invoked and none is needed: this is Ohm's law on a known geometry.

WHAT THIS IS NOT
----------------
It does **not** predict temperature rise, and temperature rise is the thing
IPC-2152 actually gives you. Turning watts into degrees needs the board's
thermal resistance to ambient, which depends on copper area, layer count,
airflow, and neighbouring parts. This script deliberately stops at watts.

**Do not fabricate on the strength of this file alone.** It tells you which
copper weight is defensible and where the copper is thin; it does not tell you
the board will stay below a temperature limit.

WHY NOT JUST USE THE IPC-2221 EQUATION
---------------------------------------
The widely-copied `A = (I / (k * dT^0.44))^(1/0.725)` with k = 0.048/0.024 is
from **IPC-2221 Appendix A**, not IPC-2152. It is frequently mislabelled as
"the IPC-2152 formula" -- including by one of the PCB reference sets consulted
for this project on 2026-08-16, whose own quick-reference table also disagreed
with the formula it printed by roughly 2x at 10 A. IPC-2152 exists precisely
because the 2221 curves were found to be inaccurate. Quoting 2221's constants
under a 2152 citation would be a fabricated citation under AGENTS.md Sec.1.3,
so this project does neither: it derives from physics and leaves IPC-2152 open.

THE THERMAL ANCHOR WE DO HAVE
------------------------------
REFERENCES.md [47] is an instrumented continuous-load test of a shipping
6S/50 A ESC: 50.18 A produced 103 C at 29 C ambient with EDF airflow, on a
40 x 17 mm board (680 mm^2). That is a real measured datapoint at this exact
current, and it is the sanity check to compare any thermal claim against. Our
board is 30 x 60 mm (1800 mm^2), 2.6x the area, so at equal copper weight and
equal airflow a lower rise is expected -- but "expected" is not "measured".

Usage:
    python3 docs/tools/conductor_sizing.py
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-16. AI-generated derivation
# from published material constants; flagged as an engineering judgment call
# per AGENTS.md Sec.4, NOT a standards result. Not human-authored.

from dataclasses import dataclass

RHO_20 = 1.68e-8          # ohm*m, annealed copper at 20 C
ALPHA = 0.00393           # /K
OZ_MM = 0.0348            # 1 oz copper = 34.8 um
BOARD_T_MM = 1.6

# The build's rating and geometry, from builds/6s/50A/CAN_485_faraday/.
PHASE_CURRENT_A = 50.0
PHASE_POUR_W_MM = 7.5
PHASE_POUR_L_MM = 22.0
COPPER_TEMP_C = 85.0      # assumed operating copper temperature, not measured


def sheet_resistance(oz: float, temp_c: float = COPPER_TEMP_C) -> float:
    """Ohms per square for a given copper weight at a given temperature."""
    rho = RHO_20 * (1 + ALPHA * (temp_c - 20.0))
    return rho / (oz * OZ_MM * 1e-3)


def pour_resistance(oz: float, width_mm: float, length_mm: float) -> float:
    """Resistance of a rectangular pour, in ohms."""
    return sheet_resistance(oz) * (length_mm / width_mm)


def via_barrel_area_mm2(drill_mm: float, plating_mm: float = 0.025) -> float:
    """Cross-section of a plated via barrel, treated as a thin annulus."""
    return 3.14159 * drill_mm * plating_mm


@dataclass
class Row:
    """One copper-weight option and what it costs."""
    oz: float
    r_ohm: float
    drop_v: float
    watts_each: float
    watts_total: float


def phase_options() -> list[Row]:
    """Per-phase pour resistance and dissipation for each copper weight."""
    out = []
    for oz in (1.0, 2.0, 3.0):
        r = pour_resistance(oz, PHASE_POUR_W_MM, PHASE_POUR_L_MM)
        w = PHASE_CURRENT_A ** 2 * r
        out.append(Row(oz, r, PHASE_CURRENT_A * r, w, 3 * w))
    return out


def vias_to_match_pour(oz: float, drill_mm: float,
                       plating_mm: float = 0.025) -> tuple[int, float]:
    """Vias needed so a layer transition is not thinner than the pour itself.

    Sized by equivalent copper cross-section, which is the honest comparison:
    a via field that presents less copper than the pour it continues is the
    new narrowest point in the conductor.
    """
    pour_area = PHASE_POUR_W_MM * oz * OZ_MM
    each = via_barrel_area_mm2(drill_mm, plating_mm)
    n = int(-(-pour_area // each))
    return n, PHASE_CURRENT_A / n


def main() -> int:
    """Print the sizing tables."""
    print("CONDUCTOR SIZING -- derivation from material constants")
    print("NOT an IPC-2152 result. Watts only; no temperature prediction.\n")

    print(f"Sheet resistance at {COPPER_TEMP_C:.0f} C copper:")
    for oz in (1.0, 2.0, 3.0):
        print(f"   {oz:.0f} oz   {sheet_resistance(oz) * 1e3:6.3f} mOhm/square")

    print(f"\nPhase pour {PHASE_POUR_W_MM} x {PHASE_POUR_L_MM} mm "
          f"({PHASE_POUR_L_MM / PHASE_POUR_W_MM:.2f} squares) at "
          f"{PHASE_CURRENT_A:.0f} A:")
    print(f"   {'oz':>3} {'R (mOhm)':>9} {'drop (mV)':>10} "
          f"{'W/phase':>8} {'W all 3':>8}")
    for r in phase_options():
        print(f"   {r.oz:>3.0f} {r.r_ohm * 1e3:>9.3f} {r.drop_v * 1e3:>10.1f} "
              f"{r.watts_each:>8.2f} {r.watts_total:>8.2f}")

    print("\n   For scale: the six TPHR8504PL FETs [49] dissipate 6 x 1.75 W")
    print("   = 10.5 W of conduction loss at this current. At 1 oz the phase")
    print("   POURS alone beat that, which is the argument for 2 oz minimum.")

    print("\nVia field, if a phase must change layers "
          "(sized by equivalent copper):")
    for oz in (2.0,):
        for drill, plat in ((0.3, 0.025), (0.4, 0.025), (0.3, 0.035)):
            n, per = vias_to_match_pour(oz, drill, plat)
            print(f"   {oz:.0f} oz pour, {drill} mm drill / {plat * 1000:.0f} um"
                  f" -> {n:3d} vias, {per:.1f} A per via")
    print("\n   Cheapest fix: DON'T change layers. Keep each phase terminal on")
    print("   the same side as its pour and the via field disappears entirely.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
