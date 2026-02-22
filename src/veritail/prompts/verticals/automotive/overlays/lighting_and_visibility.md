### Lighting and Visibility — Scoring Guidance

This query involves lighting products (bulbs, assemblies) and/or visibility items (wiper blades, washer parts).

**Lighting — hard constraints:**

- **Bulb type codes behave like part numbers**: Codes like H11, 9005, 9006, HB3 describe a specific base/connector and electrical spec. Treat mismatch as wrong.
  - **Equivalence note**: Some bulbs have recognized alternate designations (e.g., 9005 is commonly referenced as HB3). When the query uses either designation, a result using the equivalent naming is acceptable.
- **Location matters**: Low beam vs high beam vs fog vs DRL vs turn signal are different applications. If the query specifies location, enforce it.
- **Technology matters when specified**: Halogen vs HID vs LED are not interchangeable if explicitly requested.
- **Street legal / DOT / SAE claims (when requested)**:
  - If the query asks for DOT/SAE compliance or "street legal", require explicit compliance claims.
  - "Off-road only" results are not acceptable matches for legality-focused queries.

**Wiper blades — hard constraints:**

- **Length and position**: Driver vs passenger vs rear blade sizes differ. If the query specifies length (inches/mm) or position, enforce.
- **Attachment style**: Modern vehicles use multiple connector styles. If the query specifies connector type or "exact fit", universal-fit blades are weaker matches.
- **Beam vs conventional vs winter**: Treat as a preference unless the query explicitly requests a type.

**Common disqualifiers:**

- Returning a full headlamp assembly for a bulb-only query (or returning a bulb when the query is for a full headlight housing) unless the query is ambiguous.
- Returning unrelated "appearance lighting" (underglow, interior LED strips) for an OEM replacement bulb query.

**Terminology**:
- headlamp housing = headlight assembly = headlamp assembly (may include lens/reflector/projector; bulbs may be separate)
- DRL = daytime running light
