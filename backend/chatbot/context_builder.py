"""
Context builder for the chatbot.

Each method maps to a tool the LLM can call. Methods gather the data the
chatbot needs for the current user. The DB session is passed per call and
never stored on the class.
"""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from services.food_log_service import FoodLogService
from services.symptom_log_service import SymptomLogService


class ContextBuilder:
    def __init__(self):
        self.food_log_service = FoodLogService()
        self.symptom_log_service = SymptomLogService()

    def get_revealed_insights(self, db: Session, user_id: UUID) -> list[dict]:
        """
        Labels and explanations for revealed food groups only.
        The reveal policy is applied here on the server, never by the LLM.
        """
        raise NotImplementedError

    def get_logs(self, db: Session, username: str, days: int = 30) -> dict:
        """
        Food logs, symptom logs and check-ins for a date range.
        """
        # TODO: check_ins
        now = datetime.now(timezone.utc)

        food_logs = self.food_log_service.get_food_logs_by_username(db, username)
        symptom_logs = self.symptom_log_service.get_symptom_logs_by_username(db, username)

        filtered_food_log = []
        filtered_symptom_log = []

        days_ago = now - timedelta(days=days)

        for log in food_logs:
            if log.timestamp >= days_ago and log.timestamp <= now:
                filtered_food_log.append(log)

        for log in symptom_logs:
            if log.timestamp >= days_ago and log.timestamp <= now:
                filtered_symptom_log.append(log)

        return {
            "food_logs": filtered_food_log,
            "symptom_logs": filtered_symptom_log,
            "check_ins": [],  # TODO: Here
        }

    def get_trends(self, db: Session, user_id: str, days: int = 30) -> dict:
        """
        per symptom
        Pre-computed summaries for a date range: symptom frequency,
        intensity and logging consistency.
        """
        logs = self.get_logs(db, user_id, days)

        # symptom_id -> every intensity logged for it (count = len of the list)
        intensities_by_symptom: dict[UUID, list[int]] = {}

        for log in logs["symptom_logs"]:
            intensities_by_symptom.setdefault(log.symptom_id, []).append(log.intensity)

        trends = {
            str(symptom_id): {
                "count": len(values),
                "avg_intensity": round(sum(values) / len(values), 1),
                "max_intensity": max(values),
                "min_intensity": min(values),
                "logging_frequency": round(len(values) / days, 1),
            }
            for symptom_id, values in intensities_by_symptom.items()
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
