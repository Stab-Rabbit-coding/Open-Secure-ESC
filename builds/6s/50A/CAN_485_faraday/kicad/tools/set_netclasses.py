#!/usr/bin/env python3
"""Define net classes for the build, so power nets are not routed as signals.

KiCad 7+ keeps net classes in the PROJECT file, not the board, so this edits
`open_secure_esc_6s_50a_can485_faraday.kicad_pro`. The board and the
Specctra DSN handed to the auto-router both pick the widths up from here --
without them every net, including the pack and phase conductors, would be
routed at the 0.2 mm default.

CLASSES
-------
    Power     VM, GND, PH_A, PH_B, PH_C
              The pack feed, the return, and the three motor phases: every
              conductor that carries the 50 A the build is rated for.
    Sense     ISENSE_A_HI / _B_HI / _C_HI
              Shunt taps. Low current, but they run alongside the switching
              node and are read differentially, so they get their own class
              to keep the widths and clearances consistent between phases.
    Isolated  CAN_ISO_GND, RS485_ISO_GND, CAN_VISOIN_OPEN, CAN_VISOOUT,
              RS485_VISOIN_OPEN, RS485_VISOOUT
              The far side of the two isolators. Grouped so the isolated
              nets are identifiable and consistently routed -- NOT to carry
              the isolation barrier itself.

              An earlier revision of this file gave this class a 1.6 mm
              clearance to "enforce" the barrier. That was wrong and is
              recorded here so it is not retried: these nets include pins
              that are ADJACENT ON THE SAME PACKAGE (CAN_ISO_GND on U3.11
              and CAN_VISOIN_OPEN on U3.16 are 1.27 mm-pitch pins of one
              SOIC-20W), so a clearance wider than the pin pitch is
              unsatisfiable by construction. It produced 346 clearance
              violations.

              The barrier is enforced geometrically instead: the isolated
              side of both transceivers faces the board edge, and a copper
              KEEPOUT (tools/build_pcb.py) removes every plane and pour from
              the isolated band, so no ground plane runs under the barrier.
    Default   everything else.

THE WIDTHS ARE NOT VERIFIED -- READ THIS BEFORE FABRICATING
------------------------------------------------------------
The Power width below is an ENGINEERING DEFAULT recorded per AGENTS.md
Sec.4, not a computed conductor size. IPC-2152 is the governing standard for
current-carrying capacity and it is NOT in REFERENCES.md: it is paywalled and
was not read, so per AGENTS.md Sec.1.3 no number derived from it may be
asserted here.

What that means in practice: 3 mm of 1 oz copper does not carry 50 A. The
design does not rely on it doing so -- VM and GND are poured planes
(tools/build_pcb.py), and the tracks are a supplement to the copper pour, not
the conductor. But the three PHASE nets currently reach the motor connector
partly as routed track, and that IS load-bearing. Before fab someone must
either pour the phases as well or size them against IPC-2152, and pick the
copper weight to match. Logged in TODO.md.

The isolation BARRIER width is likewise unverified. The real creepage and
clearance figures come from the chosen transceiver variant, and ../README.md
still lists ADM3055E-vs-ADM3057E (5000 V rms vs 3750 V rms) and
ADM2582E-vs-ADM2587E as open design questions. The keepout band in
tools/build_pcb.py is sized to clear the isolated pin rows, not to any
creepage table. Setting it properly is logged in TODO.md and depends on
closing the variant choice first.

Usage:
    python3 tools/set_netclasses.py
"""
# Authored by Claude Opus 5 (Anthropic) during the 2026-08-15 layout pass,
# TODO.md 12.4. AI-generated; reviewed against the primary sources named
# in the docstring above. Not human-authored.


import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRO = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pro"

