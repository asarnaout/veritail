### Makeup Vanities & Dressing Tables — Scoring Guidance

This query is about **bedroom/closet grooming furniture**: vanity tables, dressing tables,
and makeup stations (often with mirror and/or lighting).

#### Critical distinctions to enforce

- **Bathroom vanity vs makeup vanity**:
  - Bathroom vanities have a sink/top and plumbing intent.
  - Makeup/dressing vanities are desk-like and may include mirrors, drawers, and seating.
  If the query mentions sinks, faucet holes, plumbing, or "bathroom", it is not this overlay.
- **Vanity vs dressing table nuance**:
  - Many buyers expect a "vanity table" to be makeup-oriented and often paired with a mirror.
  A "dressing table" may be similar but is often referenced as a general grooming surface.
  If the query is strict about a mirror, require the mirror included.
- **Mirror and lighting as hard constraints when specified**:
  - "Vanity with mirror" implies the mirror is included (not just a table).
  - "Hollywood vanity" strongly implies a large mirror with integrated bulbs/LED lighting.
- **Vanity set completeness**:
  - Many vanity "sets" include a matching stool/bench. If the query expects a set, table-only is
    incomplete.

#### Common disqualifiers

- Returning a bathroom sink vanity for a makeup vanity query.
- Returning a wall mirror alone for a "vanity set" query.
