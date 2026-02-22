### Printer Ink, Toner, and Consumables — Scoring Guidance

This query involves printer consumables where the model number is the compatibility key.

**Critical distinctions to enforce:**

- **Exact cartridge model numbers dominate**: Treat cartridge identifiers (e.g., HP 63 vs 65, TN vs DR series) as hard gates. Similar-looking numbers are often incompatible.

- **Standard vs high-yield (XL) nuance**: "XL"/high-yield variants are typically compatible with the same printers as the standard cartridge but have different yields/costs. If the query explicitly requests XL, do not substitute standard yield and vice versa.

- **Toner vs drum are different parts**: For many laser printers, the toner cartridge and the drum/imaging unit are separate consumables. If the query requests a drum unit, do not return toner cartridges, and vice versa.

- **Region/firmware constraints**: If the query mentions region-coded cartridges or "genuine/OEM only", treat that as a meaningful hard requirement—compatibles may be rejected by firmware or policy.
