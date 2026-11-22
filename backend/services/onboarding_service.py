import math
from datetime import datetime, timezone
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from analysis.model_constants import INITIAL_LOG_ODDS, initial_background_rate
from analysis.nightly_refresh import lookback, nightly_refresh
from models.symptom_family import MODELED_FAMILIES
from models.user_component_state import UserComponentState
from repositories.food_log_repository import FoodLogRepository
from repositories.symptom_log_repository import SymptomLogRepository
from repositories.user_component_state_repository import UserComponentStateRepository
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
        self.repo = UserComponentStateRepository()
        self.food_repo = FoodLogRepository()
        self.symptom_repo = SymptomLogRepository()

    def initialize_user_state(self, db: Session, username: str) -> int:
        """Create one row per component per modeled family for a new user. Returns row count, 0 if already seeded."""
        if self.repo.has_state(db, username):
            return 0

        user = self.repo.get_user(db, username)
        components = self.repo.get_all_components(db)
        if not components:
            raise ValueError("No components in the database; run scripts/seed_taxonomy.py first")
        config = _load_condition_multipliers()
        user_diseases = user.disease or []
        now = datetime.now(timezone.utc)

        rows = []
        for component in components:
            log_odds = INITIAL_LOG_ODDS + math.log(_compute_multiplier(user_diseases, component.slug, config))
            for family in MODELED_FAMILIES:
                rows.append(
                    UserComponentState(
                        username=username,
                        component_id=component.id,
                        family=family.value,
                        log_odds=log_odds,
                        expected_reactions=0.0,
                        exposure_count=0,
                        background_rate=initial_background_rate(family),
                        background_total=0.0,
                        hours_since_onboarding=0.0,
                        last_update=now,
                    )
                )

        self.repo.bulk_insert(db, rows)
        return len(rows)

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
        states = self.repo.get_states_for_user(db, username)
        if not states:
            self.initialize_user_state(db, username)
            states = self.repo.get_states_for_user(db, username)

        last_update = min(s.last_update for s in states)
        if as_of <= last_update:
            return

        meals, symptoms = self.collect_night_logs(db, username, last_update, as_of)
        nightly_refresh(meals, symptoms, as_of, last_update, states)
        for s in states:
            s.last_update = as_of
        self.repo.update_states(db, states)
