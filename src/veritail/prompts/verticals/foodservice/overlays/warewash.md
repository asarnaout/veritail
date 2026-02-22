### Warewashing — Scoring Guidance

This query involves commercial warewashing equipment (dishwashers, glasswashers, pot/utensil washers), ware racks, and dishmachine chemicals (detergent, rinse aid, dishmachine sanitizer).

**Critical distinctions to enforce:**

- **Machine class / throughput**:
  * Undercounter / bar glasswashers (small footprint)
  * Door-type / hood-type (single-rack, 20×20 racks common)
  * Conveyor / flight-type (high volume)
  These are different scales—do not substitute a bar glasswasher for a conveyor query.
- **Sanitization method**:
  * High-temp machines sanitize via hot-water final rinse (typically requiring a booster heater).
  * Low-temp machines sanitize via chemical sanitizer in the final rinse.
  If the query specifies high-temp vs low-temp (or "chemical sanitizing"), treat as hard.
- **Rack size**: 20×20 racks are a common standard for many door-type/conveyor machines; if a query specifies rack size or "20×20", enforce compatibility.
- **Ventless / hood requirements**: "Ventless"/"hoodless" dishmachines use heat recovery/condensing designs. If the query specifies ventless, it is a hard requirement; do not return standard hood-required machines.
- **Chemical type and format**: Dishmachine detergents, rinse aids, and sanitizers are distinct products. Chlorine vs iodine vs other sanitizer formulations are not automatically interchangeable when specified. Concentrate vs ready-to-use vs solid block are format constraints when specified.

**Compatibility rule**: If the query includes a machine brand/model, chemical results must be explicitly compatible with that machine type (high-temp vs low-temp) and feeding system when stated.
