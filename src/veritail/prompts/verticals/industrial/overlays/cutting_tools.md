### Cutting Tools and Toolholding — Scoring Guidance

This query involves metalworking cutting tools, inserts, drills, end mills, taps, or toolholding systems.

**Critical distinctions to enforce:**

- **ISO insert designation (ISO 1832)**: CNMG 120408 decodes as: C = 80° diamond shape, N = 0° clearance (negative rake, enables double-sided use), M = medium tolerance class, G = hole with chipbreaker both faces. Dimensions: 12 = 12.70mm IC (inscribed circle), 04 = 4.76mm thickness, 08 = 0.8mm nose radius. The ANSI equivalent (CNMG 432) uses 1/8" IC increments, 1/16" thickness, and 1/64" nose radius. A CNMG insert CANNOT go in a WNMG holder — the shape letter must match the toolholder's pocket geometry. Every element of the designation is a hard constraint.
- **Carbide grade ISO application ranges**: P (steel) = blue, M (stainless) = yellow, K (cast iron) = red, N (non-ferrous) = green, S (superalloys) = brown, H (hardened steel) = grey. Each manufacturer (Sandvik, Kennametal, Iscar, Seco) has proprietary grade designations within these ranges that do NOT cross-reference directly. If the query specifies a manufacturer grade (e.g., "Sandvik GC4325"), treat as a hard constraint.
- **Coating type matters**: CVD coatings (TiCN/Al₂O₃/TiN multilayer) are thicker and better for roughing at moderate speeds. PVD coatings (TiAlN, AlCrN) are thinner and better for finishing, interrupted cuts, and non-ferrous materials. Uncoated is preferred for aluminum (coated edges promote built-up edge). If coating is specified, treat as hard.
- **Toolholder taper systems are NOT interchangeable**: CAT40 and BT40 have the same taper angle but different flange geometry — CAT uses a V-flange, BT uses a different flange common in Japanese machines. HSK (hollow shank taper) is a completely different system. Morse taper (MT), R8 (Bridgeport mills), 5C (collet systems) are all incompatible. If the query specifies a taper system, it is a hard constraint.
- **Drill bit sizing systems overlap**: Fractional (1/16" increments), letter (A=0.234" through Z=0.413"), number (#1=0.228" through #80=0.0135"), and metric (0.1mm increments) all overlap. A 1/4" drill, an E letter drill (0.250"), and a 6.35mm drill are the same size. Point angle matters: 118° for soft materials; 135° split-point for harder materials and self-centering. If point angle is specified, enforce it.
- **Tap types**: Taper (starting tap), plug (general purpose), bottoming (threads close to bottom of blind hole) serve different functions. Thread specification (size, pitch, UNC/UNF/metric) must match exactly. Form taps (roll taps) vs cutting taps produce threads by different methods.

**Terminology**:
- IC = inscribed circle (insert size)
- CNMG = insert designation (shape-clearance-tolerance-chipbreaker)
- CAT40 = V-flange taper, 40 taper size (most common US CNC)
- BT40 = Japanese-style taper, 40 taper size
- HSK = Hollow Shank Taper (high-speed/precision)
