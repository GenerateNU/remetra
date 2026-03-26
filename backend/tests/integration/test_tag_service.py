"""Integration tests for TagRepository and TagService."""

from uuid import uuid4

import pytest

from models.tag import FoodTag, Tag
from repositories.tag_repository import TagRepository
from schemas.tag import TagCreate, TagResponse
from services.tag_service import TagService


@pytest.fixture
def sample_tag_data():
    """A basic user-defined tag."""
    return TagCreate(name="nightshades", description="Nightshade family", is_system=True)


@pytest.fixture
def second_tag_data():
    """A second tag for multi-tag tests."""
    return TagCreate(name="FODMAPs", description="High FODMAP ingredient", is_system=True)


class TestTagRepository:
    """Integration tests for TagRepository."""

    def test_create_tag(self, db_session, sample_tag_data):
        """Creating a tag persists it with the correct fields."""
        repo = TagRepository()

        result = repo.create_tag(db_session, sample_tag_data)

        assert isinstance(result, Tag)
        assert result.id is not None
        assert result.name == sample_tag_data.name
        assert result.description == sample_tag_data.description
        assert result.is_system is True
        assert result.created_at is not None

    def test_create_tag_defaults_is_system_false(self, db_session):
        """is_system defaults to False when not specified."""
        repo = TagRepository()

        result = repo.create_tag(db_session, TagCreate(name="custom-tag"))

        assert result.is_system is False

    def test_get_tag_by_id(self, db_session, sample_tag_data):
        """get_tag_by_id returns the correct tag."""
        repo = TagRepository()
        created = repo.create_tag(db_session, sample_tag_data)

        result = repo.get_tag_by_id(db_session, created.id)

        assert result is not None
        assert result.id == created.id
        assert result.name == sample_tag_data.name

    def test_get_tag_by_id_not_found(self, db_session):
        """get_tag_by_id returns None for a non-existent ID."""
        repo = TagRepository()

        result = repo.get_tag_by_id(db_session, uuid4())

        assert result is None

    def test_get_tag_by_name(self, db_session, sample_tag_data):
        """get_tag_by_name returns the correct tag."""
        repo = TagRepository()
        created = repo.create_tag(db_session, sample_tag_data)

        result = repo.get_tag_by_name(db_session, sample_tag_data.name)

        assert result is not None
        assert result.id == created.id

    def test_get_tag_by_name_not_found(self, db_session):
        """get_tag_by_name returns None when the name does not exist."""
        repo = TagRepository()

        result = repo.get_tag_by_name(db_session, "does-not-exist")

        assert result is None

    def test_get_all_tags(self, db_session, sample_tag_data, second_tag_data):
        """get_all_tags returns all tags in the database."""
        repo = TagRepository()
        repo.create_tag(db_session, sample_tag_data)
        repo.create_tag(db_session, second_tag_data)

        results = repo.get_all_tags(db_session)

        names = [t.name for t in results]
        assert sample_tag_data.name in names
        assert second_tag_data.name in names

    def test_add_tags_to_food(self, db_session, created_food, sample_tag_data, second_tag_data):
        """add_tags_to_food creates FoodTag join rows for each tag."""
        repo = TagRepository()
        tag_a = repo.create_tag(db_session, sample_tag_data)
        tag_b = repo.create_tag(db_session, second_tag_data)

        food_tags = repo.add_tags_to_food(db_session, created_food.id, [tag_a.id, tag_b.id])

        assert len(food_tags) == 2
        assert all(isinstance(ft, FoodTag) for ft in food_tags)
        assert all(ft.food_id == created_food.id for ft in food_tags)

    def test_add_tags_to_food_skips_duplicates(self, db_session, created_food, sample_tag_data):
        """Calling add_tags_to_food twice with the same tag does not create duplicates."""
        repo = TagRepository()
        tag = repo.create_tag(db_session, sample_tag_data)

        repo.add_tags_to_food(db_session, created_food.id, [tag.id])
        food_tags = repo.add_tags_to_food(db_session, created_food.id, [tag.id])

        assert food_tags == []  # second call skips the already-existing join row
        count = db_session.query(FoodTag).filter(FoodTag.food_id == created_food.id).count()
        assert count == 1

    def test_get_tags_by_food_id(self, db_session, created_food, sample_tag_data, second_tag_data):
        """get_tags_by_food_id returns the Tag objects linked to a food."""
        repo = TagRepository()
        tag_a = repo.create_tag(db_session, sample_tag_data)
        tag_b = repo.create_tag(db_session, second_tag_data)
        repo.add_tags_to_food(db_session, created_food.id, [tag_a.id, tag_b.id])

        results = repo.get_tags_by_food_id(db_session, created_food.id)

        assert len(results) == 2
        names = [t.name for t in results]
        assert sample_tag_data.name in names
        assert second_tag_data.name in names

    def test_get_tags_by_food_id_empty(self, db_session, created_food):
        """get_tags_by_food_id returns an empty list when no tags are assigned."""
        repo = TagRepository()

        results = repo.get_tags_by_food_id(db_session, created_food.id)

        assert results == []


