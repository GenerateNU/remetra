"""User database model."""

from sqlalchemy import ARRAY, Column, Date, DateTime, Float, String
from sqlalchemy.sql import func

from database import Base


class User(Base):
    """User ORM model mapped to existing Supabase users table."""

    __tablename__ = "users"

    username = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    disease = Column(ARRAY(String), nullable=True)
    weight = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
