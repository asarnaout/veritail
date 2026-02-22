### PC Cases and Cooling — Scoring Guidance

This query involves PC enclosures or cooling hardware.

**Critical distinctions to enforce:**

- **Case compatibility is structural**: Motherboard size support (ATX/mATX/ITX), PSU size support (ATX/SFX), GPU length clearance, CPU cooler height, and radiator mount sizes are hard constraints when specified.

- **Socket mounting is non-negotiable for CPU coolers**: If the query specifies CPU socket (AM4/AM5/LGA 1700/...) or explicitly targets a cooler for a specific platform, do not return a cooler without the matching mounting hardware or confirmed compatibility.

- **AIO radiator size matters**: 120/240/280/360 mm radiators are not interchangeable. If the query requests a specific size, treat it as hard.

- **Fan size and connector type**: 120 mm vs 140 mm fan size and PWM (4-pin) vs DC (3-pin) can be hard requirements when specified, especially for noise/fit builds.

- **Do not confuse thermal paste/pads with coolers**: If the query is for a full cooler, thermal compounds alone are not substitutes. If the query is for paste/pads, coolers are overbroad and irrelevant.
