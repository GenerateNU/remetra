import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.tag import Tag, FoodTag
from schemas.tag import TagCreate


class TagRepository:
    """
    Repository for handling database interactions related to tags.
    """

    def __init__(self):
        pass

    def create_tag(self, db: Session, tag: TagCreate) -> Tag:
        """
        Create a new tag in the database.

        Args:
            tag: Validated data from TagCreate model

        Returns:
            The created tag
        """
        logging.info(f"Creating tag in database: {tag.name}")

        try:
            tag_dict = tag.model_dump()
            db_tag = Tag(**tag_dict)
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
            return db_tag
        except Exception as e:
            logging.error(f"Error creating tag in database: {e}")
            db.rollback()
            raise e

    def get_tag_by_id(self, db: Session, tag_id: UUID) -> Optional[Tag]:
        """
        Retrieve a tag by its ID.
        """
        logging.info(f"Retrieving tag with ID {tag_id} from database")
        return db.query(Tag).filter(Tag.id == tag_id).first()

    def get_tag_by_name(self, db: Session, name: str) -> Optional[Tag]:
        """
        Retrieve a tag by its name.
        """
        logging.info(f"Retrieving tag with name {name} from database")
        return db.query(Tag).filter(Tag.name == name).first()

    def get_all_tags(self, db: Session) -> list[Tag]:
        """
        Retrieve all tags.
        """
        logging.info("Retrieving all tags from database")
        return db.query(Tag).all()

    def add_tags_to_food(self, db: Session, food_id: UUID, tag_ids: list[UUID]) -> list[FoodTag]:
        """
        Add confirmed tags to a food via the FoodTag join table.
        Skips duplicates.

        Args:
            food_id: The ID of the food
            tag_ids: List of tag IDs to associate with the food

        Returns:
            List of created FoodTag entries
        """
        logging.info(f"Adding tags {tag_ids} to food {food_id}")

        try:
            food_tags = []
            for tag_id in tag_ids:
                existing = db.query(FoodTag).filter(
                    FoodTag.food_id == food_id,
                    FoodTag.tag_id == tag_id
                ).first()
                if not existing:
                    food_tag = FoodTag(food_id=food_id, tag_id=tag_id)
                    db.add(food_tag)
                    food_tags.append(food_tag)
            db.commit()
            return food_tags
        except Exception as e:
            logging.error(f"Error adding tags to food: {e}")
            db.rollback()
            raise e

    def get_tags_by_food_id(self, db: Session, food_id: UUID) -> list[Tag]:
        """
        Retrieve all confirmed tags for a given food.

        Args:
            food_id: The ID of the food

        Returns:
            List of tags associated with the food
        """
        logging.info(f"Retrieving tags for food {food_id}")
        return (
            db.query(Tag)
            .join(FoodTag, FoodTag.tag_id == Tag.id)
            .filter(FoodTag.food_id == food_id)
            .all()
        )