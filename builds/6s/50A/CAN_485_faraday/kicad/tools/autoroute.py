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

# --- KiCad 9.0.2: the DSN class injection this file used to do is OBSOLETE ---
# The comment that used to live here said `pcbnew.LoadBoard()` standalone does
# not read the .kicad_pro, so ExportSpecctraDSN put every net in one
# `kicad_default` class at 0.2 mm, and the first routed board came back with
# the pack and all three phases on 0.2 mm track.
#
# Re-checked 2026-08-19 against KiCad 9.0.2 (`pcbnew 9.0.2+dfsg-1`): that is no
# longer true. LoadBoard() resolves the project net classes -- `FindNet("VM")
# .GetNetClassName()` returns "Power" -- and ExportSpecctraDSN writes real
# `(class Power ...)`, `(class Sense ...)`, `(class Isolated ...)` blocks with
# the project widths (3000 / 500 / 400 um). Injecting them by hand is now
# redundant, so it is gone.
#
# The precondition is that the classes actually EXIST in the .kicad_pro. They
# were found missing on 2026-08-19 -- only "Default" was defined, so every net,
# pack and phases included, would have exported at 0.2 mm exactly as the old
# comment describes. The failure mode did not change; only its cause did.
# `assert_netclasses()` below turns that silent loss into a hard stop.
NETCLASS_EXPECTED: dict[str, float] = {
    "VM": 3.0,
    "GND": 3.0,
    "PH_A": 3.0,
    "PH_B": 3.0,
    "PH_C": 3.0,
    "ISENSE_A_HI": 0.5,
    "CAN_ISO_GND": 0.4,
}

# Nets the router is NOT allowed to touch. Each is carried by a poured plane
# (tools/build_pcb.py) and each also lands on 0.5 mm-pitch WQFN-40 pins on U5.
# One netclass width cannot serve both ends: at the 3.0 mm Power width the
# router cannot leave a 0.25 mm QFN pad at all, and at a width it CAN leave,
# the router would quietly put a signal-scale trace in series with a 50 A
# conductor. So they are withheld from the router and placed deliberately by
# tools/route_power.py instead.
PLANE_NETS: tuple[str, ...] = ("VM", "GND", "PH_A", "PH_B", "PH_C")

# Width handed to the router for the plane nets, and the total routed length
# per net above which that is reported as suspicious rather than accepted.
PLANE_STUB_WIDTH_UM = 500
PLANE_STUB_MAX_MM = 60.0

# Inner layers that are poured planes, not routing space.
PLANE_LAYERS: tuple[str, ...] = ("In1.Cu", "In2.Cu")
EDGE_CLEARANCE_MM = 0.50  # .kicad_pro min_copper_edge_clearance

# DSN coordinates are DECIMAL micrometres -- KiCad writes the board outline as
# "50092.9 -19952.4", not as integers. An integer-only `-?\d+` regex splits
# each of those into two numbers, which silently scrambles the whole
# coordinate list: the first attempt at inset_boundary() turned a 32 x 66 mm
# outline into the rectangle (-85547, -491) .. (51450, -85550) and the router
# went on hugging the real board edge. Nothing errored; the boundary was just
# nonsense. Match the decimals.
DSN_NUM = r"-?\d+(?:\.\d+)?"

# FreeRouting holds the track CENTRELINE inside the boundary, so half a track
# still hangs over it. Inset by the edge clearance PLUS half the widest track
# the router may lay down.
BOUNDARY_INSET_MM = EDGE_CLEARANCE_MM + (PLANE_STUB_WIDTH_UM / 1000.0) / 2

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


