from datetime import datetime

import pytest

from analysis.algorithm import get_analysis
from analysis.models import FoodLogEntry, SymptomLogEntry


def food(ts: str, ingredients: list[str]) -> FoodLogEntry:
    return FoodLogEntry(timestamp=datetime.fromisoformat(ts), ingredients=ingredients)


def symptom(ts: str, name: str, intensity: int) -> SymptomLogEntry:
    return SymptomLogEntry(
        timestamp=datetime.fromisoformat(ts),
        symptom_name=name,
        location="",
        sensation="",
        intensity=intensity,
    )


# ---------------------------------------------------------------------------
# Basic metrics
# ---------------------------------------------------------------------------


def test_trigger_rate_base_rate_and_rr():
    # gluten appears before 2 of 3 bloating events, and in 3 of 4 total food logs
    food_logs = [
        food("2024-01-01T08:00", ["gluten"]),  # within window of symptom 1
        food("2024-01-02T08:00", ["gluten"]),  # within window of symptom 2
        food("2024-01-03T08:00", ["gluten"]),  # NOT within any symptom window
        food("2024-01-04T08:00", ["rice"]),  # within window of symptom 3
    ]
    symptom_logs = [
        symptom("2024-01-01T10:00", "bloating", 7),
        symptom("2024-01-02T10:00", "bloating", 5),
        symptom("2024-01-04T10:00", "bloating", 3),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=4)
    gluten = result["bloating"]["gluten"]

    assert gluten.trigger_rate == 0.6667
    assert gluten.base_rate == 1
    assert 0.0 <= gluten.fishers_p_value <= 1.0


def test_average_intensity():
    food_logs = [
        food("2024-01-01T08:00", ["dairy"]),
        food("2024-01-02T08:00", ["dairy"]),
    ]
    symptom_logs = [
        symptom("2024-01-01T10:00", "cramps", 4),
        symptom("2024-01-02T10:00", "cramps", 8),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=4)
    assert result["cramps"]["dairy"].average_intensity == pytest.approx(6.0)


# ---------------------------------------------------------------------------
# Fisher's exact — direction check
# ---------------------------------------------------------------------------


def test_fishers_p_value_high_for_no_association():
    # ingredient appears at the same rate before symptoms and otherwise
    food_logs = [
        food("2024-01-01T08:00", ["wheat"]),
        food("2024-01-02T08:00", ["wheat"]),
        food("2024-01-03T08:00", ["wheat"]),
        food("2024-01-04T08:00", ["wheat"]),
    ]
    # only 1 of 4 food events precedes a symptom — same rate as base
    symptom_logs = [symptom("2024-01-01T10:00", "nausea", 3)]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=4)
    # RR ≈ 1, p-value should not be significant
    assert result["nausea"]["wheat"].fishers_p_value > 0.05


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_ingredient_never_before_symptom_is_absent_from_result():
    food_logs = [
        food("2024-01-01T08:00", ["safe"]),
        food("2024-01-02T06:00", ["trigger"]),  # outside 2h window
    ]
    symptom_logs = [symptom("2024-01-02T10:00", "bloating", 5)]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=2)
    assert "trigger" not in result.get("bloating", {})


def test_no_food_logs_returns_empty():
    result = get_analysis([], [symptom("2024-01-01T10:00", "pain", 3)], time_window_hours=4)
    assert result == {}


def test_no_symptom_logs_returns_empty():
    result = get_analysis([food("2024-01-01T08:00", ["gluten"])], [], time_window_hours=4)
    assert result == {}


def test_multiple_symptoms_independent():
    food_logs = [
        food("2024-01-01T08:00", ["gluten"]),
        food("2024-01-02T08:00", ["dairy"]),
    ]
    symptom_logs = [
        symptom("2024-01-01T10:00", "bloating", 6),
        symptom("2024-01-02T10:00", "cramps", 4),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=4)
    assert "gluten" in result["bloating"]
    assert "dairy" in result["cramps"]
    assert "dairy" not in result["bloating"]
    assert "gluten" not in result["cramps"]


# ---------------------------------------------------------------------------
# Multi-ingredient foods
# ---------------------------------------------------------------------------


