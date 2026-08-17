#!/usr/bin/env python3
"""Mechanical repairs after the 2026-08-17 front/back re-placement.

Governed by AGENTS.md. Does ONLY the unambiguous fixes -- the ones with a
single right answer that needs no design judgement. Everything requiring a
call is left alone and listed in TODO.md 12.5.y.

THE RE-PLACEMENT
----------------
The repo owner restructured the board so the front carries power (pack ->
FETs -> phase terminals) and the back carries control and comms (MCU,
security element, isolated transceivers), with comms and pack input at the
same end. That opened the F.Cu corridor `U3`/`U4` used to block, which is
what unblocks the phase gap (TODO.md 12.5.t). The structure is right; four
mechanical consequences needed cleaning up.

WHAT THIS FIXES

1. **PH_A and PH_C were crossed.** `J4A` sat at x 21.6 while its FETs
   (`Q1`/`Q2`) sat at x 2.2-6.0, and `J4C` was the mirror image -- a 19.4 mm
   lateral span each, with the two 50 A nets having to cross one another.
   Swapping the two terminals takes both spans to about 4 mm. `PH_B` was
   already correct and is untouched.

2. **Four footprints overhung the board edge.** `J4A`/`J4B`/`J4C` by 0.17 mm
   at the bottom, `J1` by 0.07 mm at the right. Nudged inboard.

3. **Stale routing.** All 400 track/via items were laid by FreeRouting
   against the PREVIOUS placement and no longer match any pad; they produced
   123 shorting_items and 190 clearance violations purely by sitting where
   parts used to be. Removed. Routing has to be redone once placement is
   final anyway, and `tools/autoroute.py` clears tracks on entry regardless.

4. **Stale copper pours.** Zones do not follow footprints. The three phase
   pours still sat at y 11.10..33.10 while the FETs had moved to
   y 23.35..44.35, and the F.Cu VM pour still sat at y 0.60..15.50 while the
   high-side drains had moved to y 23..36. Both are rebuilt from the pads
   they actually have to reach, one phase pour per FET column, extended down
   to the phase terminal now that the corridor is open.

WHAT THIS DELIBERATELY DOES NOT FIX -- see TODO.md 12.5.y

  * `C1` is now 17.6-24.0 mm from the high-side drains (was 4.1-9.7). That is
    the commutation loop the 40 V FET choice depends on -- placement call.
  * `U6`/`U7`/`U8` are now 22-28 mm from their shunts (was 1.2-2.6). Those are
    millivolt differential taps -- placement call.
  * The isolation keepout still sits at y 50.60..59.30 while the isolated
    parts moved to y 0.19..22.77. Moving it is NOT mechanical: the pack input
    is at the top and the FETs are in the middle, so VM must now traverse the
    band the keepout would occupy. That is a real structural conflict and
    needs a decision, not a script.
  * The In2.Cu VM/GND split still sits at y 34.60, which was correct when the
    power stage was at the top. Depends on the same decision.

Usage:
    python3 tools/fix_after_replacement.py [--dry-run]
"""
# Authored by Claude Opus 5 (Anthropic) 2026-08-17, TODO.md 12.5.y.
# AI-generated. Every coordinate is measured off the board, not assumed.
# Not human-authored.

import argparse
import shutil
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
PCB = HERE.parent / "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
BACKUP = PCB.with_suffix(".kicad_pcb.pre-fix.bak")

# Column x-bands, one per phase, taken from the FET columns and the terminals
# they now sit above. Gaps between bands exceed the 0.3 mm zone clearance.
COLUMNS = {"PH_A": (0.55, 8.20), "PH_B": (8.70, 16.50), "PH_C": (17.00, 24.95)}
POUR_BOTTOM = 59.60          # inner edge, matches the existing GND pour
PHASE_PRIORITY = 3
VM_PRIORITY = 2
CLEARANCE_MM = 0.3
EDGE_MARGIN = 0.03           # push overhanging parts this far back inside
# Board-edge copper clearance from the project rules. Courtyards are not the
# binding constraint here -- a solder-pad footprint's courtyard is only
# 0.25 mm bigger than its pad, so clearing the outline by courtyard still
# left the PADS at 0.305 mm against a 0.5 mm rule.
EDGE_COPPER_CLEARANCE = 0.5


