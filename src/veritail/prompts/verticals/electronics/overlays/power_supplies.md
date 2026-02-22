### Power Supplies (PSUs) — Scoring Guidance

This query involves a PC power supply unit.

**Critical distinctions to enforce:**

- **Form factor is a hard fit constraint**: ATX vs SFX vs SFX-L vs TFX/FlexATX are not interchangeable without case support. Treat form factor as hard when specified (especially for SFF builds).

- **Modern GPU power connectors**: If the query is for a PSU that supports a 16-pin GPU connector (12VHPWR / 12V-2x6, often marketed as PCIe 5.x / ATX 3.x), treat that as a hard requirement. A PSU without the required connector (or without enough wattage/rails) is a mismatch.

- **Wattage and headroom**: If the query states wattage (e.g., 850W) treat it as a hard minimum unless "around" or a range is clearly implied.

- **Modular cabling**: Fully modular vs semi-modular vs non-modular is a meaningful constraint in cable-management-sensitive builds; enforce it when specified.

- **Input voltage constraints**: Some PSUs are 200–240V only. If the query implies a specific market or explicitly requests 110V/US use, penalize voltage-limited units that would not work.

- **Do not substitute laptop power bricks**: Laptop AC adapters / USB-C chargers are not PSU alternatives.
