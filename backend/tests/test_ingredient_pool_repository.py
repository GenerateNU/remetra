from contextlib import contextmanager
from datetime import date
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError

from auth_context import current_username
from models.ingredient_pool import IngredientPool
from models.user import User
from repositories.ingredient_pool_repository import IngredientPoolRepository

TODAY = date(2026, 10, 26)
TOMORROW = date(2026, 10, 27)


@contextmanager
def signed_in_as(username: str):
    token = current_username.set(username)
    try:
        yield
    finally:
        current_username.reset(token)


@pytest.fixture
def pool_user(db_session):
    user = User(username="pooluser", email="pool@test.com", password_hash="fakehash")
    db_session.add(user)
    db_session.flush()
    with signed_in_as(user.username):
        yield user


@pytest.fixture
def second_user(db_session):
    user = User(username="pooluser2", email="pool2@test.com", password_hash="fakehash")
    db_session.add(user)
    db_session.flush()
    return user


def _pool_kwargs(**overrides):
    defaults = {
        "username": "pooluser",
        "pool_date": TODAY,
        "ingredient_ids": ["rice", "chicken_breast", "carrot", "olive_oil"],
        "washout": False,
    }
    defaults.update(overrides)
    return defaults


class TestCreate:
    def test_creates_pool(self, db_session, pool_user):
        repo = IngredientPoolRepository()
        pool = repo.create(db_session, **_pool_kwargs())
        assert pool.id is not None
        assert pool.username == pool_user.username
        assert pool.pool_date == TODAY
        assert pool.washout is False
        assert pool.created_at is not None

    def test_preserves_ingredient_order(self, db_session, pool_user):
        repo = IngredientPoolRepository()
        ids = ["zucchini", "apple", "rice", "beef"]
        repo.create(db_session, **_pool_kwargs(ingredient_ids=ids))
        fetched = repo.get_by_user_and_date(db_session, pool_user.username, TODAY)
        assert fetched.ingredient_ids == ids

    def test_persists_washout_true(self, db_session, pool_user):
        repo = IngredientPoolRepository()
        repo.create(db_session, **_pool_kwargs(washout=True))
        fetched = repo.get_by_user_and_date(db_session, pool_user.username, TODAY)
        assert fetched.washout is True

    def test_allows_empty_ingredient_list(self, db_session, pool_user):
        repo = IngredientPoolRepository()
        repo.create(db_session, **_pool_kwargs(ingredient_ids=[]))
        fetched = repo.get_by_user_and_date(db_session, pool_user.username, TODAY)
        assert fetched.ingredient_ids == []

    def test_owner_is_signed_in_user(self, db_session, pool_user, second_user):
        repo = IngredientPoolRepository()
        pool = repo.create(db_session, **_pool_kwargs(username=second_user.username))
        assert pool.username == pool_user.username

    def test_rejects_duplicate_user_and_date(self, db_session, pool_user):
        repo = IngredientPoolRepository()
        repo.create(db_session, **_pool_kwargs())
        with pytest.raises(IntegrityError):
            repo.create(db_session, **_pool_kwargs(ingredient_ids=["beef"]))

    def test_same_user_different_dates(self, db_session, pool_user):
        repo = IngredientPoolRepository()
        repo.create(db_session, **_pool_kwargs(pool_date=TODAY))
        repo.create(db_session, **_pool_kwargs(pool_date=TOMORROW))
        count = db_session.query(IngredientPool).filter_by(username=pool_user.username).count()
        assert count == 2

    def test_two_users_same_date(self, db_session, pool_user, second_user):
        repo = IngredientPoolRepository()
        repo.create(db_session, **_pool_kwargs(username=pool_user.username))
        with signed_in_as(second_user.username):
            repo.create(db_session, **_pool_kwargs(username=second_user.username))
            assert repo.get_by_user_and_date(db_session, second_user.username, TODAY) is not None
        assert repo.get_by_user_and_date(db_session, pool_user.username, TODAY) is not None

    def test_rolls_back_and_reraises_on_error(self, db_session, pool_user):
        repo = IngredientPoolRepository()
        with (
            patch.object(db_session, "commit", side_effect=Exception("db error")),
            patch.object(db_session, "rollback") as rollback,
        ):
            with pytest.raises(Exception, match="db error"):
                repo.create(db_session, **_pool_kwargs())
        rollback.assert_called_once()


class TestGetByUserAndDate:
    def test_returns_none_when_missing(self, db_session, pool_user):
        repo = IngredientPoolRepository()
        assert repo.get_by_user_and_date(db_session, pool_user.username, TODAY) is None

    def test_returns_only_requested_date(self, db_session, pool_user):
        repo = IngredientPoolRepository()
        repo.create(db_session, **_pool_kwargs(pool_date=TODAY, ingredient_ids=["rice"]))
        repo.create(db_session, **_pool_kwargs(pool_date=TOMORROW, ingredient_ids=["beef"]))
        fetched = repo.get_by_user_and_date(db_session, pool_user.username, TOMORROW)
        assert fetched.ingredient_ids == ["beef"]

    def test_does_not_return_other_users_pool(self, db_session, pool_user, second_user):
        repo = IngredientPoolRepository()
        repo.create(db_session, **_pool_kwargs())
        with signed_in_as(second_user.username):
            assert repo.get_by_user_and_date(db_session, second_user.username, TODAY) is None
            assert repo.get_by_user_and_date(db_session, pool_user.username, TODAY) is None


class TestOwnershipScoping:
    def test_other_user_cannot_see_pool(self, db_session, pool_user, second_user):
        repo = IngredientPoolRepository()
        repo.create(db_session, **_pool_kwargs())
        with signed_in_as(second_user.username):
            assert db_session.query(IngredientPool).count() == 0
        assert db_session.query(IngredientPool).count() == 1

    def test_no_signed_in_user_sees_nothing(self, db_session, pool_user):
        repo = IngredientPoolRepository()
        repo.create(db_session, **_pool_kwargs())
        token = current_username.set(None)
        try:
            assert db_session.query(IngredientPool).count() == 0
        finally:
            current_username.reset(token)
