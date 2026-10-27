"""Safety filters and food-log component history for the daily ingredient pool."""

from collections import Counter
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from analysis.models import FoodLogEntry
from analysis.pool_picker import (
    POOL_SIZE,
    UserContext,
    _highest_level_components,
    build_user_context,
    components_eaten_since,
    components_in_log,
    eligible_ingredients,
    has_celiac,
    rank_pool,
)
from schemas.symptom_log import WashoutStatus
from services.ingredient_pool_service import IngredientPoolService
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


def with_ingredients(taxonomy, **extra: dict[str, int]):
    """Add ingredients to a catalog() copy, each as {component: level}."""
    for iid, levels in extra.items():
        taxonomy.ingredients[iid] = {"id": iid, "canonical_name": iid, "elimination_base": "false"}
        taxonomy.pairs[iid] = [{"component": cid, "level": str(level)} for cid, level in levels.items()]
    return taxonomy


def top_component_counts(taxonomy, pool: list[str]) -> Counter:
    return Counter(component for iid in pool for component in _highest_level_components(taxonomy, iid))


class TestRankPool:
    def test_component_eaten_daily_for_14_days_ranks_below_one_never_eaten(self):
        # pasta (gluten) sorts before tomato (nightshade) on a tie, so only the count can move it down
        assert rank_pool(["pasta", "tomato"], catalog(), {}) == ["pasta", "tomato"]

        assert rank_pool(["pasta", "tomato"], catalog(), {"gluten": 14}) == ["tomato", "pasta"]

    def test_14_daily_logs_count_14_times_and_rank_lower(self):
        service = IngredientPoolService()
        service.taxonomy = SimpleNamespace(lookup=lookup)
        logs = [log(["bread"], days_ago=day) for day in range(14)]

        counts = service._count_recent_components(logs, NOW)

        assert counts["gluten"] == 14
        assert rank_pool(["pasta", "tomato"], catalog(), counts) == ["tomato", "pasta"]

    def test_lower_prior_tier_ranks_lower(self):
        taxonomy = catalog()
        taxonomy.components["gluten"]["prior_tier"] = "low"

        assert rank_pool(["pasta", "tomato"], taxonomy, {}) == ["tomato", "pasta"]

    def test_never_three_with_the_same_highest_level_component(self):
        taxonomy = with_ingredients(catalog(), rye={"gluten": 3}, barley={"gluten": 3}, spelt={"gluten": 3})
        gluten_heavy = ["barley", "pasta", "rye", "spelt", "wheat_bread"]

        pool = rank_pool(gluten_heavy + ["tomato"], taxonomy, {}, size=10)

        assert len([iid for iid in pool if iid in gluten_heavy]) == 2
        assert "tomato" in pool

    def test_tied_highest_components_count_toward_both(self):
        taxonomy = with_ingredients(
            catalog(),
            gluten_milk={"gluten": 3, "milk_protein": 3},
            rye={"gluten": 3},
            cream={"milk_protein": 3},
        )

        pool = rank_pool(["gluten_milk", "rye", "pasta", "cream", "cheese"], taxonomy, {}, size=10)

        assert top_component_counts(taxonomy, pool)["gluten"] == 2
        assert top_component_counts(taxonomy, pool)["milk_protein"] == 2

    def test_lower_level_components_do_not_hit_the_cap(self):
        # gluten is not the highest level in custard, so it does not count toward gluten's limit
        taxonomy = with_ingredients(catalog(), rye={"gluten": 3})

        pool = rank_pool(["pasta", "rye", "custard"], taxonomy, {}, size=10)

        assert sorted(pool) == ["custard", "pasta", "rye"]

    def test_level_zero_components_do_not_score_or_count(self):
        assert rank_pool(["trace_grain", "maple_syrup"], catalog(), {}) == ["maple_syrup", "trace_grain"]

        taxonomy = with_ingredients(catalog(), rye={"gluten": 3})
        assert "trace_grain" in rank_pool(["pasta", "rye", "trace_grain"], taxonomy, {}, size=10)

    def test_ties_are_broken_by_ingredient_id(self):
        assert rank_pool(["white_rice", "maple_syrup"], catalog(), {}) == ["maple_syrup", "white_rice"]

    def test_respects_size(self):
        eligible = sorted(INGREDIENTS)

        assert rank_pool(eligible, catalog(), {}, size=0) == []
        assert len(rank_pool(eligible, catalog(), {}, size=3)) == 3

    def test_empty_eligible_list(self):
        assert rank_pool([], catalog(), {}) == []


def test_ranking_holds_on_the_real_taxonomy():
    taxonomy = get_taxonomy()
    eligible = eligible_ingredients(taxonomy, context(*taxonomy.components), INACTIVE)

    default_pool = rank_pool(eligible, taxonomy, {})
    full_pool = rank_pool(eligible, taxonomy, {}, size=len(eligible))

    assert 0 < len(default_pool) <= POOL_SIZE
    assert len(set(full_pool)) == len(full_pool)
    assert set(full_pool) <= set(eligible)
    assert max(top_component_counts(taxonomy, full_pool).values(), default=0) <= 2
