# Design Decision: Motor Speed Sensor — Physical Integration

Status: DRAFT (authoring complete)
Applies to: All build variants (Brushed + Brushless)
Governing rules: AGENTS.md §1–§3 — every technical claim that requires a primary source must be verified and added to REFERENCES.md; UNVERIFIED markers applied where the repo lacks the primary source.

Summary
- Requirement: every ESC variant MUST provide a motor-speed input interface (Hall / optical encoder / analog tachometer) as a first-class item in BOM and schematic. This doc defines electrical integration, connector choices, front-end protection, PCB routing and layout notes, failure modes, and test points.

Rationale
- Closed-loop speed control and safe transitions between sensorless and sensor-based operation require an explicit per-vehicle sensor input. For high-safety systems, hardware-level detection and robust wiring reduce failure modes and improve testability.

Interfaces supported (prioritized)
1. Hall-effect (digital)
   - Typical use: 3-wire Hall (Vcc / GND / open-collector pulse) or single digital pulse per revolution.
   - MCU side: digital input with interrupt; optional Schmitt/differential input if using differential buffer.
   - Electrical front-end:
     - Series resistor (e.g., 1–10 kΩ) + pull-up to 3.3 V on MCU side (value: UNVERIFIED — choose per sensor datasheet).
     - Optional small RC to filter EMI on signal (time constant chosen to preserve maximum RPM edge frequency).
     - ESD protection (TVS diode to 3.3 V/GND) and clamping diodes where appropriate.
   - Connector: 3-pin keyed JST shrouded (VCC, GND, SIG) on board; add testpoint for SIG.

2. Quadrature encoder (optical / magnetic)
   - Typical use: two channels A/B ±index; TTL-level/RS422-style differential outputs for long cable runs.
   - MCU side: hardware quadrature timer input(s) where available; else ISR-based decode with minimal jitter.
   - Electrical front-end:
     - If sensor outputs are differential (RS422), provide small differential receiver (e.g., comparator/line receiver) or use MCU differential-capable inputs.
     - Level-shift circuit when 5 V encoder used (use resistor divider or proper level-shifter IC).
     - EMI filtering and twisted-pair wiring required; common-mode choke optional for long runs.
     - ESD protection and TVS diodes on each channel.
   - Connector: 4–6 pin (A, B, Index, Vcc, Gnd, Shield optional); keyed header recommended.

3. Analog tachometer (voltage proportional to speed)
   - Typical use: legacy analog tach outputs (0–Vpeak).
   - MCU side: routed to an ADC channel, preceded by anti-alias low-pass filter and input protection circuit.
   - Electrical front-end:
     - Input attenuation / offset circuit if signal is bipolar (use op-amp level shift).
     - Anti-alias filter (order and cutoff set to twice expected rotation fundamental; exact values UNVERIFIED until spec).
     - Over-voltage protection clamp and TVS.
     - Sample and hold / averaging in firmware; calibration routine required.
   - Connector: 2–3 pin (SIG, GND, Shield optional).

Connector & mechanical
- Use keyed, shrouded connectors with clear polarity (e.g., JST SH series or Molex MicroLock) sized to mechanical/ambient needs.
- Include shield lug on connector and tie to chassis ground only at a single point as per grounding policy (add to layout checklist per EMI tier).
- Provide a testpoint per sensor signal for bench verification.

Pin assignment & MCU resources
- Reserve:
  - At least 2 GPIO/interrupt-capable pins for Hall/encoder (more for quadrature index).
  - 1 ADC channel for analog tach plus an op-amp if signal conditioning required.
  - Optional spare timer/quadrature hardware channel depending on MCU peripheral count.
- Implementation note: exact pin numbers are UNVERIFIED until `symbols/specs/MSPM0G3518_Q1_PM.json` and primary pinmap are finalized — update when available (Cn).

Protection & EMI
- All sensor inputs receive:
  - Series resistor
  - ESD/TVS clamp sized for automotive/industrial environment (choose per EMI/ESD targets; UNVERIFIED until selected).
  - Common-mode filtering for long runs (differential receiver or choke).
  - Input low-pass filtering where analog sampling is used.
- Layout:
  - Route sensor lines away from high-current power traces and MOSFET switching nodes.
  - Place op-amps and ADC decoupling close to MCU ADC pins.
  - For quadrature/differential signals use controlled-impedance, matched-length pairs where speeds/edge timing require it.

Failure modes & safety
- Detect open, short-to-rail, and stalled sensor conditions in firmware:
  - Hall/encoder: loss of pulses → enter safe fallback (sensorless or reduced-power mode) or to predefined safe-state per safety policy (2.2). Behavior must be defined by system integrator.
  - Analog tach: out-of-range voltage → fault.
- Watchdog and cross-check: compare RPM reported by sensor with motor-modelled RPM (if sensorless estimator exists); on mismatch exceed threshold → fault.
- All failure-handling policies must be recorded and linked to AGENTS.md checklist before merging.

Testing
- Provide bench test vectors:
  - Pulse-rate verification (Hall)
  - Quadrature phase correctness (A leads B vs B leads A)
  - ADC scale/offset calibration (analog)
- Include HIL tests for noise immunity and EMI injection tests.

References & verification
- Trace sensor front-end component choices and filter corner values to component datasheets and EMI standards (add entries to `REFERENCES.md` with IEEE format). Mark values UNVERIFIED until primary-source citations added.

Authored-by: repo maintainers; see AGENTS.md for contributor rules.