def test_multi_ingredient_food_all_ingredients_counted():
    """A single food with 4 ingredients before a symptom should create
    entries for all 4 ingredients, not just the food."""
    food_logs = [
        food("2024-01-01T08:00", ["wheat flour", "yeast", "salt", "butter"]),
        food("2024-01-02T08:00", ["rice", "soy sauce", "vegetables"]),
    ]
    symptom_logs = [
        symptom("2024-01-01T12:00", "bloating", 7),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)
    bloating = result.get("bloating", {})
    # all 4 ingredients from the bread should appear
    for ing in ["wheat flour", "yeast", "salt", "butter"]:
        assert ing in bloating, f"{ing} missing from results"
    # rice/soy/vegetables were not in the window before the symptom
    for ing in ["rice", "soy sauce", "vegetables"]:
        assert ing not in bloating, f"{ing} should not appear"


def test_shared_ingredient_across_foods_counted_once_per_symptom():
    """Two foods in the same 6hr window both contain 'salt'. Salt should
    be counted once for this symptom event, not twice. If it were counted
    twice, a (count) would exceed S and c = S - a would go negative."""
    food_logs = [
        food("2024-01-01T08:00", ["wheat flour", "yeast", "salt"]),  # bread
        food("2024-01-01T10:00", ["eggs", "butter", "salt"]),  # eggs
        # day without symptom
        food("2024-01-02T08:00", ["rice", "chicken"]),
    ]
    symptom_logs = [
        symptom("2024-01-01T13:00", "bloating", 6),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)
    bloating = result.get("bloating", {})

    salt = bloating["salt"]
    assert salt.trigger_rate == 1, "Every salt event occured before bloating, should be 1"
    assert salt.base_rate == 0, "Every bloating symptom had a salt in the window before"
    assert salt.average_intensity == 6


def test_confounded_ingredients_both_surface():
    """Wheat flour and yeast always appear together (they're both in bread).
    Both should surface with similar trigger rates since the algorithm
    can't separate them."""
    food_logs = [
        food("2024-01-01T08:00", ["wheat flour", "yeast", "salt"]),
        food("2024-01-02T08:00", ["wheat flour", "yeast", "salt"]),
        food("2024-01-03T08:00", ["wheat flour", "yeast", "salt"]),
        food("2024-01-04T08:00", ["wheat flour", "yeast", "salt"]),
        food("2024-01-05T08:00", ["wheat flour", "yeast", "salt"]),
        # non-bread days
        food("2024-01-06T08:00", ["rice", "chicken"]),
        food("2024-01-07T08:00", ["rice", "chicken"]),
        food("2024-01-08T08:00", ["rice", "chicken"]),
    ]
    symptom_logs = [
        symptom("2024-01-01T12:00", "bloating", 7),
        symptom("2024-01-02T12:00", "bloating", 6),
        symptom("2024-01-03T12:00", "bloating", 8),
        symptom("2024-01-04T12:00", "bloating", 5),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)
    bloating = result.get("bloating", {})
    assert "wheat flour" in bloating
    assert "yeast" in bloating
    # they should have identical trigger rates since they always co-occur
    assert bloating["wheat flour"].trigger_rate == bloating["yeast"].trigger_rate


# ---------------------------------------------------------------------------
# Overlapping ingredient sets — credit assignment
# ---------------------------------------------------------------------------


def test_overlapping_ingredients_different_trigger_rates():
    """Meals A (gluten + dairy) and B (dairy + rice) both contain dairy.
    Only meal A precedes symptoms. Gluten should have a higher trigger
    rate than dairy, and dairy higher than rice."""
    food_logs = [
        # meal A days — gluten + dairy, symptom follows
        # meal B days — dairy + rice, no symptom
        food("2024-01-01T08:00", ["gluten", "dairy", "salt"]),
        food("2024-01-02T08:00", ["dairy", "rice", "salt"]),
        food("2024-01-03T08:00", ["gluten", "dairy", "salt"]),
        food("2024-01-04T08:00", ["dairy", "rice", "salt"]),
        food("2024-01-05T08:00", ["gluten", "dairy", "salt"]),
        food("2024-01-06T08:00", ["dairy", "rice", "salt"]),
        food("2024-01-07T08:00", ["gluten", "dairy", "salt"]),
        food("2024-01-08T08:00", ["dairy", "rice", "salt"]),
        food("2024-01-09T08:00", ["gluten", "dairy", "salt"]),
        food("2024-01-10T08:00", ["dairy", "rice", "salt"]),
    ]
    symptom_logs = [
        symptom("2024-01-01T12:00", "bloating", 7),
        symptom("2024-01-03T12:00", "bloating", 6),
        symptom("2024-01-05T12:00", "bloating", 8),
        symptom("2024-01-07T12:00", "bloating", 7),
        symptom("2024-01-09T12:00", "bloating", 6),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)
    bloating = result.get("bloating", {})

    # gluten: 5 exposures, 5 before symptoms → trigger_rate = 1.0
    assert bloating["gluten"].trigger_rate == pytest.approx(1.0)
    # dairy: 10 exposures, 5 before symptoms → trigger_rate = 0.5
    assert bloating["dairy"].trigger_rate == pytest.approx(0.5)
    assert bloating["dairy"].base_rate == pytest.approx(0)
    # rice: 5 exposures, 0 before symptoms → should not appear or trigger_rate = 0
    assert "rice" not in bloating or bloating["rice"].trigger_rate == pytest.approx(0.0)


