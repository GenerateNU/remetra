"""Router for symptom-food association algorithm endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.algorithm import AlgorithmAssociationResponse, AlgorithmRunRequest, AlgorithmRunResponse
from services.algorithm_service import AlgorithmService

router = APIRouter(prefix="/algorithm", tags=["Algorithm"])


@router.post("/run", response_model=AlgorithmRunResponse)
async def run_algorithm(
    payload: AlgorithmRunRequest,
    db: Session = Depends(get_db),
) -> AlgorithmRunResponse:
    """Run association algorithm and persist user+symptom+food metrics."""
    service = AlgorithmService()
    associations = service.run_algorithm(db, payload)
    return AlgorithmRunResponse(associations=associations)


@router.get("/user/{user_id}", response_model=list[AlgorithmAssociationResponse])
async def get_associations(
    user_id: str,
    symptom_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> list[AlgorithmAssociationResponse]:
    """Fetch stored association rows for a user, optionally filtered by symptom."""
    service = AlgorithmService()
    symptom_ids = [symptom_id] if symptom_id else None
    return service.get_associations(db, user_id, symptom_ids)
