"""Foodservice vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

FOODSERVICE = VerticalContext(
    core=load_prompt("verticals/foodservice/core.md"),
    overlays={
        "beverage_equipment": VerticalOverlay(
            description=(
                "Beverage EQUIPMENT — coffee machines, espresso machines, fountain "
                "dispensers, frozen drink machines, tea brewers, draft beer systems "
                "(NOT consumable drink products)"
            ),
            content=load_prompt("verticals/foodservice/overlays/beverage_equipment.md"),
        ),
        "underbar": VerticalOverlay(
            description=(
                "Bar undercounter & workstation hardware: underbar cocktail stations, "
                "ice bins, bar sinks, speed rails, blender stations (not beverage "
                "dispensing machines)"
            ),
            content=load_prompt("verticals/foodservice/overlays/underbar.md"),
        ),
        "water_filtration": VerticalOverlay(
            description=(
                "Water filters and filtration systems for ice machines, "
                "coffee/espresso, steamers, beverage dispensers, and equipment "
                "protection"
            ),
            content=load_prompt("verticals/foodservice/overlays/water_filtration.md"),
        ),
        "replacement_parts": VerticalOverlay(
            description=(
                "Replacement parts, repair kits, and maintenance items for commercial "
                "foodservice equipment (not whole equipment units)"
            ),
            content=load_prompt("verticals/foodservice/overlays/replacement_parts.md"),
        ),
        "beverages": VerticalOverlay(
            description=(
                "Consumable drinks: coffee, tea, soda syrups, juices, water, beer/wine "
                "(NOT equipment)"
            ),
            content=load_prompt("verticals/foodservice/overlays/beverages.md"),
        ),
        "cooking": VerticalOverlay(
            description=(
                "Cooking equipment: ranges, ovens, fryers, griddles, grills, steamers, "
                "kettles, warmers (not ventilation)"
            ),
            content=load_prompt("verticals/foodservice/overlays/cooking.md"),
        ),
        "dairy_eggs": VerticalOverlay(
            description=(
                "Dairy & eggs: milk, cream, cheese, butter, eggs, yogurt, dairy "
                "alternatives"
            ),
            content=load_prompt("verticals/foodservice/overlays/dairy_eggs.md"),
        ),
        "dry_goods": VerticalOverlay(
            description=(
                "Dry pantry goods: flour, sugar, salt, spices, canned goods, rice, "
                "pasta, oils, sauces, baking supplies"
            ),
            content=load_prompt("verticals/foodservice/overlays/dry_goods.md"),
        ),
        "disposables": VerticalOverlay(
            description=(
                "Single-use and disposable items: cups, lids, takeout containers, "
                "cutlery, gloves, film/foil, napkins, paper goods"
            ),
            content=load_prompt("verticals/foodservice/overlays/disposables.md"),
        ),
        "food_prep": VerticalOverlay(
            description=(
                "Food prep equipment: mixers, slicers, processors, scales, cutters, "
                "prep stations (not cookware/smallwares)"
            ),
            content=load_prompt("verticals/foodservice/overlays/food_prep.md"),
        ),
        "furniture": VerticalOverlay(
            description=(
                "Restaurant seating, tables, booths, bar stools, and dining room "
                "furniture"
            ),
            content=load_prompt("verticals/foodservice/overlays/furniture.md"),
        ),
        "janitorial": VerticalOverlay(
            description=(
                "Facility cleaning: sanitizers, floor care, mops, can liners, paper "
                "dispensers, dilution systems"
            ),
            content=load_prompt("verticals/foodservice/overlays/janitorial.md"),
        ),
        "frozen_dessert_equipment": VerticalOverlay(
            description=(
                "Frozen dessert equipment: soft serve machines, shake machines, ice "
                "cream dipping cabinets, gelato machines"
            ),
            content=load_prompt(
                "verticals/foodservice/overlays/frozen_dessert_equipment.md"
            ),
        ),
        "refrigeration": VerticalOverlay(
            description=(
                "Refrigeration & freezers for cold storage and cold prep (reach-ins, "
                "undercounters, prep tables, walk-ins; not ice makers)"
            ),
            content=load_prompt("verticals/foodservice/overlays/refrigeration.md"),
        ),
        "ice_machines": VerticalOverlay(
            description=(
                "Ice makers, ice machine heads, undercounter ice machines, ice bins, "
                "and ice dispensers (not refrigerators/freezers)"
            ),
            content=load_prompt("verticals/foodservice/overlays/ice_machines.md"),
        ),
        "serving_holding": VerticalOverlay(
            description=(
                "Serving and holding: hot holding cabinets, soup warmers, steam "
                "tables, heat lamps, food wells, display cases"
            ),
            content=load_prompt("verticals/foodservice/overlays/serving_holding.md"),
        ),
        "storage_transport": VerticalOverlay(
            description=(
                "Storage and transport: shelving, racks, carts, ingredient bins, food "
                "pan carriers, transport cabinets"
            ),
            content=load_prompt("verticals/foodservice/overlays/storage_transport.md"),
        ),
        "smallwares": VerticalOverlay(
            description=(
                "Pans, food storage, utensils, cookware, and kitchen hand tools (not "
                "disposables)"
            ),
            content=load_prompt("verticals/foodservice/overlays/smallwares.md"),
        ),
        "tabletop": VerticalOverlay(
            description=(
                "Tabletop: plates, bowls, glassware, flatware, servingware, barware "
                "(reusable, not disposables)"
            ),
            content=load_prompt("verticals/foodservice/overlays/tabletop.md"),
        ),
        "ventilation": VerticalOverlay(
            description=(
                "Kitchen ventilation: hoods, make-up air, exhaust fans, filters, fire "
                "suppression (not cooking equipment)"
            ),
            content=load_prompt("verticals/foodservice/overlays/ventilation.md"),
        ),
        "proteins": VerticalOverlay(
            description=(
                "Meat and seafood: beef, pork, poultry, fish, shellfish, processed "
                "proteins"
            ),
            content=load_prompt("verticals/foodservice/overlays/proteins.md"),
        ),
        "prepared_foods": VerticalOverlay(
            description=(
                "Prepared foods: frozen entrees, appetizers, ready-to-eat items, "
                "par-cooked products"
            ),
            content=load_prompt("verticals/foodservice/overlays/prepared_foods.md"),
        ),
        "produce": VerticalOverlay(
            description=(
                "Produce: fruits, vegetables, fresh herbs, fresh-cut, bulk produce and "
                "case packs"
            ),
            content=load_prompt("verticals/foodservice/overlays/produce.md"),
        ),
        "plumbing": VerticalOverlay(
            description=(
                "Commercial kitchen plumbing & fixtures: sinks, faucets, floor drains, "
                "grease traps/interceptors, and plumbing hardware"
            ),
            content=load_prompt("verticals/foodservice/overlays/plumbing.md"),
        ),
        "waste_reduction": VerticalOverlay(
            description=(
                "Waste handling and waste reduction: garbage disposers, waste pulpers, "
                "trash compactors, and fryer-oil disposal equipment"
            ),
            content=load_prompt("verticals/foodservice/overlays/waste_reduction.md"),
        ),
        "warewash": VerticalOverlay(
            description=(
                "Commercial dishwashers and glasswashers, racks, dishtables, and "
                "dishmachine chemicals (not general janitorial)"
            ),
            content=load_prompt("verticals/foodservice/overlays/warewash.md"),
        ),
    },
)
