#!/usr/bin/env python3
"""Delete autorouter tracks on the 50 A nets, and say what they would cost.

Governed by AGENTS.md. Run this after `tools/autoroute.py`, every time.

WHY THIS EXISTS
---------------
`tools/autoroute.py` hands FreeRouting a "power" net class at 3.0 mm for
VM, GND and PH_A/PH_B/PH_C. 3.0 mm is a defensible width for a signal-class
power rail. It is not a defensible width for 50 A, and the router has no way
to know the difference -- it satisfies the class it was given.

Measured on this board at 2 oz, 85 C copper (`docs/tools/conductor_sizing.py`):

  * the three phase runs from pour edge to terminal, at 3.0 mm, dissipate
    11.4 W between them -- MORE than all six TPHR8504PL FETs' conduction loss
    combined (10.5 W), and in series with the pours' own 6.7 W;
  * the VM run from J5A to the far high-side drain, at 3.0 mm, dissipates
    5.2 W where the same span as a pour costs 0.7 W.

A routed-looking board carrying those tracks is worse than an obviously
unrouted one, because the ratsnest stops warning you. So the tracks come out
and the connections go back to being visibly open, pending TODO.md 12.5.s
(VM) and 12.5.t (the phase gap), both of which need a POUR or a placement
change rather than a track.

WHAT IT DOES NOT DO
-------------------
It does not touch GND. GND is carried by four zones (In1 solid, In2 partial,
F.Cu and B.Cu pours) and its remaining connections are genuine short stitches
between pours and pads, which a 3.0 mm track serves correctly.

Usage:
    python3 tools/strip_high_current_tracks.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-16, TODO.md 12.5.s/12.5.t.
# AI-generated. The dissipation figures quoted above are computed by
# docs/tools/conductor_sizing.py, an AGENTS.md Sec.4 engineering derivation
# from copper's resistivity -- watts, not degrees. Not human-authored.

import argparse
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"

# GND is deliberately absent -- see the docstring.
HIGH_CURRENT_NETS = ("VM", "PH_A", "PH_B", "PH_C")


def main() -> int:
    """Strip high-current tracks and report the resulting open connections."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be removed, change nothing")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    doomed = [t for t in board.GetTracks()
              if t.GetNetname() in HIGH_CURRENT_NETS]

    if not doomed:
        print("no tracks on " + "/".join(HIGH_CURRENT_NETS)
              + " -- nothing to strip")
        return 0

    by_net: dict[str, list[float]] = {}
    for t in doomed:
        by_net.setdefault(t.GetNetname(), []).append(
            pcbnew.ToMM(t.GetWidth()) if t.GetClass() == "PCB_TRACK" else 0.0)

    print(f"{'net':8s} {'segments':>9} {'widest mm':>10}")
    for net, widths in sorted(by_net.items()):
        print(f"{net:8s} {len(widths):>9} {max(widths):>10.2f}")

    if args.dry_run:
        print("\n--dry-run: nothing changed")
        return 0

    for t in doomed:
        board.Remove(t)

    # Re-pour: the removed tracks were pushing the pour outlines around.
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    board.Save(str(PCB))

    print(f"\nremoved {len(doomed)} items; zones refilled")
    print(f"unconnected now: "
          f"{board.GetConnectivity().GetUnconnectedCount(False)}")
    print("The 50 A nets are open ON PURPOSE. Close them with a pour or a "
          "placement change -- TODO.md 12.5.s and 12.5.t.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
