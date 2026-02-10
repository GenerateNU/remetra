"""Integration tests for authentication with real database."""

import pytest
from fastapi import HTTPException

from repositories.user_repository import UserRepository
from schemas.user import UserCreate
from services.auth_service import AuthService, decode_access_token


class TestAuthServiceIntegration:
    """Integration tests for auth service with real database."""

    def test_register_user_success(self, db_session, sample_user_data):
        """Test successful user registration."""
        service = AuthService()

        user_create = UserCreate(**sample_user_data)
        user = service.register_user(db_session, user_create)

        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]
        assert user.disease == sample_user_data["disease"]
        assert user.weight == sample_user_data["weight"]
        assert user.created_at is not None

    def test_register_user_duplicate_username(self, db_session, sample_user_data):
        """Test that duplicate usernames are prevented."""
        service = AuthService()

        user_create = UserCreate(**sample_user_data)
        service.register_user(db_session, user_create)

        duplicate_data = sample_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        user_create2 = UserCreate(**duplicate_data)

        with pytest.raises(HTTPException) as exc_info:
            service.register_user(db_session, user_create2)

        assert exc_info.value.status_code == 400
        assert "Username already registered" in exc_info.value.detail

    def test_register_user_duplicate_email(self, db_session, sample_user_data):
        """Test that duplicate emails are prevented."""
        service = AuthService()

        user_create = UserCreate(**sample_user_data)
        service.register_user(db_session, user_create)

        duplicate_email_data = sample_user_data.copy()
        duplicate_email_data["username"] = "different_user"
        user_create2 = UserCreate(**duplicate_email_data)

        with pytest.raises(HTTPException) as exc_info:
            service.register_user(db_session, user_create2)

        assert exc_info.value.status_code == 400
        assert "Email already registered" in exc_info.value.detail

    def test_authenticate_user_success(self, db_session, sample_user_data):
        """Test successful user authentication."""
        service = AuthService()

        user_create = UserCreate(**sample_user_data)
        service.register_user(db_session, user_create)

        token_data = service.authenticate_user(db_session, sample_user_data["username"], sample_user_data["password"])

        assert token_data is not None
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["username"] == sample_user_data["username"]

        # Verify token is valid
        payload = decode_access_token(token_data["access_token"])
        assert payload is not None
        assert payload["sub"] == sample_user_data["username"]

    def test_authenticate_user_wrong_password(self, db_session, sample_user_data):
        """Test authentication fails with wrong password."""
        service = AuthService()

        user_create = UserCreate(**sample_user_data)
        service.register_user(db_session, user_create)

        token_data = service.authenticate_user(db_session, sample_user_data["username"], "wrongpassword")

        assert token_data is None

    def test_authenticate_user_not_found(self, db_session):
        """Test authentication fails when user doesn't exist."""
        service = AuthService()

        token_data = service.authenticate_user(db_session, "nonexistent", "password")

        assert token_data is None

    def test_get_current_user_success(self, db_session, sample_user_data):
        """Test getting current user after registration."""
        service = AuthService()

        user_create = UserCreate(**sample_user_data)
        registered_user = service.register_user(db_session, user_create)

        user = service.get_current_user(db_session, registered_user.username)

        assert user is not None
        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]

    def test_get_current_user_not_found(self, db_session):
        """Test get current user returns None when user doesn't exist."""
        service = AuthService()

        user = service.get_current_user(db_session, "nonexistent")

        assert user is None

    def test_complete_registration_and_login_flow(self, db_session, sample_user_data):
        """Test complete user flow from registration to getting current user."""
        service = AuthService()

        # 1. Register
        user_create = UserCreate(**sample_user_data)
        registered_user = service.register_user(db_session, user_create)
        assert registered_user.username == sample_user_data["username"]

        # 2. Login
        token_data = service.authenticate_user(db_session, sample_user_data["username"], sample_user_data["password"])
        assert token_data is not None

        # 3. Decode token and get user
        payload = decode_access_token(token_data["access_token"])
        username = payload["sub"]

        current_user = service.get_current_user(db_session, username)
        assert current_user.username == sample_user_data["username"]
        assert current_user.email == sample_user_data["email"]


class TestUserRepositoryIntegration:
    """Integration tests for user repository."""

    def test_create_user(self, db_session):
        """Test creating a user through repository."""
        repo = UserRepository()

        user = repo.create(
            db=db_session,
            username="repotest",
            email="repo@test.com",
            password_hash="hashed_password",
            dob="2000-01-01",
            disease=["celiac"],
            weight=160.0,
        )

        assert user.username == "repotest"
        assert user.email == "repo@test.com"
        assert user.disease == ["celiac"]
        assert user.weight == 160.0

    def test_get_by_username(self, db_session):
        """Test retrieving user by username."""
        repo = UserRepository()

        repo.create(db=db_session, username="findme", email="findme@test.com", password_hash="hash", disease=["lupus"])

        user = repo.get_by_username(db_session, "findme")

        assert user is not None
        assert user.username == "findme"
        assert user.email == "findme@test.com"

    def test_get_by_username_not_found(self, db_session):
        """Test get_by_username returns None when user doesn't exist."""
        repo = UserRepository()

        user = repo.get_by_username(db_session, "doesnotexist")

        assert user is None

    def test_get_by_email(self, db_session):
        """Test retrieving user by email."""
        repo = UserRepository()

        repo.create(
            db=db_session, username="emailtest", email="find@email.com", password_hash="hash", disease=["celiac"]
        )

        user = repo.get_by_email(db_session, "find@email.com")

        assert user is not None
        assert user.username == "emailtest"
        assert user.email == "find@email.com"

    def test_get_by_email_not_found(self, db_session):
        """Test get_by_email returns None when email doesn't exist."""
        repo = UserRepository()

        user = repo.get_by_email(db_session, "notfound@example.com")

        assert user is None
