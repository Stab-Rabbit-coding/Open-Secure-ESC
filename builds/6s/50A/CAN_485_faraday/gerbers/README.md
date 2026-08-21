# gerbers/ — 6S / 50A / CAN-FD+RS-485 / Faraday

Still empty, and deliberately so.

## What changed 2026-08-15

Two of the three conditions this folder was waiting on are now met:
`../kicad/open_secure_esc_6s_50a_can485_faraday.kicad_pcb` **has** its netlist
(44 footprints, 73 nets, every pad netted from the schematic), and it **is**
routed, with poured planes on all four layers. The schematic is ERC-clean at
0 errors. See `../kicad/README.md`.

## Why gerbers are still not generated

**Conductor sizing has not been verified.** IPC-2152 [46] is the governing
standard for current-carrying capacity; it is paywalled, and only its Table of
Contents has been read, so under `AGENTS.md` §1.3 no width on this board may be
presented as a computed value. `VM` and `GND` are poured planes and the three
phase nets now have their own pours over each half-bridge, but the run from
each phase pour out to the motor terminal is still routed track, and that is
load-bearing at 50 A. Exporting fab output now would ship a board whose
headline rating — 50 A — is the one number nobody has checked.

Also still open, per `TODO.md` §12.4:

- **No real power connector has been selected.** `J4` and `J5` are KiCad
  6 mm² solder-wire pads, chosen because the previous `J4` was a 2.54 mm pin
  header. No part number, no verified current rating.
- **The BOM is not locked.** Every line in `../README.md` is still
  `Candidate` per `AGENTS.md` §5, and three design questions are genuinely
  unresolved: the CAN-FD and RS-485 transceiver variants, and
  DRV8353S-vs-INA240 current-sense sourcing. The transceiver choice also sets
  the isolation barrier width, which the layout currently sizes only to clear
  the isolated pin rows.
- **Placement has not had a human review.** It is DRC-clean and respects
  REFERENCES.md [21] §11.1's gate-loop and bulk-capacitor constraints, but
  thermal and manufacturability review of the power stage has not been done.

Datasheet verification and BOM lock-in are two different gates
(`../README.md`, "Open items"). Every part here has a verified datasheet; none
is locked.

## When those close

Export the standard fab set — `*.gbr` per copper/mask/silk/edge layer, `*.drl`
drill files, and a `*.gbrjob` — with `kicad-cli pcb export gerbers` and
`... export drill`, or `Plot` in the PCB Editor. Then update this file with the
KiCad version and the exact export settings used, per `AGENTS.md` §4: record
*why* those settings, not just *what* was exported. Copper weight in
particular is a decision that follows from the IPC-2152 work above and must be
stated here, not left to the fab's default.

Tracked in `TODO.md` §12.4.k / §12.4.l (blocking), then §10.2 (BOM
finalization) → §10.3 (manufacturing/fab release).
