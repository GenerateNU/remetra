"""
Router for symptom log endpoints.

Handles HTTP requests for creating, reading, updating, and deleting symptom logs.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from models.symptom_log_model import SymptomLogCreate, SymptomLogResponse
from repositories.symptom_log_repo import SymptomLogRepository
from services.symptom_log_ser import SymptomLogService

# Create router
router = APIRouter(
    prefix="/symptom-logs",
    tags=["Symptom Logs"],
)

symptom_log_repo = SymptomLogRepository()
symptom_log_service = SymptomLogService(symptom_log_repo)

@router.post(
    "/",
    response_model=SymptomLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_symptom_log(log: SymptomLogCreate) -> SymptomLogResponse:
    """
    Create a new symptom log.

    """
    try:
        created_log = await symptom_log_service.create_symptom_log(log)
        return created_log
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get(
    "/{log_id}",
    response_model=SymptomLogResponse,
)
async def get_symptom_log(log_id: int) -> SymptomLogResponse:
    """
    Get a specific symptom log by ID.


    """
    log = await symptom_log_service.get_symptom_log(log_id)
    
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
async def delete_symptom_log(log_id: int):
    """
    Delete a symptom log.

    """
    deleted = await symptom_log_service.delete_symptom_log(log_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symptom log with ID {log_id} not found",
        )
