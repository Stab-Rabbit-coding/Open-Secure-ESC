#!/usr/bin/env python3
"""Geometric net tracer for this sheet -- an annotation-independent check.

WHY THIS EXISTS
---------------
This schematic is fully unannotated (every reference is `U?`/`R?`/`C?`), and
`kicad-cli sch export netlist` keys its nodes on (reference, pin number).  When
two different parts both report `U?` and both have a pin `8`, the exported
netlist MERGES them into one node.  That makes the netlist unreliable for
node-level verification here -- it silently hid whether the OPTIGA Trust M was
still attached after the MSPM0G3518-Q1 swap moved `SE_I2C_SCL` from MCU pin 28
onto MCU pin 8, colliding with the Trust M's own pin 8.  Tracked as TODO.md
12.3.i.

This tool ignores references entirely.  It resolves every symbol pin to an
absolute sheet coordinate from the embedded `lib_symbol` geometry plus the
instance transform, unions the wire graph, and reports which real pins share a
net.  Labels name the nets.

Usage:
    python3 trace_nets.py                # print every net
    python3 trace_nets.py SE_I2C_SCL ... # print only these nets

Written by Claude Opus 5 (`claude-opus-5`) under human direction, 2026-08-10.
"""

import math
import re
import sys
from collections import defaultdict
from pathlib import Path

SCH = Path(__file__).resolve().parent.parent / \
    "open_secure_esc_6s_50a_can485_faraday.kicad_sch"


def walk(t, i):
    d = 0
    for q in range(i, len(t)):
        if t[q] == "(":
            d += 1
        elif t[q] == ")":
            d -= 1
            if d == 0:
                return t[i:q + 1], q + 1
    raise ValueError("unbalanced")


def blocks(t, tag, depth_tabs=None):
    """Yield every top-level-ish block opening with (tag."""
    for m in re.finditer(rf"\({tag}\b", t):
        if depth_tabs is not None:
            line0 = t.rfind("\n", 0, m.start()) + 1
            if t[line0:m.start()] != "\t" * depth_tabs:
                continue
        yield m.start(), walk(t, m.start())[0]


def key(x, y):
    return (round(x, 2), round(y, 2))


def main():
    s = SCH.read_text()

    # --- lib_symbol pin geometry -------------------------------------------
    libpins = {}
    for i, blk in blocks(s, 'symbol "', depth_tabs=2):
        nm = re.match(r'\(symbol "([^"]+)"', blk).group(1)
        if ":" not in nm:
            continue
        pins = []
        for m in re.finditer(
                r'\(pin \w+ \w+\s*\(at (-?[\d.]+) (-?[\d.]+) \d+\)'
                r'[\s\S]*?\(name "([^"]*)"[\s\S]*?\(number "([^"]*)"', blk):
            pins.append((float(m.group(1)), float(m.group(2)),
                         m.group(3), m.group(4)))
        libpins[nm] = pins

    # --- instances ---------------------------------------------------------
    pinat = defaultdict(list)
    for i, blk in blocks(s, "symbol", depth_tabs=1):
        lm = re.search(r'\(lib_id "([^"]+)"\)', blk)
        am = re.search(r"\(at (-?[\d.]+) (-?[\d.]+) (\d+)\)", blk)
        if not lm or not am or lm.group(1) not in libpins:
            continue
        ix, iy, rot = float(am.group(1)), float(am.group(2)), int(am.group(3))
        mir = re.search(r"\(mirror (x|y)\)", blk)
        val = re.search(r'\(property "Value" "([^"]*)"', blk)
        val = val.group(1) if val else "?"
        th = math.radians(rot)
        for px, py, pname, pnum in libpins[lm.group(1)]:
            qx, qy = px, py
            if mir:
                if mir.group(1) == "y":
                    qx = -qx
                else:
                    qy = -qy
            rx = qx * math.cos(th) - qy * math.sin(th)
            ry = qx * math.sin(th) + qy * math.cos(th)
            pinat[key(ix + rx, iy - ry)].append(
                f"{val}.{pnum}[{pname}]")

    # --- wire graph --------------------------------------------------------
    g = defaultdict(set)
    for i, blk in blocks(s, "wire", depth_tabs=2):
        p = re.findall(r"\(xy (-?[\d.]+) (-?[\d.]+)\)", blk)
        if len(p) == 2:
            a = key(float(p[0][0]), float(p[0][1]))
            b = key(float(p[1][0]), float(p[1][1]))
            g[a].add(b)
            g[b].add(a)

    labels = defaultdict(set)
    for tag in ("label", "global_label", "hierarchical_label"):
        for i, blk in blocks(s, tag, depth_tabs=2):
            nm = re.match(rf'\({tag} "([^"]+)"', blk).group(1)
            m = re.search(r"\(at (-?[\d.]+) (-?[\d.]+)", blk)
            labels[key(float(m.group(1)), float(m.group(2)))].add(nm)

    # --- connected components ---------------------------------------------
    nodes = set(g) | set(pinat) | set(labels)
    seen, nets = set(), []
    for n in nodes:
        if n in seen:
            continue
        comp, st = set(), [n]
        seen.add(n)
        while st:
            c = st.pop()
            comp.add(c)
            for m in g[c]:
                if m not in seen:
                    seen.add(m)
                    st.append(m)
        nm = sorted({l for c in comp for l in labels.get(c, ())})
        pins = sorted({p for c in comp for p in pinat.get(c, ())})
        if pins or nm:
            nets.append((nm, pins, comp))

    want = set(sys.argv[1:])
    for nm, pins, comp in sorted(nets, key=lambda x: (x[0] or ["~"])[0]):
        label = "/".join(nm) if nm else "<unnamed>"
        if want and not (want & set(nm)):
            continue
        print(f"{label}  ({len(pins)} pin(s))")
        for p in pins:
            print(f"      {p}")
        if len(nm) > 1:
            print(f"      !! MULTIPLE LABELS ON ONE NET: {nm}")
        if not pins:
            print("      !! label with no pin (dangling)")


if __name__ == "__main__":
    main()
