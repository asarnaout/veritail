### Hydraulic Fittings and Hose — Scoring Guidance

This query involves hydraulic fittings, adapters, hose, or couplings used in hydraulic power systems operating at high pressure (typically 1,000-10,000 PSI).

**Critical distinctions to enforce:**

- **Fitting standard confusion is the most dangerous trap in industrial MRO**: The following fitting types share thread sizes on multiple dash sizes, meaning they will physically thread together but create leak paths or catastrophic failures at hydraulic pressures:
  * JIC 37° flare (SAE J514) — metal-to-metal 37° cone seal, UNF threads
  * SAE 45° flare (SAE J512) — 45° cone seal, same UNF threads as JIC on dash sizes -02 through -10. VISUALLY SIMILAR to JIC but 8° seat difference guarantees a leak.
  * O-Ring Boss / ORB (SAE J1926) — straight UNF thread with o-ring at base. Same threads as JIC but completely different sealing mechanism.
  * O-Ring Face Seal / ORFS (SAE J1453) — flat face with o-ring groove, UNF thread. Highest leak-free reliability.
  * NPT/NPTF — tapered 60° pipe thread, seals by thread deformation. PTFE tape is used on NPT but must NEVER be used on o-ring fittings.
  * BSPP (ISO 228) — parallel 55° Whitworth thread, seals with o-ring or bonded washer. NOT compatible with NPT despite both being "pipe thread."
  * BSPT (ISO 7) — tapered 55° Whitworth thread. NOT compatible with NPT (different thread angle: 55° vs 60°).
  If the query specifies or implies a fitting standard (JIC, SAE 45°, ORFS, ORB, NPT, BSP), treat it as an absolute hard constraint.
- **Dash size means different things in different contexts**: For hoses, dash size = ID in sixteenths of an inch (-4 = 1/4" ID, -8 = 1/2" ID). For tube fittings, dash size = OD in sixteenths (-4 = 1/4" OD). For fitting port threads, dash maps to a UNF thread that follows neither rule simply. An LLM must not conflate these three meanings.
- **Hose construction determines pressure rating**: SAE 100R1 (1-wire braid) handles ~2,750 PSI; R2 (2-wire braid) handles ~5,000 PSI; R12 (4-spiral wire) handles ~4,000 PSI constant. The standard burst-to-working pressure safety factor is 4:1. EN 853 1SN/2SN are European equivalents of R1/R2 but are NOT identical specs. If the query specifies an SAE or EN hose series, match it.
- **Quick-disconnect body size and type**: ISO A, ISO B, flat-face, and various OEM-specific styles (Pioneer, Parker 60/71 series) are NOT cross-compatible. If a brand or series is specified, treat as hard.

**Terminology**:
- JIC = Joint Industry Council (37° flare standard)
- ORFS = O-Ring Face Seal
- ORB = O-Ring Boss
- dash size = "-4", "-6", "-8", "-10", "-12", "-16" (size designation)
- SAE 45° = inverted flare (automotive/refrigeration, NOT hydraulic)
