"""User database model."""

from sqlalchemy import ARRAY, Column, Date, DateTime, Float, String
from sqlalchemy.sql import func

from database import Base


class User(Base):
    """User ORM model mapped to the users table."""

    __tablename__ = "users"

    username = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    clerk_user_id = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    disease = Column(ARRAY(String), nullable=True)
    weight = Column(Float, nullable=True)
    gender = Column(String, nullable=True)
    medication = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
