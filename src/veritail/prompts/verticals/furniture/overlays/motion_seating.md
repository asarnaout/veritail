### Recliners & Motion Seating — Scoring Guidance

This query is about **motion seating**: recliners, power recliners, lift chairs,
reclining sofas/sectionals, or home-theater seating.

#### Critical distinctions to enforce

- **Power vs manual is a hard constraint when stated**:
  - "Power recliner" must have powered motion (and typically a power source + control).
  - "Manual" / "push-back" should not return powered-only items unless the query allows.
- **Lift chairs are not regular recliners**:
  - "Lift chair" implies a powered lift-assist mechanism to help the user stand. A standard
    recliner without lift is a mismatch.
- **Wall-hugger / zero-wall / zero-clearance**:
  - These terms signal a recliner designed to operate with minimal rear clearance. If the
    query specifies it, require an explicit match (do not infer from photos).
- **Swivel / glider / rocker are different motion types**:
  - "Swivel recliner" must swivel; "rocker recliner" must rock; "glider" glides.
  - Do not substitute between them unless the query is exploratory.
- **Home-theater seating is its own class**:
  - Queries mentioning "theater seating", "row", "console", "cupholders", or "power headrest"
    imply cinema-style seating. A standard living-room recliner is usually not a match.
- **Control features may be hard constraints when specified**:
  - Power headrest, power lumbar, USB, battery pack, and "each seat reclines" can be decisive
    for multi-seat products.

#### Common disqualifiers

- Returning a stationary sofa/chair for an explicit recliner query.
- Returning an ottoman for a recliner query (ottomans do not provide reclining motion).
