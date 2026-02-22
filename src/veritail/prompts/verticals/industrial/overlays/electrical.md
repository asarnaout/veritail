### Electrical Components — Scoring Guidance

This query involves electrical distribution, wiring, protection, or enclosure components — wire, cable, conduit, connectors, fuses, breakers, enclosures, relays, or terminal blocks.

**Critical distinctions to enforce:**

- **AWG is inverse**: Smaller AWG number = larger wire. 10 AWG is larger than 14 AWG. This counter-intuitive convention means "larger gauge" is ambiguous — clarify by actual AWG number. Key ampacity values (NEC Table 310.16, copper, 75°C column): 14 AWG = 20A, 12 AWG = 25A, 10 AWG = 35A, 8 AWG = 50A, 6 AWG = 65A. However, NEC 240.4(D) limits overcurrent protection to 15A for 14 AWG, 20A for 12 AWG, and 30A for 10 AWG, regardless of actual ampacity.
- **Wire insulation types are not interchangeable**: THHN (thermoplastic, high heat 90°C dry, nylon jacket) is the most common building wire. Most modern THHN is dual-rated THHN/THWN-2, approved for 90°C wet and dry. XHHW-2 is cross-linked polyethylene rated 90°C wet/dry, preferred for larger sizes. THHN is not rated for direct burial; UF (underground feeder) or USE-2 is required. If the query specifies an insulation type, match it.
- **Conduit trade sizes are nominal**: 1/2" EMT has an OD of ~0.840" and an ID of ~0.706" — NOT 0.500". Trade sizes are labels with no direct dimensional meaning. EMT, IMC, and rigid (RMC) conduit in the same trade size have different wall thicknesses and therefore different IDs. Conduit type (EMT, IMC, rigid, PVC, FMC, LFMC) is a hard constraint — they use different fittings and have different code applications.
- **NEMA enclosure ratings ≠ IP ratings**: NEMA includes tests for corrosion, icing, oil, and gasket aging that IP does not. A NEMA-rated enclosure meets or exceeds the mapped IP rating, but an IP-rated enclosure does NOT necessarily meet the corresponding NEMA standard. Key mappings: NEMA 1 ≈ IP10 (indoor), NEMA 3R ≈ IP14 (outdoor rain), NEMA 4 ≈ IP66 (watertight), NEMA 4X ≈ IP66 + corrosion resistance, NEMA 12 ≈ IP52 (dust/drip). NEMA numbering is non-linear — NEMA 12 provides LESS water protection than NEMA 4.
- **Fuse classes are physical rejection features**: Class J, RK1, RK5, CC, and T fuses have different physical dimensions to prevent incorrect insertion. Class J provides highest current-limiting performance. RK1 and RK5 share dimensions with non-current-limiting Class H, but R-type rejection holders prevent insertion of Class H. If a specification requires a specific fuse class, it is a hard constraint — often tied to equipment UL listing.
- **Circuit breaker frame and trip**: Breaker frame size determines physical dimensions and maximum amperage. Trip rating is the actual overcurrent setpoint. Both frame and trip must match. Bolt-on, plug-in, and DIN-rail mount are physically incompatible form factors.

**Terminology**:
- EMT = electrical metallic tubing (thin-wall conduit)
- IMC = intermediate metal conduit
- RMC = rigid metal conduit
- FMC = flexible metal conduit ("Greenfield")
- LFMC = liquid-tight flexible metal conduit ("Sealtite")
- NEMA 4X = outdoor watertight + corrosion resistant (stainless/fiberglass)
