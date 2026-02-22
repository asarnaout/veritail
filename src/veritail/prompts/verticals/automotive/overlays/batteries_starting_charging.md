### Batteries, Starting, and Charging — Scoring Guidance

This query involves a vehicle battery, starter, alternator, or battery/charging accessories.

**Hard constraints (battery fitment):**

- **BCI group size is physical fit + terminal layout**: Group size standardizes battery dimensions and terminal placement. A wrong group size is commonly a non-fit or unsafe cable routing.
- **Terminal type and orientation**:
  - Top-post vs side-post is a hard boundary when specified.
  - Terminal orientation matters; reversed orientation can cause cables not to reach or can create polarity hazards.
- **Battery chemistry/type when specified (especially start-stop)**:
  - Many start-stop vehicles are equipped with EFB or AGM batteries.
  - If the query specifies AGM or EFB, results must match that type. Do not downgrade AGM → flooded or AGM → EFB unless the query explicitly allows it.

**Hard constraints (electrical performance when specified):**

- **CCA rating**: If the query specifies a minimum CCA, enforce it. Higher CCA is generally acceptable as long as physical fitment and terminal layout match.
- **Voltage**: Automotive SLI batteries are typically 12V; if the query specifies 6V or 24V (special applications), it is a hard constraint.

**Starting/charging parts:**

- **Starter vs alternator**: These are not interchangeable categories. Do not score an alternator as relevant for a starter query or vice versa.
- **Remanufactured vs new**: If the query specifies new vs reman, enforce.

**Common disqualifiers / critical errors:**

- Returning a battery charger/jump starter for a "replacement battery" query (unless explicitly requested).
- Returning a battery with the wrong post type (side vs top) when the query is explicit.

**Terminology**:
- SLI = starting, lighting, ignition (standard 12V vehicle battery use case)
- AGM = absorbent glass mat (sealed lead-acid design, high cycle capability)
- EFB = enhanced flooded battery (improved cycle capability vs standard flooded; common for some start-stop systems)
- CCA is a standardized cold-start performance rating at low temperature
