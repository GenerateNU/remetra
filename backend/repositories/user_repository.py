"""User repository for database operations."""

from typing import Optional

from sqlalchemy.orm import Session

from models.user import User
from schemas.user import UserUpdate


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

    def get_by_clerk_id(self, db: Session, clerk_user_id: str) -> Optional[User]:
        """Retrieve a user by their Clerk user id."""
        return db.query(User).filter(User.clerk_user_id == clerk_user_id).first()

    def create(
        self,
        db: Session,
        username: str,
        email: str,
        clerk_user_id: str | None = None,
        password_hash: str | None = None,
    ) -> User:
        """
        Create a new user in the database.

        Args:
            db: SQLAlchemy database session
            username: Unique username for the new user
            email: Unique email address for the new user
            clerk_user_id: Clerk user id
            password_hash: Unused for Clerk users, nullable

        Returns:
            User: The newly created user object with all fields populated

        Raises:
            IntegrityError: If username, email, or clerk_user_id already exists
        """
        user = User(
            username=username,
            email=email,
            clerk_user_id=clerk_user_id,
            password_hash=password_hash,
        )
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception:
            db.rollback()
            raise

    def update_user(self, db: Session, username: str, user_update: UserUpdate) -> User:
        """
        Update an existing user's information.

        Args:
            db: SQLAlchemy database session
            username: The username of the user to update
            user_update: UserUpdate schema containing fields to update

        Returns:
            User: The updated user object

        Raises:
            ValueError: If the user with the given username does not exist
        """
        user = self.get_by_username(db, username)
        if not user:
            raise ValueError(f"User with username '{username}' not found")

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user
