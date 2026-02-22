### Accessories and Tools — Scoring Guidance

This query involves automotive accessories, towing hardware, tools/garage items, or detailing products.

**Hard constraints (when specified):**

- **Vehicle-specific vs universal fit**:
  - Many accessories are custom-fit (floor mats, seat covers, window deflectors, roof racks, many hitches).
  - If the query includes a Y/M/M or a specific vehicle, treat "custom-fit" compatibility as critical. Universal-fit accessories are weaker unless the query explicitly wants universal.
- **Scope of a set**: "Front row only" vs "full set" vs "cargo liner" are different. If the query specifies row coverage or cargo area coverage, treat mismatches as major errors.

**Towing / hitch-specific constraints:**

- **Receiver size is a hard boundary**: Standard trailer hitch receiver sizes include 1-1/4", 2", 2-1/2" and 3". If the query specifies receiver size, enforce it.
- **Hitch class and capacity (when specified)**: Class and tongue weight / GTW ratings matter. Do not treat a lower class hitch as a match for a higher-capacity intent.
- **Adapters change capacity**: If the query includes an adapter (e.g., 1-1/4" to 2"), reduced capacity and torque limitations are part of the intent; prefer results that explicitly address these constraints.

**Tools / diagnostics constraints:**

- **OBD-II compatibility is not just a plug shape**:
  - OBD-II vehicles can use multiple communication protocols (e.g., SAE J1850 PWM/VPW, ISO 9141-2, ISO 14230-4, and ISO 15765-4 CAN).
  - If the query specifies OBD-II support or specific protocols, require explicit support claims.
- **Consumable vs tool**: Do not return a tool for a consumable query or vice versa (e.g., detailing chemicals vs polishing machine) unless ambiguity exists.

**Common disqualifiers:**

- Returning decorative items for functional tool queries (or vice versa).
- Returning trailer balls / ball mounts when the query is for a receiver hitch, unless the query explicitly asks for the full towing setup.

**Terminology**:
- GTW = gross trailer weight
- TW = tongue weight
