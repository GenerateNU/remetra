"""Food-group labels from onboarding, and the taxonomy rows each one expands to."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FoodGroup:
    """Component slugs and ingredient slugs that one onboarding chip covers."""

    components: tuple[str, ...] = ()
    slugs: tuple[str, ...] = ()


# Chip text is the contract with the app. Poultry and legumes are regulars-only;
# the rest appear on at least one of the exclusion, suspicion, or regulars screens.
ONBOARDING_GROUPS: dict[str, FoodGroup] = {
    "Alcohol": FoodGroup(components=("alcohol",)),
    "Beans & lentils": FoodGroup(components=("gos",)),
    "Citrus": FoodGroup(
        slugs=(
            "orange",
            "lemon",
            "lime",
            "grapefruit",
            "mandarin",
            "orange_juice",
            "lemon_juice",
            "lime_juice",
            "grapefruit_juice",
        )
    ),
    "Coffee": FoodGroup(slugs=("coffee", "espresso", "instant_coffee", "decaf_coffee")),
    "Dairy": FoodGroup(components=("lactose", "milk_protein")),
    "Eggs": FoodGroup(components=("egg",)),
    "Fish": FoodGroup(components=("fish",)),
    "Gluten": FoodGroup(components=("gluten",)),
    "Legumes": FoodGroup(components=("gos",)),
    "Mushrooms": FoodGroup(slugs=("button_mushrooms", "canned_mushrooms", "oyster_mushrooms")),
    "Nightshades": FoodGroup(components=("nightshades",)),
    "Onion & garlic": FoodGroup(components=("fructans_allium",)),
    "Peanuts": FoodGroup(components=("peanut",)),
    "Pork": FoodGroup(slugs=("pork", "ham", "bacon", "uncured_bacon", "lard")),
    "Poultry": FoodGroup(slugs=("chicken_breast", "turkey_breast")),
    "Red meat": FoodGroup(components=("mammalian_meat",)),
    "Sesame": FoodGroup(components=("sesame",)),
    "Shellfish": FoodGroup(components=("shellfish",)),
    "Soy": FoodGroup(components=("soy",)),
    "Spicy food": FoodGroup(components=("capsaicin",)),
    "Tree nuts": FoodGroup(components=("tree_nuts",)),
}
