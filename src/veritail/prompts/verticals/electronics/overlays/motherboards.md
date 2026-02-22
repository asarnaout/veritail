### Motherboards — Scoring Guidance

This query involves a motherboard.

**Critical distinctions to enforce:**

- **Socket and chipset are hard gates**: Match motherboard socket to the CPU platform implied by the query. Do not substitute between sockets even if the board is the same brand or price tier.

- **DDR generation support**: Motherboards are typically either DDR4 or DDR5. If the query specifies DDR4 or DDR5, treat it as a hard requirement; the wrong memory generation will not fit.

- **Form factor controls physical fit**: ATX vs micro-ATX vs mini-ITX is a hard constraint when specified because it determines case compatibility and expansion slot layout.

- **Integrated Wi-Fi / connectivity**: If the query specifies Wi-Fi (especially a generation such as Wi-Fi 6E or Wi-Fi 7), treat it as a requirement; many boards come in both Wi-Fi and non-Wi-Fi variants with nearly identical names.

- **M.2 / PCIe slot capabilities**: If the query specifies PCIe Gen 5 storage, NVMe slot count, or specific M.2 lengths (2230/2280/22110), treat these as hard constraints. A board may have an M.2 slot physically but not support the requested protocol or generation.

- **Motherboard vs accessories**: Do not treat "I/O shield", "Wi-Fi antennas", or "motherboard standoffs" as relevant results for a motherboard query.
