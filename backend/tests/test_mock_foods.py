"""The mock food library must use real taxonomy ingredients and give every planted trigger enough foods."""

import csv

from scripts.mock_users.foods import FOODS_BY_SLOT
from scripts.mock_users.shapes import load_user_types
from scripts.mock_users.symptoms import ingredient_components
from scripts.seed_taxonomy import INGREDIENTS_CSV

ALL_FOODS = [food for foods in FOODS_BY_SLOT.values() for food in foods]


def _components(food):
    by_ingredient = ingredient_components()
    return {c for ingredient in food.ingredients for c in by_ingredient.get(ingredient, ())}


def test_every_ingredient_is_a_canonical_taxonomy_name():
    with open(INGREDIENTS_CSV, newline="", encoding="utf-8") as f:
        canonical_names = {row["canonical_name"] for row in csv.DictReader(f)}

    for food in ALL_FOODS:
        for ingredient in food.ingredients:
            assert ingredient in canonical_names, f"{food.name}: '{ingredient}' is not a canonical taxonomy name"


def test_food_names_are_unique():
    names = [food.name for food in ALL_FOODS]

    assert len(names) == len(set(names))


def test_each_trigger_component_is_in_several_foods():
    types, _ = load_user_types()

    for user_type in types.values():
        if user_type.trigger:
            with_trigger = [f for f in ALL_FOODS if user_type.trigger.component in _components(f)]
            assert len(with_trigger) >= 3, f"only {len(with_trigger)} foods contain {user_type.trigger.component}"


def test_each_slot_has_foods_without_each_trigger():
    types, _ = load_user_types()
    triggers = [t.trigger.component for t in types.values() if t.trigger]

    for slot, foods in FOODS_BY_SLOT.items():
        for component in triggers:
            assert any(component not in _components(f) for f in foods), f"every {slot} has {component}"


def test_level_zero_rows_do_not_count_as_containing_a_component():
    # ghee -> milk_protein is listed at concentration level 0 in ingredient_components.csv
    assert "milk_protein" not in ingredient_components().get("ghee", frozenset())
