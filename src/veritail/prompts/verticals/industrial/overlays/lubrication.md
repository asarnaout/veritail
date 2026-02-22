### Lubrication — Scoring Guidance

This query involves lubricants (grease, oil, dry lubricant) or lubrication application tools.

**Critical distinctions to enforce:**

- **ISO VG numbers are NOT the same as SAE numbers**: ISO VG (Viscosity Grade) is kinematic viscosity in centistokes at 40°C per ISO 3448. ISO VG 32, 46, and 68 are the most common hydraulic oil grades. Each grade spans ±10% of its midpoint. The SAE viscosity system (automotive) and AGMA (gear) systems are completely separate — ISO VG 32 ≈ SAE 10W, ISO VG 68 ≈ SAE 20, ISO VG 150 ≈ SAE 40, but these are approximate cross-references only. If the query specifies ISO VG, do not substitute SAE grades.
- **NLGI grease grade is consistency, NOT performance**: The scale runs from 000 (semi-fluid) through 6 (very hard, block-like). NLGI 2 is the standard for most general bearing applications. NLGI 1 is used for centralized lubrication systems; NLGI 3 for vertical shafts or high-speed bearings. The number says nothing about base oil type, additive package, temperature range, or load capacity. If the query specifies an NLGI grade, it is a hard constraint.
- **Grease thickener compatibility is critical**: Mixing incompatible thickener types causes softening or hardening and bearing failure. Lithium + lithium complex = compatible. Lithium + polyurea = INCOMPATIBLE. Calcium sulfonate + lithium complex = questionable. If the query specifies a thickener type (lithium, polyurea, calcium sulfonate, etc.), enforce it.
- **Oil types are application-specific**: Hydraulic oil (AW = anti-wear), gear oil (EP = extreme pressure), compressor oil (specific to compressor type — rotary screw vs reciprocating), way oil (slideway lubricant with tackifier), and spindle oil (very low viscosity) are NOT interchangeable. EP additives in gear oil can corrode yellow metals (bronze bushings) in hydraulic systems. If the query specifies an oil type, match it.
- **Food-grade lubricants**: NSF H1 = incidental food contact. NSF H2 = no food contact. NSF H3 = soluble oils for direct food contact (rare). H1 and H2 are NOT interchangeable when food contact is a requirement.

**Terminology**:
- AW = Anti-Wear (hydraulic oil additive type)
- EP = Extreme Pressure (gear oil additive type)
- ISO VG = ISO Viscosity Grade (centistokes at 40°C)
- NLGI = National Lubricating Grease Institute (consistency grade)
- cSt = centistokes (kinematic viscosity unit)
