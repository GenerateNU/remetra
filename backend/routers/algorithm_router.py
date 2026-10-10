"""Router for symptom-food association algorithm endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from schemas.algorithm import AlgorithmAssociationResponse, AlgorithmRunRequest, AlgorithmRunResponse
from schemas.user import UserResponse
from services.algorithm_service import AlgorithmService

router = APIRouter(prefix="/algorithm", 
                   tags=["Algorithm"],
                   dependencies=[Depends(get_current_user)]
                )


@router.post("/run", response_model=AlgorithmRunResponse)
async def run_algorithm(
    payload: AlgorithmRunRequest,
    db: Session = Depends(get_db),
) -> AlgorithmRunResponse:
    """Run association algorithm and persist user+symptom+food metrics."""
    service = AlgorithmService()
    associations = service.run_algorithm(db, payload)
    return AlgorithmRunResponse(associations=associations)


@router.get("/associations", response_model=list[AlgorithmAssociationResponse])
async def get_associations(
    symptom_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[AlgorithmAssociationResponse]:
    """Fetch stored association rows for the signed-in user, optionally filtered by symptom."""
    service = AlgorithmService()
    symptom_ids = [symptom_id] if symptom_id else None
    return service.get_associations(db, current_user.username, symptom_ids)