# name -> (track width mm, clearance mm, via diameter mm, via drill mm, nets)
CLASSES: dict[str, tuple[float, float, float, float, tuple[str, ...]]] = {
    # CLEARANCE, 2026-08-19: every class here is now 0.2 mm, and that is not
    # a weakening -- it is the same lesson the Isolated class already learned
    # (see its note below) applied to Power and Sense, where it had been
    # missed.
    #
    # A KiCad net-class clearance is a FLOOR applied to every copper item on
    # the net, INCLUDING two adjacent pins of the same package. Power at
    # 0.4 mm and Sense at 0.3 mm are wider than the 0.28 mm pin-to-pin gap of
    # U5's 0.5 mm-pitch WQFN-40, so they were unsatisfiable by construction
    # and produced 24 clearance violations that no amount of routing could
    # clear -- VM/PH/ISENSE pins against their own neighbours on U5, U1, U2
    # and J1.
    #
    # The wide spacing that Power actually wants is between ROUTED COPPER, not
    # inside an IC. That is expressed in `open_secure_esc.kicad_dru` as a
    # custom rule scoped to non-pad items, which is the KiCad 9 tool for the
    # job. The net class keeps the width and via size, which are per-net and
    # meaningful; the clearance moves to where it can be stated correctly.
    "Power": (3.0, 0.2, 1.2, 0.6, ("VM", "GND", "PH_A", "PH_B", "PH_C")),
    "Sense": (0.5, 0.2, 0.8, 0.4,
              ("ISENSE_A_HI", "ISENSE_B_HI", "ISENSE_C_HI")),
    # 2026-08-19: the isolated net NAMES were re-spun by
    # tools/add_isolated_supply_ferrites.py and
    # tools/add_isolated_supply_caps.py -- the bead splits each isolated
    # rail into a _GNDISO / _ISO_GND pair and a _VISOIN / _VISOOUT pair.
    # The names this file carried until now (CAN_VISOIN_OPEN,
    # RS485_VISOIN_OPEN) no longer exist on the board, so those two
    # assignments silently matched nothing. Verified against the net table
    # in open_secure_esc_6s_50a_can485_faraday.kicad_pcb.
    "Isolated": (0.4, 0.2, 0.8, 0.4,
                 ("CAN_ISO_GND", "CAN_GNDISO",
                  "CAN_VISOIN", "CAN_VISOOUT",
                  "RS485_ISO_GND", "RS485_GNDISO",
                  "RS485_VISOIN", "RS485_VISOOUT",
                  "RS485_A", "RS485_B",
                  "Net-(J2-Pin_1)", "Net-(J2-Pin_2)")),
    # FINE class REMOVED 2026-08-19 -- MEASURED, AND IT BOUGHT NOTHING.
    #
    # The class was 0.10 mm track at 0.09 mm clearance, sized so exactly one
    # trace fits the 0.280 mm gap between U5's 0.5 mm-pitch pads, on the
    # theory that Default geometry (0.2 + 2 x 0.2 = 0.600 mm) was what kept 46
    # pad connections on U1 and U5 unrouted.
    #
    # A full router run says otherwise: **72 -> 69 unrouted**, a gain of three
    # connections, in exchange for leaving the fab envelope kicad/README.md
    # commits to (0.09 mm trace/space is mainstream vendors' published
    # MINIMUM, normally an advanced-tier upcharge).
    #
    # The reason it did nothing was found afterwards and is worth keeping
    # here so the idea is not retried: **U5 is enclosed by SH1's shield land**
    # -- a closed 1.5 mm-wide B.Cu ring at x 24.85..47.05, y 51.70..68.30,
    # with U5's pads entirely inside it. No B.Cu trace escapes that ring at
    # ANY width, so trace width was never the binding constraint. The land is
    # B.Cu only, so the escape has to be a via to F.Cu and a crossing there.
    # Tracked in TODO.md 12.5.ay.
}


def main() -> int:
    """Write the net classes and their net assignments into the project."""
    pro = json.loads(PRO.read_text(encoding="utf-8"))
    net_settings = pro.setdefault("net_settings", {})
    classes = net_settings.setdefault("classes", [])

    template = next((c for c in classes if c.get("name") == "Default"), {})
    keep = [c for c in classes if c.get("name") == "Default"]

    for priority, (name, (width, clr, via_d, via_dr, _)) in enumerate(
            CLASSES.items()):
        entry = dict(template)
        entry.update({
            "name": name,
            "track_width": width,
            "clearance": clr,
            "via_diameter": via_d,
            "via_drill": via_dr,
            "priority": priority,
        })
        keep.append(entry)
    net_settings["classes"] = keep

    assignments: dict[str, str] = {}
    for name, (_, _, _, _, nets) in CLASSES.items():
        for net in nets:
            assignments[net] = name

    # A net-class assignment naming a net that does not exist is silent: the
    # class is written, the net is never matched, and the affected conductor
    # quietly routes at the Default width. That is how CAN_VISOIN_OPEN and
    # RS485_VISOIN_OPEN survived here after the ferrite respin renamed them.
    # Check the names against the board and refuse rather than write a lie.
    pcb = PRO.with_suffix(".kicad_pcb")
    if pcb.is_file():
        board_nets = set(re.findall(r'\(net \d+ "([^"]*)"\)',
                                    pcb.read_text(encoding="utf-8")))
        missing = sorted(n for n in assignments if n not in board_nets)
        if missing:
            raise SystemExit(
                "these nets are named here but do not exist on the board:\n  "
                + "\n  ".join(missing))
    net_settings["netclass_assignments"] = assignments
    # KiCad 8+ stores per-net overrides as netclass_patterns. 9.0.2 still
    # honours netclass_assignments, but writing both means a future KiCad
    # that drops the legacy key does not silently return every net to
    # Default -- which is exactly how these classes were lost once already
    # (the board was found with only "Default" defined, so the pack and
    # phase conductors would have auto-routed at the 0.2 mm signal width).
    net_settings["netclass_patterns"] = [
        {"pattern": net, "netclass": cls}
        for net, cls in assignments.items()
    ]

    PRO.write_text(json.dumps(pro, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {PRO}")
    for name, (width, clr, *_rest) in CLASSES.items():
        nets = CLASSES[name][4]
        print(f"  {name:9} width {width:>4} mm  clearance {clr:>4} mm  "
              f"{len(nets)} nets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
