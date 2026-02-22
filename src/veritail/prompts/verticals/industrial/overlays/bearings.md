### Bearings — Scoring Guidance

This query involves bearings — ball, roller, needle, thrust, spherical, mounted units (pillow blocks, flanges), or linear motion bearings.

**Critical distinctions to enforce:**

- **Bearing number decoding**: Standard designations encode type, series, and bore. Example: 6205-2RS-C3 → 6 = deep groove ball, 2 = light width series, 05 = 25mm bore, 2RS = double rubber seal, C3 = increased clearance. The bore code is intuitive for 04+ (multiply by 5: 04=20mm, 05=25mm, 06=30mm), but is irregular below 04: 00=10mm, 01=12mm, 02=15mm, 03=17mm. Treat the complete bearing designation including all suffixes as a single hard-match identifier.
- **Suffix codes change the product fundamentally**:
  * 2RS (rubber contact seal) vs ZZ (metal shield) — 2RS provides better contamination protection but generates more friction/heat. Not interchangeable in high-speed or high-temp applications.
  * C3 (increased radial clearance) vs C0/unmarked (normal clearance) — C3 is required for interference shaft fits or high temperature differentials. Using C3 on a slip fit unnecessarily reduces bearing life. Clearance progression: C2 (reduced) → C0 (normal) → C3 → C4 → C5 (maximum).
  * If the query specifies any suffix, treat it as hard.
- **ABEC tolerance is NOT a quality ladder**: ABEC 1 (= ISO P0) is the standard normal class, not "low quality." ABEC 1 is sufficient for the vast majority of industrial applications. ABEC 5+ is for machine tool spindles and precision instruments. The ABEC scale (1,3,5,7,9) maps to ISO classes that run in the OPPOSITE direction (P0, P6, P5, P4, P2). ABEC controls bore/OD tolerances and runout but does NOT control internal clearance, lubrication, ball grade, noise level, or cage type. Do not treat higher ABEC as universally "better."
- **Mounted bearing designations**: A pillow block is a HOUSING type, not a bearing type. UCP205 = UC205 insert bearing in a P205 pillow block housing. UCF205 = same insert in an F205 four-bolt flange. The insert mounting method (set screw vs eccentric collar) is NOT interchangeable. If the query specifies UCP, UCF, UCFL, UCFC, or similar, the housing type is a hard constraint.
- **Bearing type substitution**: Deep groove ball, angular contact, cylindrical roller, tapered roller, spherical roller, and needle bearings serve fundamentally different load cases (radial, axial, combined, self-aligning). Do not substitute across bearing types even if bore/OD/width match.

**Terminology**:
- pillow block = plummer block (UK term)
- 2RS = 2RSR = DDU = LLU (brand-specific suffix for double rubber seal)
- ZZ = 2Z = DD (brand-specific suffix for double metal shield)
- bearing insert = housed bearing inner unit
