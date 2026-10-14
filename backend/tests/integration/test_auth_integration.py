"""Integration tests for Clerk."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from repositories.user_repository import UserRepository
from schemas.user import UserUpdate
from services.auth_service import AuthService, clerk_auth_options, fetch_clerk_profile, profile_from_clerk_user


def _clerk_user(username="ada", email="ada@example.com", primary_id="em_1"):
    return SimpleNamespace(
        username=username,
        primary_email_address_id=primary_id,
        email_addresses=[SimpleNamespace(id=primary_id, email_address=email)],
    )


class TestAuthServiceIntegration:
    """Integration tests for auth service with real database."""

    def test_provision_user_success(self, db_session):
        service = AuthService()

        user = service.provision_user(db_session, "user_clerk_1", "ada", "ada@example.com")

        assert user.username == "ada"
        assert user.email == "ada@example.com"
        stored = UserRepository().get_by_clerk_id(db_session, "user_clerk_1")
        assert stored is not None
        assert stored.username == "ada"

    def test_provision_user_duplicate_username(self, db_session):
        service = AuthService()
        service.provision_user(db_session, "user_clerk_1", "ada", "ada@example.com")

        with pytest.raises(HTTPException) as exc_info:
            service.provision_user(db_session, "user_clerk_2", "ada", "other@example.com")

        assert exc_info.value.status_code == 400
        assert "Username already registered" in exc_info.value.detail

    def test_provision_user_duplicate_email(self, db_session):
        service = AuthService()
        service.provision_user(db_session, "user_clerk_1", "ada", "ada@example.com")

        with pytest.raises(HTTPException) as exc_info:
            service.provision_user(db_session, "user_clerk_2", "other", "ada@example.com")

        assert exc_info.value.status_code == 400
        assert "Email already registered" in exc_info.value.detail

    def test_provision_user_integrity_error(self, db_session, monkeypatch):
        service = AuthService()

        def raise_integrity(*_args, **_kwargs):
            raise IntegrityError("insert", {}, Exception("duplicate"))

        monkeypatch.setattr(service.user_repo, "create", raise_integrity)

        with pytest.raises(HTTPException) as exc_info:
            service.provision_user(db_session, "user_clerk_1", "ada", "ada@example.com")

        assert exc_info.value.status_code == 400

    def test_resolve_user_returns_existing_without_clerk_call(self, db_session, monkeypatch):
        service = AuthService()
        service.provision_user(db_session, "user_clerk_1", "ada", "ada@example.com")

        def fail_fetch(_clerk_user_id):
            raise AssertionError("Clerk should not be called for an existing user")

        monkeypatch.setattr("services.auth_service.fetch_clerk_profile", fail_fetch)

        user = service.resolve_user(db_session, "user_clerk_1")
        assert user.username == "ada"
        assert user.email == "ada@example.com"

    def test_resolve_user_provisions_on_first_sight(self, db_session, monkeypatch):
        monkeypatch.setattr(
            "services.auth_service.fetch_clerk_profile",
            lambda _clerk_user_id: ("ada", "ada@example.com"),
        )

        user = AuthService().resolve_user(db_session, "user_clerk_1")

        assert user.username == "ada"
        assert user.email == "ada@example.com"
        assert UserRepository().get_by_clerk_id(db_session, "user_clerk_1") is not None

    def test_update_user_success(self, db_session):
        service = AuthService()
        service.provision_user(db_session, "user_clerk_1", "ada", "ada@example.com")

        updated_user = service.update_user(
            db_session,
            "ada",
            UserUpdate(disease=["lupus"], weight=150.0, gender="Female"),
        )

        assert updated_user.disease == ["lupus"]
        assert updated_user.weight == 150.0
        assert updated_user.gender == "Female"

    def test_update_user_not_found(self, db_session):
        with pytest.raises(ValueError):
            AuthService().update_user(db_session, "missing", UserUpdate(weight=120.0))


class TestClerkAuthOptions:
    def test_reads_env(self, monkeypatch):
        monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test")
        monkeypatch.setenv("CLERK_JWT_KEY", "line1\\nline2")
        monkeypatch.setenv("CLERK_AUTHORIZED_PARTIES", "http://localhost:8081, https://app.example")

        options = clerk_auth_options()

        assert options.secret_key == "sk_test"
        assert options.jwt_key == "line1\nline2"
        assert options.authorized_parties == ["http://localhost:8081", "https://app.example"]
        assert options.accepts_token == ["session_token"]

    def test_empty_parties_are_unset(self, monkeypatch):
        monkeypatch.delenv("CLERK_SECRET_KEY", raising=False)
        monkeypatch.delenv("CLERK_JWT_KEY", raising=False)
        monkeypatch.setenv("CLERK_AUTHORIZED_PARTIES", " , ")

        options = clerk_auth_options()

        assert options.secret_key is None
        assert options.jwt_key is None
        assert options.authorized_parties is None


class TestClerkProfile:
    def test_profile_from_primary_email(self):
        username, email = profile_from_clerk_user(_clerk_user())
        assert username == "ada"
        assert email == "ada@example.com"

    def test_profile_falls_back_to_first_email(self):
        clerk_user = SimpleNamespace(
            username="ada",
            primary_email_address_id="missing",
            email_addresses=[{"id": "em_2", "email_address": "ada@example.com"}],
        )
        assert profile_from_clerk_user(clerk_user) == ("ada", "ada@example.com")

    def test_profile_missing_username(self):
        with pytest.raises(HTTPException) as exc_info:
            profile_from_clerk_user(_clerk_user(username=None))
        assert exc_info.value.status_code == 400

    def test_profile_missing_email(self):
        clerk_user = SimpleNamespace(username="ada", primary_email_address_id=None, email_addresses=[])
        with pytest.raises(HTTPException) as exc_info:
            profile_from_clerk_user(clerk_user)
        assert exc_info.value.status_code == 400

    def test_fetch_requires_secret(self, monkeypatch):
        monkeypatch.delenv("CLERK_SECRET_KEY", raising=False)
        with pytest.raises(HTTPException) as exc_info:
            fetch_clerk_profile("user_clerk_1")
        assert exc_info.value.status_code == 500

    def test_fetch_loads_user(self, monkeypatch):
        monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test")
        clerk_user = _clerk_user()

        class Users:
            @staticmethod
            def get(user_id):
                assert user_id == "user_clerk_1"
                return clerk_user

        class FakeClerk:
            def __init__(self, bearer_auth):
                assert bearer_auth == "sk_test"
                self.users = Users()

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        monkeypatch.setattr("services.auth_service.Clerk", FakeClerk)
        assert fetch_clerk_profile("user_clerk_1") == ("ada", "ada@example.com")

    def test_fetch_missing_user(self, monkeypatch):
        monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test")

        class Users:
            @staticmethod
            def get(user_id):
                return None

        class FakeClerk:
            def __init__(self, bearer_auth):
                self.users = Users()

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        monkeypatch.setattr("services.auth_service.Clerk", FakeClerk)
        with pytest.raises(HTTPException) as exc_info:
            fetch_clerk_profile("user_clerk_1")
        assert exc_info.value.status_code == 401

    def test_fetch_clerk_error(self, monkeypatch):
        monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test")

        class FakeClerk:
            def __init__(self, bearer_auth):
                pass

            def __enter__(self):
                raise RuntimeError("clerk down")

            def __exit__(self, *_args):
                return False

        monkeypatch.setattr("services.auth_service.Clerk", FakeClerk)
        with pytest.raises(HTTPException) as exc_info:
            fetch_clerk_profile("user_clerk_1")
        assert exc_info.value.status_code == 502


class TestUserRepositoryIntegration:
    """Integration tests for user repository."""

    def test_create_user(self, db_session):
        repo = UserRepository()

        user = repo.create(db=db_session, username="repotest", email="repo@test.com", clerk_user_id="user_repo")

        assert user.username == "repotest"
        assert user.email == "repo@test.com"
        assert user.clerk_user_id == "user_repo"
        assert user.password_hash is None

    def test_get_by_username(self, db_session):
        repo = UserRepository()

        repo.create(db=db_session, username="findme", email="findme@test.com", clerk_user_id="user_find")

        user = repo.get_by_username(db_session, "findme")

        assert user is not None
        assert user.username == "findme"
        assert user.email == "findme@test.com"

    def test_get_by_username_not_found(self, db_session):
        repo = UserRepository()

        user = repo.get_by_username(db_session, "doesnotexist")

        assert user is None

    def test_get_by_email(self, db_session):
        repo = UserRepository()

        repo.create(db=db_session, username="emailtest", email="find@email.com", clerk_user_id="user_email")

        user = repo.get_by_email(db_session, "find@email.com")

        assert user is not None
        assert user.username == "emailtest"
        assert user.email == "find@email.com"

    def test_get_by_email_not_found(self, db_session):
        repo = UserRepository()

        user = repo.get_by_email(db_session, "notfound@example.com")

        assert user is None

    def test_get_by_clerk_id(self, db_session):
        repo = UserRepository()
        repo.create(db=db_session, username="clerktest", email="clerk@test.com", clerk_user_id="user_lookup")

        user = repo.get_by_clerk_id(db_session, "user_lookup")

        assert user is not None
        assert user.username == "clerktest"

    def test_get_by_clerk_id_not_found(self, db_session):
        assert UserRepository().get_by_clerk_id(db_session, "user_missing") is None


class TestMeEndpoint:
    """HTTP-level integration tests for GET /auth/me."""

    def test_me_success(self, test_client, authenticated_user):
        """Test /me returns the user injected by the auth dependency."""
        response = test_client.get("/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == authenticated_user["username"]
        assert data["email"] == authenticated_user["email"]
        assert "password_hash" not in data
        assert "created_at" in data

    def test_me_invalid_token(self, test_client):
        """Test /me returns 401 for an invalid token."""
        response = test_client.get("/auth/me", headers={"authorization": "Bearer invalidtoken"})

        assert response.status_code == 401

    def test_me_missing_bearer_prefix(self, test_client):
        """Test /me returns 401 when Authorization header lacks 'Bearer ' prefix."""
        response = test_client.get("/auth/me", headers={"authorization": "invalidtoken"})

        assert response.status_code == 401

    def test_me_missing_authorization_header(self, test_client):
        """Test /me returns 401 when Authorization header is absent."""
        response = test_client.get("/auth/me")

        assert response.status_code == 401
