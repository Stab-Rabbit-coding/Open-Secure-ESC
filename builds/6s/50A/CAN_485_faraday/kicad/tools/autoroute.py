#!/usr/bin/env python3
"""Auto-route the board with FreeRouting, then re-pour and report.

The `autoroute` skill in ~/.claude/skills/autoroute/ does the same job but is
hard-coded for a macOS KiCad install (it shells out to
`/Applications/KiCad/KiCad.app/.../python3`). This machine is Linux with
KiCad 9.0.2, whose `pcbnew` module is importable directly, so the round trip
is done in-process here instead.

WHAT GETS ROUTED, AND WHAT DELIBERATELY DOES NOT
-------------------------------------------------
VM and GND are carried by poured planes (In1.Cu solid GND, In2.Cu VM over the
power stage, GND pours on both outer layers) -- see tools/build_pcb.py. Those
nets are already connected before the router runs, so FreeRouting only has to
stitch what the planes do not reach. That ordering matters: a router handed an
unpoured board will happily connect a 50 A pack net with a signal-width trace.

The isolation keepout from tools/build_pcb.py is exported into the DSN as a
plane-free region, so the router will not drop copper across the transceivers'
isolation barrier.

Existing tracks are cleared before export so each run starts from the same
state and the result is reproducible.

AFTER ROUTING
-------------
Zones are re-poured (the new tracks change the pour outlines) and connectivity
rebuilt, so the saved board is in the same state KiCad would leave it in. The
script reports track count, via count, and any remaining unrouted connections
-- a partial route is normal and is reported, not hidden.

Usage:
    python3 tools/autoroute.py [--passes N] [--jar PATH]
"""
# Authored by Claude Opus 5 (Anthropic) during the 2026-08-15 layout pass,
# TODO.md 12.4. AI-generated; reviewed against the primary sources named
# in the docstring above. Not human-authored.


import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
KICAD_DIR = HERE.parent
PCB = KICAD_DIR / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-autoroute.bak")

# name -> (track width um, clearance um, nets). Mirrors tools/set_netclasses.py.
# These have to be injected into the DSN by hand: net classes live in the
# .kicad_pro, and `pcbnew.LoadBoard()` used standalone does not read the
# project file, so ExportSpecctraDSN puts EVERY net in one "kicad_default"
# class at the default 0.2 mm. The first routed board came back with the pack
# and all three motor phases on 0.2 mm track because of exactly this.
DSN_CLASSES: dict[str, tuple[int, int, tuple[str, ...]]] = {
    "power": (3000, 400, ("VM", "GND", "PH_A", "PH_B", "PH_C")),
    "sense": (500, 300, ("ISENSE_A_HI", "ISENSE_B_HI", "ISENSE_C_HI")),
}

DEFAULT_JARS = (
    Path("/usr/share/freerouting-2.2.4-linux-x64/lib/app/freerouting-executable.jar"),
    Path.home() / ".claude" / "skills" / "autoroute" / "freerouting.jar",
)


def find_jar(explicit: str | None) -> Path:
    """Locate a FreeRouting jar."""
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise SystemExit(f"no such jar: {p}")
        return p
    for cand in DEFAULT_JARS:
        if cand.is_file():
            return cand
    raise SystemExit("FreeRouting jar not found; pass --jar")


