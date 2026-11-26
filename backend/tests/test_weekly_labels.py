"""Unit tests for the pure weekly label rules."""

import math

import pytest

from analysis.weekly_labels import (
    Label,
    combine,
    is_no_clear_pattern,
    label_for,
    load_merge_groups,
    meal_exposures,
    meaningful_components,
    to_probability,
)


def test_to_probability_inverts_log_odds():
    assert to_probability(0.0) == pytest.approx(0.5)
    assert to_probability(math.log(0.04 / 0.96)) == pytest.approx(0.04)


def test_combine_is_chance_at_least_one_is_real():
    # Three families at 4% give 11.5% (docs/model-v2-draft.md)
    assert combine([0.04, 0.04, 0.04]) == pytest.approx(0.115264)
    assert combine([]) == 0.0


class TestMealExposures:
    LEVELS = {"onion": {"fructans_allium": 3}, "garlic powder": {"fructans_allium": 1}, "milk": {"lactose": 2}}

    def test_sums_ingredients_and_caps_at_one(self):
        assert meal_exposures(["onion", "garlic powder"], self.LEVELS) == {"fructans_allium": 1.0}

    def test_matches_case_and_whitespace_insensitively_and_skips_unknown(self):
        exposures = meal_exposures([" Milk ", "unicorn", 42], self.LEVELS)
        assert exposures == {"lactose": pytest.approx(2 / 3)}

    def test_level_one_alone_is_not_meaningful(self):
        exposures = meal_exposures(["garlic powder"], self.LEVELS)
        assert meaningful_components(exposures) == set()
        assert meaningful_components(meal_exposures(["garlic powder", "garlic powder"], self.LEVELS)) == {
            "fructans_allium"
        }


class TestLabelFor:
    def test_likely_trigger_needs_high_confidence_and_recheck(self):
        assert label_for(0.90, 5, recheck_completed=True) == Label.LIKELY_TRIGGER
        assert label_for(0.95, 5, recheck_completed=False) == Label.STILL_LEARNING
        assert label_for(0.89, 5, recheck_completed=True) == Label.STILL_LEARNING

    def test_looks_fine_needs_low_confidence_and_three_exposures(self):
        assert label_for(0.05, 3, recheck_completed=True) == Label.LOOKS_FINE
        assert label_for(0.05, 2, recheck_completed=True) == Label.STILL_LEARNING
        assert label_for(0.051, 10, recheck_completed=True) == Label.STILL_LEARNING


class TestNoClearPattern:
    def test_empty_is_not_no_pattern(self):
        assert is_no_clear_pattern([]) is False

    def test_sixty_percent_fine_and_nothing_concerning(self):
        labelled = [(0.01, Label.LOOKS_FINE)] * 3 + [(0.2, Label.STILL_LEARNING)] * 2
        assert is_no_clear_pattern(labelled) is True

    def test_fails_below_sixty_percent(self):
        labelled = [(0.01, Label.LOOKS_FINE)] * 1 + [(0.2, Label.STILL_LEARNING)] * 1
        assert is_no_clear_pattern(labelled) is False

    def test_fails_when_anything_reaches_thirty_percent(self):
        labelled = [(0.01, Label.LOOKS_FINE)] * 4 + [(0.30, Label.STILL_LEARNING)]
        assert is_no_clear_pattern(labelled) is False


def test_merge_groups_load_from_components_yaml():
    groups = {group.id: group for group in load_merge_groups()}
    assert groups["wheat"].members == ("gluten", "fructans_grain")
    assert groups["dairy"].display_name == "Dairy (lactose or milk protein)"
