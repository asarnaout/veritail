### Pipe, Valves, and Fittings — Scoring Guidance

This query involves piping system components: pipe, pipe fittings, valves, flanges, strainers, or steam traps.

**Critical distinctions to enforce:**

- **NPS (Nominal Pipe Size) does NOT equal any actual dimension for sizes 1/8" through 12"**: NPS 1/2 pipe has an OD of 0.840", NOT 0.500". NPS 1 = 1.315" OD. NPS 2 = 2.375" OD. For NPS 14+, nominal equals actual OD. The OD is fixed for each NPS; pipe schedule changes the wall thickness (and therefore the ID) while OD remains constant. Schedule 40 is "standard wall" for most sizes; Schedule 80 is "extra heavy." This equivalence breaks down above NPS 10 (Sch 40 ≠ STD wall for large pipe).
- **Pipe size ≠ tube size**: Tube OD IS the actual outside diameter — a 1/2" tube has 0.500" OD. A 1/2" NPS pipe has 0.840" OD. Pipe fittings and tube fittings are physically incompatible despite the same nominal size. This is one of the most common confusion errors.
- **Valve pressure class is NOT a direct PSI value**: Class 150, 300, 600, 900, 1500, 2500 are dimensionless designators. Class 150 WCB carbon steel is rated to 285 PSIG at ambient temperature, decreasing with temperature. "150#", "Class 150", and "150 Lb" are all synonymous. If the query specifies a pressure class, it is a hard constraint.
- **Valve type determines function**:
  * Gate valves: on/off isolation ONLY — NOT for throttling (partial opening causes erosion and vibration).
  * Globe valves: designed for throttling and flow regulation.
  * Ball valves: quarter-turn on/off. Full-port vs standard (reduced) port affects flow restriction significantly.
  * Check valves: swing, lift, wafer, and dual-plate types serve different flow/pressure conditions.
  * Butterfly valves: wafer, lug, and double-flanged mounting types are NOT interchangeable. Lug-style allows dead-end service; wafer does not.
  Do not substitute across valve types unless the query is generic.
- **Flange face types are safety-critical**: Raised Face (RF), Flat Face (FF), and Ring-Type Joint (RTJ) are NOT interchangeable. Using a raised-face gasket against a flat-face cast iron flange creates a bending moment that can crack the flange — this is a code violation per ASME B31.
- **Valve body materials**: WCB = carbon steel (most common), CF8M = 316 stainless, CF8 = 304 stainless, LCC = low-temp carbon steel, WC6 = chrome-moly. These casting codes are different from wrought specs (A105, F316). If the query specifies material, match the correct standard.
- **Fitting classes**: Threaded fittings: 150# and 300# for cast (ASME B16.3/B16.4), and 2000#/3000#/6000# for forged (ASME B16.11). Socket weld fittings: 3000# or 6000#. Butt weld fittings (ASME B16.9) match pipe schedule. "Malleable iron" vs "cast iron" vs "ductile iron" are three different materials — malleable is impact-resistant; gray cast iron is brittle; ductile iron is strongest.

**Terminology**:
- NPT = National Pipe Thread (tapered, self-sealing with sealant)
- NPS = Nominal Pipe Size (dimension system, NOT thread)
- Sch 40 = Schedule 40 = standard wall (for most sizes)
- 150# = Class 150 = 150 Lb (flange/valve pressure class)
- RF = raised face, FF = flat face, RTJ = ring-type joint (flange faces)
- WCB = cast carbon steel (ASTM A216 Grade WCB)
