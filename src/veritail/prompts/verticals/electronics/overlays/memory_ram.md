### Memory (RAM) — Scoring Guidance

This query involves system memory (RAM).

**Critical distinctions to enforce:**

- **DDR generation is non-negotiable**: DDR4 and DDR5 are not interchangeable. If the query specifies DDR4 or DDR5, treat it as a hard gate.

- **Form factor matters**: DIMM (desktop) and SO-DIMM (laptop/mini PC) are different physical modules. If the query specifies SO-DIMM, do not return desktop DIMMs and vice versa.

- **ECC / registered vs unbuffered**: If the query asks for ECC memory, enforce ECC. If it asks for RDIMM/registered or UDIMM/unbuffered, enforce that distinction—server-class RDIMMs are not valid substitutes for consumer UDIMMs.

- **Kit composition is part of the spec**: "2×16GB" is not the same as "1×32GB" for buyers optimizing dual-channel behavior. If the query specifies sticks count, treat it as a requirement.

- **Overclock profiles are platform-specific**: If the query references Intel XMP or AMD EXPO, treat it as a real compatibility signal. Do not assume a kit tuned for one platform is equally appropriate for the other when the query is explicit.

- **Speed units and naming**: Listings may mix MHz/MT/s marketing language. Treat requested speed (e.g., DDR5-6000) as a hard constraint when specified, especially for performance-oriented builds.
