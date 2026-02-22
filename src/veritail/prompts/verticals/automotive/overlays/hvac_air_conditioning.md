### HVAC and Air Conditioning — Scoring Guidance

This query involves automotive HVAC / air conditioning parts or refrigerants.

**Hard constraints:**

- **Refrigerant type**: R-134a vs R-1234yf is a hard boundary. If the query specifies one, results for the other are wrong.
- **Unique service fittings / compatibility**:
  - Refrigerant systems use different service fittings/quick couplers to reduce the risk of cross-contamination.
  - If the query specifies a refrigerant system type (R-134a vs R-1234yf), require matching fittings/compatibility claims in service tools/hoses/adapters.
- **Component category matters**:
  - compressor ≠ condenser ≠ evaporator ≠ accumulator/drier ≠ expansion valve/orifice tube
  Do not treat adjacent components as substitutes.
- **Compressor oil type (when specified)**: PAG vs POE vs other specified oils are not interchangeable when explicitly requested (especially in hybrid/electric compressor contexts).

**Significant penalties:**

- "Universal" hoses or fittings that require custom fabrication when the query implies an OE-direct-fit replacement.
- Returning stop-leak products for a refrigerant query unless explicitly asked.

**Common disqualifiers:**

- Returning a refrigerant can for a mechanical component query and vice versa unless the query explicitly asks for both.
