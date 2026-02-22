### MacBooks — Scoring Guidance

This query is about Apple MacBook laptops (MacBook Air / MacBook Pro).

**Critical distinctions to enforce:**

- **Model line and size are not interchangeable**: "MacBook Air" vs "MacBook Pro" and screen size (13/14/15/16-inch) are strong constraints when specified.

- **Apple Silicon generation matters**: If the query specifies M-series generation (e.g., M1/M2/M3/M4) or tier (base vs Pro vs Max vs Ultra), treat it as a hard identifier. Adjacent generations are weaker matches unless the query is explicitly broad (e.g., "MacBook Air").

- **Unified memory vs storage**: Many listings present "16GB / 512GB" where the first is unified memory and the second is SSD storage. Do not confuse these.

- **Ports and charging**: If the query explicitly requests MagSafe charging, specific Thunderbolt/USB-C port counts, or HDMI/SD slot presence, enforce it. Accessory ecosystems differ across generations.

- **Do not confuse MacBooks with iPads**: For queries containing "MacBook", do not return iPads or iPad keyboard cases as substitutes, even if they are "laptop-like", unless the query explicitly allows tablet alternatives.
