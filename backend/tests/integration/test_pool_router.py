"""Integration tests for the ingredient pool router."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from auth_context import current_username, system_access
from main import app
from models.ingredient_pool import IngredientPool
from repositories.user_repository import UserRepository
from routers.auth import get_current_user
from schemas.user import UserResponse
from services.taxonomy_service import get_taxonomy

DAY_ONE = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


def _frozen_at(moment: datetime):
    """datetime stand-in for the service module whose now() returns `moment`."""

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return moment if tz is None else moment.astimezone(tz)

    return patch("services.ingredient_pool_service.datetime", FrozenDatetime)


@pytest.fixture
def auth_headers(authenticated_user):
    """Bearer auth header; get_current_user is overridden by authenticated_user, so the token is not verified."""
    return {"Authorization": "Bearer test-token"}


def _sign_in(user) -> None:
    """Override get_current_user so requests run as the given user."""
    profile = UserResponse.model_validate(user)

    async def override_current_user():
        token = current_username.set(user.username)
        try:
            yield profile
        finally:
            current_username.reset(token)

    app.dependency_overrides[get_current_user] = override_current_user


class TestGetTodayPool:
    """Tests for GET /pool/today."""

    def test_returns_todays_pool(self, test_client, auth_headers):
        """A signed-in user gets a pool dated today."""
        response = test_client.get("/pool/today", headers=auth_headers)

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["pool_date"] == datetime.now(timezone.utc).date().isoformat()
        assert isinstance(body["ingredients"], list)
        assert all(isinstance(name, str) for name in body["ingredients"])

    def test_response_hides_internal_fields(self, test_client, auth_headers):
        """Only id, pool_date and ingredients are exposed."""
        response = test_client.get("/pool/today", headers=auth_headers)

        assert set(response.json()) == {"id", "pool_date", "ingredients"}

    def test_persists_pool_for_signed_in_user(self, test_client, db_session, auth_headers, authenticated_user):
        """The generated pool is saved and owned by the signed-in user."""
        response = test_client.get("/pool/today", headers=auth_headers)

        with system_access():
            pools = db_session.query(IngredientPool).all()
        assert len(pools) == 1
        assert str(pools[0].id) == response.json()["id"]
        assert pools[0].username == authenticated_user["username"]

    def test_second_call_returns_same_pool(self, test_client, db_session, auth_headers):
        """The pool is generated once per day and reused afterwards."""
        first = test_client.get("/pool/today", headers=auth_headers)
        second = test_client.get("/pool/today", headers=auth_headers)

        assert second.status_code == 200
        assert second.json() == first.json()
        with system_access():
            assert db_session.query(IngredientPool).count() == 1

    def test_second_call_does_not_regenerate(self, test_client, auth_headers):
        """Once today's pool exists, ranking is skipped."""
        test_client.get("/pool/today", headers=auth_headers)

        with patch("services.ingredient_pool_service.rank_pool") as rank_pool:
            response = test_client.get("/pool/today", headers=auth_headers)

        assert response.status_code == 200
        rank_pool.assert_not_called()

    def test_each_user_gets_their_own_pool(self, test_client, db_session, auth_headers, authenticated_user):
        """Another user's request creates a separate pool instead of reading the first one."""
        first = test_client.get("/pool/today", headers=auth_headers)
        other_user = UserRepository().create(
            db=db_session,
            username="otheruser",
            email="other@example.com",
            clerk_user_id="user_otherclerk",
        )
        _sign_in(other_user)

        second = test_client.get("/pool/today", headers=auth_headers)

        assert second.status_code == 200, second.text
        assert second.json()["id"] != first.json()["id"]
        with system_access():
            owners = {pool.username for pool in db_session.query(IngredientPool).all()}
        assert owners == {authenticated_user["username"], "otheruser"}

    def test_unauthenticated_request_returns_401(self, test_client):
        """Requests without a bearer token are rejected."""
        app.dependency_overrides.pop(get_current_user, None)

        response = test_client.get("/pool/today")

        assert response.status_code == 401

    def test_next_day_creates_a_new_pool(self, test_client, db_session, auth_headers):
        """A request on a later UTC date stores a new row instead of reusing yesterday's."""
        with _frozen_at(DAY_ONE):
            first = test_client.get("/pool/today", headers=auth_headers)
        with _frozen_at(DAY_ONE + timedelta(days=1)):
            second = test_client.get("/pool/today", headers=auth_headers)

        assert first.status_code == 200, first.text
        assert second.status_code == 200, second.text
        assert first.json()["pool_date"] == "2026-10-26"
        assert second.json()["pool_date"] == "2026-10-27"
        assert second.json()["id"] != first.json()["id"]
        with system_access():
            assert db_session.query(IngredientPool).count() == 2

    def test_response_contains_display_names_only(self, test_client, db_session, auth_headers):
        """The pool lists display names; ingredient ids, component ids and scores never leak."""
        taxonomy = get_taxonomy()
        display_names = {row["canonical_name"] for row in taxonomy.ingredients.values()}
        # ids that differ from their own name, e.g. wheat_bread vs "wheat bread"
        id_only = {iid for iid, row in taxonomy.ingredients.items() if row["canonical_name"] != iid}

        response = test_client.get("/pool/today", headers=auth_headers)

        names = response.json()["ingredients"]
        assert names
        assert set(names) <= display_names
        assert not set(names) & set(taxonomy.components)
        assert not set(names) & id_only
        assert "component" not in response.text
        assert "score" not in response.text
        with system_access():
            stored = db_session.query(IngredientPool).one().ingredient_ids
        assert names == [taxonomy.ingredients[iid]["canonical_name"] for iid in stored]

    def test_other_user_cannot_read_or_change_pool(self, test_client, db_session, auth_headers, authenticated_user):
        """User B gets their own pool, and user A's stored pool is left untouched."""
        alice_pool = test_client.get("/pool/today", headers=auth_headers).json()
        bob = UserRepository().create(
            db=db_session,
            username="bob",
            email="bob@example.com",
            clerk_user_id="user_bob",
        )
        _sign_in(bob)

        bob_pool = test_client.get("/pool/today", headers=auth_headers).json()

        assert bob_pool["id"] != alice_pool["id"]
        with system_access():
            alice_row = db_session.query(IngredientPool).filter_by(username=authenticated_user["username"]).one()
            bob_row = db_session.query(IngredientPool).filter_by(username="bob").one()
        taxonomy = get_taxonomy()
        assert [taxonomy.ingredients[iid]["canonical_name"] for iid in alice_row.ingredient_ids] == alice_pool[
            "ingredients"
        ]
        assert str(bob_row.id) == bob_pool["id"]
