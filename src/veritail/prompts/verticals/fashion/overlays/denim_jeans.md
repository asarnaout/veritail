### Denim and Jeans — Scoring Guidance

This query is about denim garments, especially jeans (and sometimes denim jackets/skirts when explicitly requested).

**Critical distinctions to enforce:**

- **Raw/dry denim vs washed denim**: "Raw", "dry", or "unwashed" denim refers to denim that has not been pre-washed/processed. Washed, heavily distressed, or "pre-faded" jeans are poor matches for raw denim queries.
- **Selvedge denim is about how the fabric is woven**: "Selvedge/selvage" indicates a self-finished edge from shuttle-loom weaving. Selvedge is not synonymous with raw; enforce the exact term that the shopper used.
- **Sanforized vs unsanforized (shrink-to-fit) matters**: If the query signals "shrink-to-fit" or unsanforized denim, expect shrink after wash; treat standard pre-shrunk denim as a mismatch when the shopper explicitly wants shrink-to-fit behavior.
- **Denim weight ("oz") is not decorative**: Ounce weight refers to fabric weight; when specified (e.g., 12oz, 16oz), treat it as a quality/feel constraint.
- **Size notation is often waist × inseam**: Queries like "W32 L34" or "32x34" are usually waist (inches) and inseam (inches). Treat mismatched inseam as a meaningful relevance failure for shoppers who care about length.

**Terminology / jargon to interpret correctly:**

- "Rigid" denim typically means little/no stretch; "stretch" implies elastane and a softer fit tolerance.
- "Rise" cues where the waistband sits; "low/mid/high rise" are meaningful fit constraints when specified.
- "Leg opening" / "taper" matters for fits like straight vs slim vs skinny vs bootcut vs wide-leg; do not treat these as interchangeable when the query is explicit.

**Common scoring pitfalls:**

- Treating "black jeans" and "dark wash indigo" as equivalent; wash/color are primary for denim shoppers.
- Returning jeggings or coated pants for a denim query unless the query signals openness.