def assert_netclasses(board) -> None:
    """Refuse to route if the project net classes went missing.

    They live in the .kicad_pro, not the board, so any tool that rewrites the
    project file can drop them -- which is how the board reached 2026-08-19
    with only "Default" defined. Failing loudly here is the whole point: a
    silently-Default board routes the 50 A pack net at 0.2 mm and nothing
    downstream complains.
    """
    MM = pcbnew.pcbIUScale.IU_PER_MM
    bad = []
    for name, want in NETCLASS_EXPECTED.items():
        net = board.FindNet(name)
        if net is None:
            continue
        got = net.GetNetClassSlow().GetTrackWidth() / MM
        if abs(got - want) > 1e-6:
            bad.append(f"{name}: {got} mm (expected {want} mm)")
    if bad:
        raise SystemExit(
            "net classes are not in effect -- run tools/set_netclasses.py:\n  "
            + "\n  ".join(bad)
        )


def strip_pour_keepouts(dsn: Path, board) -> int:
    """Delete DSN keepouts that came from pour-only rule areas.

    KiCad's Specctra exporter writes EVERY rule area as a bare Specctra
    `(keepout ...)`, which to FreeRouting means "no wire and no via here" --
    it does not carry KiCad's per-item allowed/not_allowed flags across. The
    board's isolation rule area is `copperpour not_allowed` but `tracks
    allowed` / `vias allowed`, so exporting it verbatim tells the router that
    y 76.50..86.55 is off limits on all four layers. U1 (the LQFP-64 MCU),
    U2 and J1 all sit inside that band, so the router could not have connected
    the MCU at all -- it would have reported them unrouted and looked like a
    congestion problem.

    Only keepouts whose source rule area allows both tracks and vias are
    removed; a genuine no-route area would be left in place.
    """
    MM = pcbnew.pcbIUScale.IU_PER_MM
    routable: list[tuple[float, float, float, float]] = []
    for z in board.Zones():
        if not z.GetIsRuleArea():
            continue
        if z.GetDoNotAllowTracks() or z.GetDoNotAllowVias():
            continue
        bb = z.GetBoundingBox()
        routable.append(
            (
                bb.GetLeft() / MM,
                bb.GetRight() / MM,
                bb.GetTop() / MM,
                bb.GetBottom() / MM,
            )
        )
    if not routable:
        return 0

    text = dsn.read_text(encoding="utf-8")
    out, removed, i = [], 0, 0
    while True:
        k = text.find("(keepout ", i)
        if k < 0:
            out.append(text[i:])
            break
        depth, j = 0, k
        while j < len(text):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blk = text[k : j + 1]
        nums = [float(v) / 1000.0 for v in re.findall(DSN_NUM, blk)[1:]]
        xs, ys = nums[0::2], [-v for v in nums[1::2]]
        hit = any(
            abs(min(xs) - l) < 0.1
            and abs(max(xs) - r) < 0.1
            and abs(min(ys) - t) < 0.1
            and abs(max(ys) - b) < 0.1
            for l, r, t, b in routable
        )
        out.append(text[i:k])
        if hit:
            removed += 1
            # swallow the trailing newline/indent so the file stays tidy
            j = j + 1
            while j < len(text) and text[j] in " \t":
                j += 1
            if j < len(text) and text[j] == "\n":
                j += 1
            j -= 1
        else:
            out.append(blk)
        i = j + 1
    if removed:
        dsn.write_text("".join(out), encoding="utf-8")
    return removed


def restrict_plane_layers(dsn: Path) -> int:
    """Mark the inner plane layers non-routable.

    This board is a 4-layer SIG / GND / VM / SIG stack: In1.Cu is a solid GND
    pour over the whole board and In2.Cu is VM over the power stage and GND
    below it. Neither is a signal layer. KiCad's Specctra exporter does not
    know that -- it writes `(type signal)` for every copper layer -- so
    FreeRouting treats both planes as free routing space.

    It does exactly that when allowed. The 2026-08-19 four-layer run put
    **59 segments / 196.7 mm of signal through the In1.Cu ground plane and
    29 segments / 218.3 mm through the In2.Cu VM plane**. Every one of those
    is a slot cut in a reference plane, on a board whose whole reason for
    existing is surviving the EMI of a 50 A inverter: return current under a
    signal crossing the slot has to detour around it, and the detour is the
    loop antenna. The route looked BETTER for it -- fewer unrouted
    connections -- which is why this has to be enforced by the tool rather
    than noticed afterwards.

    Specctra `(type power)` layers are excluded from routing by FreeRouting
    while still being read as copper, which is the behaviour wanted.
    """
    text = dsn.read_text(encoding="utf-8")
    changed = 0
    for layer in PLANE_LAYERS:
        marker = f"(layer {layer}\n      (type signal)"
        if marker in text:
            text = text.replace(marker, f"(layer {layer}\n      (type power)")
            changed += 1
    if changed:
        dsn.write_text(text, encoding="utf-8")
    return changed


