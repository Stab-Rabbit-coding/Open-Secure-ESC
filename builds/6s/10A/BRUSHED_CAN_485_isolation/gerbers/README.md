# gerbers/ — 6S / 10A / BRUSHED / CAN-FD+RS-485 / Isolation

Empty, and deliberately so. This build is at **schematic + BOM readiness**
(`../kicad/README.md`): the schematic is ERC-clean and its netlist has been
verified, but no PCB has been placed or routed. Gerbers are generated only
after the layout follow-up (`TODO.md` 18.6) closes:

1. Buck inductors and catch diodes selected against the 4 mm height budget
   and their datasheets held locally (`TODO.md` 18.3).
2. Placement inside the 42.9 × 36.5 mm host envelope with the isolated rows
   on the long axis and the primary side clear of the barrier
   (`docs/tools/isolation_envelope.py` result in `../kicad/README.md`).
3. Conductor sizing for the 3 A branch / 2.9 A motor stall
   (`docs/tools/conductor_sizing.py`; IPC-2152 [46] is still paywalled, so no
   width may be presented as computed until it is read).
4. DRC clean at `--severity-error`, including the isolation-barrier via rule
   in the `.kicad_dru` and its negative control.
