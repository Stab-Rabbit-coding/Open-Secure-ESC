# Gerbers — 6S / 50A / CAN-FD + RS-485 / Faraday / Same-end egress

**Empty by design.** No fabrication output has been generated for this build.

Three gates stand before gerbers are meaningful, all recorded in
[`../README.md`](../README.md):

1. **No stackup** — layer count, copper weight, dielectric heights and
   surface finish are unspecified (`TODO.md` 15.2). Gerbers without a stackup
   cannot be quoted or built.
2. **VM distribution unresolved** — `J5A` (VM) and `J5B` (GND) are
   unconnected at the new terminal end, pending the `TODO.md` 12.5.ae
   rule-area decision.
3. **Routing incomplete** — 150 unconnected items, inherited from the parent
   build.

Generate with KiCad **9.0.2** only. The board file is `version 20241229` /
`generator_version "9.0"`; running KiCad 10 against it would advance the
format.