def inset_boundary(dsn: Path, inset_mm: float, board) -> bool:
    """DISABLED -- kept for the record. Do not re-enable without reading this.

    THIS APPROACH DOES NOT WORK ON THIS BOARD, and the failure is expensive
    rather than obvious. Two full runs were lost to it on 2026-08-19: both
    hung until their time limit (2700 s and 3000 s) and produced no .ses file
    at all, with no error from FreeRouting either time.

    The reason is that an inset boundary contradicts the rest of the DSN. The
    GND, VM and phase pours are exported as `(plane ...)` polygons that reach
    the board edge at x 20.45..51.45 and y 20.50..85.50 -- so any boundary
    inset from the outline leaves conductor areas, and initially three pads,
    OUTSIDE the region the router is allowed to work in. Clamping the inset to
    the pads (which the code below still does) fixed the pad half and the
    router still hung, because the pours are the larger problem and they
    cannot be clamped away: they are supposed to reach the edge.

    The edge-clearance problem this was meant to solve is real and is still
    open -- 11 `copper_edge_clearance` violations, 6 of them on the isolated
    comms nets. The candidate fix is a Specctra clearance rule of type
    `wire_area` / `via_area`, which expresses clearance TO the boundary
    instead of moving it. That is UNTESTED here and is logged in TODO.md
    12.5.az rather than asserted to work.

    Original intent, for whoever picks this up:

    The DSN boundary KiCad writes is the Edge.Cuts outline itself, with no
    margin, and FreeRouting routes right up to it. KiCad's own
    `min_copper_edge_clearance` (0.50 mm here) is a board setup constraint
    that never reaches the DSN, so the 2026-08-19 run came back with six
    `copper_edge_clearance` violations -- CAN_VISOIN and RS485_GNDISO tracks
    0.317 mm from the edge. Those are the isolated comms nets, i.e. the ones
    where edge copper matters most.

    Shrinking the boundary is done on the rectangular hull rather than by
    offsetting the real outline: the outline has rounded corners, a true
    polygon offset needs a geometry library the DSN text path does not have,
    and a hull inset is conservative everywhere (it never allows copper the
    real outline would have forbidden).

    THE INSET IS CLAMPED SO IT NEVER CROSSES A PAD, and that is not a nicety.
    The first working version inset a flat 0.75 mm, which put J4A/J4B/J4C --
    the three motor phase terminals, 5 x 10 mm solder-wire pads reaching to
    y 85.50 -- **outside the routing boundary**, 0.20 mm past its 85.30 edge.
    FreeRouting did not reject that and did not error. It started routing and
    never finished: the run was killed at its 3000 s limit having produced no
    .ses file at all, and because the tool clears the board before exporting,
    the board came back with 548 segments deleted and nothing to replace them.
    A board whose pads sit outside its own routing boundary is not a board the
    router can solve, so the edge inset yields to the pads wherever they
    conflict.
    """
    text = dsn.read_text(encoding="utf-8")
    start = text.find("(boundary")
    if start < 0:
        return False
    depth, i = 0, start
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    block = text[start : i + 1]
    nums = [float(v) for v in re.findall(DSN_NUM, block)]
    if len(nums) < 6:
        return False
    coords = nums[1:]  # drop the leading path width 0
    xs, ys = coords[0::2], coords[1::2]
    d = inset_mm * 1000.0  # DSN resolution is um
    left, right = min(xs) + d, max(xs) - d
    top, bottom = min(ys) + d, max(ys) - d

    # Clamp to the pads. DSN y is the negated board y, so a pad's board-space
    # top becomes the larger (less negative) DSN value; compare in DSN space
    # to keep the arithmetic in one coordinate system.
    mm = pcbnew.pcbIUScale.IU_PER_MM
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            bb = pad.GetBoundingBox()
            px0, px1 = bb.GetLeft() / mm * 1000.0, bb.GetRight() / mm * 1000.0
            py0, py1 = -bb.GetBottom() / mm * 1000.0, -bb.GetTop() / mm * 1000.0
            left, right = min(left, px0), max(right, px1)
            top, bottom = min(top, py0), max(bottom, py1)
    rect = (
        f"(boundary\n      (path pcb 0  {left:.1f} {top:.1f}"
        f"  {right:.1f} {top:.1f}  {right:.1f} {bottom:.1f}"
        f"  {left:.1f} {bottom:.1f}  {left:.1f} {top:.1f})\n    )"
    )
    dsn.write_text(text[:start] + rect + text[i + 1 :], encoding="utf-8")
    return True


