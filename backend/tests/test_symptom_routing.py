import pytest

from schemas.symptom_log import SymptomFamily, SymptomRoute, SymptomRouteType
from services.symptom_routing import get_routing, load_routing, route_symptom

# Mirrors frontend/src/types/symptomOptions.ts (the frontend isn't mounted in the backend container).
SENSATION_OPTIONS = [
    "Bloating", "Pain", "Stiffness", "Fatigue", "Swelling", "Burning", "Tingling", "Numbness", "Itching",
    "Cramping", "Throbbing", "Weakness", "Tenderness", "Tightness", "Aching", "Soreness", "Sensitivity",
    "Heaviness", "Spasms", "Prickling", "Pressure", "Bleeding", "Other",
]  # fmt: skip
LOCATION_OPTIONS = [
    "Whole Body", "Head", "Neck", "Jaw", "Chest", "Upper Back", "Lower Back", "Abdomen", "Shoulders", "Elbows",
    "Wrists", "Hands / Fingers", "Hips", "Knees", "Ankles", "Feet / Toes", "Eyes", "Skin", "Throat",
    "Joints (Multiple)",
]  # fmt: skip


@pytest.mark.parametrize(
    ("sensation", "location", "route"),
    [
        ("Pain", "Chest", SymptomRouteType.RED_FLAG),
        ("Tightness", "Chest", SymptomRouteType.RED_FLAG),
        ("Bleeding", "Knees", SymptomRouteType.RED_FLAG),
        ("Bleeding", "Abdomen", SymptomRouteType.RED_FLAG),
        ("Itching", "Throat", SymptomRouteType.ALLERGY_LIKE),
        ("Swelling", "Eyes", SymptomRouteType.ALLERGY_LIKE),
    ],
)
def test_safety_routes_have_message_and_no_family(sensation, location, route):
    # Act
    result = route_symptom(sensation, location)
    # Assert
    assert result.route == route
    assert result.family is None
    assert result.safety_message


@pytest.mark.parametrize(
    ("sensation", "location", "family"),
    [
        ("Bloating", "Abdomen", SymptomFamily.GI),
        ("Pain", "Abdomen", SymptomFamily.GI),
        ("Itching", "Skin", SymptomFamily.SKIN),
        ("Throbbing", "Head", SymptomFamily.HEAD),
        ("Tingling", "Skin", SymptomFamily.OTHER),
        ("Aching", "Joints (Multiple)", SymptomFamily.OTHER),
        ("Fatigue", "Whole Body", SymptomFamily.OTHER),
        ("Burning", "Chest", SymptomFamily.OTHER),
    ],
)
def test_model_routes_set_family(sensation, location, family):
    # Act
    result = route_symptom(sensation, location)
    # Assert
    assert result.route == SymptomRouteType.MODEL
    assert result.family == family
    assert result.safety_message is None


def test_matching_ignores_case_and_whitespace():
    # Act
    result = route_symptom("  PAIN ", " chest")
    # Assert
    assert result.route == SymptomRouteType.RED_FLAG


def test_uses_routing_passed_in():
    # Arrange
    routing = {"safety_messages": {}, "rules": [], "default": {"route": "model", "family": "head"}}
    # Act
    result = route_symptom("pain", "chest", routing=routing)
    # Assert
    assert result.route == SymptomRouteType.MODEL
    assert result.family == SymptomFamily.HEAD


def test_get_routing_is_cached_and_matches_file():
    # Act
    routing = get_routing()
    # Assert
    assert routing is get_routing()
    assert routing == load_routing()


@pytest.mark.parametrize("location", LOCATION_OPTIONS)
@pytest.mark.parametrize("sensation", SENSATION_OPTIONS)
def test_every_frontend_option_resolves(sensation, location):
    # Act
    result = route_symptom(sensation, location)
    # Assert
    assert isinstance(result, SymptomRoute)
    assert (result.family is not None) == (result.route == SymptomRouteType.MODEL)


def test_unknown_values_fall_back_to_other_model():
    # Act
    result = route_symptom("Wobbly", "Left Pinky")
    # Assert
    assert result.route == SymptomRouteType.MODEL
    assert result.family == SymptomFamily.OTHER


def test_every_yaml_value_is_a_frontend_option():
    # Arrange
    sensations = {s.lower() for s in SENSATION_OPTIONS}
    locations = {loc.lower() for loc in LOCATION_OPTIONS}
    # Act
    rules = get_routing()["rules"]
    # Assert
    for rule in rules:
        assert set(rule.get("sensations", [])) <= sensations, rule["id"]
        assert set(rule.get("locations", [])) <= locations, rule["id"]


def test_every_safety_rule_cites_a_source():
    # Act
    safety_rules = [r for r in get_routing()["rules"] if r["route"] != SymptomRouteType.MODEL]
    # Assert
    assert safety_rules
    for rule in safety_rules:
        assert rule.get("sources"), rule["id"]
