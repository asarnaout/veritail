"""Groceries vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

GROCERIES = VerticalContext(
    core=load_prompt("verticals/groceries/core.md"),
    overlays={
        "nutrition_free_from": VerticalOverlay(
            description=(
                "Dietary restrictions and regulated label claims: gluten-free, "
                "allergen-free, vegan, keto/low-carb, sugar-free/no added sugar, low "
                "sodium, kosher/halal (cross-category)."
            ),
            content=load_prompt("verticals/groceries/overlays/nutrition_free_from.md"),
        ),
        "produce_fresh": VerticalOverlay(
            description=(
                "Fresh produce: fruits, vegetables, herbs, salad kits, and produce "
                "sold by each/bunch/bag or by weight (per lb/kg). Excludes "
                "frozen/canned produce."
            ),
            content=load_prompt("verticals/groceries/overlays/produce_fresh.md"),
        ),
        "meat_poultry": VerticalOverlay(
            description=(
                "Meat & poultry (not seafood): beef, pork, chicken, turkey, lamb; "
                "ground meat ratios (80/20), steaks/roasts, bone-in vs boneless, fresh "
                "vs frozen poultry, and animal-raising label nuances."
            ),
            content=load_prompt("verticals/groceries/overlays/meat_poultry.md"),
        ),
        "seafood_shellfish": VerticalOverlay(
            description=(
                "Seafood & shellfish: fish fillets/steaks, shrimp, scallops, crab, "
                "lobster, mussels, oysters; size jargon (shrimp 21/25, scallops U-10), "
                "IQF, wild-caught vs farmed, raw vs cooked."
            ),
            content=load_prompt("verticals/groceries/overlays/seafood_shellfish.md"),
        ),
        "deli_prepared": VerticalOverlay(
            description=(
                "Deli and prepared foods: sliced-to-order deli meat/cheese, "
                "pre-packaged deli, rotisserie chicken, salads, heat-and-eat meals. "
                "Often sold by the pound/variable weight."
            ),
            content=load_prompt("verticals/groceries/overlays/deli_prepared.md"),
        ),
        "dairy_eggs": VerticalOverlay(
            description=(
                "Dairy & eggs (chilled): milk, cream, yogurt, cheese, butter, eggs/egg "
                "substitutes, and dairy alternatives (oat/almond/soy). Includes "
                "lactose-free vs dairy-free nuances."
            ),
            content=load_prompt("verticals/groceries/overlays/dairy_eggs.md"),
        ),
        "bakery_bread": VerticalOverlay(
            description=(
                "Bakery & bread: loaves, buns, bagels, tortillas/wraps, rolls, "
                "pastries, fresh bakery vs packaged bread. Excludes baking ingredients "
                "like flour/yeast."
            ),
            content=load_prompt("verticals/groceries/overlays/bakery_bread.md"),
        ),
        "frozen_foods": VerticalOverlay(
            description=(
                "Frozen foods: frozen meals, frozen vegetables, frozen fruit, frozen "
                "pizza, ice cream and novelties, frozen meat/seafood; includes IQF "
                "items."
            ),
            content=load_prompt("verticals/groceries/overlays/frozen_foods.md"),
        ),
        "pantry_cooking": VerticalOverlay(
            description=(
                "Pantry & cooking ingredients: canned goods, pasta, rice, beans, "
                "spices, oils, sauces/condiments, baking staples (flour, sugar, baking "
                "soda/powder), and specialty ingredient queries (e.g., DOP San Marzano "
                "tomatoes)."
            ),
            content=load_prompt("verticals/groceries/overlays/pantry_cooking.md"),
        ),
        "snacks_candy": VerticalOverlay(
            description=(
                "Snacks & candy: chips, crackers, cookies, granola bars, nuts, trail "
                "mix, candy, gum/mints, jerky, snack multipacks."
            ),
            content=load_prompt("verticals/groceries/overlays/snacks_candy.md"),
        ),
        "beverages_soft_drinks": VerticalOverlay(
            description=(
                "Beverages (non-alcohol): soda, sparkling water, still water, juice, "
                "sports/energy drinks, drink mixes, kids drinks. Focus on pack sizes "
                "(12-pack/24-pack), diet/zero/caffeine-free variants, and carbonation "
                "types (seltzer vs tonic vs club soda)."
            ),
            content=load_prompt(
                "verticals/groceries/overlays/beverages_soft_drinks.md"
            ),
        ),
        "coffee_tea": VerticalOverlay(
            description=(
                "Coffee & tea: whole bean, ground, instant, pods/capsules, K-Cup, "
                "Nespresso Original vs Vertuo, espresso vs drip grind, tea bags vs "
                "loose leaf, caffeinated vs decaf."
            ),
            content=load_prompt("verticals/groceries/overlays/coffee_tea.md"),
        ),
        "cleaning_disinfectants": VerticalOverlay(
            description=(
                "Cleaning and disinfection: household cleaners, disinfectants, "
                "sanitizers, bleach, wipes, sprays, bathroom/kitchen cleaners, pest "
                "control. Focus on disinfect vs sanitize vs clean and EPA registration "
                "nuances."
            ),
            content=load_prompt(
                "verticals/groceries/overlays/cleaning_disinfectants.md"
            ),
        ),
        "laundry": VerticalOverlay(
            description=(
                "Laundry: laundry detergent, pods, liquid, powder, fabric softener, "
                "stain remover, bleach boosters, dryer sheets. Focus on HE vs "
                "standard, scent/free & clear, and format."
            ),
            content=load_prompt("verticals/groceries/overlays/laundry.md"),
        ),
        "paper_disposables_trash": VerticalOverlay(
            description=(
                "Paper, disposables, and trash: paper towels, toilet paper, tissues, "
                "napkins, paper plates/cups, plastic wrap/bags, trash bags, food "
                "storage (zip bags), disposable tableware."
            ),
            content=load_prompt(
                "verticals/groceries/overlays/paper_disposables_trash.md"
            ),
        ),
        "health_otc_vitamins": VerticalOverlay(
            description=(
                "Health & wellness: OTC medicines, first aid, allergy/cold/flu, pain "
                "relief, digestive health, vitamins and supplements. Focus on active "
                "ingredient, strength, dosage form, count, and age targeting."
            ),
            content=load_prompt("verticals/groceries/overlays/health_otc_vitamins.md"),
        ),
        "personal_care_beauty": VerticalOverlay(
            description=(
                "Personal care & beauty: shampoo/conditioner, body wash, deodorant, "
                "razors, skincare, makeup, sun care, oral care, feminine care, "
                "incontinence. Focus on scent, skin sensitivity, and product type."
            ),
            content=load_prompt("verticals/groceries/overlays/personal_care_beauty.md"),
        ),
        "baby_care": VerticalOverlay(
            description=(
                "Baby care: diapers (sizes newborn-7), wipes, baby toiletries, baby "
                "food, and infant feeding (infant formula "
                "powder/concentrate/ready-to-feed). Includes infant vs toddler formula "
                "distinction."
            ),
            content=load_prompt("verticals/groceries/overlays/baby_care.md"),
        ),
        "pet_supplies": VerticalOverlay(
            description=(
                "Pet supplies: dog/cat food, treats, litter, pet health items. Focus "
                "on species, life stage (puppy/kitten/adult/senior), diet claims "
                "(grain-free, limited ingredient), and wet vs dry formats."
            ),
            content=load_prompt("verticals/groceries/overlays/pet_supplies.md"),
        ),
        "adult_beverages_alcohol": VerticalOverlay(
            description=(
                "Adult beverages (alcohol): beer, wine, spirits, hard seltzer/RTD "
                "cocktails. Focus on ABV/proof, style/varietal, package size, and "
                "non-alcoholic vs alcoholic distinctions."
            ),
            content=load_prompt(
                "verticals/groceries/overlays/adult_beverages_alcohol.md"
            ),
        ),
    },
)
