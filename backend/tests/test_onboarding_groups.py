"""The onboarding chip list and the taxonomy map have to stay the same set of labels."""

from services.onboarding_groups import ONBOARDING_GROUPS

# Kept in step with frontend/src/store/onboardingStore.ts
EXCLUSIONS = [
    "Shellfish",
    "Mushrooms",
    "Pork",
    "Dairy",
    "Eggs",
    "Fish",
    "Peanuts",
    "Tree nuts",
    "Soy",
    "Sesame",
    "Nightshades",
    "Onion & garlic",
    "Spicy food",
    "Beans & lentils",
    "Red meat",
    "Citrus",
    "Alcohol",
    "Coffee",
    "Gluten",
]
SUSPICIONS = [
    "Onion & garlic",
    "Dairy",
    "Coffee",
    "Alcohol",
    "Spicy food",
    "Beans & lentils",
    "Red meat",
    "Citrus",
]
REGULARS = [
    "Dairy",
    "Eggs",
    "Fish",
    "Poultry",
    "Red meat",
    "Legumes",
    "Soy",
    "Tree nuts",
    "Peanuts",
    "Coffee",
    "Alcohol",
]


def test_every_onboarding_chip_maps_to_a_food_group():
    """Each chip the app can send is a key the label endpoint accepts."""
    assert set(EXCLUSIONS + SUSPICIONS + REGULARS) == set(ONBOARDING_GROUPS)


def test_each_food_group_names_taxonomy_rows():
    """A chip with no components and no slugs would save nothing and look successful."""
    for label, group in ONBOARDING_GROUPS.items():
        assert group.components or group.slugs, label
