import math
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from models.user_component_state import UserComponentState
from repositories.user_component_state_repository import UserComponentStateRepository

CONDITION_FILE = Path(__file__).resolve().parent.parent / "data" / "taxonomy" / "condition_multipliers.yaml"
FAMILIES = ["GI", "SKIN", "HEAD"]
STARTING_BACKGROUND = {"GI": 0.20, "SKIN": 0.11, "HEAD": 0.15}


def _load_condition_multipliers() -> dict:
    with open(CONDITION_FILE) as f:
        return yaml.safe_load(f)


def _compute_multiplier(user_diseases: list[str], component_slug: str, config: dict) -> float:
    multiplier = 1.0
    for disease in user_diseases:
        condition = config["conditions"].get(disease.lower())
        if condition and component_slug in condition["components"]:
            multiplier *= condition["multiplier"]
    return multiplier


class OnboardingService:

    def __init__(self):
        self.repo = UserComponentStateRepository()

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
                    )
                )

        self.repo.bulk_insert(db, rows)
        return len(rows)
