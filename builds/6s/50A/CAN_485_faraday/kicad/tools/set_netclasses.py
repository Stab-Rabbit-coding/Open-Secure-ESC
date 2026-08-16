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
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRO = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pro"

# name -> (track width mm, clearance mm, via diameter mm, via drill mm, nets)
CLASSES: dict[str, tuple[float, float, float, float, tuple[str, ...]]] = {
    "Power": (3.0, 0.4, 1.2, 0.6, ("VM", "GND", "PH_A", "PH_B", "PH_C")),
    "Sense": (0.5, 0.3, 0.8, 0.4,
              ("ISENSE_A_HI", "ISENSE_B_HI", "ISENSE_C_HI")),
    "Isolated": (0.4, 0.3, 0.8, 0.4,
                 ("CAN_ISO_GND", "RS485_ISO_GND",
                  "CAN_VISOIN_OPEN", "CAN_VISOOUT",
                  "RS485_VISOIN_OPEN", "RS485_VISOOUT")),
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
    net_settings["netclass_assignments"] = assignments

    PRO.write_text(json.dumps(pro, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {PRO}")
    for name, (width, clr, *_rest) in CLASSES.items():
        nets = CLASSES[name][4]
        print(f"  {name:9} width {width:>4} mm  clearance {clr:>4} mm  "
              f"{len(nets)} nets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