def origin(board):
    """Top-left of the board outline."""
    box = board.GetBoardEdgesBoundingBox()
    return box.GetLeft(), box.GetTop()


def fp(board, ref):
    """Footprint by reference, or None."""
    for f in board.Footprints():
        if f.GetReference() == ref:
            return f
    return None


def courtyard(f):
    """Courtyard bbox on whichever side the footprint sits."""
    p = f.GetCourtyard(pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd)
    return p.BBox() if p.OutlineCount() else f.GetBoundingBox(False, False)


def net_pad_span(board, net, x1, x2, only=None):
    """Vertical span of `net`'s pads whose centre falls inside [x1, x2].

    `only` restricts the search to a set of references. That matters for VM:
    the net also lands on `U5`, `R8` and `C6`, which are low-current taps
    (gate-driver supply, sense divider, decoupling) sitting far down the
    board. Sizing the F.Cu power pour to reach them would drag 50 A copper
    across the whole control section for the sake of a few milliamps.
    """
    ox, oy = origin(board)
    ys = []
    for f in board.Footprints():
        if only is not None and f.GetReference() not in only:
            continue
        for p in f.Pads():
            if p.GetNetname() != net:
                continue
            x = pcbnew.ToMM(p.GetPosition().x - ox)
            if not (x1 <= x <= x2):
                continue
            pb = p.GetBoundingBox()
            ys += [pcbnew.ToMM(pb.GetTop() - oy),
                   pcbnew.ToMM(pb.GetBottom() - oy)]
    return (min(ys), max(ys)) if ys else None


# The parts the F.Cu VM pour actually has to bond: pack input, bulk cap, and
# the three high-side drains. Everything else on VM is a low-current tap.
VM_POWER_PARTS = {"J5A", "C1", "Q1", "Q3", "Q5"}


def add_zone(board, net, layer, priority, x1, y1, x2, y2):
    """Rectangular filled zone in board-local millimetres."""
    ox, oy = origin(board)
    z = pcbnew.ZONE(board)
    z.SetNet(board.GetNetInfo().GetNetItem(net))
    z.SetLayer(layer)
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(pcbnew.FromMM(CLEARANCE_MM))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    o = z.Outline()
    o.NewOutline()
    for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        o.Append(ox + pcbnew.FromMM(x), oy + pcbnew.FromMM(y))
    board.Add(z)
    return z


