### Computer Monitors — Scoring Guidance

This query involves a computer monitor.

**Critical distinctions to enforce:**

- **Refresh rate and resolution are often hard requirements**: If the query specifies 240 Hz, 4K, 3440×1440, or ultrawide aspect ratio, treat it as hard. A 165 Hz panel is not a good match for an explicit 240 Hz query.

- **Port requirements can be functional gates**: If the query specifies DisplayPort version, HDMI 2.1 for 4K120, or USB-C video, enforce it. Many monitors include USB-C ports that are data-only or do not provide sufficient USB Power Delivery for laptop charging.

- **USB-C monitor nuance**: A USB-C connector does not guarantee video output. If the query implies "single-cable laptop setup" (USB-C video + charging + USB hub), require explicit support for DisplayPort Alt Mode (or equivalent) and sufficient USB-C PD wattage.

- **HDR claims are not all equivalent**: If the query asks for VESA DisplayHDR tiers (e.g., DisplayHDR 600 or True Black), treat the certification tier as the requirement, not generic "HDR" marketing.

- **Adaptive sync compatibility**: If the query specifies G-SYNC (native/compatible) or FreeSync, treat that as a requirement; do not assume any monitor supports the requested VRR ecosystem.

- **Do not substitute TVs for monitors**: TVs are weaker matches for explicit "monitor" intent due to different ergonomics (pixel density, subpixel layouts, wake behavior) unless the query explicitly allows.
