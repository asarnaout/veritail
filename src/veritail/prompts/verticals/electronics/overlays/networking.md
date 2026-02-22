### Networking (Wi-Fi, Mesh, Modems, Switches) — Scoring Guidance

This query involves networking gear.

**Critical distinctions to enforce:**

- **Wi-Fi generation and bands**: Wi-Fi 6 vs 6E vs 7 are meaningfully different. If the query specifies 6E, it implies 6 GHz support; if it specifies Wi-Fi 7, it implies 802.11be-class hardware. Treat these as hard when specified.

- **Router vs modem vs gateway**: A modem (DOCSIS/DSL/fiber ONT) is not a router. A router is not a modem. A "gateway" may include both. Enforce device role when the query is specific.

- **Mesh systems vs single routers**: If the query asks for a mesh system, prefer multi-node kits or explicitly mesh-capable routers; a single non-mesh router is a weak match unless the query is open-ended.

- **DOCSIS compatibility**: If the query requires DOCSIS 3.1 (common for gigabit cable plans), treat it as a hard requirement. Do not substitute DOCSIS 3.0 for an explicit 3.1 request.

- **Ethernet speed tiers**: 1GbE vs 2.5GbE vs 10GbE ports are hard constraints when specified. Do not treat a 1GbE-only switch as a match for an explicit 2.5GbE/10GbE request.

- **Do not confuse extenders with routers**: Range extenders, Wi-Fi adapters, and powerline kits are not routers/modems unless explicitly stated.
