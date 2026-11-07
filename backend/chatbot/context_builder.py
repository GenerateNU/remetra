"""
Context builder for the chatbot.

Each method maps to a tool the LLM can call. Methods gather the data the
chatbot needs for the current user. The DB session is passed per call and
never stored on the class.
"""

from collections import Counter
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

import auth_context as auth
from services.food_log_service import FoodLogService
from services.food_service import FoodService
from services.symptom_log_service import SymptomLogService
from services.symptom_service import SymptomService

# fields copied straight from the log. id, username and created_at stay out.
FOOD_LOG_DUMP_FIELDS = {"food_id", "quantity", "timestamp", "notes"}
SYMPTOM_LOG_DUMP_FIELDS = {"symptom_id", "intensity", "timestamp", "duration", "notes"}

# what the bot sees. ids let it point at one log, names let it say what they were.
FOOD_LOG_FIELDS = FOOD_LOG_DUMP_FIELDS | {"food"}
SYMPTOM_LOG_FIELDS = SYMPTOM_LOG_DUMP_FIELDS | {"symptom"}

UNKNOWN = "unknown"


class ContextBuilder:
    def __init__(self):
        self.food_log_service = FoodLogService()
        self.symptom_log_service = SymptomLogService()
        self.food_service = FoodService()
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
        days_ago = now - timedelta(days=days)

        food_logs = self.food_log_service.get_food_logs_by_username(db, username)
        symptom_logs = self.symptom_log_service.get_symptom_logs_by_username(db, username)

        # looked up once per call, not once per log
        food_names = self._food_names(db, username)
        symptom_labels = self._symptom_labels(db, username)

        filtered_food_log = []
        filtered_symptom_log = []

        for log in food_logs:
            if days_ago <= log.timestamp <= now:
                entry = log.model_dump(include=FOOD_LOG_DUMP_FIELDS)
                entry["food"] = food_names.get(log.food_id, UNKNOWN)
                filtered_food_log.append(entry)

        for log in symptom_logs:
            if days_ago <= log.timestamp <= now:
                entry = log.model_dump(include=SYMPTOM_LOG_DUMP_FIELDS)
                entry["symptom"] = symptom_labels.get(log.symptom_id, UNKNOWN)
                filtered_symptom_log.append(entry)

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
            raise ValueError("days must be greater than 0")

        logs = self.get_logs(db, days)

        # symptom label -> all the intensities logged for it
        intensities_by_symptom: dict[str, list[int]] = {}

        for log in logs["symptom_logs"]:
            intensities_by_symptom.setdefault(log["symptom"], []).append(log["intensity"])

        return {
            label: {
                "count": len(values),
                "avg_intensity": round(sum(values) / len(values), 1),
                "max_intensity": max(values),
                "min_intensity": min(values),
                "avg_logs_per_day": round(len(values) / days, 1),
            }
            for label, values in intensities_by_symptom.items()
        }

    def _food_names(self, db: Session, username: str) -> dict[UUID, str]:
        """food id -> name"""
        return {food.id: food.name for food in self.food_service.get_all_foods(db, username)}

    def _symptom_labels(self, db: Session, username: str) -> dict[UUID, str]:
        """
        symptom id -> the name the bot sees.

        two symptoms can share a name, so a shared one gets its location added
        to keep their trends apart.
        """
        symptoms = self.symptom_service.get_all_symptoms(db, username)
        times_used = Counter(symptom.name for symptom in symptoms)

        return {
            symptom.id: (symptom.name if times_used[symptom.name] == 1 else f"{symptom.name} ({symptom.location})")
            for symptom in symptoms
        }

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
