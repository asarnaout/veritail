### Raw Materials — Scoring Guidance

This query involves metal or plastic raw material stock (bar, plate, sheet, tube, rod, extrusion, or rubber/gasket sheet).

**Critical distinctions to enforce:**

- **Steel grade specifies chemistry and properties**: AISI/SAE grades encode alloy system (first two digits) and carbon content (last two digits in hundredths of %). 1018 = plain carbon, 0.18% C (low carbon, easily machinable and weldable). 4140 = chrome-moly, 0.40% C (much harder, requires preheat for welding). A36 = structural steel (36 ksi yield). A572 Grade 50 = HSLA (50 ksi yield). A500 = specifically for hollow structural sections (HSS tube), NOT interchangeable with A36 plate. If the query specifies a grade, it is a hard constraint.
- **Stainless steel types**: 304 (18-8, general purpose, good corrosion resistance), 316 (marine/chemical resistance, contains molybdenum), 303 (free-machining, reduced corrosion resistance), 410 (martensitic, hardenable, magnetic), 17-4PH (precipitation hardening, aerospace). These are NOT interchangeable — 304 vs 316 can be the difference between corrosion failure and success in chloride environments. The "L" suffix (304L, 316L) indicates low carbon for weld corrosion resistance.
- **Aluminum temper designations are critical**: T6 = solution heat treated + artificially aged (maximum hardness but residual stress). T651 = T6 + stretching for stress relief — REQUIRED for plate stock to prevent warping during machining. T6511 = T6 + stretching + straightening — preferred for extruded bar/rod. 6061-T6 (45 ksi UTS) is general purpose and readily weldable. 7075-T6 (83 ksi UTS) is aerospace-grade and essentially NON-weldable by conventional methods. If temper is specified, it is a hard constraint.
- **Form factor matters**: Round bar, hex bar, flat bar, plate, sheet, tube (seamless vs welded), pipe (different from tube — see pipe_valves_fittings overlay), angle, channel, and I-beam are all distinct products. "Hot-rolled" vs "cold-rolled" vs "cold-drawn" affect dimensional tolerance, surface finish, and mechanical properties. If the query specifies a form or condition, treat as hard.
- **Plastic types are NOT interchangeable**: Delrin/acetal/POM (high strength, low friction), UHMW polyethylene (impact/abrasion resistant, FDA), Nylon PA6 vs PA66 (different moisture absorption and temp limits), PEEK (high-performance, high-cost, high-temp), PTFE/Teflon (low friction, chemical resistant, poor structural strength). Each serves specific engineering requirements. If the query names a specific plastic, enforce it.

**Terminology**:
- CRS = Cold Rolled Steel
- HRS = Hot Rolled Steel
- HR = Hot Rolled (surface condition)
- CF = Cold Finished (= cold drawn, tighter tolerances)
- HSS = Hollow Structural Section (steel tube, NOT High Speed Steel)
- Delrin = acetal = POM (DuPont brand name for polyoxymethylene)
- UHMW = Ultra-High Molecular Weight Polyethylene
