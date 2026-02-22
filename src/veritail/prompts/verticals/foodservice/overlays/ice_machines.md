### Ice Machines — Scoring Guidance

This query involves commercial ice production or ice dispensing equipment.

**Critical distinctions to enforce:**

- **Ice form / ice type**: Cube (regular/dice/half-dice), crescent, nugget/cubelet/pellet, and flake ice have different beverage and display use cases. If the query specifies the ice type, it is a hard constraint.
- **Machine type**:
  * *Modular* (head-only) units require a separate storage bin or dispenser.
  * *Self-contained undercounter* units include a built-in bin and fit under counters.
  Do not return a head-only machine for an undercounter-with-bin query, and do not return a bin-only product for an ice-maker query unless the query is explicitly about bins.
- **Condenser / cooling method**: Air-cooled vs water-cooled vs remote-cooled configurations are not interchangeable when specified (different utilities + install).
- **Production ratings**: Ice makers often publish "maximum" production at 70°F air / 50°F water and a lower AHRI "standard" production at 90°F air / 70°F water. If the query specifies a lbs/day capacity, match the correct rating basis when it is stated; otherwise treat the listed range as an approximation.
- **Bin/dispensing configuration**: Ice dispensers (hotel/beverage dispensers) are not simple storage bins. If the query says "dispenser", "hotel dispenser", or "chewable nugget dispenser", require a dispensing unit.

**Terminology**:
- nugget ice = cubelet ice = pellet ice (often called "chewable")
- cuber = cube ice machine
- flaker = flake ice machine
