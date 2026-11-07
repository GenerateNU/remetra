from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from auth_context import current_username
from repositories.symptom_log_repository import SymptomLogRepository
from schemas.symptom_log import (
    SymptomFamily,
    SymptomLogCreate,
    SymptomLogResponse,
    SymptomLogUpdate,
    SymptomRoute,
    SymptomRouteType,
    WashoutStatus,
)
from services.symptom_routing import route_symptom

WASHOUT_INTENSITY = 7  # a model-routed symptom at or above this starts a washout
FAMILY_SPAN_WINDOW = timedelta(hours=24)  # 2+ families within this window starts a washout
WASHOUT_LENGTH = timedelta(hours=48)  # measured from the latest triggering symptom


def _spans_families(model_symptoms: list[tuple[SymptomRoute, int, datetime]], at: datetime) -> bool:
    """True if 2+ families (excluding OTHER) were logged in the 24 h ending at `at`."""
    families = {
        route.family
        for route, _, ts in model_symptoms
        if at - FAMILY_SPAN_WINDOW <= ts <= at and route.family not in (None, SymptomFamily.OTHER)
    }
    return len(families) >= 2


def washout_window(symptoms: list[tuple[SymptomRoute, int, datetime]], now: datetime) -> WashoutStatus:
    """Pure: given (route, intensity, timestamp) per symptom, is a washout active at `now`?

    A model-routed symptom triggers a washout if its intensity is >= 7, or if it completes a span of
    2+ families (OTHER doesn't count) within 24 h. The washout lasts 48 h from the latest trigger.
    Symptoms after `now` are ignored. ends_at is None when no washout is active.
    """
    model_symptoms = sorted(
        (s for s in symptoms if s[0].route == SymptomRouteType.MODEL and s[2] <= now),
        key=lambda s: s[2],
    )
    for route, intensity, ts in reversed(model_symptoms):
        triggered = intensity >= WASHOUT_INTENSITY or (
            route.family not in (None, SymptomFamily.OTHER) and _spans_families(model_symptoms, ts)
        )
        if triggered:
            ends_at = ts + WASHOUT_LENGTH
            if now < ends_at:
                return WashoutStatus(active=True, ends_at=ends_at)
            break
    return WashoutStatus(active=False, ends_at=None)


def _to_response(log) -> SymptomLogResponse:
    """Build the response with the route computed from the log's symptom."""
    route = route_symptom(log.symptom.sensation, log.symptom.location)
    stored = {
        name: getattr(log, name) for name in SymptomLogResponse.model_fields if name not in SymptomRoute.model_fields
    }
    return SymptomLogResponse(**stored, **route.model_dump())


class SymptomLogService:
    """Business logic for symptom logs."""

    def __init__(self):
        self.repo = SymptomLogRepository()

    def get_symptom_log(self, db: Session, log_id: UUID) -> Optional[SymptomLogResponse]:
        log = self.repo.get_by_id(db, log_id)
        if not log:
            return None
        return _to_response(log)

    def create_symptom_log(self, db: Session, data: SymptomLogCreate) -> SymptomLogResponse:
        log = self.repo.create(db, data)
        return _to_response(log)

    def get_symptom_logs_by_username(self, db: Session, username: str) -> list[SymptomLogResponse]:
        logs = self.repo.get_by_username(db, username)
        return [_to_response(log) for log in logs]

    def update_symptom_log(self, db: Session, log_id: UUID, data: SymptomLogUpdate) -> Optional[SymptomLogResponse]:
        updated = self.repo.update(db, log_id, data)
        if not updated:
            return None
        return _to_response(updated)

    def delete_symptom_log(self, db: Session, log_id: UUID) -> bool:
        return self.repo.delete(db, log_id)

    def get_washout_status(self, db: Session, now: datetime) -> WashoutStatus:
        """Washout status for the signed-in user."""
        since = now - WASHOUT_LENGTH - FAMILY_SPAN_WINDOW
        logs = [log for log in self.repo.get_by_username(db, current_username.get()) if log.timestamp >= since]
        symptoms = [
            (route_symptom(log.symptom.sensation, log.symptom.location), log.intensity, log.timestamp) for log in logs
        ]
        return washout_window(symptoms, now)
