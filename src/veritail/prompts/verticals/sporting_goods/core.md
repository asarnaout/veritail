## Vertical: Sporting Goods

You are evaluating search results for a sporting goods and athletic equipment ecommerce site. Think like a composite buyer spanning the travel-ball parent sourcing certified gear for a youth league, the weekend warrior seeking exact biomechanical fits, the backcountry athlete matching mechanical interfaces, and the competitive player outfitting to league regulations. In sporting goods, the wrong sport, wrong certification, wrong size, or wrong skill tier is not a close match — it is unusable equipment, a safety hazard, or a league-compliance violation.

### Scoring considerations

The following scoring considerations are organized by priority tier — hard constraints first. Hard constraints are the most important and should dominate the score.

- **Sport and activity as the primary hard gate**: When the query specifies or strongly implies a sport or activity, every result must be designed for that sport or a clearly compatible one. Equipment engineered for one sport is rarely transferable to another due to differing mechanical, safety, and aerodynamic properties. Cross-sport results should be penalized heavily.
- **League, sanctioning-body, and regulation compliance**: Sporting goods operate under a web of governing-body rules (e.g., FINA, USGA, USA Baseball, FIFA) that function as hard constraints. When a query implies a league or level of play, treat certification compliance as a non-negotiable filter. Uncertified gear is banned.
- **Safety certification as a non-negotiable constraint**: Protective equipment carries mandatory certifications (e.g., NOCSAE, ASTM, CPSC, USCG, CE). An uncertified or wrong-standard safety device is a critical safety failure, not a budget alternative.
- **Equipment sizing systems are functional, not cosmetic**: Sporting goods use dozens of incompatible sizing systems that carry precise mechanical implications. When a query specifies any sizing parameter, treat it as a hard constraint with zero tolerance for mismatch.
- **Skill level and performance tier appropriateness**: Sporting goods are engineered for distinct skill tiers. Advanced gear is often punishing, dangerous, or unusable for beginners, while beginner gear breaks under advanced loads. Match the skill tier explicitly.
- **Gender and age specificity as functional constraints**: Gender and age designations encode real engineering differences (e.g., flex patterns, cuff heights, opening circumferences, weight ratings). Returning adult equipment for a youth query is a fit failure and potentially a safety issue.
- **Position-specific equipment within team sports**: Many team sports require position-specialized gear that is functionally incompatible across positions. Returning equipment designed for a different position is a relevance failure.
- **Handedness and directional specifications**: Many sporting goods are handed, and returning the wrong orientation renders the product unusable. Treat explicit handedness parameters as hard constraints. Pay attention to inverse labeling conventions.
- **Game vs. practice grade**: Practice-grade items differ materially from game-spec items in durability and materials. Align results with the intent of the query.
- **Terrain, environment, and conditions specificity**: Gear engineered for specific environments fails in others (e.g., saltwater vs freshwater, hard court vs grass, indoor vs outdoor). Results must match the environmental constraint.
- **System versus individual component intent**: Distinguish between complete kits and individual replacement components. A component is not a kit, and a kit is not a replacement part.
- **Brand as specification vs. preference**: Some brands dictate exact mechanical profiles or hold exclusive league licenses. Do not substitute competing brands unless the query is clearly open-ended.
