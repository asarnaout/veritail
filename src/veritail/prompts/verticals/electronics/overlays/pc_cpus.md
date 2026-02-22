### Desktop CPUs / Processors — Scoring Guidance

This query is about a CPU sold as a standalone component, not a complete computer.

**Critical distinctions to enforce:**

- **CPU vs full PC**: Do not treat full desktops/laptops as relevant for a CPU-only query. If the query is for a CPU, matching the CPU model is the primary signal.

- **Model identifier includes suffix**: Intel and AMD suffix letters are part of the model identity. Intel "F" models require discrete graphics (no iGPU), while "K" indicates an unlocked SKU. Treat these as hard when the query includes them. For AMD, "G" desktop parts indicate integrated graphics variants (commonly listed as "with Radeon Graphics")—do not treat a non-G CPU as the same part.

- **Socket / platform constraints**: If a query references a socket/platform (AM4 vs AM5; LGA 1700 vs newer), treat it as a hard requirement. CPUs cannot be used across sockets, even within the same brand.

- **Boxed vs tray / OEM**: If the query specifies "boxed" (retail) vs "tray/OEM", treat that as a stated requirement. In many markets, boxed CPUs have different included accessories (e.g., cooler) and warranty paths compared with OEM/tray.

- **Cooler included vs not**: If the query explicitly asks for a CPU "with cooler" or references a stock cooler name, treat inclusion as a meaningful constraint.

- **Avoid series-name substitution**: Within a brand family, adjacent SKUs can differ materially. Treat "Ryzen 7 5700X" vs "5700G" or "Intel i5-14600K" vs "i5-14600" as distinct products unless the query explicitly allows alternatives.
