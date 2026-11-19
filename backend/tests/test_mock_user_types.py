"""The mock user type config must only name real taxonomy components and sensible delay windows."""

import yaml

from scripts.mock_users.shapes import load_user_types
from scripts.seed_taxonomy import COMPONENTS_YAML


def test_user_types_load_with_starting_types():
    types, background_rate = load_user_types()

    assert set(types) == {"onion_garlic", "lactose", "alcohol", "no_trigger"}
    assert types["no_trigger"].trigger is None
    assert background_rate > 0


def test_trigger_components_exist_in_taxonomy():
    types, _ = load_user_types()
    components = {c["id"] for c in yaml.safe_load(COMPONENTS_YAML.read_text(encoding="utf-8"))["components"]}

    for user_type in types.values():
        if user_type.trigger:
            assert user_type.trigger.component in components, user_type.name


def test_delay_windows_are_valid():
    types, _ = load_user_types()

    for user_type in types.values():
        if user_type.trigger:
            assert 0 <= user_type.trigger.delay_min_hours < user_type.trigger.delay_max_hours, user_type.name
