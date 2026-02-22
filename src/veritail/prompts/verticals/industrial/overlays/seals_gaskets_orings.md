### Seals, Gaskets, and O-Rings — Scoring Guidance

This query involves sealing components: o-rings, oil/shaft seals, gaskets, packing, or mechanical seals.

**Critical distinctions to enforce:**

- **O-ring sizing (AS568 dash numbers)**: Dash numbers encode ID and cross-section. They are grouped by cross-section series:
  * -001 to -049 = 1/16" cross-section
  * -102 to -178 = 3/32" cross-section
  * -201 to -284 = 1/8" cross-section
  * -309 to -395 = 3/16" cross-section
  * -425 to -475 = 1/4" cross-section
  Both the dash number AND the material must match. A -210 Viton o-ring is a different product from a -210 Buna-N o-ring. Metric o-ring sizes (ID × CS in mm) do NOT map directly to AS568 dash numbers.
- **O-ring material compatibility is the hardest constraint**:
  * Buna-N / Nitrile / NBR: petroleum, hydraulic oil, fuels — the general-purpose material. FAILS in ketones, ozone, esters.
  * Viton / FKM: broad chemical resistance, high temp (400°F), but NOT compatible with ketones, esters, ammonia, or hot water/steam.
  * EPDM: water, steam, brake fluids, phosphate esters — but DESTROYED by petroleum products. Using EPDM in a hydraulic system is catastrophic.
  * Silicone: wide temp range (-100°F to 450°F) but poor abrasion resistance and incompatible with most petroleum products.
  * PTFE: near-universal chemical compatibility but NO elasticity — used as backup rings, not primary sealing elements.
  * Kalrez / FFKM: near-universal resistance at extreme temps — very expensive ($50-500+ per o-ring).
  If the query specifies a material, it is a hard constraint driven by the service environment. Do not substitute materials.
- **Durometer (Shore A hardness)**: Standard is 70A. 90A is for high-pressure applications. 50A is for vacuum service. If specified, treat as hard.
- **Oil seal / shaft seal specifications**: ID (shaft size), OD (bore size), width, lip material, and spring-loaded vs springless are all constraining. Single-lip seals retain lubricant; double-lip seals also exclude contaminants. If any dimension is specified, it is hard.
- **Gasket types are not interchangeable**: Spiral wound (ASME B16.20, for flanged pipe joints), sheet gasket (cut to fit), ring joint (RTJ, high pressure), and compressed fiber gaskets serve different pressure/temperature classes.

**Terminology**:
- Buna-N = nitrile = NBR (same material, different names)
- Viton = FKM (Viton is a Chemours/DuPont brand name)
- Kalrez = FFKM (Kalrez is a DuPont brand name)
- TC = double-lip oil seal (common Chinese/metric designation)
- dash number = AS568 size designation (e.g., -210, -214)
