"""Pet supplies vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

PET_SUPPLIES = VerticalContext(
    core=load_prompt("verticals/pet_supplies/core.md"),
    overlays={
        "otc_pet_nutrition": VerticalOverlay(
            description=(
                "Over-the-counter (OTC) daily nutrition for dogs and cats: dry kibble, "
                "wet food, food toppers, and treats (Excludes prescription/veterinary "
                "diets)."
            ),
            content=load_prompt("verticals/pet_supplies/overlays/otc_pet_nutrition.md"),
        ),
        "veterinary_prescription_diets": VerticalOverlay(
            description=(
                "Veterinary therapeutic and prescription diets for diagnosed medical "
                "conditions (e.g., Hill's Prescription Diet, Royal Canin Veterinary "
                "Diet)."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/veterinary_prescription_diets.md"
            ),
        ),
        "pharmacy_and_parasiticides": VerticalOverlay(
            description=(
                "Flea and tick preventatives, heartworm medication, NSAIDs, "
                "antibiotics, and veterinary pharmacy supplies."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/pharmacy_and_parasiticides.md"
            ),
        ),
        "dog_training_and_walking_gear": VerticalOverlay(
            description=(
                "Dog collars, harnesses, leashes, head halters, and training equipment "
                "for walking and behavioral management."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/dog_training_and_walking_gear.md"
            ),
        ),
        "grooming_equipment": VerticalOverlay(
            description=(
                "Professional and home grooming tools: clippers, clipper blades, "
                "shears, deshedding tools, and shampoos."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/grooming_equipment.md"
            ),
        ),
        "feline_habitat_and_litter": VerticalOverlay(
            description=(
                "Cat litter, litter boxes, waste management, stain/odor removers, and "
                "scratching furniture."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/feline_habitat_and_litter.md"
            ),
        ),
        "aquarium_hardware_and_filtration": VerticalOverlay(
            description=(
                "Fish tank hardware: filtration systems, filter media, lighting, "
                "heaters, and pumps (Freshwater and Marine)."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/aquarium_hardware_and_filtration.md"
            ),
        ),
        "aquatic_livestock_and_medications": VerticalOverlay(
            description=(
                "Fish food, aquatic water conditioners, nitrogen cycle supplements, "
                "and fish medications."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/aquatic_livestock_and_medications.md"
            ),
        ),
        "reptile_husbandry_and_habitat": VerticalOverlay(
            description=(
                "Reptile and amphibian terrariums, substrate, heat lamps, UVB "
                "lighting, and dietary supplements."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/reptile_husbandry_and_habitat.md"
            ),
        ),
        "avian_habitat_and_safety": VerticalOverlay(
            description=(
                "Bird cages, perches, parrot toys, and avian health accessories."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/avian_habitat_and_safety.md"
            ),
        ),
        "small_mammal_husbandry": VerticalOverlay(
            description=(
                "Nutrition, bedding, and habitats for small pocket pets (Guinea pigs, "
                "rabbits, hamsters, rats, ferrets, chinchillas)."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/small_mammal_husbandry.md"
            ),
        ),
        "equine_tack_and_feed": VerticalOverlay(
            description=(
                "Horse equipment, saddles, bits, bridles, and equine nutritional feed."
            ),
            content=load_prompt(
                "verticals/pet_supplies/overlays/equine_tack_and_feed.md"
            ),
        ),
    },
)
