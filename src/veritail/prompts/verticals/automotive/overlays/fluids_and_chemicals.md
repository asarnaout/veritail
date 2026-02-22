### Fluids and Chemicals (Non-Engine-Oil) — Scoring Guidance

This query involves vehicle fluids, chemicals, or service consumables other than engine oil/oil filters.

**Hard constraints (mismatches are disqualifiers):**

- **Exact fluid specification is the product**: If the query names a fluid spec (ATF+4, Dexron VI, Mercon LV, Toyota WS, CVT fluid, gear oil 75W-90, DOT 4, etc.), results must explicitly meet that same spec. Do not assume "multi-vehicle" fluids are compatible unless they explicitly list the requested spec.
- **CVT / DCT / manual vs conventional ATF**: CVT fluids and DCT fluids are not interchangeable with standard ATF. Confusing these is a hard failure.
- **Gear oil vs engine oil scales**: Gear oils (SAE J306, e.g., 75W-90) and engine oils (SAE J300, e.g., 5W-30) use different grade systems. Do not treat them as equivalent based on the numbers.
- **API GL ratings and friction modifiers (when specified)**:
  - If the query specifies API GL-4 vs GL-5 (or limited-slip / LS friction modifier), treat that as a hard requirement. Do not silently substitute.
- **Coolant must match the correct chemistry/spec**:
  - Coolant color is not a reliable compatibility guarantee.
  - If the query specifies an OEM spec (e.g., Ford WSS-...), a technology family (IAT/OAT/HOAT), or an OE brand family, results must explicitly match.
  - Concentrate vs 50/50 pre-diluted is a format constraint when specified.
- **Brake fluid DOT class is safety-critical**:
  - DOT 3 / DOT 4 / DOT 5.1 are glycol-based families; DOT 5 is silicone-based.
  - Do not treat DOT 5 as mixable/interchangeable with DOT 3/4/5.1.
  - If the query specifies DOT class, it is a hard requirement.

**Significant penalties:**

- **Generic / "universal" claims without the requested spec**: A generic "multi-vehicle ATF" that does not explicitly list the required spec is a poor match for a spec-request query.
- **Wrong intent**: Stop-leak, flush chemicals, and additives are not substitutes for the actual required fluid unless the query explicitly asks for them.

**Terminology notes (useful for classification and tiebreaking):**
- ATF = automatic transmission fluid
- "diff fluid" = differential gear oil (often 75W-90/75W-140, but follow the exact spec in query)
- "antifreeze" = coolant (still must match OEM spec, not just color)
