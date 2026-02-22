### Beverages (Consumables) — Scoring Guidance

This query involves consumable beverages (not machines).

**Critical distinctions to enforce:**

- **Concentrate vs ready-to-drink**: Syrup concentrates (BIB, bag-in-box) are not drinks; they are for dispensing systems. If query requests "BIB" or "soda syrup", do not return bottled soda.
- **Coffee format**: Whole bean vs ground vs pods; roast profile; decaf vs regular are hard requirements when specified. Espresso grind vs drip grind mismatch is a functional error.
- **Tea format**: Iced tea bags, loose leaf, and RTD are distinct. Sweetened vs unsweetened and flavor (peach, lemon) are hard constraints when specified.
- **Alcohol**: If query includes beer/wine/kegs, match packaging (keg size, bottle/can) and style (IPA vs lager). Do not return NA products for alcoholic queries and vice versa.

**Terminology**:
- BIB = bag-in-box syrup
- RTD = ready-to-drink
