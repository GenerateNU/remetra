import uuid

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class DailyHealthMetrics(Base):
    __tablename__ = "daily_health_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    timezone = Column(String, nullable=False)
    sleep_total_min = Column(Integer, nullable=True)
    sleep_deep_min = Column(Integer, nullable=True)
    sleep_rem_min = Column(Integer, nullable=True)
    sleep_core_min = Column(Integer, nullable=True)
    sleep_awake_min = Column(Integer, nullable=True)
    hrv_avg_ms = Column(Float, nullable=True)
    resting_hr_bpm = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
    UniqueConstraint("username", "date", name="uq_daily_health_user_date"),
    )
    