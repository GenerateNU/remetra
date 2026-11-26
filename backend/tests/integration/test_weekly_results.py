"""Integration tests for the weekly results repository, service and endpoint."""

import math
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from models.component import Component
from models.food import Food
from models.food_log import FoodLog
from models.ingredient import Ingredient
from models.ingredient_component import IngredientComponent
from models.symptom_family import MODELED_FAMILIES, SymptomFamily
from models.user import User
from models.user_background_total import UserBackgroundTotal
from models.user_family_confidence import UserFamilyConfidence
from repositories.weekly_results_repository import WeeklyResultsRepository
from services.weekly_results_service import WeeklyResultsService

NOW = datetime(2026, 11, 24, 12, tzinfo=timezone.utc)
SETTLED = NOW - timedelta(days=3)  # past the 48 h window
FRESH = NOW - timedelta(hours=12)  # still inside it

COMPONENTS = {
    "fructans_allium": "Onion & garlic",
    "egg_protein": "Egg",
    "gluten": "Gluten",
    "fructans_grain": "Wheat fructans",
    "lactose": "Lactose",
    "milk_protein": "Milk protein",
}
INGREDIENTS = {
    # slug: (canonical name, aliases, {component: level})
    "onion": ("Onion", ["onions"], {"fructans_allium": 3}),
    "garlic_powder": ("Garlic powder", [], {"fructans_allium": 1}),
    "eggs": ("Eggs", [], {"egg_protein": 3}),
    "wheat_bread": ("Wheat bread", [], {"gluten": 3, "fructans_grain": 2}),
    "milk": ("Milk", [], {"lactose": 3, "milk_protein": 3}),
}


@pytest.fixture
def taxonomy(db_session):
    """A small taxonomy: two always-together groups (wheat, dairy) and two single components."""
    for model in (UserFamilyConfidence, UserBackgroundTotal, IngredientComponent, Ingredient, Component):
        db_session.execute(delete(model))

    components = {}
    for slug, name in COMPONENTS.items():
        components[slug] = Component(
            slug=slug, display_name=name, category="test", inclusion_confidence="high", prior_tier="high"
        )
    db_session.add_all(components.values())
    db_session.flush()

    for slug, (name, aliases, levels) in INGREDIENTS.items():
        ingredient = Ingredient(slug=slug, canonical_name=name, aliases=aliases)
        db_session.add(ingredient)
        db_session.flush()
        for component_slug, level in levels.items():
            db_session.add(
                IngredientComponent(
                    ingredient_id=ingredient.id,
                    component_id=components[component_slug].id,
                    concentration_level=level,
                    confidence="high",
                )
            )
    db_session.flush()
    return components


def _set_confidence(db, username, components, slug, confidence):
    """Store rows so that Q_c == confidence: all of it in GI, ~0 in the other families."""
    for family in MODELED_FAMILIES:
        q = confidence if family == SymptomFamily.GI else 1e-12
        db.execute(
            sa.insert(UserFamilyConfidence).values(
                username=username,
                component_id=components[slug].id,
                family=family.value,
                log_odds=math.log(q / (1 - q)),
            )
        )


def _log_meal(db, username, ingredients, when):
    """Insert a food and one log of it with Core inserts, so rows can belong to any user."""
    food_id = uuid.uuid4()
    db.execute(sa.insert(Food).values(id=food_id, name=f"meal {food_id}", ingredients=ingredients, username=username))
    db.execute(sa.insert(FoodLog).values(id=uuid.uuid4(), username=username, food_id=food_id, timestamp=when))


@pytest.fixture
def planted_onion_user(db_session, authenticated_user, taxonomy):
    """Mirrors a mock onion_garlic user: onion is the planted trigger, everything else is clean."""
    username = authenticated_user["username"]
    for slug, q in {
        "fructans_allium": 0.95,
        "egg_protein": 0.01,
        "gluten": 0.02,
        "fructans_grain": 0.02,
        "lactose": 0.01,
        "milk_protein": 0.01,
    }.items():
        _set_confidence(db_session, username, taxonomy, slug, q)

    for _ in range(4):
        _log_meal(db_session, username, ["Onions", "eggs"], SETTLED)
        _log_meal(db_session, username, ["wheat bread"], SETTLED)
    # Dairy is never eaten at a meaningful amount, so it never appears
    db_session.flush()
    return username


class TestWeeklyResultsRepository:
    def test_ingredient_levels_cover_slug_name_and_aliases(self, db_session, taxonomy):
        levels = WeeklyResultsRepository().get_ingredient_levels(db_session)
        assert levels["onion"] == levels["onions"] == {"fructans_allium": 3}
        assert levels["wheat bread"] == {"gluten": 3, "fructans_grain": 2}

    def test_meal_ingredients_only_includes_the_users_meals_before_the_cutoff(
        self, db_session, authenticated_user, taxonomy
    ):
        username = authenticated_user["username"]
        db_session.add(User(username="other_user", email="other@example.com"))
        db_session.flush()
        _log_meal(db_session, username, ["eggs"], SETTLED)
        _log_meal(db_session, username, ["milk"], FRESH)
        _log_meal(db_session, "other_user", ["onion"], SETTLED)

        meals = WeeklyResultsRepository().get_meal_ingredients(db_session, username, NOW - timedelta(hours=48))
        assert meals == [["eggs"]]

    def test_first_meal_time_is_the_earliest_log_or_none(self, db_session, authenticated_user):
        username = authenticated_user["username"]
        repo = WeeklyResultsRepository()
        assert repo.get_first_meal_time(db_session, username) is None

        _log_meal(db_session, username, ["eggs"], FRESH)
        _log_meal(db_session, username, ["eggs"], SETTLED)
        db_session.flush()

        assert repo.get_first_meal_time(db_session, username) == SETTLED


