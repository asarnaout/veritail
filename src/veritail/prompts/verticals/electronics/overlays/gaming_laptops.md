### Gaming Laptops — Scoring Guidance

This query involves a gaming laptop / gaming notebook.

**Critical distinctions to enforce:**

- **Laptop GPU ≠ desktop GPU**: Portable GPUs are configured by OEMs and can vary widely in power/performance even with the same name. Do not treat a desktop GPU listing as relevant for a gaming-laptop query, and do not assume a desktop-level performance tier from the name alone.

- **GPU name must match, including tier markers**: "Ti", "SUPER", and distinct series numbers are not synonyms. If the query specifies a GPU tier (e.g., "RTX 4070"), do not treat "RTX 4060" or "RTX 4070 Ti" as close matches.

- **TGP / wattage constraints**: If the query includes GPU power (TGP) or laptop "wattage" constraints, treat them as hard. Otherwise, do not penalize a correct GPU-name match just because the listing omits TGP (but do penalize results clearly outside the requested power class, e.g., ultra-thin 35W variants for explicit "high watt" requests).

- **Display specs are often hard requirements**: Screen size, resolution (1080p/1440p/4K), refresh rate (144/165/240 Hz), and panel type (OLED/IPS) should be treated as hard when specified. A 165 Hz panel is not a good match for an explicit 240 Hz request.

- **Connector expectations**: If the query includes "Thunderbolt", "USB4", "HDMI 2.1", or specific port needs (for external monitors/docks), enforce those constraints. Many gaming laptops have USB-C ports that are data-only or do not support DisplayPort output.

- **Do not confuse RAM vs VRAM**: A query for "16GB RAM" is system memory, not "16GB GPU VRAM". Treat them as different constraints.

- **Chargers and docks are not laptops**: If the query is for a "laptop charger", "replacement adapter", or "dock", do not surface laptops.
