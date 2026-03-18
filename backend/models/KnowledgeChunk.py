import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class KnowledgeChunk(Base):
    __tablename__ = "chunk"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    source = Column(String, nullable=False)