def test_ingredient_in_window_from_different_foods():
    """Garlic appears in two different food events eaten before the same symptom.
    Exposures = 2 because there were two distinct food events containing garlic,
    both of which preceded the symptom. Each food event is its own exposure."""
    food_logs = [
        food("2024-01-01T08:00", ["garlic", "olive oil", "chicken"]),
        food("2024-01-01T11:00", ["garlic", "tomato", "pasta"]),
        # control day
        food("2024-01-02T08:00", ["rice", "chicken"]),
    ]
    symptom_logs = [
        symptom("2024-01-01T14:00", "nausea", 5),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)
    nausea = result.get("nausea", {})
    assert nausea["garlic"].exposures == 2


def test_overlapping_symptom_windows_food_counted_once():
    """A food event that falls inside two overlapping symptom windows (e.g.
    nausea at 10:00 and again at 11:00, both with a 6-hour window) must only
    count as one exposure. trigger_rate must stay <= 1.0."""
    food_logs = [
        food("2024-01-01T08:00", ["garlic"]),  # in both windows
        food("2024-01-01T09:00", ["garlic"]),  # in both windows
        food("2024-01-02T08:00", ["rice"]),  # control — no symptom follows
    ]
    symptom_logs = [
        symptom("2024-01-01T10:00", "nausea", 5),
        symptom("2024-01-01T11:00", "nausea", 7),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)
    nausea = result.get("nausea", {})

    garlic = nausea["garlic"]
    # 2 distinct garlic food events, each counted once despite overlapping windows
    assert garlic.exposures == 2
    # trigger_rate must never exceed 1.0
    assert garlic.trigger_rate <= 1.0
    assert garlic.trigger_rate == pytest.approx(1.0)
    # intensities from both symptom events are collected
    assert garlic.average_intensity == pytest.approx(6.0)  # mean of [5, 7, 5, 7]


# ---------------------------------------------------------------------------
# Intensity tracking with multi-ingredient foods
# ---------------------------------------------------------------------------


def test_intensity_tracked_per_ingredient_across_events():
    """Different symptom events have different intensities. Each ingredient
    in the window should record the intensity of the symptom it preceded."""
    food_logs = [
        food("2024-01-01T08:00", ["gluten", "dairy"]),
        food("2024-01-02T08:00", ["gluten", "rice"]),
        food("2024-01-03T08:00", ["dairy", "rice"]),
    ]
    symptom_logs = [
        symptom("2024-01-01T12:00", "bloating", 4),  # gluten + dairy
        symptom("2024-01-02T12:00", "bloating", 8),  # gluten + rice
        symptom("2024-01-03T12:00", "bloating", 6),  # dairy + rice
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)
    bloating = result.get("bloating", {})

    # gluten: intensities [4, 8] → avg 6.0
    assert bloating["gluten"].average_intensity == pytest.approx(6.0)
    # dairy: intensities [4, 6] → avg 5.0
    assert bloating["dairy"].average_intensity == pytest.approx(5.0)
    # rice: intensities [8, 6] → avg 7.0
    assert bloating["rice"].average_intensity == pytest.approx(7.0)


# ---------------------------------------------------------------------------
# Multiple symptoms from same multi-ingredient meal
# ---------------------------------------------------------------------------


