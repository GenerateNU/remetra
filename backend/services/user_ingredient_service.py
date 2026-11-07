from sqlalchemy.orm import Session

from models.user_ingredient import IngredientPreference
from repositories.user_ingredient_repository import UserIngredientRepository
from schemas.user import IngredientSummary, UserIngredientsResponse, UserIngredientsUpdate


class UserIngredientService:
    """Business logic for a user's ingredient preferences."""

    def __init__(self):
        self.repo = UserIngredientRepository()

    def get_ingredients(self, db: Session, username: str) -> UserIngredientsResponse:
        grouped = {preference: [] for preference in IngredientPreference}
        for preference, ingredient in self.repo.get_with_ingredients(db, username):
            grouped[preference].append(IngredientSummary.model_validate(ingredient))
        return UserIngredientsResponse(
            avoid=grouped[IngredientPreference.AVOID],
            suspect=grouped[IngredientPreference.SUSPECT],
            safe=grouped[IngredientPreference.SAFE],
        )

    def replace_ingredients(self, db: Session, username: str, data: UserIngredientsUpdate) -> UserIngredientsResponse:
        preferences = {
             **{ingredient_id: IngredientPreference.AVOID for ingredient_id in data.avoid},
            **{ingredient_id: IngredientPreference.SUSPECT for ingredient_id in data.suspect},
            **{ingredient_id: IngredientPreference.SAFE for ingredient_id in data.safe},
        }

        missing = set(preferences) - self.repo.get_existing_ingredient_ids(db, set(preferences))
        if missing:
            raise ValueError(f"Unknown ingredient IDs {', '.join(str(i) for i in missing)}")

        self.repo.replace_for_user(db, username, preferences)
        return self.get_ingredients(db, username)