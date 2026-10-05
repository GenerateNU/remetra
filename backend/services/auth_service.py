"""Authentication service.

Clerk owns credentials. This service resolves a verified Clerk user id to the
local profile row and updates health fields that stay in our database.
"""

import os
from typing import Any, Optional

from clerk_backend_api import AuthenticateRequestOptions, Clerk
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from repositories.user_repository import UserRepository
from schemas.user import UserResponse, UserUpdate


class AuthService:
    """Service layer for resolving Clerk users to local profiles."""

    def __init__(self):
        self.user_repo = UserRepository()

    def resolve_user(self, db: Session, clerk_user_id: str) -> UserResponse:
        """Return the local user for a Clerk id, creating the row on first sight."""
        existing = self.user_repo.get_by_clerk_id(db, clerk_user_id)
        if existing:
            return UserResponse.model_validate(existing)

        username, email = fetch_clerk_profile(clerk_user_id)
        return self.provision_user(db, clerk_user_id, username, email)

    def provision_user(self, db: Session, clerk_user_id: str, username: str, email: str) -> UserResponse:
        """Insert a local user linked to a Clerk account."""
        if self.user_repo.get_by_username(db, username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

        if self.user_repo.get_by_email(db, email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        try:
            user = self.user_repo.create(
                db=db,
                username=username,
                email=email,
                clerk_user_id=clerk_user_id,
            )
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            ) from exc

        return UserResponse.model_validate(user)

    def update_user(self, db: Session, username: str, user_update: UserUpdate) -> UserResponse:
        """
        Update a user's health profile.

        Args:
            db: database session
            username: The username of the user to update
            user_update: UserUpdate schema containing fields to update

        Returns:
            UserResponse: The updated user data

        Raises:
            ValueError: If the user with the given username does not exist
        """
        updated_user = self.user_repo.update_user(db, username, user_update)
        return UserResponse.model_validate(updated_user)


def fetch_clerk_profile(clerk_user_id: str) -> tuple[str, str]:
    """Load username and primary email for a Clerk user. Called once per new account."""
    secret = os.getenv("CLERK_SECRET_KEY")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CLERK_SECRET_KEY is not configured",
        )

    try:
        with Clerk(bearer_auth=secret) as clerk:
            clerk_user = clerk.users.get(user_id=clerk_user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not load Clerk user",
        ) from exc

    if clerk_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return profile_from_clerk_user(clerk_user)


def profile_from_clerk_user(clerk_user: Any) -> tuple[str, str]:
    """Read the username and primary email off a Clerk user object."""
    username = getattr(clerk_user, "username", None)
    email = _primary_email(clerk_user)
    if not username or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clerk user is missing a username or email",
        )
    return username, email


def _primary_email(clerk_user: Any) -> Optional[str]:
    emails = getattr(clerk_user, "email_addresses", None) or []
    primary_id = getattr(clerk_user, "primary_email_address_id", None)
    for address in emails:
        if _email_id(address) == primary_id and _email_address(address):
            return _email_address(address)
    for address in emails:
        email = _email_address(address)
        if email:
            return email
    return None


def _email_id(address: Any) -> Optional[str]:
    if isinstance(address, dict):
        return address.get("id")
    return getattr(address, "id", None)


def _email_address(address: Any) -> Optional[str]:
    if isinstance(address, dict):
        return address.get("email_address")
    return getattr(address, "email_address", None)


def clerk_auth_options() -> AuthenticateRequestOptions:
    """Build Clerk request-verification options from the environment."""
    raw_parties = os.getenv("CLERK_AUTHORIZED_PARTIES", "")
    parties = [part.strip() for part in raw_parties.split(",") if part.strip()]
    jwt_key = os.getenv("CLERK_JWT_KEY")
    if jwt_key:
        jwt_key = jwt_key.replace("\\n", "\n")

    return AuthenticateRequestOptions(
        secret_key=os.getenv("CLERK_SECRET_KEY"),
        jwt_key=jwt_key,
        authorized_parties=parties or None,
        accepts_token=["session_token"],
    )