def apply_dsn_classes(dsn: Path) -> int:
    """Move the power/sense nets out of kicad_default into their own classes.

    DSN lengths are in micrometres (the file declares `(resolution um 10)`
    and KiCad writes a 0.2 mm track as `width 200`).
    """
    text = dsn.read_text(encoding="utf-8")
    start = text.index("(class kicad_default")
    head_end = text.index("(circuit", start)
    members = text[start + len("(class kicad_default"):head_end]

    assigned = {n for _, _, nets in DSN_CLASSES.values() for n in nets}
    kept, moved = [], 0
    for tok in members.split():
        if tok.strip('"') in assigned:
            moved += 1
            continue
        kept.append(tok)
    if not moved:
        return 0

    rebuilt = ("(class kicad_default " + " ".join(kept) + "\n      "
               + text[head_end:])
    text = text[:start] + rebuilt

    # Insert AFTER the whole kicad_default class closes. Counting parens is
    # the only safe way: an earlier attempt indexed forward from "clearance"
    # and dropped the new classes INSIDE kicad_default's own (rule ...) block,
    # which is malformed even though the file's parens still balanced.
    anchor = text.index("(class kicad_default")
    depth, i = 0, anchor
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    insert_at = text.index("\n", i) + 1

    # Reuse kicad_default's own via padstack rather than naming one: the
    # padstack name encodes the layer span ("Via[0-3]..." on this 4-layer
    # board), so a guessed name would not resolve.
    via = re.search(r"\(use_via\s+([^)]+)\)", text[anchor:i])
    use_via = via.group(1).strip() if via else '"Via[0-3]_600:300_um"'

    blocks = []
    for name, (width, clearance, nets) in DSN_CLASSES.items():
        names = " ".join(f'"{n}"' for n in nets)
        blocks.append(
            f"    (class {name} {names}\n"
            f"      (circuit\n"
            f"        (use_via {use_via})\n"
            f"      )\n"
            f"      (rule\n"
            f"        (width {width})\n"
            f"        (clearance {clearance})\n"
            f"      )\n"
            f"    )\n"
        )
    dsn.write_text(text[:insert_at] + "".join(blocks) + text[insert_at:],
                   encoding="utf-8")
    return moved


def unrouted_count(board) -> int:
    """Number of ratsnest connections still unrouted."""
    board.BuildConnectivity()
    return board.GetConnectivity().GetUnconnectedCount(False)


def main() -> int:
    """Export DSN, run FreeRouting, import SES, re-pour, report."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--passes", type=int, default=100,
                    help="maximum router passes (default 100)")
    ap.add_argument("--jar", default=None, help="path to freerouting jar")
    ap.add_argument("--timeout", type=int, default=3600,
                    help="router wall-clock limit in seconds")
    args = ap.parse_args()

    jar = find_jar(args.jar)
    shutil.copy2(PCB, BACKUP)
    print(f"backed up -> {BACKUP.name}")

    board = pcbnew.LoadBoard(str(PCB))
    tracks = list(board.GetTracks())
    for t in tracks:
        board.Remove(t)
    if tracks:
        print(f"cleared {len(tracks)} existing track segments")
    board.BuildConnectivity()
    before = unrouted_count(board)
    print(f"unrouted before routing: {before}")
    board.Save(str(PCB))

    with tempfile.TemporaryDirectory() as td:
        dsn = Path(td) / "board.dsn"
        ses = Path(td) / "board.ses"
        if not pcbnew.ExportSpecctraDSN(board, str(dsn)):
            raise SystemExit("ExportSpecctraDSN failed")
        moved = apply_dsn_classes(dsn)
        print(f"exported DSN ({dsn.stat().st_size // 1024} kB); "
              f"{moved} nets moved into power/sense classes")

        cmd = ["java", "-jar", str(jar),
               "-de", str(dsn), "-do", str(ses),
               "-mp", str(args.passes), "-dr", "0"]
        print("running:", " ".join(cmd[:3]), "...")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=args.timeout)
        except subprocess.TimeoutExpired:
            raise SystemExit(f"router exceeded {args.timeout}s")
        tail = (proc.stdout or "").strip().splitlines()[-6:]
        for line in tail:
            print(f"  {line}")
        if not ses.is_file():
            print((proc.stderr or "").strip()[-2000:], file=sys.stderr)
            raise SystemExit("router produced no .ses file")

        routed = pcbnew.LoadBoard(str(PCB))
        if not pcbnew.ImportSpecctraSES(routed, str(ses)):
            raise SystemExit("ImportSpecctraSES failed")

    segs = sum(1 for t in routed.GetTracks()
               if t.GetClass() == "PCB_TRACK")
    vias = sum(1 for t in routed.GetTracks() if t.GetClass() == "PCB_VIA")

    filler = pcbnew.ZONE_FILLER(routed)
    filler.Fill(routed.Zones())
    after = unrouted_count(routed)
    routed.Save(str(PCB))

    print(f"\nrouted: {segs} track segments, {vias} vias")
    print(f"unrouted after routing: {after} (was {before})")
    if after:
        print("NOTE: remaining connections need manual routing or a "
              "placement change -- see kicad/README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
