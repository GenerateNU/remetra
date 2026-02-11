"""User repository for database operations."""

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from models.user import User


class UserRepository:
    """Repository for user-related database operations."""

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Retrieve a user by their username.

        Args:
            db: SQLAlchemy database session
            username: The username to search for

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Args:
            db: SQLAlchemy database session
            email: The email address to search for

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    def create(
        self,
        db: Session,
        username: str,
        email: str,
        password_hash: str,
        dob: Optional[date] = None,
        disease: Optional[str] = None,
        weight: Optional[float] = None,
    ) -> User:
        """
        Create a new user in the database.

        Args:
            db: SQLAlchemy database session
            username: Unique username for the new user
            email: Unique email address for the new user
            password_hash: Bcrypt hashed password
            dob: Date of birth (optional)
            disease: Disease information (optional)
            weight: User weight in appropriate units (optional)

        Returns:
            User: The newly created user object with all fields populated

        Raises:
            IntegrityError: If username or email already exists
        """
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            dob=dob,
            disease=disease,
            weight=weight,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
