#!/usr/bin/env python3
"""Detect accidental shorts in a .kicad_sch: two wire segments that are
collinear and overlap in range, but belong to electrically different nets.

This class of bug does not show up in a kiutils round-trip or a plain
`kicad-cli sch export svg/netlist` -- both happily load/export a file with
overlapping-but-differently-intended wires, since nothing there evaluates
connectivity the way ERC does. Real KiCad's ERC (`kicad-cli sch erc`,
unavailable in this environment -- see kicad/README.md) reads overlapping
collinear segments as a single electrically-connected net, i.e. a short,
and reports it as a pin_to_pin violation. This script reproduces that
specific check locally so routing bugs can be caught before pushing.

Usage:
    python3 check_shorts.py path/to/project.kicad_sch
Exit code is 1 if any conflict is found, 0 otherwise.
"""

import sys

from kiutils.schematic import Schematic

parent = {}


def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb


def pt(p):
    return (round(p.X, 3), round(p.Y, 3))


def seg_key(a, b):
    if a[0] == b[0]:
        return ("V", a[0], min(a[1], b[1]), max(a[1], b[1]))
    if a[1] == b[1]:
        return ("H", a[1], min(a[0], b[0]), max(a[0], b[0]))
    return ("D", a, b)  # diagonal -- shouldn't happen, all routing is axis-aligned


def overlap_1d(lo1, hi1, lo2, hi2):
    # Strict: sharing a single point is fine (that's a valid L-bend corner).
    return max(lo1, lo2) < min(hi1, hi2)


def main(path):
    s = Schematic.from_file(path)

    segments = []
    for w in s.graphicalItems:
        pts = [pt(p) for p in w.points]
        for i in range(len(pts) - 1):
            union(pts[i], pts[i + 1])
            segments.append((pts[i], pts[i + 1]))

    label_at = {}
    for lbl in s.globalLabels:
        p = pt(lbl.position)
        label_at.setdefault(find(p), set()).add(lbl.text)

    net_of = {root: "|".join(sorted(texts)) for root, texts in label_at.items()}

    def net_id(p):
        return net_of.get(find(p), f"anon:{find(p)}")

    keyed = [(seg_key(a, b), net_id(a), net_id(b)) for a, b in segments]

    conflicts = []
    n = len(keyed)
    for i in range(n):
        k1, na1, nb1 = keyed[i]
        if k1[0] == "D":
            continue
        for j in range(i + 1, n):
            k2, na2, nb2 = keyed[j]
            if k2[0] == "D" or k1[0] != k2[0] or k1[1] != k2[1]:
                continue
            if overlap_1d(k1[2], k1[3], k2[2], k2[3]):
                nets1, nets2 = {na1, nb1}, {na2, nb2}
                if nets1 - nets2 or nets2 - nets1:
                    conflicts.append((k1, k2, nets1, nets2))

    print(f"segments: {len(segments)}")
    print(
        f"collinear-overlap conflicts between differently-identified nets: {len(conflicts)}"
    )
    for k1, k2, n1, n2 in conflicts:
        print(" ", k1, "vs", k2, "nets:", n1, n2)
    return 1 if conflicts else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} path/to/project.kicad_sch", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
