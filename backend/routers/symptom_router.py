"""Authentication routes for symptom CRUD."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.symptom import SymptomCreate, SymptomResponse
from schemas.user import UserResponse
from services.symptom_service import SymptomService

router = APIRouter(
    prefix="/symptom",
    tags=["Symptom"],
)


# create symptom
@router.post("/", response_model=SymptomResponse, status_code=status.HTTP_201_CREATED)
async def create_symptom(
    symptom: SymptomCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> SymptomResponse:
    """
    Creates new symptom item with ID, name, location, sensation.

    """

    symptom.username = current_user.username
    symptom_service = SymptomService()
    created_symptom = symptom_service.create_symptom(db, symptom)
    return created_symptom


# get symptom
@router.get("/{symptom_id}", response_model=SymptomResponse)
async def get_symptom(symptom_id: UUID, db: Session = Depends(get_db)) -> SymptomResponse:
    """
    Get a specific symptom by ID.

    Path parameters (like {symptom_id}) are extracted from the URL automatically.
    Example: GET /symptoms/42 → symptom_id = 42

    Args:
        symptom_id: ID from URL path parameter

    Returns:
        The requested symptom

    Raises:
        HTTPException: If symptom ID doesn't exist
    """
    symptom_service = SymptomService()
    symptom = symptom_service.get_symptom_by_id(db, symptom_id)

    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symptom with ID {symptom_id} not found",
        )

    return symptom


# get all symptom items
@router.get(
    "/",
    response_model=list[SymptomResponse],
)
async def get_all_symptoms(db: Session = Depends(get_db)) -> list[SymptomResponse]:
    """
    Get all symptom items.

    Returns:
        List of all symptom items
    """

    symptom_service = SymptomService()
    symptoms = symptom_service.get_all_symptoms(db)
    return symptoms


# put route - update symptom
@router.put("/{symptom_id}", response_model=SymptomResponse)
async def update_symptom(symptom_id: UUID, symptom: SymptomCreate, db: Session = Depends(get_db)) -> SymptomResponse:
    """
    Update an existing symptom by ID.

    Args:
        symptom_id: ID of the symptom to update
        symptom: Updated symptom data

    Returns:
        The updated symptom

    Raises:
        HTTPException: If symptom ID doesn't exist or input data is invalid
    """
    symptom_service = SymptomService()
    symptom_dict = symptom.model_dump()
    updated_symptom = symptom_service.update_symptom_by_id(db, symptom_id, symptom_dict)

    if not updated_symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symptom with ID {symptom_id} not found",
        )

    return updated_symptom


# delete route - delete symptom
@router.delete("/{symptom_id}", response_model=SymptomResponse)
async def delete_symptom(symptom_id: UUID, db: Session = Depends(get_db)) -> SymptomResponse:
    """Delete an existing symptom by ID.

    Args:
        symptom_id (UUID): ID of the symptom to update

    Returns:
        SymptomResponse: The deleted symptom

    Raises:
        HTTPException: If symptom ID doesn't exist
    """
    symptom_service = SymptomService()
    deleted_symptom = symptom_service.delete_symptom_by_id(db, symptom_id)
    if not deleted_symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symptom with ID {symptom_id} not found",
        )

    return deleted_symptom
