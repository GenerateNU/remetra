"""
Router for symptom log endpoints.

Handles HTTP requests for creating, reading, and deleting symptom logs.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.symptom_log import SymptomLogCreate, SymptomLogResponse
from services.symptom_log_service import SymptomLogService

router = APIRouter(
    prefix="/symptom-logs",
    tags=["Symptom Logs"],
)


@router.post(
    "/",
    response_model=SymptomLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_symptom_log(log: SymptomLogCreate, db: Session = Depends(get_db)) -> SymptomLogResponse:
    """Create a new symptom log."""
    try:
        service = SymptomLogService()
        return service.create_symptom_log(db, log)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{log_id}",
    response_model=SymptomLogResponse,
)
async def get_symptom_log(log_id: UUID, db: Session = Depends(get_db)) -> SymptomLogResponse:
    """Get a specific symptom log by ID."""
    service = SymptomLogService()
    log = service.get_symptom_log(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symptom log with ID {log_id} not found",
        )
    return log


@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_symptom_log(log_id: UUID, db: Session = Depends(get_db)):
    """Delete a symptom log."""
    service = SymptomLogService()
    deleted = service.delete_symptom_log(db, log_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symptom log with ID {log_id} not found",
        )
