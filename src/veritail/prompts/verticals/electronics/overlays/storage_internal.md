### Internal Storage (SSD / HDD) — Scoring Guidance

This query involves internal storage: SSDs and hard drives.

**Critical distinctions to enforce:**

- **NVMe vs SATA is a hard protocol distinction**: M.2 is a shape; SSDs can be SATA or NVMe. If the query says NVMe / PCIe, do not return SATA M.2 drives. If it says SATA, do not return NVMe-only products.

- **M.2 length is a physical fit constraint**: 2230/2242/2280/22110 indicate length variants. If the query specifies a size (common for handhelds, ultrabooks, and consoles), treat it as hard.

- **Drive role and interface**: 2.5-inch SATA SSDs, 3.5-inch HDDs, and M.2 sticks are not interchangeable without adapters/bays. Match form factor and interface implied by the query.

- **PCIe generation requests are real**: "Gen4" vs "Gen3" vs "Gen5" matters when specified—especially for platforms with minimum performance recommendations.

- **NAS / RAID nuance: SMR vs CMR**: If the query includes NAS, RAID, ZFS, or rebuild-heavy workloads, prefer drives marketed for those uses and avoid SMR models unless the query explicitly requests SMR. SMR can behave very differently under sustained random writes and rebuild scenarios.

- **Do not confuse internal drives with external enclosures**: If the query is for the SSD itself, USB enclosures, docks, and adapters are not substitutes unless the query asks for a bundle.
