# Design Decision: Brushed ESC Variant — Physical and Firmware Integration

Status: DRAFT (authoring complete)
Applies to: Brushed-ESC build variants (new branch of builds)
Governing rules: AGENTS.md §1–§3 — verify all part claims against primary datasheets; mark `UNVERIFIED` when not available.

Summary

- Provide a design decision record describing how the brushed-ESC variant differs from brushless designs at the schematic, BOM, PCB, and firmware levels, and document safety/protection specifics.

Why support brushed motors

- Brushed motors remain common in many industrial and hobbyist use cases; supporting a dedicated H-bridge variant increases product applicability. Brushed variant simplifies commutation logic but requires careful H-bridge and protection design.

Electrical architecture (high level)

- Replace 3-phase inverter drive + gate-driver stage with a single H-bridge (half-bridge pair) sized for target amperage tier.
- Provide current sensing, dead-time control, and flyback/clamping protection appropriate for inductive motor loads and regenerative events.
- Include direction control signal and PWM input (single channel + direction) in firmware mapping.

Power-stage components & protection (to be VERIFIED)

- H-bridge MOSFETs or integrated H-bridge ICs sized per amperage tier (candidate parts tracked in TODO; all parts UNVERIFIED until datasheets added).
- Freewheeling / flyback diodes or synchronous MOSFET conduction strategy: design must handle regenerative currents; include regenerative path to bus or clamp/regulator and report to firmware.
- RC snubbers, TVS for transients, and precharge/soft-start for large motor inductance loads.
- Current sensing: shunt + amplifier or integrated current-sense filter placement to provide overcurrent detection and closed-loop current limit.

Schematic & PCB layout notes

- H-bridge placed close to power connectors; copper pour for heat dissipation.
- Thermal considerations: footprint for thermal vias, heatpad and heatsink provision.
- Keep sensitive analog/logic routing (speed-sensor, ADC, encoder lines) physically separated and shielded from switching nodes and gate traces.
- Provide component footprints and mechanical constraints in `builds/<voltage>/<amperage>/BRUSHED_<variant>/kicad/`.

Firmware implications

- Add brushed control code path:

  - PWM + direction mapping
  - Closed-loop speed control via speed sensor (see design-speed-sensor-integration.md)
  - Current-limiting and regenerative handling logic
  - Dead-time configuration and MOSFET gate timing safe defaults

- Define test vectors and unit tests for:

  - Direction change safety (ensure motor spins down or safe transition)
  - Short-circuit and overcurrent cutoff behavior
  - Regeneration absorption/limiting

Safety & failure modes

- Define safe-state on faults (fail-safe vs fail-operational decision required; reference to `TODO.md` 12.3 and project safety requirements).
- On MOSFET cross-conduction detection: hard disable PWM and assert fault.
- On current-sense overthreshold: limit duty cycle, then trip if persists.

Acceptance checklist (before layout/fab)

- H-bridge ERC clean
- Current-sense integrated and validated in schematic
- Dead-time validated in simulation/tooling
- Thermal analysis for MOSFETs and heatsinking
- Firmware test harness for brushed flow
- BOM lines for H-bridge parts present and each has a `REFERENCES.md` entry (IEEE format)

Testing & verification

- Bench test: H-bridge switching, measured dead-time and shoot-through current, regen absorption behavior, thermal soak tests.
- HIL test: closed-loop speed under disturbance and sensor-failure scenarios.

References & verification

- All H-bridge device claims and power-handling assertions must carry primary datasheet citations in `REFERENCES.md` before merging. Any design value not verified is to be annotated `UNVERIFIED — needs primary source`.

Authored-by: repo maintainers; see AGENTS.md for contributor rules.
