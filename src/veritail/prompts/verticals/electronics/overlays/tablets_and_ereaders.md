### Tablets and E-Readers — Scoring Guidance

This query involves a tablet or an e-reader device.

**Critical distinctions to enforce:**

- **Tablet vs laptop vs accessory**: If the query is for the tablet device, do not return keyboard cases, folios, screen protectors, or styluses as substitutes.

- **Wi-Fi vs cellular is a core SKU split**: If the query specifies cellular/5G/LTE, require a cellular-capable model. If it specifies Wi-Fi-only (or is price-sensitive and only mentions Wi-Fi), do not assume cellular.

- **Generation and screen size are part of compatibility**: Many tablets share the same family name across generations, but accessories (cases, keyboard connectors, styluses) can be generation-specific. Treat the exact generation/year or model identifier as a hard requirement when provided.

- **Storage and RAM disambiguation**: For tablets, "128GB/256GB/..." typically refers to storage, not RAM. If the query specifies both (common in Android tablets), keep them distinct.

- **Stylus ecosystem**: If the query implies an active stylus (e.g., "Apple Pencil", "pen support"), be aware that stylus compatibility can be generation-specific; do not treat any generic capacitive stylus as equivalent for active-pen intent.

- **E-readers are not generic tablets**: For Kindle/Kobo-like intent, do not substitute Android tablets unless the query explicitly allows a general-purpose tablet.
