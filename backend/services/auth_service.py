"""Authentication service for user registration and login."""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from repositories.user_repository import UserRepository
from schemas.user import UserCreate, UserResponse

SECRET_KEY = os.getenv("SECRET_KEY", "Ch@ng31tN0W!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The bcrypt hashed password to compare against

    Returns:
        bool: True if password matches hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        str: The bcrypt hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in the token (e.g., {"sub": username})
        expires_delta: Optional custom expiration time. If None, defaults to 15 minutes

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.

    Args:
        token: The JWT token string to decode

    Returns:
        Optional[dict]: Dictionary containing the token payload if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


class AuthService:
    """Service layer for authentication operations."""

    def __init__(self):
        self.user_repo = UserRepository()

    def register_user(self, db: Session, user_data: UserCreate) -> UserResponse:
        """
        Register a new user.

        Args:
            db: Database session
            user_data: User registration data including username, email, password, and optional fields

        Returns:
            UserResponse: The created user object without password hash

        Raises:
            HTTPException 400: If username or email already exists in the database
        """
        if self.user_repo.get_by_username(db, user_data.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

        if self.user_repo.get_by_email(db, user_data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        password_hash = get_password_hash(user_data.password)

        user = self.user_repo.create(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            dob=user_data.dob,
            disease=user_data.disease,
            weight=user_data.weight,
        )

        return UserResponse.model_validate(user)

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[dict]:
        """
        Authenticate a user and return access token.

        Args:
            db: Database session
            username: Username to authenticate
            password: Plain text password to verify

        Returns:
            Optional[dict]: Dictionary containing access_token, token_type, and username if
                          authentication successful, None if credentials are invalid
        """
        user = self.user_repo.get_by_username(db, username)
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

        return {"access_token": access_token, "token_type": "bearer", "username": user.username}

    def get_current_user(self, db: Session, username: str) -> Optional[UserResponse]:
        """
        Get current user by username from JWT token.

        Args:
            db: Database session
            username: Username extracted from JWT token payload

        Returns:
            Optional[UserResponse]: User data without password if found, None otherwise
        """
        user = self.user_repo.get_by_username(db, username)
        if not user:
            return None

        return UserResponse.model_validate(user)
