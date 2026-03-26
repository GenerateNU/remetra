"""Service layer for tag operations."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from repositories.tag_repository import TagRepository
from schemas.tag import TagCreate, TagResponse

logger = logging.getLogger(__name__)


class TagService:

    def create_tag(self, db: Session, tag: TagCreate) -> TagResponse:
        """Create a new tag."""
        tag_repo = TagRepository()
        created = tag_repo.create_tag(db, tag)
        return TagResponse.model_validate(created)

    def get_all_tags(self, db: Session) -> list[TagResponse]:
        """Return all tags."""
        tag_repo = TagRepository()
        tags = tag_repo.get_all_tags(db)
        return [TagResponse.model_validate(t) for t in tags]

    def get_tag_by_id(self, db: Session, tag_id: UUID) -> Optional[TagResponse]:
        """Return a single tag by ID, or None if not found."""
        tag_repo = TagRepository()
        tag = tag_repo.get_tag_by_id(db, tag_id)
        if not tag:
            return None
        return TagResponse.model_validate(tag)

    def add_tags_to_food(self, db: Session, food_id: UUID, tag_ids: list[UUID]) -> list[TagResponse]:
        """Persist confirmed tags to a food, then return the full tag objects."""
        tag_repo = TagRepository()
        tag_repo.add_tags_to_food(db, food_id, tag_ids)
        tags = tag_repo.get_tags_by_food_id(db, food_id)
        return [TagResponse.model_validate(t) for t in tags]

    def get_tags_by_food_id(self, db: Session, food_id: UUID) -> list[TagResponse]:
        """Return all confirmed tags for a food."""
        tag_repo = TagRepository()
        tags = tag_repo.get_tags_by_food_id(db, food_id)
        return [TagResponse.model_validate(t) for t in tags]