import math
from datetime import datetime, timezone
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from analysis.model_constants import INITIAL_LOG_ODDS
from analysis.nightly_refresh import lookback, nightly_refresh
from models.symptom_family import MODELED_FAMILIES
from repositories.family_confidence_repository import FamilyConfidenceRepository
from repositories.food_log_repository import FoodLogRepository
from repositories.symptom_log_repository import SymptomLogRepository
from repositories.user_model_run_repository import UserModelRunRepository
from repositories.user_repository import UserRepository
from schemas.food_log import FoodLogResponse
from schemas.symptom_log import SymptomLogResponse
from services.symptom_log_service import to_symptom_log_response

CONDITION_FILE = Path(__file__).resolve().parent.parent / "data" / "taxonomy" / "condition_multipliers.yaml"


def _load_condition_multipliers() -> dict:
    with open(CONDITION_FILE) as f:
        return yaml.safe_load(f)


def _compute_multiplier(user_diseases: list[str], component_slug: str, config: dict) -> float:
    # TODO: 3x multiplier for suspected foods when that is added to user table?
    multiplier = 1.0
    for disease in user_diseases:
        condition = config["conditions"].get(disease.lower())
        if condition and component_slug in condition["components"]:
            multiplier *= condition["multiplier"]
    return multiplier


class OnboardingService:
    def __init__(self):
        self.repo = FamilyConfidenceRepository()
        self.run_repo = UserModelRunRepository()
        self.user_repo = UserRepository()
        self.food_repo = FoodLogRepository()
        self.symptom_repo = SymptomLogRepository()

    def initialize_user_state(self, db: Session, username: str) -> int:
        """Seed a new user's model state: family confidences raised by their onboarding conditions, background
        totals, and the nightly run marker (last_update = now).

        Returns the number of confidence rows created, 0 if the user already had them. Safe to call again: each
        piece is only created if it is missing.
        """
        created = 0
        if not self.repo.has_confidences(db, username):
            user = self.user_repo.get_by_username(db, username)
            if user is None:
                raise ValueError(f"User '{username}' not found")
            components = self.repo.get_all_components(db)
            if not components:
                raise ValueError("No components in the database; run scripts/seed_taxonomy.py first")
            config = _load_condition_multipliers()
            user_diseases = user.disease or []
            starting_log_odds = {
                component.id: INITIAL_LOG_ODDS + math.log(_compute_multiplier(user_diseases, component.slug, config))
                for component in components
            }
            self.repo.initialize_for_user(db, username, starting_log_odds)
            created = len(components) * len(MODELED_FAMILIES)

        if self.run_repo.get(db, username) is None:
            self.run_repo.create(db, username, datetime.now(timezone.utc))
        return created

    def collect_night_logs(
        self, db: Session, username: str, last_update: datetime, as_of: datetime
    ) -> tuple[list[FoodLogResponse], list[SymptomLogResponse]]:
        """Logs a nightly run needs to observe everything in (last_update, as_of].

        Symptoms: every modeled-family symptom logged in the window.
        Meals: every meal in the window. When there are symptoms, the meal window is widened back to the
        earliest point any of them could have been caused (symptom time - its family's lookback), so meals
        eaten before last_update are included as candidate causes. With no symptoms, no older meals are read.
        """
        symptoms = [
            to_symptom_log_response(log)
            for log in self.symptom_repo.get_by_username_between(db, username, last_update, as_of)
            if log.timestamp > last_update
        ]
        symptoms = [s for s in symptoms if s.family in MODELED_FAMILIES]

        meal_start = min([last_update, *(s.timestamp - lookback(s.family) for s in symptoms)])
        meals = [
            FoodLogResponse.model_validate(log)
            for log in self.food_repo.get_food_logs_by_username_between(db, username, meal_start, as_of)
        ]
        return meals, symptoms

    def run_user_night(self, db: Session, username: str, as_of: datetime) -> None:
        """Observe everything logged since the user's last nightly run, then move last_update to as_of.

        Runs outside a request, so callers must wrap it in auth_context.system_access().
        """
        self.initialize_user_state(db, username)
        run = self.run_repo.get(db, username)

        last_update = run.last_update
        if as_of <= last_update:
            return

        meals, symptoms = self.collect_night_logs(db, username, last_update, as_of)
        nightly_refresh(meals, symptoms, as_of, last_update)
        self.run_repo.set_last_update(db, run, as_of)
