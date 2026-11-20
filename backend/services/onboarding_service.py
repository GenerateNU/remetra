import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from analysis.nightly_refresh import nightly_refresh
from models.user_component_state import UserComponentState
from repositories.food_log_repository import FoodLogRepository
from repositories.symptom_log_repository import SymptomLogRepository
from repositories.user_component_state_repository import UserComponentStateRepository

CONDITION_FILE = Path(__file__).resolve().parent.parent / "data" / "taxonomy" / "condition_multipliers.yaml"
FAMILIES = ["GI", "SKIN", "HEAD"]
STARTING_BACKGROUND = {"GI": 0.20, "SKIN": 0.11, "HEAD": 0.15}


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
        """Create 120 rows (40 components x 3 families) for a new user. Returns row count, 0 if already seeded."""
        if self.repo.has_state(db, username):
            return 0

        user = self.repo.get_user(db, username)
        components = self.repo.get_all_components(db)
        config = _load_condition_multipliers()

        base_confidence = config["defaults"]["base_confidence"]
        user_diseases = user.disease or []

        rows = []
        for component in components:
            w = _compute_multiplier(user_diseases, component.slug, config)
            log_odds = math.log(base_confidence / (1 - base_confidence)) + math.log(w)

            for family in FAMILIES:
                background_rate = -math.log(1 - STARTING_BACKGROUND[family]) / 24

                rows.append(
                    UserComponentState(
                        username=username,
                        component_id=component.id,
                        family=family,
                        log_odds=log_odds,
                        expected_reactions=0.0,
                        exposure_count=0,
                        background_rate=background_rate,
                        background_total=0.0,
                        hours_since_onboarding=0.0,
                        last_update=datetime.now(timezone.utc),
                    )
                )

        self.repo.bulk_insert(db, rows)
        return len(rows)

    def run_user_night(self, db: Session, username: str, as_of: datetime) -> None:
        states = self.repo.get_states_for_user(db, username)
        if not states:
            self.initialize_user_state(db, username)
            states = self.repo.get_states_for_user(db, username)

        last_update = states[0].last_update
        if as_of <= last_update:
            return

        start = last_update - timedelta(hours=72)
        new_meals = []
        new_symptoms = []
        meals = self.food_repo.get_food_logs_by_username(db, username)
        for meal in meals:
            if meal.timestamp >= start:
                new_meals.append(meal)
        symptoms = self.symptom_repo.get_by_username(db, username)
        for symptom in symptoms:
            if symptom.timestamp >= start:
                new_symptoms.append(symptom)
        nightly_refresh(new_meals, new_symptoms, as_of, last_update, states)
        for s in states:
            s.last_update = as_of
        self.repo.update_states(db, states)