def test_one_food_triggers_multiple_symptom_types():
    """A single multi-ingredient meal precedes two different symptom types.
    Each symptom type should independently track the ingredients."""
    food_logs = [
        food("2024-01-01T08:00", ["gluten", "dairy", "tomato"]),
        food("2024-01-02T08:00", ["rice", "chicken"]),
        food("2024-01-03T08:00", ["gluten", "dairy", "tomato"]),
        food("2024-01-04T08:00", ["rice", "chicken"]),
        food("2024-01-05T08:00", ["gluten", "dairy", "tomato"]),
    ]
    symptom_logs = [
        # bloating follows all gluten meals
        symptom("2024-01-01T12:00", "bloating", 6),
        symptom("2024-01-03T12:00", "bloating", 7),
        symptom("2024-01-05T12:00", "bloating", 8),
        # headache only follows some gluten meals
        symptom("2024-01-01T13:00", "headache", 5),
        symptom("2024-01-05T13:00", "headache", 7),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)

    # bloating: gluten has 3 exposed out of 3 exposures
    assert result["bloating"]["gluten"].exposures == 3
    # headache: gluten has 2 exposed out of 3 exposures
    assert result["headache"]["gluten"].exposures == 2


# ---------------------------------------------------------------------------
# Null ingredients handling
# ---------------------------------------------------------------------------


def test_food_with_no_ingredients_is_skipped():
    """Foods like 'Banana' have ingredients=None or []. They should not
    crash the algorithm or contribute phantom ingredients."""
    food_logs = [
        FoodLogEntry(timestamp=datetime.fromisoformat("2024-01-01T08:00"), ingredients=[]),
        FoodLogEntry(timestamp=datetime.fromisoformat("2024-01-02T08:00"), ingredients=["gluten"]),
    ]
    symptom_logs = [
        symptom("2024-01-01T12:00", "bloating", 5),
        symptom("2024-01-02T12:00", "bloating", 7),
    ]
    # should not raise
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)
    assert "gluten" in result.get("bloating", {})


# ---------------------------------------------------------------------------
# Window boundary precision with multi-ingredient meals
# ---------------------------------------------------------------------------


def test_window_boundary_includes_exact_edge():
    """A food eaten exactly 6 hours before a symptom should be included
    in a 6-hour window. A food at 6h01m should not."""
    food_logs = [
        food("2024-01-01T05:59", ["soy", "rice"]),  # 6h01m before — outside
        food("2024-01-01T06:00", ["gluten", "dairy"]),  # exactly 6hrs before
    ]
    symptom_logs = [
        symptom("2024-01-01T12:00", "bloating", 5),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)
    bloating = result.get("bloating", {})

    assert "gluten" in bloating
    assert "dairy" in bloating
    assert "soy" not in bloating
    assert "rice" not in bloating


# ---------------------------------------------------------------------------
# Realistic multi-food meal scenario
# ---------------------------------------------------------------------------


def test_realistic_meal_with_shared_base_ingredients():
    """Simulate a realistic dinner: pasta (gluten, water, salt), marinara
    (tomato, garlic, olive oil, salt), and salad (lettuce, olive oil, salt).
    Salt and olive oil appear in multiple dishes. All should be counted
    once per symptom event."""
    food_logs = [
        # dinner on day 1 — three dishes
        food("2024-01-01T18:00", ["gluten", "water", "salt"]),  # pasta
        food("2024-01-01T18:00", ["tomato", "garlic", "olive oil", "salt"]),  # sauce
        food("2024-01-01T18:00", ["lettuce", "olive oil", "salt"]),  # salad
        # lunch on day 2 — safe meal
        food("2024-01-02T12:00", ["rice", "chicken", "broccoli"]),
        # dinner on day 3 — same pasta dinner
        food("2024-01-03T18:00", ["gluten", "water", "salt"]),
        food("2024-01-03T18:00", ["tomato", "garlic", "olive oil", "salt"]),
        food("2024-01-03T18:00", ["lettuce", "olive oil", "salt"]),
        # lunch on day 4 — safe meal
        food("2024-01-04T12:00", ["rice", "chicken", "broccoli"]),
        # dinner on day 5 — pasta again
        food("2024-01-05T18:00", ["gluten", "water", "salt"]),
        food("2024-01-05T18:00", ["tomato", "garlic", "olive oil", "salt"]),
        food("2024-01-05T18:00", ["lettuce", "olive oil", "salt"]),
    ]
    symptom_logs = [
        symptom("2024-01-01T22:00", "bloating", 7),
        symptom("2024-01-03T22:00", "bloating", 6),
        symptom("2024-01-05T22:00", "bloating", 8),
    ]
    result = get_analysis(food_logs, symptom_logs, time_window_hours=6)
    bloating = result.get("bloating", {})

    assert bloating["salt"].exposures == 9
    assert bloating["gluten"].exposures == 3
    assert bloating["olive oil"].exposures == 6

    # rice/chicken/broccoli only appear on non-symptom days
    for ing in ["rice", "chicken", "broccoli"]:
        assert ing not in bloating or bloating[ing].exposures == 0
