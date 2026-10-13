import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class HealthKitEvent(Base):
    __tablename__ = "healthkit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    hk_uuid = Column(UUID(as_uuid=True), nullable=False)
    category = Column(String, nullable=False)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("username", "hk_uuid", name="uq_healthkit_user_hkuuid"),
    )
