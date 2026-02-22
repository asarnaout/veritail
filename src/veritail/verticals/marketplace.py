"""Marketplace vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

MARKETPLACE = VerticalContext(
    core=load_prompt("verticals/marketplace/core.md"),
    overlays={
        "automotive_parts": VerticalOverlay(
            description=(
                "Automotive parts, car accessories, replacement components, and "
                "fitment-dependent vehicle hardware."
            ),
            content=load_prompt("verticals/marketplace/overlays/automotive_parts.md"),
        ),
        "refurbished_electronics": VerticalOverlay(
            description=(
                "Used, renewed, and refurbished consumer electronics, laptops, "
                "smartphones, and tablets."
            ),
            content=load_prompt(
                "verticals/marketplace/overlays/refurbished_electronics.md"
            ),
        ),
        "graded_collectibles": VerticalOverlay(
            description=(
                "Graded trading cards (sports, Pokémon, MTG) and graded comic books, "
                "involving specific grading authorities like PSA, BGS, CGC."
            ),
            content=load_prompt(
                "verticals/marketplace/overlays/graded_collectibles.md"
            ),
        ),
        "luxury_goods": VerticalOverlay(
            description=(
                "High-end luxury fashion, designer handbags, footwear, and accessories "
                "(e.g., Louis Vuitton, Chanel, Hermes) involving authenticity signals."
            ),
            content=load_prompt("verticals/marketplace/overlays/luxury_goods.md"),
        ),
        "fine_jewelry": VerticalOverlay(
            description=(
                "Fine jewelry, natural diamonds, lab-grown diamonds, and gemstone "
                "certification (GIA, IGI)."
            ),
            content=load_prompt("verticals/marketplace/overlays/fine_jewelry.md"),
        ),
        "power_tools": VerticalOverlay(
            description=(
                "Power tools, cordless drills, saws, impact drivers, and tool "
                "batteries (e.g., DeWalt, Milwaukee, Makita)."
            ),
            content=load_prompt("verticals/marketplace/overlays/power_tools.md"),
        ),
        "apparel_and_footwear": VerticalOverlay(
            description=(
                "General clothing, shoes, sneakers, and apparel sizing variations "
                "across international standards."
            ),
            content=load_prompt(
                "verticals/marketplace/overlays/apparel_and_footwear.md"
            ),
        ),
        "physical_media": VerticalOverlay(
            description=(
                "Vinyl records, LPs, collectible books, first editions, and physical "
                "media."
            ),
            content=load_prompt("verticals/marketplace/overlays/physical_media.md"),
        ),
        "baby_and_juvenile": VerticalOverlay(
            description=(
                "Baby gear, strollers, cribs, car seats, and infant toys subject to "
                "child safety regulations."
            ),
            content=load_prompt("verticals/marketplace/overlays/baby_and_juvenile.md"),
        ),
        "health_and_supplements": VerticalOverlay(
            description=(
                "Vitamins, dietary supplements, skincare, cosmetics, and wellness "
                "goods."
            ),
            content=load_prompt(
                "verticals/marketplace/overlays/health_and_supplements.md"
            ),
        ),
        "video_games": VerticalOverlay(
            description=(
                "Video games, gaming consoles, physical discs/cartridges, and digital "
                "download codes."
            ),
            content=load_prompt("verticals/marketplace/overlays/video_games.md"),
        ),
        "heavy_goods_and_logistics": VerticalOverlay(
            description=(
                "Large appliances (refrigerators, washers), heavy furniture, and goods "
                "requiring freight/LTL shipping."
            ),
            content=load_prompt(
                "verticals/marketplace/overlays/heavy_goods_and_logistics.md"
            ),
        ),
        "sports_safety_equipment": VerticalOverlay(
            description=(
                "Protective athletic gear, helmets, and sports equipment requiring "
                "impact certifications."
            ),
            content=load_prompt(
                "verticals/marketplace/overlays/sports_safety_equipment.md"
            ),
        ),
    },
)
