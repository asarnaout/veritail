### Shredders and Data Destruction — Scoring Guidance

This query involves document destruction equipment, which is heavily regulated by international data security standards.

**Critical distinctions to enforce:**

- **DIN 66399 P-Levels (Hard Constraints)**: Shredders are classified by particle size maximums.
  * *P-1 / P-2*: Basic strip-cut (low security).
  * *P-3 / P-4*: Cross-cut (moderate security). P-4 is the minimum standard for general confidential business documents.
  * *P-5*: Micro-cut (high security). Required for highly confidential, personal, or medical (HIPAA) data. Do not return P-3 or P-4 cross-cut shredders for "micro-cut" queries.
  * *P-6 / P-7*: Extremely high security. P-7 is the NSA/CSS standard for Top Secret classified government documents (particles ≤ 5 mm²). If a query requests "NSA approved" or "Top Secret," P-5 and P-6 are critical compliance failures.
- **Sheet Capacity vs. Duty Cycle**: "10-sheet capacity" refers to a single pass, whereas "duty cycle" or "continuous run time" dictates how long the motor can run before cool-down. Match the capacity needs requested by the buyer.
