"""Integration tests for user ingredient preferenced."""

from uuid import uuid4

import pytest

from models.ingredient import Ingredient
from models.user import User
from models.user_ingredient import UserIngredient


@pytest.fixture
def ingredients(db_session):
    """Three real ingredients to categorize."""
    rows = [
        Ingredient(slug="gluten", canonical_name="gluten"),
        Ingredient(slug="garlic", canonical_name="garlic"),
        Ingredient(slug="rice", canonical_name="rice"),
    ]
    db_session.add_all(rows)
    db_session.commit()
    for row in rows:
        db_session.refresh(row)
    return rows


def _put(test_client, avoid=(), suspect=(), safe=()):
    return test_client.put(
        "/users/me/ingredients",
        json={
            "avoid": [str(i) for i in avoid],
            "suspect": [str(i) for i in suspect],
            "safe": [str(i) for i in safe],
        },
    )


def _names(group):
    return [item["canonical_name"] for item in group]


class TestUserIngredientsRouter:
    """HTTP tests for the user ingredient preference endpoints."""

    def test_put_then_get_returns_same_lists(self, test_client, authenticated_user, ingredients):
        """Saved preferences come back grouped exactly as they were sent."""
        gluten, garlic, rice = ingredients
        put = _put(test_client, avoid=[gluten.id], suspect=[garlic.id], safe=[rice.id])
        assert put.status_code == 200, put.text

        body = test_client.get("/users/me/ingredients").json()

        assert _names(body["avoid"]) == ["gluten"]
        assert _names(body["suspect"]) == ["garlic"]
        assert _names(body["safe"]) == ["rice"]

    def test_get_with_nothing_saved_returns_empty_lists(self, test_client, authenticated_user):
        """All three keys are present even when the user hasn't saved anything."""
        body = test_client.get("/users/me/ingredients").json()

        assert body == {"avoid": [], "suspect": [], "safe": []}

    def test_second_put_replaces_first(self, test_client, authenticated_user, ingredients):
        """A second save replaces the first set rather than adding to it."""
        gluten, garlic, rice = ingredients
        _put(test_client, avoid=[gluten.id, garlic.id])
        _put(test_client, safe=[rice.id])

        body = test_client.get("/users/me/ingredients").json()

        assert body["avoid"] == []
        assert _names(body["safe"]) == ["rice"]

    def test_same_ingredient_in_two_lists_returns_422(self, test_client, authenticated_user, ingredients):
        """An ingredient can't be both avoided and safe."""
        gluten, _, _ = ingredients
        response = _put(test_client, avoid=[gluten.id], safe=[gluten.id])

        assert response.status_code == 422

    def test_duplicate_within_one_list_is_saved_once(self, test_client, authenticated_user, ingredients):
        """Repeating an ingredient in the same list is harmless and saved once."""
        gluten, _, _ = ingredients
        response = _put(test_client, avoid=[gluten.id, gluten.id])

        assert response.status_code == 200, response.text
        assert _names(response.json()["avoid"]) == ["gluten"]

    def test_unknown_ingredient_returns_404_and_writes_nothing(self, test_client, authenticated_user, ingredients):
        """An unknown ID is rejected and the user's existing preferences stay untouched."""
        gluten, _, _ = ingredients
        _put(test_client, avoid=[gluten.id])

        response = _put(test_client, safe=[uuid4()])

        assert response.status_code == 404
        body = test_client.get("/users/me/ingredients").json()
        assert _names(body["avoid"]) == ["gluten"]


class TestDiagnoses:
    """Diagnoses are saved through the existing profile update path."""

    def test_diagnoses_save_through_profile_update(self, test_client, authenticated_user):
        """Diagnoses are stored on the user through the existing PUT /auth/me."""
        response = test_client.put("/auth/me", json={"disease": ["celiac", "lupus"]})

        assert response.status_code == 200, response.text
        assert response.json()["disease"] == ["celiac", "lupus"]


class TestUserIngredientCascade:
    """Database-level behavior of the user_ingredients table."""

    def test_deleting_user_removes_their_preferences(self, test_client, db_session, authenticated_user, ingredients):
        """Removing a user also removes their UserIngredient rows."""
        gluten, _, _ = ingredients
        _put(test_client, avoid=[gluten.id])

        user = db_session.get(User, authenticated_user["username"])
        db_session.delete(user)
        db_session.commit()

        remaining = db_session.query(UserIngredient).filter(UserIngredient.username == authenticated_user["username"])
        assert remaining.all() == []