def main() -> int:
    """Apply the four mechanical repairs and report."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(str(PCB))
    ox, oy = origin(board)
    # The TRUE copper window, not GetBoardEdgesBoundingBox(): that box is the
    # Edge.Cuts stroke's outer extent and so is half a line width (0.05 mm)
    # bigger than the board on every side. Nudging against it left every
    # terminal pad exactly 0.02 mm short of the 0.5 mm rule.
    poly = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(poly)
    ob = poly.BBox()
    X0, W = pcbnew.ToMM(ob.GetLeft() - ox), pcbnew.ToMM(ob.GetRight() - ox)
    Y0, H = pcbnew.ToMM(ob.GetTop() - oy), pcbnew.ToMM(ob.GetBottom() - oy)

    # --- 1. swap J4A and J4C so each terminal sits under its own column ---
    a, c = fp(board, "J4A"), fp(board, "J4C")
    pa, pc = a.GetPosition(), c.GetPosition()
    a.SetPosition(pc)
    c.SetPosition(pa)
    print(f"1. swapped J4A <-> J4C  "
          f"(J4A x {pcbnew.ToMM(pa.x - ox):.2f} -> {pcbnew.ToMM(pc.x - ox):.2f} mm)")

    # --- 2. pull overhanging footprints back inside the outline ---
    moved = []
    for f in board.Footprints():
        cb = courtyard(f)
        dx = dy = 0
        over_r = pcbnew.ToMM(cb.GetRight() - ox) - W
        over_b = pcbnew.ToMM(cb.GetBottom() - oy) - H
        over_l = pcbnew.ToMM(cb.GetLeft() - ox) - X0
        over_t = pcbnew.ToMM(cb.GetTop() - oy) - Y0
        # Pads bind before courtyards do; take whichever intrudes further.
        for p in f.Pads():
            pb = p.GetBoundingBox()
            c = EDGE_COPPER_CLEARANCE
            over_r = max(over_r, pcbnew.ToMM(pb.GetRight() - ox) - (W - c))
            over_b = max(over_b, pcbnew.ToMM(pb.GetBottom() - oy) - (H - c))
            over_l = min(over_l, pcbnew.ToMM(pb.GetLeft() - ox) - (X0 + c))
            over_t = min(over_t, pcbnew.ToMM(pb.GetTop() - oy) - (Y0 + c))
        if over_r > 0:
            dx = -pcbnew.FromMM(over_r + EDGE_MARGIN)
        if over_l < 0:
            dx = pcbnew.FromMM(-over_l + EDGE_MARGIN)
        if over_b > 0:
            dy = -pcbnew.FromMM(over_b + EDGE_MARGIN)
        if over_t < 0:
            dy = pcbnew.FromMM(-over_t + EDGE_MARGIN)
        if dx or dy:
            p = f.GetPosition()
            f.SetPosition(pcbnew.VECTOR2I(p.x + dx, p.y + dy))
            moved.append(f"{f.GetReference()}"
                         f"({pcbnew.ToMM(dx):+.2f},{pcbnew.ToMM(dy):+.2f})")
    print(f"2. pulled {len(moved)} overhanging footprints inboard: "
          f"{', '.join(moved) or 'none'}")

    # --- 3. drop the stale routing ---
    tracks = list(board.GetTracks())
    for t in tracks:
        board.Remove(t)
    print(f"3. removed {len(tracks)} stale track/via items "
          f"(routed against the previous placement)")

    if not args.dry_run:
        shutil.copy2(PCB, BACKUP)
        board.Save(str(PCB))

    # --- 4. rebuild the stale pours (reload: zone removal invalidates SWIG
    #        proxies, so this is done as its own pass over a fresh board) ---
    board = pcbnew.LoadBoard(str(PCB))
    doomed = [z for z in board.Zones()
              if not z.GetIsRuleArea()
              and (z.GetNetname() in COLUMNS
                   or (z.GetNetname() == "VM" and z.IsOnLayer(pcbnew.F_Cu)))]
    print(f"4. rebuilding {len(doomed)} stale pours "
          f"({', '.join(sorted(z.GetNetname() for z in doomed))})")
    for z in doomed:
        board.Remove(z)

    for net, (x1, x2) in COLUMNS.items():
        span = net_pad_span(board, net, x1, x2)
        if span is None:
            print(f"     {net}: NO PADS in x {x1}..{x2} -- skipped")
            continue
        top = max(0.60, span[0] - 0.50)
        add_zone(board, net, pcbnew.F_Cu, PHASE_PRIORITY,
                 x1, top, x2, POUR_BOTTOM)
        print(f"     {net}: x {x1:5.2f}..{x2:5.2f}  y {top:5.2f}..{POUR_BOTTOM} "
              f"(pads span y {span[0]:.2f}..{span[1]:.2f})")

    vm = net_pad_span(board, "VM", 0.0, W, only=VM_POWER_PARTS)
    vm_bottom = min(POUR_BOTTOM, vm[1] + 0.50)
    add_zone(board, "VM", pcbnew.F_Cu, VM_PRIORITY,
             0.55, 0.60, 24.95, vm_bottom)
    print(f"     VM  : x  0.55..24.95  y  0.60..{vm_bottom:.2f} "
          f"(pads span y {vm[0]:.2f}..{vm[1]:.2f})")

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    print(f"\nunconnected after rebuild: "
          f"{board.GetConnectivity().GetUnconnectedCount(False)}")

    if args.dry_run:
        print("--dry-run: nothing written")
        return 0
    board.Save(str(PCB))
    print(f"saved {PCB.name} (backup: {BACKUP.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
