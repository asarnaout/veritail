### Productivity Laptops, Ultrabooks, 2-in-1s, and Chromebooks — Scoring Guidance

This query involves a non-gaming laptop class: thin-and-light Windows laptops, business machines, 2-in-1 convertibles, or Chromebooks.

**Critical distinctions to enforce:**

- **OS is a hard gate when specified**: Windows vs ChromeOS vs macOS are different ecosystems. A "Chromebook" query should not return Windows laptops and vice versa unless the query is ambiguous.

- **CPU segment suffixes signal class**: When the query includes suffixes such as Intel U/P/H/HX or explicit "ultrabook"/"thin and light", treat it as a performance/thermal class constraint rather than a minor preference. Do not match a low-power U-class request with a heavy gaming H/HX-class machine.

- **2-in-1 / convertible vs clamshell**: If the query specifies "2-in-1", "convertible", or "detachable", treat hinge/form factor as a hard requirement. Do not substitute a standard clamshell laptop.

- **Business features**: If the query requests business features (smart card, fingerprint, LTE/5G WWAN, vPro/management, Thunderbolt docking), enforce them. These are not generic across consumer laptops.

- **Storage vs memory disambiguation**: Many listings use "16GB + 512GB" shorthand. Treat the first as RAM and the second as SSD capacity; do not swap or conflate them.

- **"Laptop" vs accessories**: If the query is for a laptop, do not let results be dominated by laptop bags, sleeves, stands, or chargers.
