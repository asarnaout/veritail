### Veterinary Prescription Diets — Scoring Guidance

This query targets clinical therapeutic diets requiring veterinary authorization (VCPR).
These are NOT standard OTC pet foods.

**Critical distinctions to enforce:**
- **The Rx vs OTC Boundary**: A query for "Hill's k/d" is a prescription renal diet. Returning "Hill's Science Diet" (OTC wellness) is a category-level critical error. Conversely, do not return Rx diets for generic OTC queries.
- **Clinical Acronyms and Mechanics**: Manufacturers use specific acronyms that are hard constraints:
  * **Urinary (c/d vs s/d vs SO)**: Hill's c/d manages pH to prevent oxalates. Hill's   s/d is highly acidic to dissolve struvites. Royal Canin SO uses high sodium for dilution.   If a query specifies an acronym (e.g., "c/d"), DO NOT substitute another brand's urinary   diet (e.g., "SO"), as their mechanisms conflict.
  * **Renal**: k/d (Hill's).
  * **Allergy/Dermatology**: z/d, d/d (Hill's), Ultamino, HP (Royal Canin), HA (Purina).   These use hydrolyzed proteins.
- **Condition Mapping**: If the query specifies a disease ("cat kidney food"), only return relevant Rx diets designed for renal failure.
