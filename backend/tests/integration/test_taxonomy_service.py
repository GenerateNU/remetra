"""Integration tests for the taxonomy repository and service."""

import pytest
from sqlalchemy import delete

from models.component import Component
from models.ingredient import Ingredient
from models.ingredient_component import IngredientComponent
from repositories.taxonomy_repository import TaxonomyRepository
from services.taxonomy_service import TaxonomyService


def _component(slug: str) -> Component:
    return Component(
        slug=slug,
        display_name=slug,
        category="fodmap",
        inclusion_confidence="high",
        prior_tier="high",
    )


@pytest.fixture
def wheat_bread(db_session):
    """wheat_bread -> gluten (3), fructans_grain (2); plain_rice has no components."""
    # Start from empty taxonomy tables even if the DB was seeded; rolled back after the test.
    for model in (IngredientComponent, Ingredient, Component):
        db_session.execute(delete(model))
    gluten, fructans = _component("gluten"), _component("fructans_grain")
    bread = Ingredient(slug="wheat_bread", canonical_name="wheat bread")
    rice = Ingredient(slug="plain_rice", canonical_name="plain rice")
    db_session.add_all([gluten, fructans, bread, rice])
    db_session.flush()
    db_session.add_all(
        [
            IngredientComponent(
                ingredient_id=bread.id, component_id=gluten.id, concentration_level=3, confidence="high"
            ),
            IngredientComponent(
                ingredient_id=bread.id, component_id=fructans.id, concentration_level=2, confidence="high"
            ),
        ]
    )
    db_session.flush()
    return bread


class TestTaxonomyRepository:
    def test_get_components_by_slug(self, db_session, wheat_bread):
        # Act
        result = TaxonomyRepository().get_components_for_ingredient(db_session, "wheat_bread")
        # Assert
        assert result == [("fructans_grain", 2), ("gluten", 3)]

    def test_get_components_by_canonical_name_ignores_case_and_spaces(self, db_session, wheat_bread):
        # Act
        result = TaxonomyRepository().get_components_for_ingredient(db_session, "  Wheat Bread ")
        # Assert
        assert result == [("fructans_grain", 2), ("gluten", 3)]

    def test_ingredient_without_components(self, db_session, wheat_bread):
        # Act
        result = TaxonomyRepository().get_components_for_ingredient(db_session, "plain_rice")
        # Assert
        assert result == []

    def test_unknown_ingredient(self, db_session, wheat_bread):
        # Act
        result = TaxonomyRepository().get_components_for_ingredient(db_session, "nope")
        # Assert
        assert result == []


class TestTaxonomyService:
    def test_get_components(self, db_session, wheat_bread):
        # Act
        result = TaxonomyService().get_components(db_session, "wheat bread")
        # Assert
        assert result == [
            {"component": "fructans_grain", "concentration_level": 2},
            {"component": "gluten", "concentration_level": 3},
        ]

    def test_get_components_unknown_ingredient(self, db_session):
        # Act
        result = TaxonomyService().get_components(db_session, "nope")
        # Assert
        assert result == []
