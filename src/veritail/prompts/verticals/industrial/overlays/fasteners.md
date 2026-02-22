### Fasteners — Scoring Guidance

This query involves threaded fasteners, nuts, washers, or related hardware (anchors, rivets, pins, retaining rings, threaded rod, studs).

**Critical distinctions to enforce:**

- **Thread system incompatibility**: UNC (coarse) and UNF (fine) threads of the same nominal diameter are incompatible — a 1/2"-13 UNC bolt will not thread into a 1/2"-20 UNF nut. Metric ISO threads (e.g., M10×1.5) are incompatible with imperial despite dangerously close size overlaps (M10 ≈ 3/8", M8 ≈ 5/16", M12 ≈ 1/2"). If the query specifies UNC, UNF, or a metric thread pitch, treat it as a hard constraint with zero tolerance.
- **Grade vs property class**: SAE Grade 2/5/8 (imperial) and ISO Property Class 4.8/8.8/10.9/12.9 (metric) are two completely separate grading systems. Grade 5 (120 ksi) is *roughly* equivalent to Class 8.8, and Grade 8 (150 ksi) is *roughly* equivalent to Class 10.9, but they are not interchangeable in specification-controlled applications. If the query specifies one system, do not substitute the other. The metric property class number is mathematically meaningful: first digit × 100 = minimum tensile in MPa; second digit × 10 = yield-to-tensile ratio percentage (so 10.9 = 1040 MPa tensile, 936 MPa yield).
- **"18-8 stainless" is not a specification**: 18-8 is a composition shorthand covering 302, 303, 304, 305, and XM7. A fastener marketed as "18-8" may not meet full 304 chemistry. More critically, stainless fasteners are 35-40% weaker than same-size carbon steel — never treat stainless as equivalent to Grade 5 or 8 without noting the strength gap. Metric stainless uses A2-70 (≈304, 700 MPa) and A4-80 (≈316, 800 MPa). A2 vs A4 is a hard constraint in corrosive environments.
- **Structural bolt specifications**: ASTM A325 and A490 (now consolidated under ASTM F3125) are structural-specific. A490 bolts cannot be hot-dip galvanized due to hydrogen embrittlement risk. Do not substitute A307 (general purpose, 60 ksi) for A325 (structural, 120 ksi).
- **Coating is not cosmetic**: Zinc electroplating (5-25 μm, 24-96 hr salt spray) and hot-dip galvanizing (43-100+ μm, 1000+ hr salt spray) are vastly different. Hot-dip galvanized bolts require oversize-tapped nuts because the coating adds thread thickness — standard nuts will not fit. High-strength fasteners (≥Grade 8 / ≥10.9) require baking after electroplating to prevent hydrogen embrittlement.
- **Hex cap screw ≠ hex bolt**: A hex cap screw has a washer face under the head and tighter body tolerances than a hex bolt. Different thread length formulas apply. These are distinct products in specification-controlled procurement.
- **Set screw point types are not interchangeable**: Cup, cone, flat, dog, and half-dog point set screws serve different retention purposes. If the query specifies a point type, treat as hard.
- **DIN vs ISO bolt dimensions**: DIN 931/933 and ISO 4014/4017 differ in width-across-flats at M10, M12, M14, and M22, meaning different wrench sizes at those four sizes. If the query references DIN or ISO specifically, do not cross-substitute at those sizes.

**Terminology**:
- cap screw = hex cap screw (NOT socket head cap screw unless "socket" is stated)
- SHCS = socket head cap screw
- BHCS = button head cap screw
- FHCS = flat head cap screw (countersunk)
- lag screw = lag bolt (wood threads, not machine threads)
- nyloc = nylon insert lock nut
- jam nut = thin nut (approximately half height of standard)
