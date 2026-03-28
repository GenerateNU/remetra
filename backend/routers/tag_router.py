"""Routes for tag CRUD and food-tag association."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from schemas.tag import TagCreate, TagResponse
from services.tag_service import TagService

router = APIRouter()


class AddTagsRequest(BaseModel):
    tag_ids: list[UUID]


# create tag
@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)) -> TagResponse:
    """Create a new user-defined tag."""
    tag_service = TagService()
    return tag_service.create_tag(db, tag)


# get all tags
@router.get("/tags", response_model=list[TagResponse])
async def get_all_tags(db: Session = Depends(get_db)) -> list[TagResponse]:
    """Return all available tags."""
    tag_service = TagService()
    return tag_service.get_all_tags(db)


# confirm and persist tags to a food
@router.post(
    "/food/{food_id}/tags",
    response_model=list[TagResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_tags_to_food(
    food_id: UUID,
    body: AddTagsRequest,
    db: Session = Depends(get_db),
) -> list[TagResponse]:
    """Confirm and persist a list of tags to a food item."""
    tag_service = TagService()
    try:
        return tag_service.add_tags_to_food(db, food_id, body.tag_ids)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add tags to food: {e}",
        )


# get all confirmed tags for a food
@router.get("/food/{food_id}/tags", response_model=list[TagResponse])
async def get_tags_by_food_id(
    food_id: UUID,
    db: Session = Depends(get_db),
) -> list[TagResponse]:
    """Return all confirmed tags for a given food item."""
    tag_service = TagService()
    return tag_service.get_tags_by_food_id(db, food_id)