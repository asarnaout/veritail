### Gaming Desktop PCs — Scoring Guidance

This query is about an assembled, prebuilt gaming desktop PC (tower or small-form-factor gaming desktop), not a single component.

**Critical distinctions to enforce:**

- **Prebuilt PC vs parts**: Queries that read like a full system spec (CPU + RAM + storage, often GPU and Windows) expect a complete computer. Do not treat CPUs, GPUs, RAM kits, SSDs, cases, power supplies, or motherboards as relevant substitutes.

- **Desktop vs laptop vs mini PC**: Do not return gaming laptops for a desktop query. Do not return laptop-only parts (e.g., SO-DIMM kits, laptop GPUs) for a desktop PC query. A "mini PC" / "NUC-style" query expects that small chassis class; a full tower is a weaker match and a bare motherboard is a mismatch.

- **CPU model is the identifier when specified**: Treat full CPU model strings as hard requirements when present (e.g., Ryzen 7 5700G ≠ Ryzen 7 5700X). If the query calls out integrated graphics (common in "G" class APUs), do not substitute a CPU variant without iGPU unless a discrete GPU is explicitly included.

- **GPU tiers are not interchangeable**: "Ti", "SUPER", and different series numbers are distinct SKUs. If the query specifies "RTX 4070 SUPER", an RTX 4070 (non-SUPER) is not a close match. If the query is for a desktop GPU tier, do not treat a "Laptop GPU" listing as equivalent.

- **Memory and storage are purchase-defining specs**: Treat DDR generation (DDR4 vs DDR5), capacity, and often speed as strong constraints when specified. Treat NVMe vs SATA, and PCIe Gen requirements as hard constraints when requested.

- **System completeness**: If the query implies "ready to plug in and use" (common for consumer pre-builts), barebones systems (missing RAM/SSD/OS) are weaker matches unless the query explicitly says "barebones", "mini barebone", or "kit".

- **OS / license constraints**: If the query specifies Windows edition ("Windows 11 Pro") or "no OS / Linux / FreeDOS", treat that as a meaningful constraint; do not ignore it just because the hardware matches.
