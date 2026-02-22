### Seafood and Shellfish — Scoring Guidance

This query targets fish and shellfish.

**Critical distinctions to enforce:**

- **Species is hard**: Salmon vs cod vs tuna vs tilapia are not interchangeable when specified. Shellfish type matters (shrimp vs crab vs lobster vs scallops).
- **Raw vs cooked**: raw vs cooked vs smoked vs breaded are distinct products.
- **Fresh vs frozen**: Seafood is frequently sold frozen; match the query’s explicit storage state. "Fresh" should not return frozen/previously frozen unless the query explicitly allows it.
- **Seafood size jargon is meaningful**:
  * Shrimp sizes like "21/25" indicate a count-per-pound range; lower numbers     mean larger shrimp.
  * "U" means "under" (e.g., "U-10" scallops = under 10 per pound).
  If the query includes these, treat them as hard constraints (not marketing).
- **Shell-on/peeled/deveined/tail-on**: These are meaningful preparation formats; enforce when specified.
- **IQF**: Individually quick frozen means pieces are frozen separately (not clumped). If the query asks for IQF, treat it as a format constraint.
- **Wild-caught vs farmed**: Treat as hard when query specifies.

**Common disqualifiers / critical errors**:
- Returning shelf-stable canned fish for fresh seafood queries (and vice versa) unless query explicitly allows.
