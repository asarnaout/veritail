### Test and Measurement — Scoring Guidance

This query involves measurement instruments, gauges, precision measuring tools, or calibration equipment.

**Critical distinctions to enforce:**

- **Multimeter CAT ratings are NOT cumulative**: CAT (measurement category) ratings define safety against transient voltage spikes:
  * CAT I = electronic circuits (lowest transient energy)
  * CAT II = single-phase receptacle outlets
  * CAT III = distribution panels, branch circuits
  * CAT IV = utility entrance, service drops (highest transient energy)
  A CAT II 1000V meter is NOT safer than a CAT III 600V meter for panel work — CAT III requires much higher transient withstand capability. The CAT level matters more than the voltage rating for safety. If the query specifies a CAT rating, treat as hard.
- **Pressure gauge accuracy classes (ASME B40.100)**: Grade 4A = ±0.1%, 3A = ±0.25%, 2A = ±0.5%, 1A = ±1%, A = ±2%, B = ±3%, D = ±5%. Accuracy is percentage of FULL SCALE, not of reading — a 100 PSI gauge with Grade A accuracy is ±2 PSI across its entire range, meaning at 10 PSI the actual error could be 20% of reading. If accuracy class is specified, match it.
- **Calibration certificate types are not equivalent**: "Certificate of Conformance" (non-specific) ≠ "Certificate of Calibration" (with data) ≠ "ISO 17025 Accredited Calibration Certificate" (third-party verified). "NIST-traceable" means an unbroken chain of comparisons to a national standard — it does NOT mean calibrated BY NIST. If the query specifies calibration type, enforce it.
- **Precision measuring tools**: Calipers and micrometers have resolution (smallest readable increment: 0.001", 0.0001") and accuracy (conformance to true value) as separate specs. Digital vs dial vs vernier are different reading methods with different capabilities. If resolution or accuracy is specified, treat as hard.
- **Torque wrench types**: Click, beam, dial, and electronic torque wrenches have different accuracy specs (±4% clockwise is typical per ASME B107.300). Drive size (1/4", 3/8", 1/2", 3/4", 1") and torque range are both hard constraints.

**Terminology**:
- CAT III = measurement category III (distribution panel level)
- DMM = digital multimeter
- NIST-traceable = traceable calibration chain (not calibrated by NIST)
- ISO 17025 = accredited calibration laboratory standard