class TestWeeklyResultsService:
    def test_no_confidences_returns_empty_results(self, db_session, authenticated_user, taxonomy):
        results = WeeklyResultsService().get_weekly_results(db_session, authenticated_user["username"], now=NOW)
        assert results.likely_trigger == results.still_learning == results.looks_fine == []
        assert results.no_clear_pattern is False
        assert results.groups_checked == results.groups_total == 0
        assert results.first_meal_at is None

    def test_planted_trigger_stands_out(self, db_session, planted_onion_user):
        results = WeeklyResultsService().get_weekly_results(db_session, planted_onion_user, now=NOW)

        assert [item.id for item in results.likely_trigger] == ["fructans_allium"]
        assert {item.id for item in results.looks_fine} == {"egg_protein", "wheat"}
        assert results.still_learning == []
        assert results.no_clear_pattern is False

    def test_progress_counts_groups_once_and_reports_first_meal(self, db_session, planted_onion_user):
        results = WeeklyResultsService().get_weekly_results(db_session, planted_onion_user, now=NOW)

        # Units: wheat group, dairy group, onion, egg. Onion (trigger) and egg + wheat (fine) have results.
        assert results.groups_total == 4
        assert results.groups_checked == 3
        assert results.first_meal_at == SETTLED

    def test_always_together_foods_are_one_group(self, db_session, planted_onion_user):
        results = WeeklyResultsService().get_weekly_results(db_session, planted_onion_user, now=NOW)

        all_ids = [
            item.id for items in (results.likely_trigger, results.still_learning, results.looks_fine) for item in items
        ]
        assert "gluten" not in all_ids and "fructans_grain" not in all_ids
        wheat = next(item for item in results.looks_fine if item.id == "wheat")
        assert wheat.is_group is True
        assert wheat.member_slugs == ["gluten", "fructans_grain"]
        assert wheat.display_name == "Wheat, rye & barley (gluten or wheat carbs)"

    def test_group_uses_combined_confidence(self, db_session, authenticated_user, taxonomy):
        """Each member alone would look fine (0.03), but Q_G = 1 - 0.97^2 > 0.05, so the group is still learning."""
        username = authenticated_user["username"]
        _set_confidence(db_session, username, taxonomy, "gluten", 0.03)
        _set_confidence(db_session, username, taxonomy, "fructans_grain", 0.03)
        for _ in range(3):
            _log_meal(db_session, username, ["wheat bread"], SETTLED)
        db_session.flush()

        results = WeeklyResultsService().get_weekly_results(db_session, username, now=NOW)
        assert [item.id for item in results.still_learning] == ["wheat"]

    def test_only_settled_meaningful_meals_count_toward_looks_fine(self, db_session, authenticated_user, taxonomy):
        username = authenticated_user["username"]
        _set_confidence(db_session, username, taxonomy, "egg_protein", 0.01)
        _set_confidence(db_session, username, taxonomy, "fructans_allium", 0.01)
        for _ in range(2):
            _log_meal(db_session, username, ["eggs"], SETTLED)
        _log_meal(db_session, username, ["eggs"], FRESH)  # window not passed yet
        for _ in range(5):
            _log_meal(db_session, username, ["garlic powder"], SETTLED)  # below a meaningful amount
        db_session.flush()

        results = WeeklyResultsService().get_weekly_results(db_session, username, now=NOW)
        assert [item.id for item in results.still_learning] == ["egg_protein"]
        assert results.looks_fine == results.likely_trigger == []

    def test_no_clear_pattern_when_everything_eaten_looks_fine(self, db_session, authenticated_user, taxonomy):
        username = authenticated_user["username"]
        for slug in COMPONENTS:
            _set_confidence(db_session, username, taxonomy, slug, 0.01)
        for _ in range(3):
            _log_meal(db_session, username, ["eggs", "milk", "onion"], SETTLED)
        db_session.flush()

        results = WeeklyResultsService().get_weekly_results(db_session, username, now=NOW)
        assert {item.id for item in results.looks_fine} == {"egg_protein", "dairy", "fructans_allium"}
        assert results.no_clear_pattern is True


class TestWeeklyResultsEndpoint:
    def test_returns_labels_without_confidence_numbers(self, test_client, planted_onion_user):
        response = test_client.get("/results/weekly")

        assert response.status_code == 200
        body = response.json()
        assert set(body) == {
            "likely_trigger",
            "still_learning",
            "looks_fine",
            "no_clear_pattern",
            "groups_checked",
            "groups_total",
            "first_meal_at",
        }
        assert (body["groups_checked"], body["groups_total"]) == (3, 4)
        assert [item["label"] for item in body["likely_trigger"]] == ["likely_trigger"]
        for items in (body["likely_trigger"], body["still_learning"], body["looks_fine"]):
            for item in items:
                assert set(item) == {"id", "display_name", "is_group", "member_slugs", "label"}

    def test_database_error_returns_500(self, test_client, authenticated_user, monkeypatch):
        def boom(*args, **kwargs):
            raise SQLAlchemyError("db down")

        monkeypatch.setattr(WeeklyResultsService, "get_weekly_results", boom)
        response = test_client.get("/results/weekly")
        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to fetch weekly results"
