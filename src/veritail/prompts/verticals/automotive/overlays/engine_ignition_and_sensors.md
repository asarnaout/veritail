### Engine Ignition and Sensors — Scoring Guidance

This query involves spark plugs, ignition coils, engine management sensors, oxygen/air-fuel sensors, or related engine control components.

**Hard constraints:**

- **Exact part numbers dominate**: Sensors and ignition components are connector- and calibration-sensitive. If a query includes an OEM or aftermarket part number, enforce exact match or an explicit cross-reference.
- **Oxygen sensor position notation is not optional**:
  - **Upstream vs downstream**: Upstream is before the catalyst; downstream is after the catalyst in usual naming.
  - **Sensor 1 vs sensor 2**: Sensor 1 is typically upstream; sensor 2 is typically downstream.
  - **Bank 1 vs bank 2**: Bank 1 refers to the cylinder bank containing cylinder #1; bank 2 is the opposite bank.
  If the query specifies bank/sensor position (e.g., Bank 1 Sensor 2), returning a different position is wrong.
- **A/F ratio (wideband) vs conventional O2**:
  - Some vehicles use wideband air/fuel ratio sensors (often in the upstream position). Do not assume a conventional narrowband O2 sensor is interchangeable with an A/F ratio sensor when the query is explicit.
- **Spark plug specification (when specified)**:
  - **Heat range**: Heat range numbers are manufacturer-specific but meaningful. Enforce if the query specifies heat range or the exact plug part number.
  - **Gap**: If the query specifies a gap, treat it as a hard requirement; otherwise do not invent a gap spec and do not penalize "pre-gapped" listings.
- **Ignition architecture**: Coil-on-plug (COP) boots/individual coils are different from multi-output coil packs. Match the requested part class.

**Significant penalties:**

- Returning "universal" sensors that require splicing when the query implies a direct-fit plug-and-play sensor (vehicle-specific intent).
- Returning a different connector style or harness length when the query explicitly specifies it.

**Common disqualifiers:**

- Returning "downstream" sensor results for "upstream" queries (or vice versa).
- Returning unrelated exhaust parts (catalytic converters, mufflers) for a sensor query unless the query is broad and the result explicitly matches that intent.

**Terminology**:
- COP = coil-on-plug
- A/F sensor = air-fuel ratio sensor (often wideband)
- B1S1/B1S2 shorthand = Bank 1 Sensor 1 / Bank 1 Sensor 2
