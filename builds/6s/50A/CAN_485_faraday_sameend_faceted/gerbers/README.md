# Gerbers — 6S / 50A / CAN-FD + RS-485 / Faraday / Faceted

**Empty by design.** There are no board files yet, let alone fabrication
output. This build is partitioned, not placed — see [`../README.md`](../README.md).

Two panels will eventually be fabricated separately. Before either can be:

1. **Placement** — no parts are placed (`TODO.md` 16.5). The FET bridge must
   go from 3x2 (26.96 mm across) to 2x3 to fit the 23.98 mm strip.
2. **`SH1` width** — 22.75 mm against a 23.98 mm strip leaves 0.6 mm per
   edge, which is not a workable margin (`TODO.md` 16.4e).
3. **Stackup** — still undefined (`TODO.md` 15.2).
4. **Interconnect part** — no connector, busbar or flex selected.
5. **Host envelope** — unconfirmed (`TODO.md` 16.3).

Generate with KiCad **9.0.2** only.
