"""
Context builder for the chatbot.

Each method maps to a tool the LLM can call. Methods gather the data the
chatbot needs for the current user. The DB session is passed per call and
never stored on the class.
"""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

import auth_context as auth
from services.food_log_service import FoodLogService
from services.symptom_log_service import SymptomLogService
from services.symptom_service import SymptomService

# Only these fields are exposed to the LLM. Internal fields like the log id,
# username and created_at are deliberately left out.
FOOD_LOG_FIELDS = {"food_id", "quantity", "timestamp", "notes"}
SYMPTOM_LOG_FIELDS = {"symptom_id", "intensity", "timestamp", "duration", "notes"}


class ContextBuilder:
    def __init__(self):
        self.food_log_service = FoodLogService()
        self.symptom_log_service = SymptomLogService()
        self.symptom_service = SymptomService()

    def get_revealed_insights(self, db: Session, user_id: UUID) -> list[dict]:
        """
        Labels and explanations for revealed food groups only.
        The reveal policy is applied here on the server, never by the LLM.
        """
        raise NotImplementedError

    def get_logs(self, db: Session, days: int = 30) -> dict:
        """
        Food logs, symptom logs and check-ins for a date range.
        """
        # TODO: check_ins
        username = auth.current_username.get()
        if username is None:
            raise ValueError("Authenticated username is required")

        now = datetime.now(timezone.utc)

        food_logs = self.food_log_service.get_food_logs_by_username(db, username)
        symptom_logs = self.symptom_log_service.get_symptom_logs_by_username(db, username)

        filtered_food_log = []
        filtered_symptom_log = []

        days_ago = now - timedelta(days=days)

        for log in food_logs:
            if log.timestamp >= days_ago and log.timestamp <= now:
                filtered_food_log.append(log.model_dump(include=FOOD_LOG_FIELDS))

        for log in symptom_logs:
            if log.timestamp >= days_ago and log.timestamp <= now:
                filtered_symptom_log.append(log.model_dump(include=SYMPTOM_LOG_FIELDS))

        return {
            "food_logs": filtered_food_log,
            "symptom_logs": filtered_symptom_log,
            "check_ins": [],  # TODO: Here
        }

    def get_trends(self, db: Session, days: int = 30) -> dict:
        """
        per symptom
        Pre-computed summaries for a date range: symptom frequency,
        intensity and logging consistency.
        """
        if days <= 0:
            raise ValueError()

        logs = self.get_logs(db, days)

        # symptom name -> every intensity logged for it (count = len of the list)
        intensities_by_symptom: dict[str, list[int]] = {}

        for log in logs["symptom_logs"]:
            symptom = self.symptom_service.get_symptom_by_id(db, log["symptom_id"])
            intensities_by_symptom.setdefault(symptom.name, []).append(log["intensity"])

        trends = {
            str(symptom_name): {
                "count": len(values),
                "avg_intensity": round(sum(values) / len(values), 1),
                "max_intensity": max(values),
                "min_intensity": min(values),
                "avg_logs_per_day": round(len(values) / days, 1),
            }
            for symptom_name, values in intensities_by_symptom.items()
        }

        return trends

    def get_meal_ideas(self, db: Session, user_id: UUID, day: date) -> list[dict]:
        """
        Meal ideas for the given day, with ingredients, spices, steps and swaps.
        """
        raise NotImplementedError

    def adapt_recipe(self, db: Session, user_id: UUID, recipe: dict, request: str) -> dict:
        """
        An adapted recipe, validated against the user's profile constraints.
        """
        raise NotImplementedError

    def get_profile_constraints(self, db: Session, user_id: UUID) -> dict:
        """
        Conditions, exclusions, allergies and regular foods for the user.
        """
        raise NotImplementedError

    def draft_log_entry(self, db: Session, user_id: UUID, text: str) -> dict:
        """
        A proposed food or symptom entry for the person to confirm.
        Nothing is persisted here; the user confirms before saving.
        """
        raise NotImplementedError

    def create_summary(self, db: Session, user_id: UUID, start_date: date, end_date: date) -> dict:
        """
        An appointment summary document for a date range.
        """
        raise NotImplementedError
