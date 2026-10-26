"""Safety filters and food-log component history for the daily ingredient pool."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from analysis.models import FoodLogEntry
from analysis.pool_picker import (
    UserContext,
    build_user_context,
    components_eaten_since,
    components_in_log,
    eligible_ingredients,
    has_celiac,
)
from schemas.symptom_log import WashoutStatus
from services.taxonomy_service import TaxonomyService, get_taxonomy

NOW = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
INACTIVE = WashoutStatus(active=False, ends_at=None)
ACTIVE = WashoutStatus(active=True, ends_at=NOW + timedelta(hours=48))

COMPONENTS = {
    "gluten": ["allergen"],
    "fructans_grain": [],
    "milk_protein": ["allergen"],
    "lactose": [],
    "nightshade": [],
}
# ingredient id -> (elimination_base, {component: level}); level-0 rows are trace pairs, as in ghee.
INGREDIENTS = {
    "wheat_bread": (False, {"gluten": 3, "fructans_grain": 2}),
    "pasta": (False, {"gluten": 3}),
    "trace_grain": (False, {"gluten": 0}),
    "cheese": (False, {"milk_protein": 3, "lactose": 1}),
    "ghee": (False, {"milk_protein": 0}),
    "custard": (False, {"gluten": 2, "milk_protein": 3}),
    "tomato": (False, {"nightshade": 3}),
    "maple_syrup": (True, {}),
    "white_rice": (True, {}),
}


def catalog():
    """Shaped like TaxonomyData from the taxonomy PR: CSV strings, pairs keyed by ingredient."""
    return SimpleNamespace(
        components={cid: {"id": cid, "prior_tier": "high", "flags": flags} for cid, flags in COMPONENTS.items()},
        ingredients={
            iid: {"id": iid, "canonical_name": iid.replace("_", " "), "elimination_base": str(base).lower()}
            for iid, (base, _) in INGREDIENTS.items()
        },
        pairs={
            iid: [{"component": cid, "level": str(level)} for cid, level in levels.items()]
            for iid, (_, levels) in INGREDIENTS.items()
            if levels
        },
        allergen_components=frozenset(cid for cid, flags in COMPONENTS.items() if "allergen" in flags),
    )


def lookup(raw: str | None):
    """Stand-in for TaxonomyService.lookup, which returns only levels above 0."""
    components = {
        "cheddar cheese": {"milk_protein": 3, "lactose": 1},
        "bread": {"fructans_grain": 2, "gluten": 3},
        "ghee": {},
    }.get((raw or "").strip().lower(), {})
    return SimpleNamespace(components=components)


def context(*eaten: str, disease: list[str] | None = None) -> UserContext:
    return UserContext(disease=disease or [], components_eaten_last_30_days=set(eaten))


def log(ingredients: list[str], days_ago: float) -> FoodLogEntry:
    return FoodLogEntry(timestamp=NOW - timedelta(days=days_ago), ingredients=ingredients)


class TestCeliac:
    def test_celiac_user_gets_no_gluten_above_zero(self):
        eligible = eligible_ingredients(catalog(), context("gluten", "fructans_grain", disease=["celiac"]), INACTIVE)

        assert "wheat_bread" not in eligible
        assert "pasta" not in eligible
        assert "trace_grain" in eligible

    def test_non_celiac_user_can_get_gluten(self):
        eligible = eligible_ingredients(catalog(), context("gluten", "fructans_grain", disease=["lupus"]), INACTIVE)

        assert "wheat_bread" in eligible
        assert "pasta" in eligible

    @pytest.mark.parametrize("entry", ["celiac", "Celiac disease", "  CELIAC ", "coeliac", "Celiac's"])
    def test_free_text_disease_entries_match_celiac(self, entry):
        assert has_celiac(["IBS", entry])

    @pytest.mark.parametrize("disease", [None, [], ["lupus", "Crohn's"]])
    def test_other_diseases_do_not_match_celiac(self, disease):
        assert not has_celiac(disease)


class TestAllergens:
    def test_no_dairy_in_logs_excludes_milk_protein(self):
        eligible = eligible_ingredients(catalog(), context(), INACTIVE)

        assert "cheese" not in eligible
        assert "custard" not in eligible
        assert "tomato" in eligible

    def test_cheese_logged_last_week_allows_milk_protein(self):
        user = build_user_context(None, [log(["Cheddar Cheese"], days_ago=7)], lookup, NOW)

        assert "cheese" in eligible_ingredients(catalog(), user, INACTIVE)

    def test_trace_allergen_rows_still_need_history(self):
        assert "ghee" not in eligible_ingredients(catalog(), context(), INACTIVE)
        assert "trace_grain" not in eligible_ingredients(catalog(), context(), INACTIVE)
        assert "ghee" in eligible_ingredients(catalog(), context("milk_protein"), INACTIVE)

    def test_eating_a_trace_food_does_not_count_as_eating_the_allergen(self):
        user = build_user_context(None, [log(["ghee"], days_ago=1)], lookup, NOW)

        assert user.components_eaten_last_30_days == set()
        assert "cheese" not in eligible_ingredients(catalog(), user, INACTIVE)

    def test_one_novel_allergen_removes_the_ingredient(self):
        assert "custard" not in eligible_ingredients(catalog(), context("gluten"), INACTIVE)
        assert "custard" in eligible_ingredients(catalog(), context("gluten", "milk_protein"), INACTIVE)

    def test_non_allergen_components_need_no_history(self):
        assert "wheat_bread" in eligible_ingredients(catalog(), context("gluten"), INACTIVE)

    def test_celiac_wins_even_after_eating_gluten(self):
        user = build_user_context(["celiac"], [log(["bread"], days_ago=2)], lookup, NOW)

        assert user.components_eaten_last_30_days == {"gluten", "fructans_grain"}
        assert "wheat_bread" not in eligible_ingredients(catalog(), user, INACTIVE)


class TestWashout:
    def test_washout_keeps_only_elimination_base(self):
        everything = context("gluten", "fructans_grain", "milk_protein", "lactose", "nightshade")

        assert eligible_ingredients(catalog(), everything, ACTIVE) == ["maple_syrup", "white_rice"]

    def test_washout_still_applies_the_other_filters(self):
        taxonomy = catalog()
        taxonomy.ingredients["cheese"]["elimination_base"] = "true"

        assert "cheese" not in eligible_ingredients(taxonomy, context(), ACTIVE)


class TestHistory:
    def test_window_includes_30_days_and_excludes_31(self):
        assert build_user_context(None, [log(["Cheddar Cheese"], 30)], lookup, NOW).components_eaten_last_30_days
        assert not build_user_context(None, [log(["Cheddar Cheese"], 31)], lookup, NOW).components_eaten_last_30_days

    def test_logs_after_now_are_ignored(self):
        assert (
            build_user_context(None, [log(["Cheddar Cheese"], -1)], lookup, NOW).components_eaten_last_30_days == set()
        )

    def test_naive_timestamps_are_utc(self):
        naive = FoodLogEntry(timestamp=datetime(2026, 10, 20, 8, 0), ingredients=["bread"])

        assert components_eaten_since([naive], lookup, since=NOW - timedelta(days=14), now=NOW) == {
            "gluten",
            "fructans_grain",
        }

    def test_components_in_log_skips_blanks_and_unknowns(self):
        assert components_in_log(["", "pizza", "Cheddar Cheese", "cheddar cheese"], lookup) == {
            "milk_protein",
            "lactose",
        }


class TestRealTaxonomy:
    def test_logged_cheese_unlocks_milk_protein_but_ghee_does_not(self):
        service = TaxonomyService()

        cheese = build_user_context(None, [log(["Cheddar Cheese"], days_ago=7)], service.lookup, NOW)
        ghee = build_user_context(None, [log(["ghee"], days_ago=7)], service.lookup, NOW)

        assert "milk_protein" in cheese.components_eaten_last_30_days
        assert "cheese" in eligible_ingredients(service.data, cheese, INACTIVE)
        assert "milk_protein" not in ghee.components_eaten_last_30_days
        assert "cheese" not in eligible_ingredients(service.data, ghee, INACTIVE)
        assert "ghee" not in eligible_ingredients(service.data, ghee, INACTIVE)


def test_filters_hold_on_the_real_taxonomy():
    taxonomy = get_taxonomy()

    def levels(iid):
        return {row["component"]: int(row["level"]) for row in taxonomy.pairs.get(iid, [])}

    celiac = eligible_ingredients(taxonomy, context(*taxonomy.components, disease=["Celiac disease"]), INACTIVE)
    naive = eligible_ingredients(taxonomy, context(), INACTIVE)
    washout = eligible_ingredients(taxonomy, context(*taxonomy.components), ACTIVE)

    assert celiac and naive and washout
    assert all(levels(iid).get("gluten", 0) == 0 for iid in celiac)
    assert all(not levels(iid).keys() & taxonomy.allergen_components for iid in naive)
    assert "ghee" not in naive
    assert all(taxonomy.ingredients[iid]["elimination_base"] == "true" for iid in washout)
