### Pharmacy and Parasiticides — Scoring Guidance

This query involves medicinal treatments, pest prevention, or pharmacy items.

**Critical distinctions to enforce:**
- **Lethal Species Toxicity (Permethrin)**: Spot-on flea treatments for dogs frequently contain Permethrin, which is rapidly lethal to cats. A dog flea treatment returned for a cat query is a fatal critical error.
- **Neurological Risks (Isoxazolines)**: The isoxazoline class (Bravecto, Nexgard, Simparica, Credelio) carries FDA warnings for seizure risks. If a query specifies "seizure safe" or "non-systemic", do not return isoxazolines.
- **Strict Weight Banding**: Flea/tick doses are bound by strict weight integers. A dose for a 45-88 lb dog is toxic to a 10 lb dog and ineffective for a 100 lb dog. If the query specifies a weight, the product's band MUST encompass that exact weight.
- **Rx vs OTC**: Understand that antibiotics and specific NSAIDs (Carprofen, Meloxicam) are strictly prescription (Rx) and require veterinary approval.
- **Pharmacy Abbreviations**:
  * SID = once daily
  * BID = twice daily
  * PO = orally
  * mcg = microgram (do not confuse with mg/milligram).
