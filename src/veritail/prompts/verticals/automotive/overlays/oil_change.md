### Oil Change (Engine Oil + Oil Filter) — Scoring Guidance

This query involves engine oil, engine oil filters, or oil-change bundles/kits.

**Hard constraints (when present in the query):**

- **Viscosity grade is not optional**: If the query specifies a viscosity (e.g., 0W-20, 5W-30), results must match exactly.
- **Specification / approval codes are requirements**: If the query specifies an API category, ILSAC GF-6A/GF-6B, or an OEM approval (e.g., dexos), the product must explicitly claim that approval. Do not assume equivalency.
  - **GF-6B is a special case**: GF-6B applies only to SAE 0W-16 oils and is not a generic synonym for GF-6A.
- **Packaging and quantity**: 1 quart, 5-quart jug, gallon, case packs, and "oil change kit" are different buying intents. If the query asks for a kit/bundle, a result that includes only oil (or only a filter) is incomplete.

**Oil filter-specific fitment (treat as hard when the query is an oil filter):**

- **Exact filter part number dominates** (OEM or aftermarket). Close numbers often indicate different gaskets, bypass settings, or thread specs.
- **Spin-on vs cartridge**: These are different physical formats. If the query calls for a cartridge style (filter element + cap O-ring), a spin-on canister is wrong and vice versa.
- **Thread & gasket compatibility**: When the result provides thread size and gasket diameter, they must match the intended application. A mismatch can cause leaks, stripped threads, or no seal.
- **Anti-drainback valve (ADBV)**:
  - The ADBV prevents oil from draining out of the filter when the engine is off in many designs (often important when filters mount sideways or upside-down).
  - Treat ADBV as a hard constraint only when the query explicitly asks for it (or asks for an OE filter known for that feature). Otherwise, do not speculate.
- **Bypass valve**:
  - The bypass valve exists to protect the engine from oil starvation if the filter media is restricted.
  - Bypass can open when oil is cold/thick or the filter is clogged/restricted.
  - Treat bypass specification as a hard constraint only when the query explicitly calls it out (PSI) or when a specific OE filter spec is requested.

**Common category pitfalls (disqualify):**

- Returning oil additives or stop-leak products for a motor oil query (unless the query explicitly asks for additives).
- Returning transmission fluid, gear oil, or power steering fluid for an engine oil query.

**Terminology** (do not penalize synonym usage):
- "motor oil" = engine oil
- "full synthetic" vs "synthetic blend" vs "conventional" are distinct and should be enforced only when specified.
