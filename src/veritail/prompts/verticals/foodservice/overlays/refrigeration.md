### Refrigeration Equipment — Scoring Guidance

This query involves refrigeration/freezer equipment for cold storage, cold prep, or cold display (NOT ice makers; see ice_machines overlay).

**Critical distinctions to enforce:**

- **Reach-in vs undercounter vs walk-in**: Fundamentally different form factors and capacities. Walk-in queries should not return reach-in units. Undercounter units are designed for counter integration; height/clearance matters when specified.
- **Refrigerator vs freezer vs dual-temp**: Confusing these is a critical error. Match temperature class when stated (e.g., freezer, -10°F; refrigerator, 33–41°F).
- **Food-prep refrigeration types**:
  * *Sandwich/salad prep tables* commonly use shallower cutting boards and smaller top pans.
  * *Pizza prep tables* commonly have deeper cutting boards and rails designed around larger pans/toppings.
  * *Mega-top* units expand top-rail capacity.
  If the query specifies pizza vs sandwich vs mega-top, treat it as a hard subtype.
- **Door configuration**: Solid vs glass doors, number of doors/sections, and pass-thru (doors on both sides) are hard specs when specified.
- **System configuration**: Self-contained vs remote condenser (common in walk-ins and some high-capacity systems) is a hard constraint when specified.
- **Blast chillers vs standard freezers**: Blast chillers support rapid cooling for food safety. Do not treat a standard freezer as a blast chiller.

**Terminology equivalences** (do not penalize lexical mismatches when intent aligns):
- lowboy = undercounter refrigerator / freezer
- reach-in = upright commercial refrigerator / freezer
- chef base = refrigerated equipment stand / griddle stand