def relax_plane_class(dsn: Path) -> bool:
    """Give the plane nets a stub width the router can actually use.

    The Power net class is 3.0 mm, which is right for what those nets ARE: VM,
    GND and the three phases carry the pack current. It is wrong for what the
    router still has to do with them. After the pours are correct
    (tools/fix_phase_pours.py) every connection left on those nets is a small
    pad reaching the plane beside it -- and five of them are 0.25 mm pads on
    U5's 0.5 mm-pitch WQFN-40. A router told to leave a 0.25 mm pad with a
    3.0 mm track cannot do it at all; it reports the connection unrouted and
    the failure reads as congestion.

    One net class cannot describe both ends of a power net. So the class width
    is relaxed in the DSN only, for the router's benefit; the .kicad_pro keeps
    saying 3.0 mm, which is the truth about the conductor. Every track the
    router then puts on a plane net is checked afterwards
    (`report_plane_tracks`) and anything longer than a stub is reported, so a
    signal-width trace cannot quietly end up in series with 50 A.
    """
    text = dsn.read_text(encoding="utf-8")
    anchor = text.find("(class Power ")
    if anchor < 0:
        return False
    end = (
        text.index("(class ", anchor + 1)
        if "(class " in text[anchor + 1 :]
        else len(text)
    )
    block = text[anchor:end]
    fixed = re.sub(r"\(width \d+\)", f"(width {PLANE_STUB_WIDTH_UM})", block)
    if fixed == block:
        return False
    dsn.write_text(text[:anchor] + fixed + text[end:], encoding="utf-8")
    return True


def report_plane_tracks(board) -> list[str]:
    """Flag any routed track on a plane net that is longer than a stub.

    The router was handed a relaxed width for the plane nets so it could reach
    fine-pitch pads. The risk that buys is a long signal-width trace in series
    with a 50 A conductor. Anything over PLANE_STUB_MAX_MM is reported here
    rather than left for someone to find on a fabricated board.
    """
    mm = pcbnew.pcbIUScale.IU_PER_MM
    runs: dict[str, float] = {}
    for track in board.GetTracks():
        if track.GetClass() != "PCB_TRACK":
            continue
        name = track.GetNetname()
        if name in PLANE_NETS:
            runs[name] = runs.get(name, 0.0) + track.GetLength() / mm
    return [
        f"{n}: {L:.1f} mm of routed track"
        for n, L in sorted(runs.items())
        if L > PLANE_STUB_MAX_MM
    ]


def unrouted_count(board) -> int:
    """Number of ratsnest connections still unrouted."""
    board.BuildConnectivity()
    return board.GetConnectivity().GetUnconnectedCount(False)


