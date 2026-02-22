### Welding — Scoring Guidance

This query involves welding consumables, equipment, or accessories.

**Critical distinctions to enforce:**

- **Stick electrode classification (AWS A5.1/A5.5)**: E7018 decodes as: E = electrode, 70 = 70,000 PSI minimum tensile strength, 1 = all-position capable, 8 = low-hydrogen potassium coating with iron powder, AC or DCEP. The third digit encodes position capability: "1" = all-position (flat, horizontal, vertical, overhead); "2" = flat and horizontal only. The last two digits together encode coating type and polarity:
  * "10" = cellulose sodium, DCEP only (E6010 for pipe root passes)
  * "11" = cellulose potassium, AC or DCEP (E6011 = AC version of E6010)
  * "18" = low-hydrogen potassium/iron powder, AC or DCEP (E7018)
  **E6010 will NOT run on AC welding power** — E6011 is the AC equivalent. This polarity constraint is hard. E7018 is the most common structural electrode and must be stored in rod ovens (250-300°F) after opening — moisture contamination causes hydrogen cracking in welds.
- **MIG wire classification (AWS A5.18)**: ER70S-6 = ER (electrode/rod) + 70 (70 ksi tensile) + S (solid wire) + 6 (high deoxidizer chemistry). The "-6" has the highest Mn/Si deoxidizer content, ideal for slightly dirty base metals. ER70S-2 and ER70S-3 have less deoxidizer and require cleaner base metals. Wire diameter (0.023", 0.030", 0.035", 0.045") is a hard constraint determined by material thickness and machine capability.
- **Flux-core wire — gas-shielded vs self-shielded**: E71T-1 = gas-shielded flux-core ("dual shield") — requires external shielding gas. E71T-8 and E71T-11 = self-shielded ("innershield") — no external gas needed. These require completely different setups. If the query specifies gas-shielded or self-shielded flux-core, treat as hard.
- **Shielding gas is NOT interchangeable across processes**: MIG carbon steel: 75% Ar / 25% CO₂ ("C25") is standard; 100% CO₂ is cheaper with deeper penetration but more spatter. MIG stainless: requires different gas (typically 98% Ar / 2% CO₂ or tri-mix). TIG: 100% argon for most applications. If the query specifies a gas mixture, match it.
- **Process terminology**: SMAW = Stick, GMAW = MIG = wire-feed (with gas), GTAW = TIG, FCAW = Flux-Core. "Wire feed welder" is ambiguous — could be MIG (solid wire + gas) or flux-core (tubular wire ± gas). Match the specific process when identified.
- **Welding machine type**: Stick-only, MIG-only, TIG-only, and multi-process machines are different products. Input power (120V vs 240V vs dual-voltage) and output amperage range are hard specs.

**Terminology**:
- DCEP = DC Electrode Positive (= DC Reverse Polarity)
- DCEN = DC Electrode Negative (= DC Straight Polarity)
- C25 = 75% Argon / 25% CO₂ shielding gas blend
- E7018 = low-hydrogen all-position stick electrode, 70 ksi
- ER70S-6 = solid MIG wire, 70 ksi, high deoxidizer
