"""Sporting goods vertical context for LLM judge guidance."""

from veritail.types import VerticalContext, VerticalOverlay

SPORTING_GOODS = VerticalContext(
    core="""\
## Vertical: Sporting Goods

You are evaluating search results for a sporting goods and athletic equipment \
ecommerce site. Think like a composite buyer spanning the travel-ball parent \
sourcing certified gear for a youth league, the weekend warrior seeking exact \
biomechanical fits, the backcountry athlete matching mechanical interfaces, and \
the competitive player outfitting to league regulations. In sporting \
goods, the wrong sport, wrong certification, wrong size, or wrong skill tier \
is not a close match — it is unusable equipment, a safety hazard, or a \
league-compliance violation.

### Scoring considerations

The following scoring considerations are organized by priority tier — hard \
constraints first. Hard constraints are the most important and should dominate \
the score.

- **Sport and activity as the primary hard gate**: When the query specifies \
or strongly implies a sport or activity, every result must be \
designed for that sport or a clearly compatible one. Equipment engineered for \
one sport is rarely transferable to another due to differing mechanical, safety, \
and aerodynamic properties. Cross-sport results should be penalized heavily.
- **League, sanctioning-body, and regulation compliance**: Sporting goods \
operate under a web of governing-body rules (e.g., FINA, USGA, USA Baseball, FIFA) \
that function as hard constraints. When a query implies a league or level of play, \
treat certification compliance as a non-negotiable filter. Uncertified gear is banned.
- **Safety certification as a non-negotiable constraint**: Protective \
equipment carries mandatory certifications (e.g., NOCSAE, ASTM, CPSC, USCG, CE). \
An uncertified or wrong-standard safety device is a critical safety failure, not a budget alternative.
- **Equipment sizing systems are functional, not cosmetic**: Sporting goods use \
dozens of incompatible sizing systems that carry precise mechanical implications. \
When a query specifies any sizing parameter, treat it as a hard constraint with zero tolerance for mismatch.
- **Skill level and performance tier appropriateness**: Sporting goods are \
engineered for distinct skill tiers. Advanced gear is often punishing, dangerous, or unusable \
for beginners, while beginner gear breaks under advanced loads. Match the skill tier explicitly.
- **Gender and age specificity as functional constraints**: Gender and age designations \
encode real engineering differences (e.g., flex patterns, cuff heights, opening circumferences, weight ratings). \
Returning adult equipment for a youth query is a fit failure and potentially a safety issue.
- **Position-specific equipment within team sports**: Many team sports require \
position-specialized gear that is functionally incompatible across positions. \
Returning equipment designed for a different position is a relevance failure.
- **Handedness and directional specifications**: Many sporting goods are \
handed, and returning the wrong orientation renders the product unusable. \
Treat explicit handedness parameters as hard constraints. Pay attention to inverse labeling conventions.
- **Game vs. practice grade**: Practice-grade items differ materially from \
game-spec items in durability and materials. Align results with the intent of the query.
- **Terrain, environment, and conditions specificity**: Gear engineered for specific environments \
fails in others (e.g., saltwater vs freshwater, hard court vs grass, indoor vs outdoor). \
Results must match the environmental constraint.
- **System versus individual component intent**: Distinguish between complete kits \
and individual replacement components. A component is not a kit, and a kit is not a replacement part.
- **Brand as specification vs. preference**: Some brands dictate exact mechanical profiles \
or hold exclusive league licenses. Do not substitute competing brands unless the query is clearly open-ended.
""",
    overlays={
        "golf_clubs_and_wedges": VerticalOverlay(
            description=(
                "Golf equipment including drivers, irons, putters, and wedges. Covers technical "
                "club specifications like bounce, grind, loft, and shaft flex."
            ),
            content="""\
### Golf Clubs and Wedges — Scoring Guidance

**Critical distinctions to enforce:**
- **Bounce**: The angle between the club's leading edge and the ground. High bounce is for soft turf/fluffy sand; low bounce is for firm turf/tight lies. Do not treat "high bounce" as a generic positive attribute; it is a functional constraint.
- **Grind**: The removal of material from the sole to alter turf interaction when the face is manipulated. If a specific grind letter (e.g., M-Grind, S-Grind) is requested, it is a hard constraint.
- **Shaft Flex**: Ladies (L), Senior/Amateur (A), Regular (R), Stiff (S), and Extra Stiff (X). Mismatching flex leads to severe ball-flight errors. Treat as a hard constraint.
- **Handedness**: Left-handed (LH) and Right-handed (RH) clubs are physically mirrored and cannot be interchanged.

**LLM Heuristic Traps (Do not assume):**
- Do not assume a "pitching wedge" is a substitute for a "lob wedge" or "sand wedge." Loft angles dictate distance and trajectory entirely.
- Do not confuse individual clubs with full sets. A query for "Callaway Irons" generally implies a set (e.g., 4-PW), whereas "Callaway 7 iron" implies a single replacement club.
""",
        ),
        "cycling_drivetrains_and_components": VerticalOverlay(
            description=(
                "Bicycle components including groupsets, derailleurs, shifters, cassettes, and brakes "
                "for road, gravel, and mountain bikes."
            ),
            content="""\
### Cycling Components — Scoring Guidance

**Critical distinctions to enforce:**
- **Brand Ecosystems**: Shimano, SRAM, and Campagnolo components are fundamentally incompatible with one another. A Shimano shifter will not pull the correct amount of cable for a SRAM derailleur. Treat brand as a hard mechanical constraint.
- **Tier Hierarchies**:
  - Shimano Road: Dura-Ace (Top) > Ultegra > 105 > Tiagra > Sora > Claris.
  - SRAM Road: Red (Top) > Force > Rival > Apex.
- **Electronic vs Mechanical**: Di2 (Shimano), eTap/AXS (SRAM), and EPS (Campagnolo) designate electronic shifting. Do not return mechanical components for electronic queries and vice versa.
- **Speed count**: A 12-speed cassette requires a 12-speed chain and 12-speed derailleur. 11-speed is not a substitute.

**LLM Heuristic Traps (Do not assume):**
- "105" in a query refers to the highly popular Shimano 105 groupset tier, not a measurement or quantity.
- Do not assume road components fit mountain bikes. Pull ratios and mounting standards differ completely.
""",
        ),
        "winter_sports_hardgoods": VerticalOverlay(
            description=(
                "Skis, snowboards, ski boots, and bindings. Covers technical interfaces like "
                "DIN settings, Mondopoint sizing, and sole compatibility norms."
            ),
            content="""\
### Winter Sports Hardgoods — Scoring Guidance

**Critical distinctions to enforce:**
- **Sole and Binding Norms (Safety Critical)**:
  - ISO 5355 (Alpine): Traditional flat soles.
  - ISO 23223 (GripWalk): Rockered, high-traction rubber soles.
  - ISO 9523 (Touring): Heavily rockered backcountry soles.
  Standard Alpine bindings DO NOT safely accept GripWalk or Touring soles; they will fail to release in a crash. Bindings must explicitly state GripWalk or MNC (Multi-Norm Compatible) to accept them.
- **DIN Settings**: Represents the release force of the binding. High DIN (12+) is for experts/heavy skiers. Low DIN is for beginners/youth. Returning high DIN gear for beginners introduces severe physical risk.
- **Mondopoint**: Ski boot sizing is measured in centimeters (e.g., 26.5). It does not directly translate to US shoe sizes without a chart, and half-size mismatches are physical failures.

**LLM Heuristic Traps (Do not assume):**
- Do not assume WTR (Walk-To-Ride) is the same as GripWalk. WTR is an older, incompatible standard unless the binding is MNC.
- A "system ski" includes bindings; a "flat ski" does not. Match the query intent exactly.
""",
        ),
        "fishing_rods_and_reels": VerticalOverlay(
            description=(
                "Fishing equipment including rods, reels, line, and combos. Covers technical specifications "
                "like rod action, rod power, and water type."
            ),
            content="""\
### Fishing Rods and Reels — Scoring Guidance

**Critical distinctions to enforce:**
- **Power vs Action**: These are NOT synonyms.
  - *Power* (Ultra-Light to Extra Heavy) indicates the rod's strength and weight capacity.
  - *Action* (Slow to Extra Fast) indicates where the rod bends and how fast it returns to straight. Extra Fast bends only at the tip; Slow bends into the handle.
- **Reel Type Compatibility**: Baitcasting reels sit on top of the rod and require a casting rod (with a trigger grip). Spinning reels hang below the rod and require a spinning rod (larger guides, no trigger). They are completely incompatible.
- **Environment**: Saltwater reels contain sealed, corrosion-resistant bearings. Freshwater reels used in saltwater will quickly corrode and fail.

**LLM Heuristic Traps (Do not assume):**
- Do not assume an "Ultra-Light" rod is simply a rod that weighs less; it is a specific power rating for targeting small fish (panfish/trout) with very light lures.
- Do not substitute a baitcaster for a spinning reel, even if they are in the same price tier.
""",
        ),
        "archery_bows_and_arrows": VerticalOverlay(
            description=(
                "Archery equipment including recurve bows, compound bows, arrows, and accessories. "
                "Covers spine stiffness, ILF compatibility, and AMO lengths."
            ),
            content="""\
### Archery Equipment — Scoring Guidance

**Critical distinctions to enforce:**
- **Arrow Spine (Safety Critical)**: Spine measures the stiffness (deflection) of the arrow. A LOWER number indicates a STIFFER arrow (e.g., 300 spine is stiffer than 600 spine). Shooting an under-spined (high number, highly flexible) arrow from a heavy bow can cause the arrow to shatter into the user's hand.
- **Limb Mounting Systems**: ILF (International Limb Fitting) is a universal standard. Hoyt Formula is a proprietary system. Formula limbs DO NOT fit ILF risers, and vice versa.
- **AMO Length**: Archery Manufacturers Organization standard. The physical string length must be approximately 3 to 4 inches shorter than the stated AMO bow length.

**LLM Heuristic Traps (Do not assume):**
- Do not assume higher spine numbers mean stronger arrows. It is the exact opposite.
- Do not penalize a 65" string returned for a 68" AMO bow query; this is the mathematically correct sizing.
- Do not substitute crossbow bolts for vertical bow arrows.
""",
        ),
        "racket_and_paddle_sports": VerticalOverlay(
            description=(
                "Tennis rackets, pickleball paddles, and squash/badminton gear. Covers swingweight, "
                "grip sizes, head balance, and core materials."
            ),
            content="""\
### Racket and Paddle Sports — Scoring Guidance

**Critical distinctions to enforce:**
- **Static Weight vs Swingweight**: Static weight is simply the mass on a scale. Swingweight is a dynamic measure of how heavy the racket feels when swung (dictated by balance). A light racket can have a very heavy swingweight if it is Head-Heavy.
- **Grip Size**: Tennis grips are measured in 1/8-inch increments (e.g., 4 1/8", 4 1/4", 4 3/8", 4 1/2"). These are hard constraints; the wrong grip size causes tendonitis.
- **Pickleball Cores**:
  - Polymer/Polypropylene: The modern standard, quiet, good touch/control.
  - Nomex: Hard, very loud, high power.
  - Aluminum: Lightweight, less power, prone to denting.

**LLM Heuristic Traps (Do not assume):**
- Do not assume a "lightweight" racket automatically has a low swingweight or is highly maneuverable.
- If a user asks for a "quiet" pickleball paddle for neighborhood play, strictly penalize Nomex core paddles.
""",
        ),
        "field_sports_footwear": VerticalOverlay(
            description=(
                "Cleats and turf shoes for field sports like soccer, football, lacrosse, and rugby. "
                "Covers specific soleplate types and stud patterns."
            ),
            content="""\
### Field Sports Footwear — Scoring Guidance

**Critical distinctions to enforce:**
- **Surface Ratings (Safety Critical)**:
  - FG (Firm Ground): Fixed, rigid plastic studs for natural grass.
  - AG (Artificial Grass): Shorter, hollow, numerous studs to prevent getting stuck in synthetic turf.
  - SG (Soft Ground): Long, metal, removable studs for wet mud.
  - TF (Turf): Hundreds of tiny rubber nubs for thin carpet turf.
  - IN/IC (Indoor): Flat rubber soles for hard courts.
- **Safety Hazard**: Using FG cleats on AG surfaces causes the studs to stick and rotate, leading to severe knee/ACL ligament tears. Returning FG cleats for an AG query is a critical failure.

**LLM Heuristic Traps (Do not assume):**
- Do not treat football, soccer, and lacrosse cleats as fully interchangeable. Soccer cleats lack a front toe stud (to allow clean kicking), whereas football and lacrosse cleats require a toe stud for forward blocking/acceleration.
""",
        ),
        "team_licensed_jerseys": VerticalOverlay(
            description=(
                "Officially licensed apparel for professional sports teams (NFL, NBA, MLB, NHL). "
                "Covers distinct manufacturing tiers like Authentic, Swingman, Elite, and Replica."
            ),
            content="""\
### Team Licensed Jerseys — Scoring Guidance

**Critical distinctions to enforce:**
- **Manufacturing Tiers (NFL)**:
  - Elite: Exact on-field specs, sewn twill, elastic sleeves, performance chassis (Highest tier).
  - Limited: Sewn or premium heat-sealed numbers, tailored fit (Mid tier).
  - Game/Legend: Screen-printed, loose casual fit (Lowest tier).
- **Manufacturing Tiers (NBA)**:
  - Authentic: On-court performance fabric, stitched graphics, tailored athletic fit.
  - Swingman: Polyester mesh, premium printed twill.
  - Replica: Screen-printed, wide shoulder cuts.

**LLM Heuristic Traps (Do not assume):**
- Do not assume "Authentic" is just a marketing buzzword for "genuine, non-counterfeit product." In this context, Authentic/Elite denotes a specific, highly expensive manufacturing tier. Do not return a Replica when an Authentic is queried.
""",
        ),
        "hockey_skates_and_sticks": VerticalOverlay(
            description=(
                "Ice hockey and roller hockey equipment. Covers skate volume profiles (Fit 1/2/3), "
                "stick flex, and kickpoints."
            ),
            content="""\
### Hockey Skates and Sticks — Scoring Guidance

**Critical distinctions to enforce:**
- **Skate Fit Profiles**: Modern skates use a 3D volume system, replacing standard D/EE widths.
  - Fit 1: Narrow width, low volume.
  - Fit 2: Medium width, medium volume.
  - Fit 3: Wide width, high volume.
  Returning a Fit 1 skate for a player with wide feet is a total functional failure causing extreme pain.
- **Stick Flex**: A numerical rating of how much force it takes to bend the stick. A general rule is half the player's body weight.
- **Kickpoint**: Where the stick bends. Low-kick is optimized for quick releases (snapshots). Mid-kick is optimized for maximum power (heavy slapshots).

**LLM Heuristic Traps (Do not assume):**
- Do not assume "Fit 1" means "Tier 1", "first choice", or premium quality. It strictly denotes anatomical volume.
- Do not confuse ice hockey skates with inline/roller hockey skates.
""",
        ),
        "watersports_flotation": VerticalOverlay(
            description=(
                "Personal Flotation Devices (PFDs), life jackets, and safety gear for boating, "
                "kayaking, and paddleboarding."
            ),
            content="""\
### Watersports Flotation — Scoring Guidance

**Critical distinctions to enforce:**
- **USCG Ratings**: Must enforce USCG Types (I, II, III, IV, V) or Levels (50, 70, 100, 275).
  - Type III / Level 70 is the standard for recreational kayaking/paddleboarding.
  - Type IV is a throwable device (ring/cushion), NOT a wearable jacket.
- **Inflatable vs Standard Foam**: Inflatable PFDs are highly compact but require the user to trigger them manually or wait for auto-submersion mechanisms. They are strictly not recommended for non-swimmers, whitewater, or high-impact watersports.
- **Sizing Standards**: Adult PFDs are sized by chest circumference; Youth/Child PFDs are sized by weight. Match the demographic explicitly.

**LLM Heuristic Traps (Do not assume):**
- Do not return a throwable device (Type IV) if the query implies a wearable vest.
- Do not treat inflatable PFDs as suitable for children or non-swimmers.
""",
        ),
        "camping_shelter_and_sleep": VerticalOverlay(
            description=(
                "Sleeping bags, sleeping pads, and tents. Covers EN/ISO temperature ratings "
                "and R-values."
            ),
            content="""\
### Camping Shelter and Sleep — Scoring Guidance

**Critical distinctions to enforce:**
- **EN/ISO Temperature Ratings**:
  - Comfort Rating: The temperature at which a "cold sleeper" (traditionally baselined as female) sleeps comfortably.
  - Lower Limit Rating: The temperature at which a "warm sleeper" (traditionally baselined as male) sleeps without shivering.
  Women's specific sleeping bags use the Comfort Rating for their marketed name, resulting in them having more insulation/weight than a men's bag marketed with the exact same temperature number.
- **Sleeping Pad R-Value**: Measures thermal resistance/insulation. Winter camping requires an R-value of 4.0 or higher. A 1.0 R-value pad used in winter is a critical safety failure leading to hypothermia.

**LLM Heuristic Traps (Do not assume):**
- Do not assume the number in the product name is the exact survival temperature. It is often rounded for marketing. Always verify the actual EN/ISO test rating.
- Do not return summer-rated gear for winter queries simply because it is high-end or ultralight.
""",
        ),
        "lacrosse_heads": VerticalOverlay(
            description=(
                "Lacrosse heads for men's and women's sticks. Covers positional offsets, "
                "throat widths, and face shapes."
            ),
            content="""\
### Lacrosse Heads — Scoring Guidance

**Critical distinctions to enforce:**
- **Offensive Heads**: Feature a narrow face shape and tight throat. This geometry maximizes ball control, retention during cradling, and shot accuracy.
- **Defensive Heads**: Feature a wider face shape to assist in intercepting passes, knocking down shots, and scooping ground balls in traffic. Constructed with heavier, stiffer plastics to withstand violent poke checks.
- **Universal/Midfield**: A hybrid balance of the two geometries.

**LLM Heuristic Traps (Do not assume):**
- Do not mix men's and women's lacrosse heads. Women's lacrosse rules dictate entirely different pocket depths, sidewall heights, and stringing mechanics. They are physically and legally incompatible.
""",
        ),
        "volleyball_equipment": VerticalOverlay(
            description=(
                "Volleyballs and nets. Covers the distinct mechanical and material differences between "
                "indoor hardcourt and outdoor beach volleyballs."
            ),
            content="""\
### Volleyball Equipment — Scoring Guidance

**Critical distinctions to enforce:**
- **Indoor Volleyballs**: Constructed from smooth leather or synthetic leather with glued panels. They are heavier, smaller (65cm), and highly pressurized (4.3-4.6 psi) to allow for fast gameplay and hard spikes on hardwood.
- **Outdoor/Beach Volleyballs**: Constructed from softer, textured composite materials to grip with sandy/wet hands. They are slightly larger, lighter, and inflated to a much lower pressure to stabilize flight in the wind and allow for softer touches.

**LLM Heuristic Traps (Do not assume):**
- Do not assume an indoor ball can be used at the beach, or vice versa. The pressure and material differences fundamentally alter the physics of the game. If the query specifies the environment, enforce it rigidly.
""",
        ),
        "competitive_swimwear": VerticalOverlay(
            description=(
                "Technical swimwear and goggles for competitive swimming. Covers FINA regulations "
                "and age-group legalities."
            ),
            content="""\
### Competitive Swimwear — Scoring Guidance

**Critical distinctions to enforce:**
- **USA Swimming 12 & Under Rule (Safety/Compliance Critical)**: Swimmers age 12 and under are strictly banned from wearing "Technical Suits."
  - A technical suit is ANY suit with bonded or taped seams, OR any suit with woven fabric extending past the hips.
  - Because most tech suits are FINA approved, ANY suit bearing a standard "FINA Approved" logo is generally ILLEGAL for a 12 & Under swimmer.
  - The only exception is if the suit has a specific USA Swimming green checkmark next to the FINA logo.

**LLM Heuristic Traps (Do not assume):**
- Do not assume "FINA Approved" means the suit is the best choice for a youth swimmer. For 12 & under queries, a FINA-approved tech suit is a compliance violation and must be penalized heavily.
""",
        ),
        "climbing_and_mountaineering": VerticalOverlay(
            description=(
                "Climbing hardware including carabiners, harnesses, ropes, and helmets. Covers "
                "UIAA and CE life-safety certifications."
            ),
            content="""\
### Climbing and Mountaineering — Scoring Guidance

**Critical distinctions to enforce:**
- **Life-Safety Certifications**: All load-bearing climbing equipment MUST bear CE (Conformité Européenne) or UIAA (Union Internationale des Associations d'Alpinisme) certifications. Uncertified gear is a fatal hazard.
- **Statistical Ratings vs Certifications**: "3-Sigma" is a statistical method for determining breaking strength variance; it is NOT an independent safety certification. ISO 9001 denotes factory quality management, not gear safety.

**LLM Heuristic Traps (Do not assume):**
- Do not accept generic marketing terms like "heavy duty" or "tactical" as substitutes for official CE/UIAA certifications in life-safety climbing queries.
""",
        ),
        "baseball_and_softball_gloves": VerticalOverlay(
            description=(
                "Fielding gloves for baseball and softball. Covers leather types (Kip, Steerhide, Cowhide) "
                "and their break-in requirements."
            ),
            content="""\
### Baseball and Softball Gloves — Scoring Guidance

**Critical distinctions to enforce:**
- **Kip / Japanese Kip Leather**: Sourced from younger cattle. Extremely lightweight, tight grain, faster break-in. Preferred by elite infielders requiring fast hand speeds.
- **Steerhide**: Heavy, thick, and highly durable. Requires a grueling, weeks-long break-in period but holds its shape for years. Preferred by professionals.
- **Cowhide / Pigskin**: Budget-friendly, soft, pre-broken-in. Ideal for youth players with lower hand strength.

**LLM Heuristic Traps (Do not assume):**
- Do not recommend a premium, $400 stiff Steerhide glove for an 8-year-old child. The child lacks the hand strength to break it in or squeeze it, rendering the high-quality product functionally useless. Match the leather stiffness to the player profile.
""",
        ),
        "fitness_and_strength_training": VerticalOverlay(
            description=(
                "Home gym equipment, spin bikes, and weight racks. Covers flywheel dynamics "
                "and structural cage differences."
            ),
            content="""\
### Fitness and Strength Training — Scoring Guidance

**Critical distinctions to enforce:**
- **Spin Bike Flywheel Weight**: The heavy disc on a spin bike stores kinetic energy. A heavy flywheel (e.g., 30–40 lbs) produces a smoother, safer operation by generating more momentum, preventing jerky pedal strokes.
- **Power Racks vs Stands**:
  - Power Cage/Rack: Enclosed structure with 4 to 6 vertical posts, featuring safety spotter pins to safely catch dropped weights.
  - Squat Stand: Two vertical posts. Takes up less space but offers significantly less safety for heavy, unspotted lifting.

**LLM Heuristic Traps (Do not assume):**
- Do not confuse a spin bike's flywheel weight with its resistance mechanism (magnetic vs friction pad). They are distinct mechanical systems.
- If a user queries a "power cage," do not return a two-post "squat stand." The structural safety mechanisms are fundamentally different.
""",
        ),
    },
)