def main() -> int:
    """Export DSN, run FreeRouting, import SES, re-pour, report."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--passes", type=int, default=100, help="maximum router passes (default 100)"
    )
    ap.add_argument("--jar", default=None, help="path to freerouting jar")
    ap.add_argument(
        "--inset-boundary",
        action="store_true",
        help="re-enable the DSN boundary inset -- KNOWN TO HANG "
        "the router on this board, see inset_boundary()",
    )
    ap.add_argument(
        "--timeout", type=int, default=3600, help="router wall-clock limit in seconds"
    )
    args = ap.parse_args()

    jar = find_jar(args.jar)
    shutil.copy2(PCB, BACKUP)
    print(f"backed up -> {BACKUP.name}")

    board = pcbnew.LoadBoard(str(PCB))
    assert_netclasses(board)
    tracks = list(board.GetTracks())
    for t in tracks:
        board.Remove(t)
    if tracks:
        print(f"cleared {len(tracks)} existing track segments")
    board.BuildConnectivity()
    before = unrouted_count(board)
    print(f"unrouted before routing: {before}")

    with tempfile.TemporaryDirectory() as td:
        dsn = Path(td) / "board.dsn"
        ses = Path(td) / "board.ses"
        # The cleared board is saved to SCRATCH, not over PCB. It used to be
        # written straight back to PCB so the SES import had a clean base --
        # which means a router that fails leaves the real board wiped. That
        # happened on 2026-08-19: the router hung on a bad boundary, hit its
        # time limit, produced no .ses, and the board was left with 548
        # segments deleted and nothing to replace them. PCB is now only
        # written once there is a routed result to write.
        scratch = Path(td) / "cleared.kicad_pcb"
        board.Save(str(scratch))
        if not pcbnew.ExportSpecctraDSN(board, str(dsn)):
            raise SystemExit("ExportSpecctraDSN failed")
        cut = strip_pour_keepouts(dsn, board)
        planes = restrict_plane_layers(dsn)
        # inset_boundary() is OFF by default -- read its docstring before
        # turning it on. It hung the router twice for a full time limit each.
        inset = (
            inset_boundary(dsn, BOUNDARY_INSET_MM, board)
            if args.inset_boundary
            else False
        )
        relaxed = relax_plane_class(dsn)
        print(
            f"  {planes} inner layers marked non-routable; "
            f"boundary inset: {inset} (see inset_boundary docstring)"
        )
        print(
            f"exported DSN ({dsn.stat().st_size // 1024} kB); "
            f"{cut} pour-only keepouts removed; plane class "
            f"{f'relaxed to {PLANE_STUB_WIDTH_UM} um' if relaxed else 'unchanged'}"
        )

        cmd = [
            "java",
            "-jar",
            str(jar),
            "-de",
            str(dsn),
            "-do",
            str(ses),
            "-mp",
            str(args.passes),
            "-dr",
            "0",
        ]
        print("running:", " ".join(cmd[:3]), "...")
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=args.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            raise SystemExit(f"router exceeded {args.timeout}s")
        tail = (proc.stdout or "").strip().splitlines()[-6:]
        for line in tail:
            print(f"  {line}")
        if not ses.is_file():
            print((proc.stderr or "").strip()[-2000:], file=sys.stderr)
            raise SystemExit("router produced no .ses file")

        routed = pcbnew.LoadBoard(str(scratch))
        if not pcbnew.ImportSpecctraSES(routed, str(ses)):
            raise SystemExit("ImportSpecctraSES failed")

    segs = sum(1 for t in routed.GetTracks() if t.GetClass() == "PCB_TRACK")
    vias = sum(1 for t in routed.GetTracks() if t.GetClass() == "PCB_VIA")

    filler = pcbnew.ZONE_FILLER(routed)
    filler.Fill(routed.Zones())
    after = unrouted_count(routed)
    routed.Save(str(PCB))

    print(f"\nrouted: {segs} track segments, {vias} vias")
    print(f"unrouted after routing: {after} (was {before})")
    for line in report_plane_tracks(routed):
        print(f"CHECK: plane net carries more than a stub -- {line}")
    if after:
        print(
            "NOTE: remaining connections need manual routing or a "
            "placement change -- see kicad/README.md"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
