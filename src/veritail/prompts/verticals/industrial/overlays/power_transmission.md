### Power Transmission — Scoring Guidance

This query involves mechanical power transmission components: belts, chains, gears, sprockets, sheaves/pulleys, couplings, or keystock.

**Critical distinctions to enforce:**

- **V-belt cross-section designations are separate systems**: Classical (A, B, C, D, E) and narrow/wedge (3V, 5V, 8V) are different profile families. Metric V-belts (SPZ, SPA, SPB, SPC) do NOT directly correspond to classical sections. An "A" belt sheave will not accept a "3V" belt. If the query specifies a cross-section, it is a hard constraint.
- **Timing belt tooth profiles are NOT cross-compatible**: Classical profiles (XL, L, H, XH, XXH defined by pitch) use trapezoidal teeth. Curvilinear profiles (HTD, GT2/PowerGrip GT, GT3/PowerGrip GT3) use rounded teeth. A GT2 belt will NOT run on an HTD sprocket even at the same pitch because the tooth geometry differs. If the query specifies a tooth profile, it is a hard constraint.
- **Roller chain: ANSI ≠ ISO/BS despite same pitch**: ANSI chain (#35, #40, #50, #60, #80) and ISO/BS chain (06B, 08B, 10B, 12B, 16B) share the same pitch but differ in roller diameter and plate dimensions. An ANSI #40 chain (1/2" pitch) will not run properly on an 08B sprocket. The ANSI number encodes pitch: divide by 8 for pitch in inches (#40 = 4/8" = 1/2", #60 = 6/8" = 3/4"). If the query includes a chain number, match the exact standard (ANSI or ISO/BS).
- **Gear pitch systems — diametral pitch vs module**: Imperial gears use diametral pitch (DP = teeth per inch of pitch diameter). Metric gears use module (M = pitch diameter in mm / number of teeth). These are reciprocal (Module = 25.4/DP) but gears must match EXACTLY. A 20-DP gear will NOT mesh with a Module 1.25 gear despite being mathematically close. Pressure angle (14.5° legacy vs 20° standard) must also match between mating gears. If either pitch system or pressure angle is specified, treat as hard.
- **Coupling types are application-specific**: Jaw couplings, disc couplings, gear couplings, and grid couplings handle different levels of misalignment, torque, and speed. Jaw coupling spider (insert) hardness determines flexibility and damping. Bore size and keyway are hard physical constraints.

**Terminology**:
- sheave = V-belt pulley
- toothed pulley = timing pulley = synchronous sprocket
- keystock = key stock = key bar (square or rectangular drive key material)
- #40 chain = ANSI 40 chain = 40-1 (single strand) or 40-2 (duplex)