class TestTagService:
    """Integration tests for TagService."""

    def test_create_tag(self, db_session, sample_tag_data):
        """create_tag returns a TagResponse with correct fields."""
        service = TagService()

        result = service.create_tag(db_session, sample_tag_data)

        assert isinstance(result, TagResponse)
        assert result.id is not None
        assert result.name == sample_tag_data.name
        assert result.is_system is True
        assert result.created_at is not None

    def test_get_all_tags(self, db_session, sample_tag_data, second_tag_data):
        """get_all_tags returns a list of TagResponse objects."""
        service = TagService()
        service.create_tag(db_session, sample_tag_data)
        service.create_tag(db_session, second_tag_data)

        results = service.get_all_tags(db_session)

        assert all(isinstance(t, TagResponse) for t in results)
        names = [t.name for t in results]
        assert sample_tag_data.name in names
        assert second_tag_data.name in names

    def test_get_tag_by_id(self, db_session, sample_tag_data):
        """get_tag_by_id returns a TagResponse for a known ID."""
        service = TagService()
        created = service.create_tag(db_session, sample_tag_data)

        result = service.get_tag_by_id(db_session, created.id)

        assert isinstance(result, TagResponse)
        assert result.id == created.id

    def test_get_tag_by_id_not_found(self, db_session):
        """get_tag_by_id returns None for a non-existent ID."""
        service = TagService()

        result = service.get_tag_by_id(db_session, uuid4())

        assert result is None

    def test_add_tags_to_food(self, db_session, created_food, sample_tag_data, second_tag_data):
        """add_tags_to_food persists tags and returns a list of TagResponse."""
        service = TagService()
        tag_a = service.create_tag(db_session, sample_tag_data)
        tag_b = service.create_tag(db_session, second_tag_data)

        results = service.add_tags_to_food(db_session, created_food.id, [tag_a.id, tag_b.id])

        assert len(results) == 2
        assert all(isinstance(t, TagResponse) for t in results)
        names = [t.name for t in results]
        assert sample_tag_data.name in names
        assert second_tag_data.name in names

    def test_add_tags_to_food_idempotent(self, db_session, created_food, sample_tag_data):
        """Calling add_tags_to_food twice returns only one tag, no duplicates."""
        service = TagService()
        tag = service.create_tag(db_session, sample_tag_data)

        service.add_tags_to_food(db_session, created_food.id, [tag.id])
        results = service.add_tags_to_food(db_session, created_food.id, [tag.id])

        assert len(results) == 1

    def test_get_tags_by_food_id(self, db_session, created_food, sample_tag_data):
        """get_tags_by_food_id returns confirmed tags for the food."""
        service = TagService()
        tag = service.create_tag(db_session, sample_tag_data)
        service.add_tags_to_food(db_session, created_food.id, [tag.id])

        results = service.get_tags_by_food_id(db_session, created_food.id)

        assert len(results) == 1
        assert isinstance(results[0], TagResponse)
        assert results[0].name == sample_tag_data.name

    def test_get_tags_by_food_id_empty(self, db_session, created_food):
        """get_tags_by_food_id returns an empty list when no tags are assigned."""
        service = TagService()

        results = service.get_tags_by_food_id(db_session, created_food.id)

        assert results == []
