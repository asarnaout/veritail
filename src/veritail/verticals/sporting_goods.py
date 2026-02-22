"""Sporting goods vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

SPORTING_GOODS = VerticalContext(
    core=load_prompt("verticals/sporting_goods/core.md"),
    overlays={
        "golf_clubs_and_wedges": VerticalOverlay(
            description=(
                "Golf equipment including drivers, irons, putters, and wedges. Covers "
                "technical club specifications like bounce, grind, loft, and shaft "
                "flex."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/golf_clubs_and_wedges.md"
            ),
        ),
        "cycling_drivetrains_and_components": VerticalOverlay(
            description=(
                "Bicycle components including groupsets, derailleurs, shifters, "
                "cassettes, and brakes for road, gravel, and mountain bikes."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/cycling_drivetrains_and_components.md"
            ),
        ),
        "winter_sports_hardgoods": VerticalOverlay(
            description=(
                "Skis, snowboards, ski boots, and bindings. Covers technical "
                "interfaces like DIN settings, Mondopoint sizing, and sole "
                "compatibility norms."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/winter_sports_hardgoods.md"
            ),
        ),
        "fishing_rods_and_reels": VerticalOverlay(
            description=(
                "Fishing equipment including rods, reels, line, and combos. Covers "
                "technical specifications like rod action, rod power, and water type."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/fishing_rods_and_reels.md"
            ),
        ),
        "archery_bows_and_arrows": VerticalOverlay(
            description=(
                "Archery equipment including recurve bows, compound bows, arrows, and "
                "accessories. Covers spine stiffness, ILF compatibility, and AMO "
                "lengths."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/archery_bows_and_arrows.md"
            ),
        ),
        "racket_and_paddle_sports": VerticalOverlay(
            description=(
                "Tennis rackets, pickleball paddles, and squash/badminton gear. Covers "
                "swingweight, grip sizes, head balance, and core materials."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/racket_and_paddle_sports.md"
            ),
        ),
        "field_sports_footwear": VerticalOverlay(
            description=(
                "Cleats and turf shoes for field sports like soccer, football, "
                "lacrosse, and rugby. Covers specific soleplate types and stud "
                "patterns."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/field_sports_footwear.md"
            ),
        ),
        "team_licensed_jerseys": VerticalOverlay(
            description=(
                "Officially licensed apparel for professional sports teams (NFL, NBA, "
                "MLB, NHL). Covers distinct manufacturing tiers like Authentic, "
                "Swingman, Elite, and Replica."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/team_licensed_jerseys.md"
            ),
        ),
        "hockey_skates_and_sticks": VerticalOverlay(
            description=(
                "Ice hockey and roller hockey equipment. Covers skate volume profiles "
                "(Fit 1/2/3), stick flex, and kickpoints."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/hockey_skates_and_sticks.md"
            ),
        ),
        "watersports_flotation": VerticalOverlay(
            description=(
                "Personal Flotation Devices (PFDs), life jackets, and safety gear for "
                "boating, kayaking, and paddleboarding."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/watersports_flotation.md"
            ),
        ),
        "camping_shelter_and_sleep": VerticalOverlay(
            description=(
                "Sleeping bags, sleeping pads, and tents. Covers EN/ISO temperature "
                "ratings and R-values."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/camping_shelter_and_sleep.md"
            ),
        ),
        "lacrosse_heads": VerticalOverlay(
            description=(
                "Lacrosse heads for men's and women's sticks. Covers positional "
                "offsets, throat widths, and face shapes."
            ),
            content=load_prompt("verticals/sporting_goods/overlays/lacrosse_heads.md"),
        ),
        "volleyball_equipment": VerticalOverlay(
            description=(
                "Volleyballs and nets. Covers the distinct mechanical and material "
                "differences between indoor hardcourt and outdoor beach volleyballs."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/volleyball_equipment.md"
            ),
        ),
        "competitive_swimwear": VerticalOverlay(
            description=(
                "Technical swimwear and goggles for competitive swimming. Covers FINA "
                "regulations and age-group legalities."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/competitive_swimwear.md"
            ),
        ),
        "climbing_and_mountaineering": VerticalOverlay(
            description=(
                "Climbing hardware including carabiners, harnesses, ropes, and "
                "helmets. Covers UIAA and CE life-safety certifications."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/climbing_and_mountaineering.md"
            ),
        ),
        "baseball_and_softball_gloves": VerticalOverlay(
            description=(
                "Fielding gloves for baseball and softball. Covers leather types (Kip, "
                "Steerhide, Cowhide) and their break-in requirements."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/baseball_and_softball_gloves.md"
            ),
        ),
        "fitness_and_strength_training": VerticalOverlay(
            description=(
                "Home gym equipment, spin bikes, and weight racks. Covers flywheel "
                "dynamics and structural cage differences."
            ),
            content=load_prompt(
                "verticals/sporting_goods/overlays/fitness_and_strength_training.md"
            ),
        ),
    },
)
