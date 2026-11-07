"""The mock food library must use real taxonomy ingredients and give every planted trigger enough foods."""

from scripts.mock_users.foods import FOODS_BY_SLOT
from scripts.mock_users.shapes import load_user_types
from services.taxonomy_service import TaxonomyService

ALL_FOODS = [food for foods in FOODS_BY_SLOT.values() for food in foods]


def _components(food, service):
    return {c for match in service.lookup_many(food.ingredients) for c in match.components}


def test_every_ingredient_is_a_canonical_taxonomy_name():
    service = TaxonomyService()

    for food in ALL_FOODS:
        for ingredient in food.ingredients:
            match = service.lookup(ingredient)
            assert not match.is_unknown, f"{food.name}: '{ingredient}' is not in the taxonomy"
            assert match.canonical_name == ingredient, f"{food.name}: use '{match.canonical_name}'"


def test_food_names_are_unique():
    names = [food.name for food in ALL_FOODS]

    assert len(names) == len(set(names))


def test_each_trigger_component_is_in_several_foods():
    service = TaxonomyService()
    types, _ = load_user_types()

    for user_type in types.values():
        if user_type.trigger:
            with_trigger = [f for f in ALL_FOODS if user_type.trigger.component in _components(f, service)]
            assert len(with_trigger) >= 3, f"only {len(with_trigger)} foods contain {user_type.trigger.component}"


def test_each_slot_has_foods_without_each_trigger():
    service = TaxonomyService()
    types, _ = load_user_types()
    triggers = [t.trigger.component for t in types.values() if t.trigger]

    for slot, foods in FOODS_BY_SLOT.items():
        for component in triggers:
            assert any(component not in _components(f, service) for f in foods), f"every {slot} has {component}"
