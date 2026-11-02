"""Daily check in database model."""

import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class DailyCheckIn(Base):
    """A user's 'no symptoms today' check-in for one local date."""

    __tablename__ = "daily_check_ins"
    __table_args__ = (UniqueConstraint("username", "date", name="uq_daily_chek_in_user_date"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    timezone = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())