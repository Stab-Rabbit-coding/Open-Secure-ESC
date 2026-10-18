# Concepts

Shared domain vocabulary for this project — entities, named processes, and status concepts with project-specific meaning. Seeded with core domain vocabulary, then accretes as ce-compound and ce-compound-refresh process learnings; direct edits are fine. Glossary only, not a spec or catch-all.

## Decision Matrix and Builds

### Decision Matrix

The set of independent choices that together fully specify one Electronic Speed Controller (ESC) design: voltage, amperage, motor type, shaft sensor, communication protocol, control loop type, EMI hardening tier, wire egress arrangement, form factor, and ingress/environmental protection tier. Each choice is an Axis. The matrix exists so that resolving all axes together, before any schematic or layout work starts, surfaces incompatibilities between axes early — some axis combinations share almost no Bill of Materials with others and must be resolved as a joint decision, not one axis at a time.

### Axis

One independent dimension of the Decision Matrix (for example, Protocol, or Form Factor). An axis has a fixed set of named values a Build can select. Two axes are said to be *coupled* when the choice on one constrains or changes the correct choice on the other (motor type and shaft sensor are coupled this way: the sensor choice changes the power-stage topology, not just a peripheral).

### Build

One fully-resolved point through the Decision Matrix: a specific combination of axis values, realized as its own schematic, PCB, and bill of materials. A Build is not a configuration flag on a shared design — different builds can differ in power-stage topology, part count, and board shape entirely.

### Variant

A Build that shares its core axis resolution (voltage, amperage, protocol, motor) with a sibling Build but differs in one or more of the remaining axes (commonly Wire Egress or Form Factor). Variants are derived from a base Build rather than designed independently, so they share verified schematic content and diverge only where the differing axis requires it.

## Isolation and Creepage

### Isolation Barrier

The galvanic separation between the control/communication domain (MCU, secure element, low-voltage logic) and the battery/motor domain (pack voltage, phase currents). A design may carry more than one isolation barrier (for example, one per communication protocol); each barrier is a distinct safety boundary, not a shared one, unless a design decision explicitly merges them.

### Working Voltage

The maximum voltage an isolation barrier is rated to sustain continuously across its two sides. This is the number that determines how much Creepage and Clearance the barrier needs — not the part's package size, and not the actual bus voltage in use, which may be far lower than what the barrier is rated for.

### Insulation Class

The safety category an isolation barrier is certified to: Basic (a single layer of protection) or Reinforced (protection equivalent to two independent basic layers, required where a single-fault failure of the barrier would be hazardous). Reinforced insulation requires more Creepage and Clearance than Basic insulation at the same Working Voltage.

### Creepage

The shortest path along an insulating surface between two points at different Working Voltage. Creepage requirements are read from a standards table keyed by working voltage, insulation class, and pollution degree — they do not shrink because a part's physical package is smaller, and they do not divide when one isolated function is split across several physical parts (each part or gap that itself straddles the barrier needs the same full creepage independently).

### Clearance

The shortest path through air between two points at different Working Voltage, distinct from Creepage (which follows a surface). Both are typically specified together for a given working voltage and insulation class, but a design can fail one while satisfying the other.

### Widest Non-Isolated Part

The single largest component (usually the MCU) that must physically sit inboard of the isolated rows on one board cross-section. Its width is frequently the binding constraint on a Build's minimum board width — not the isolation barrier's own footprint — because that part is what has to fit in the space left after both isolated rows and their creepage margins are reserved. Shrinking a tight board is, more often than not, a matter of shrinking this part's package rather than the isolator's.

## Board Geometry

### Form Factor

The Axis describing the board's physical shape and how it mounts. Values include a flat rigid board (the default) and folded variants that conform to a curved host bore.

### Facet

One flat panel of a folded (non-flat) Form Factor board — a chord of the curved bore it is designed to sit inside. A faceted board has more than one facet joined at fold lines; components and isolated rows may be deliberately assigned to different facets so that a width constraint on one facet does not apply to the whole board.

## Trust and Security

### Secure Element

A discrete hardware component providing asymmetric cryptographic identity (device authentication, key agreement) via a certified security certification path. Distinct from a Trusted Platform Module (TPM): this project's secure element supplies the asymmetric layer a symmetric-only cryptographic engine structurally lacks, rather than acting as a general-purpose trusted platform root.

### Message Authentication Module

The on-chip symmetric cryptographic engine (AES) responsible for the per-frame authentication hot path — the high-frequency, low-latency integrity check applied to ongoing communication traffic, as opposed to the one-time or occasional asymmetric operations the Secure Element handles.

## Documentation Discipline

### Citation Tag

A stable numbered reference (`[n]`) into the project's bibliography, used consistently at every point a source is cited — in code comments, schematic notes, or documentation — and never renumbered or reused for a different source once assigned, even if the original claim is later superseded.

### UNVERIFIED Marker

An explicit status marker applied to any technical claim, specification, or design decision that cannot yet be traced to a primary, authoritative source. Content carrying this marker must not be treated as settled or acted upon as fact until the marker is replaced by a real citation — it is a standing gap, not a placeholder that quietly implies "probably fine."

### Engineering Default

A design value or component choice recorded as a judgment call rather than as a value derived from a citable requirement or standard. An Engineering Default is explicitly labeled as such at its point of use, distinguishing it from a value that has been verified against an authoritative source — this distinction is what allows the two to coexist in the same design without the judgment call being mistaken for a verified fact later.

## Flagged ambiguities

- "Secure element" and "TPM" had been used loosely; this project settled on secure element as the correct term for its root-of-trust hardware, since it explicitly does not implement the TPM platform specification.
