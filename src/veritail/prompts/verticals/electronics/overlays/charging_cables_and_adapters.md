### Charging, Cables, Adapters, Docks, and Hubs — Scoring Guidance

This query involves connectivity and power accessories where the spec is the function.

**Critical distinctions to enforce:**

- **USB-C is a connector, not a capability**: A USB-C port or cable may support only USB 2.0 data, or may lack video output, or may not support high-wattage charging. If the query specifies speed (5/10/20/40 Gbps), video, or PD wattage, enforce it.

- **USB 3.2 naming is confusing—use the speed**: If the query specifies "USB 10Gbps" / "20Gbps", treat that as the real requirement, and penalize listings that only provide USB 2.0 (480 Mbps) or lower speeds.

- **USB Power Delivery EPR (240W) requires the right cable class**: If the query requests 140W/180W/240W charging (USB-C PD 3.1/EPR), require an E-Marked/EPR-capable cable explicitly rated for the wattage. Do not treat generic USB-C cables as acceptable.

- **Thunderbolt vs USB-C hub**: If the query requests Thunderbolt (TB3/TB4/TB5), require explicit Thunderbolt certification/support. A USB-C hub is not a substitute just because the plug fits.

- **Display adapters depend on alternate modes**: USB-C to HDMI/DP requires the host device to support DisplayPort Alt Mode (or equivalent). If the query is about connecting a laptop/phone to an external display, prefer products that explicitly state DP Alt Mode compatibility.

- **HDMI cable certification levels matter**: If the query requests high-bandwidth HDMI (4K120, 8K, HDMI 2.1/2.2), prefer certified cable classes (e.g., Ultra High Speed, Ultra96) and penalize older "High Speed" cables.

- **Do not return devices**: For cable/dock queries, do not return laptops, monitors, or TVs.
