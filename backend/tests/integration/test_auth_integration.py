"""Integration tests for authentication with real database."""

import pytest
from fastapi import HTTPException

from repositories.user_repository import UserRepository
from schemas.user import UserCreate, UserUpdate
from services.auth_service import AuthService, decode_access_token


class TestAuthServiceIntegration:
    """Integration tests for auth service with real database."""

    def test_register_user_success(self, db_session, sample_user_data):
        """Test successful user registration returns token response."""
        service = AuthService()

        user_create = UserCreate(**sample_user_data)
        token_data = service.register_user(db_session, user_create)

        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["username"] == sample_user_data["username"]

        # Verify token is valid and contains correct subject
        payload = decode_access_token(token_data["access_token"])
        assert payload is not None
        assert payload["sub"] == sample_user_data["username"]

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
        token_data = service.register_user(db_session, user_create)

        user = service.get_current_user(db_session, token_data["username"])

        assert user is not None
        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]

    def test_get_current_user_not_found(self, db_session):
        """Test get current user returns None when user doesn't exist."""
        service = AuthService()

        user = service.get_current_user(db_session, "nonexistent")

        assert user is None

    def test_update_user_success(self, db_session, sample_user_data):
        """Test updating user profile fields after registration."""
        service = AuthService()

        user_create = UserCreate(**sample_user_data)
        service.register_user(db_session, user_create)

        user_update = UserUpdate(disease=["lupus"], weight=150.0, gender="Female")
        updated_user = service.update_user(db_session, sample_user_data["username"], user_update)

        assert updated_user.disease == ["lupus"]
        assert updated_user.weight == 150.0
        assert updated_user.gender == "Female"


    def test_complete_registration_and_login_flow(self, db_session, sample_user_data):
        """Test complete user flow from registration to getting current user."""
        service = AuthService()

        # 1. Register — returns token response directly
        user_create = UserCreate(**sample_user_data)
        register_token = service.register_user(db_session, user_create)
        assert register_token["username"] == sample_user_data["username"]

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
            password_hash="hashed_password"
        )

        assert user.username == "repotest"
        assert user.email == "repo@test.com"


    def test_get_by_username(self, db_session):
        """Test retrieving user by username."""
        repo = UserRepository()

        repo.create(db=db_session, username="findme", email="findme@test.com", password_hash="hash")

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
            db=db_session, username="emailtest", email="find@email.com", password_hash="hash")

        user = repo.get_by_email(db_session, "find@email.com")

        assert user is not None
        assert user.username == "emailtest"
        assert user.email == "find@email.com"

    def test_get_by_email_not_found(self, db_session):
        """Test get_by_email returns None when email doesn't exist."""
        repo = UserRepository()

        user = repo.get_by_email(db_session, "notfound@example.com")

        assert user is None


class TestMeEndpoint:
    """HTTP-level integration tests for GET /auth/me."""

    def _register_and_get_token(self, client, username: str, email: str) -> str:
        """Register a user via /auth/signup and return the access token."""
        response = client.post(
            "/auth/signup",
            json={
                "username": username,
                "email": email,
                "password": "password123",
                "disease": ["lupus"],
                "weight": 150.0,
            },
        )
        assert response.status_code == 201
        return response.json()["access_token"]

    def test_me_success(self, test_client):
        """Test /me returns user info for a valid token."""
        token = self._register_and_get_token(test_client, "me_test_user", "me_test@example.com")

        response = test_client.get("/auth/me", headers={"authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "me_test_user"
        assert data["email"] == "me_test@example.com"
        assert "password_hash" not in data
        assert "created_at" in data

    def test_me_invalid_token(self, test_client):
        """Test /me returns 401 for an invalid token."""
        response = test_client.get("/auth/me", headers={"authorization": "Bearer invalidtoken"})

        assert response.status_code == 401

    def test_me_missing_bearer_prefix(self, test_client):
        """Test /me returns 401 when Authorization header lacks 'Bearer ' prefix."""
        token = self._register_and_get_token(test_client, "me_nobearer_user", "me_nobearer@example.com")
        response = test_client.get("/auth/me", headers={"authorization": token})

        assert response.status_code == 401

    def test_me_missing_authorization_header(self, test_client):
        """Test /me returns 401 when Authorization header is absent."""
        response = test_client.get("/auth/me")

        assert response.status_code == 401
