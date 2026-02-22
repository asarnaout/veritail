### Exhaust and Emissions — Scoring Guidance

This query involves exhaust hardware and/or emissions-control components.

**Hard constraints:**

- **Emissions legality (when specified)**:
  - If the query says CARB, California, or 50-state legal, the result must explicitly indicate CARB legality (commonly via a CARB Executive Order / EO reference).
  - "49-state legal" is not a match for a CARB/California query.
- **CARB converter application specificity**:
  - CARB-legal aftermarket catalytic converters are approved for specific vehicle applications. Treat "CARB EO present" as necessary but not sufficient: results should also be for the correct make/class/model-year range when the query is vehicle-specific.
  - When a product exposes label details, look for: EO number + converter part number + production date markings.
- **Direct-fit vs universal catalytic converters**:
  - Direct-fit converters are application-specific and typically match the OE connector/flange geometry.
  - Universal converters require welding/fabrication.
  Enforce direct-fit vs universal intent based on query wording.
- **Exhaust configuration constraints**: Pipe diameter, inlet/outlet orientation, and sensor port (O2 bung) locations are application-specific. If the query specifies any of these, treat mismatch as a disqualifier.
- **Upstream vs downstream emissions hardware scope**:
  - Catalytic converter is not an oxygen sensor.
  - Muffler/resonator is not a catalytic converter.
  Mixing these categories is a critical error.

**Significant penalties:**

- Mismatching "front" vs "rear" converter on multi-cat systems when the query is explicit.
- Returning "test pipe" or off-road-only parts for a street-legal/certified query.

**Common disqualifiers:**

- Returning a universal muffler for an OEM-direct-fit muffler query (unless the query explicitly asks for universal size).
- Returning emissions defeat devices or "O2 simulator" products for legality-focused queries.

**Terminology**:
- cat = catalytic converter
- EO = Executive Order (emissions exemption documentation in some contexts)
