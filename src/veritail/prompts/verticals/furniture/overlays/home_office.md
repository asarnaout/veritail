### Home Office — Scoring Guidance

This query is about **office chairs** and **desks**, including standing desks and gaming setups.

#### Critical distinctions to enforce

- **Office-chair standards often matter when named**:
  - ANSI/BIFMA X5.1 is a common standard reference for general-purpose office seating. If the query
    specifies BIFMA/X5.1, require an explicit compliance/certification claim.
- **Desk/table standards may appear in commercialish home-office queries**:
  - ANSI/BIFMA X5.5 is commonly referenced for desk/table products. Treat explicit X5.5 mentions
    as a hard constraint.
- **Caster / floor compatibility**:
  - Hard wheels are often marketed for carpet; soft/PU wheels are often marketed to protect hard floors.
  If the query specifies "hard floor casters" or "for carpet", require an explicit match and do not guess.
- **Ergonomic adjustability is not generic**:
  - If the query requires specific adjustments (lumbar support, headrest, 4D arms, seat depth),
    treat missing adjustments as a major relevance penalty.
- **Standing desks: height range is the fitment spec**:
  - Many standing desks market a height adjustment range roughly in the ~24"–50" neighborhood.
  If the query specifies a minimum/maximum height (or "BIFMA height range"), require explicit specs.
- **Desk size and monitor count**:
  - If the query specifies desktop size (e.g., 60"×30"), corner/L-shape, or multi-monitor setups,
    treat size/shape as a hard requirement.

#### Common disqualifiers

- Returning dining chairs for an office-chair query.
- Returning desk accessories (cable trays, monitor arms) for a desk query unless explicitly requested.
