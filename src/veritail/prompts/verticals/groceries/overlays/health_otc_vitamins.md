### Health, OTC, and Vitamins — Scoring Guidance

This query targets health and wellness items.

**Critical distinctions to enforce:**

- **Active ingredient + strength are hard**: For OTC medicines, match the active ingredient and the strength/dose (mg) when specified. "PM"/"nighttime" or "non-drowsy" versions are distinct variants.
- **Dosage form is hard**: tablets vs capsules vs gelcaps vs liquids vs gummies vs powders are not interchangeable when specified.
- **Age targeting is hard**: infant/children/adult/senior formulations differ.
- **Vitamins/supplements**:
  * "D3" vs "D2" differ; fish oil vs algal oil differ.
  * Units matter (IU vs mcg vs mg). Do not treat them as interchangeable.
  * "gummy" vs "softgel" vs "tablet" are distinct forms.
- **Medical nutrition products**: If a query specifies "infant" or a medical formula, route to the baby overlay (not general supplements).

**Common disqualifiers / critical errors**:
- Returning a cosmetic item for a medicine query (and vice versa) unless ambiguous.
