### Pumps — Scoring Guidance

This query involves pumps of any type — centrifugal, positive displacement, submersible, or specialty pumps.

**Critical distinctions to enforce:**

- **Head is NOT pressure**: Centrifugal pump head is measured in feet of water (or meters). The conversion is 2.31 feet of water = 1 PSI (for water). A pump rated for 100 feet of head produces ~43 PSI with water but a different pressure with fluids of different specific gravity. Do not conflate "feet of head" with PSI in search matching.
- **NPSH is the most misunderstood spec**: NPSHr (required, a pump characteristic) must be exceeded by NPSHa (available, an installation characteristic) to prevent cavitation. NPSHr is a product spec; NPSHa is the buyer's responsibility. If the query references NPSH, ensure the result provides NPSHr data.
- **ANSI B73.1 vs API 610**: ANSI B73.1 chemical process pumps are dimensionally standardized across manufacturers — all sizes are interchangeable footprint and piping connections. API 610 pumps are custom-engineered with higher construction standards, centerline mounting, and a mandated 20-year design life. These are fundamentally different product categories despite both being "centrifugal pumps." If the query specifies ANSI or API, treat as hard.
- **Pump type determines application**: Centrifugal pumps handle clean, low-viscosity fluids. Positive displacement pumps (gear, diaphragm, peristaltic, progressive cavity, piston) are required for high-viscosity fluids, precise metering, self-priming, or shear-sensitive products. Do not substitute PD for centrifugal or vice versa when the query specifies a type.
- **Seal type matters**: Mechanical seals vs packing vs sealless (magnetic-drive or canned-motor) pumps have completely different maintenance profiles and fluid compatibility. Sealless pumps eliminate leak paths for hazardous fluids. If specified, treat as hard.
- **Port size and connection type**: Pump inlet and outlet sizes (e.g., 2" × 1.5") with flanged, threaded, or cam-lock connections are hard specs.

**Terminology**:
- BEP = Best Efficiency Point (optimal operating region on pump curve)
- TDH = Total Dynamic Head (total head the pump must overcome)
- GPM = gallons per minute (flow rate)
- mag-drive = magnetic drive (sealless pump)
