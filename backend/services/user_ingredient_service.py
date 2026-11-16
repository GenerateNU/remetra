from uuid import UUID

from sqlalchemy.orm import Session

from models.user_ingredient import IngredientPreference
from repositories.taxonomy_repository import TaxonomyRepository
from repositories.user_ingredient_repository import UserIngredientRepository
from schemas.user import (
    IngredientSummary,
    UserIngredientLabelsUpdate,
    UserIngredientsResponse,
    UserIngredientsUpdate,
)
from services.onboarding_groups import ONBOARDING_GROUPS


class UnknownOnboardingLabel(Exception):
    """A food-group label from the client is not one onboarding collects."""

    def __init__(self, labels: list[str]):
        self.labels = labels
        super().__init__(f"Unknown food groups: {', '.join(labels)}")


class UserIngredientService:
    """Business logic for a user's ingredient preferences."""

    def __init__(self):
        self.repo = UserIngredientRepository()
        self.taxonomy = TaxonomyRepository()

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
        preferences = {}
        for ingredient_id in data.avoid:
            preferences[ingredient_id] = IngredientPreference.AVOID
        for ingredient_id in data.suspect:
            preferences[ingredient_id] = IngredientPreference.SUSPECT
        for ingredient_id in data.safe:
            preferences[ingredient_id] = IngredientPreference.SAFE

        missing = set(preferences) - self.repo.get_existing_ingredient_ids(db, set(preferences))
        if missing:
            raise ValueError(f"Unknown ingredient IDs {', '.join(str(i) for i in missing)}")

        self.repo.replace_for_user(db, username, preferences)
        return self.get_ingredients(db, username)

    def replace_from_labels(
        self, db: Session, username: str, data: UserIngredientLabelsUpdate
    ) -> UserIngredientsResponse:
        """Replace preferences from onboarding labels.

        A label in a higher-priority list wins when groups share an ingredient:
        avoid, then suspect, then safe. An empty payload clears every preference.
        """
        unknown = [
            label for label in dict.fromkeys([*data.avoid, *data.suspect, *data.safe]) if label not in ONBOARDING_GROUPS
        ]
        if unknown:
            raise UnknownOnboardingLabel(unknown)

        avoid_ids = self._ids_for_labels(db, data.avoid)
        suspect_ids = self._ids_for_labels(db, data.suspect) - avoid_ids
        safe_ids = self._ids_for_labels(db, data.safe) - avoid_ids - suspect_ids

        preferences: dict[UUID, IngredientPreference] = {}
        for ingredient_id in avoid_ids:
            preferences[ingredient_id] = IngredientPreference.AVOID
        for ingredient_id in suspect_ids:
            preferences[ingredient_id] = IngredientPreference.SUSPECT
        for ingredient_id in safe_ids:
            preferences[ingredient_id] = IngredientPreference.SAFE

        self.repo.replace_for_user(db, username, preferences)
        return self.get_ingredients(db, username)

    def _ids_for_labels(self, db: Session, labels: list[str]) -> set[UUID]:
        components: set[str] = set()
        slugs: set[str] = set()
        for label in labels:
            group = ONBOARDING_GROUPS[label]
            components.update(group.components)
            slugs.update(group.slugs)
        if not components and not slugs:
            return set()
        return self.taxonomy.ingredient_ids_for(db, component_slugs=components, ingredient_slugs=slugs)
