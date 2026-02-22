### Memory Cards and Flash Storage — Scoring Guidance

This query involves removable flash storage where speed-class markings and form factor are the compatibility key.

**Critical distinctions to enforce:**

- **Form factor is non-negotiable**: SD vs microSD vs CFexpress/CFast are physically different. If the query specifies microSD, do not return full-size SD without an adapter, and vice versa.

- **SDHC / SDXC nuance**: If the query specifies SDHC vs SDXC (or capacity boundaries that imply them), enforce it; some hosts have constraints or require updates for SDXC.

- **Speed-class markings measure different things**: UHS Speed Class (U1/U3), Video Speed Class (V30/V60/V90), and Application Performance Class (A1/A2) are not interchangeable labels. Match the specific class requested.

- **Host-interface limitations**: A UHS-II card will work in a UHS-I host, but only at UHS-I speeds. If the query is about a device that only supports UHS-I (e.g., some consoles), do not up-score UHS-II as inherently more relevant unless the query explicitly seeks maximum transfer speed for off-device workflows.

- **USB flash drives vs memory cards**: Do not substitute USB flash drives for SD/microSD queries or vice versa unless an explicit adapter/bundle is requested.
