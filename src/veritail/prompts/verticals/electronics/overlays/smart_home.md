### Smart Home Devices — Scoring Guidance

This query involves smart home devices, whose usefulness depends on ecosystem and radio protocol compatibility.

**Critical distinctions to enforce:**

- **Ecosystem claims are not interchangeable**: "Works with Alexa" does not imply HomeKit support, and vice versa. If the query names a platform (Apple Home/HomeKit, Google Home, Alexa, SmartThings), treat that as a hard requirement.

- **Matter is about interoperability, but not universal**: If the query specifies Matter, require explicit Matter support. If the query specifies Matter-over-Thread, require Thread capability and be mindful that Thread devices typically need a Thread Border Router / controller in the home.

- **Zigbee and Z-Wave are distinct radios**: Zigbee devices generally require a Zigbee coordinator/hub, and Z-Wave is its own mesh ecosystem. Do not treat Zigbee and Z-Wave products as substitutes unless the product is explicitly a multi-protocol hub/bridge.

- **Device role matters**: A "smart bulb" is not a "smart switch". A "hub" is not an endpoint. Enforce device category when the query is explicit.

- **Security device constraints**: For locks and security sensors, query-specified standards (e.g., "Thread lock", "HomeKey", "local control") should be treated as hard; cloud-only devices are weaker matches for explicit local-control intent.
