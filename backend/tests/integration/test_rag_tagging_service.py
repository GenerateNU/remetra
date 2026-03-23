"""Integration tests for RAGTaggingService."""

from unittest.mock import MagicMock, patch

import pytest

from schemas.tag import SuggestedIngredientResponse, SuggestedTagsAndIngredientsResponse
from services.RAGTaggingService import RAGTaggingService


class TestRAGTaggingService:
    """Tests for RAGTaggingService."""

    @patch("services.RAGTaggingService.genai")
    def test_suggest_with_ingredients_returns_structured_response(self, mock_genai, db_session):
        """Given a food with populated ingredients, returns non-empty suggested_ingredients with buckets."""
        mock_llm = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_llm
        mock_llm.generate_content.return_value = MagicMock(
            text="""{"suggested_ingredients": [{"name": "wheat flour", "buckets": ["gluten", "wheat"]}], "suggested_buckets": [{"name": "gluten", "description": "contains wheat flour"}]}"""
        )

        service = RAGTaggingService()
        result = service.suggest(db_session, "white bread", ["wheat flour", "water", "yeast", "salt"])

        assert isinstance(result, SuggestedTagsAndIngredientsResponse)
        assert len(result.suggested_ingredients) > 0
        ingredient_names = [i.name for i in result.suggested_ingredients]
        assert "wheat flour" in ingredient_names
        for ingredient in result.suggested_ingredients:
            assert isinstance(ingredient, SuggestedIngredientResponse)
            assert len(ingredient.buckets) > 0

    @patch("services.RAGTaggingService.genai")
    def test_suggest_with_no_ingredients_returns_suggestions_from_food_name(self, mock_genai, db_session):
        """Given a food with ingredients=None, returns conservative suggestions without hallucinating."""
        mock_llm = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_llm
        mock_llm.generate_content.return_value = MagicMock(
            text="""{"suggested_ingredients": [{"name": "milk", "buckets": ["dairy"]}], "suggested_buckets": [{"name": "dairy", "description": "ice cream typically contains milk"}]}"""
        )

        service = RAGTaggingService()
        result = service.suggest(db_session, "ice cream", None)

        assert isinstance(result, SuggestedTagsAndIngredientsResponse)
        assert len(result.suggested_ingredients) > 0
        for ingredient in result.suggested_ingredients:
            assert ingredient.name != ""
            assert len(ingredient.buckets) > 0

    @patch("services.RAGTaggingService.genai")
    def test_suggest_does_not_persist_to_db(self, mock_genai, db_session):
        """Suggestions must never be saved — no new rows in tags or food_tags tables."""
        from models.tag import FoodTag, Tag

        mock_llm = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_llm
        mock_llm.generate_content.return_value = MagicMock(
            text="""{"suggested_ingredients": [{"name": "cheese", "buckets": ["dairy"]}], "suggested_buckets": [{"name": "dairy", "description": "contains cheese"}]}"""
        )

        tags_before = db_session.query(Tag).count()
        food_tags_before = db_session.query(FoodTag).count()

        service = RAGTaggingService()
        service.suggest(db_session, "pizza", ["dough", "cheese", "tomato sauce"])

        assert db_session.query(Tag).count() == tags_before
        assert db_session.query(FoodTag).count() == food_tags_before

    @patch("services.RAGTaggingService.genai")
    def test_suggest_handles_llm_json_parse_failure_gracefully(self, mock_genai, db_session):
        """If LLM returns malformed JSON, returns empty lists rather than crashing."""
        mock_llm = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_llm
        mock_llm.generate_content.return_value = MagicMock(text="this is not json")

        service = RAGTaggingService()
        result = service.suggest(db_session, "mystery food", ["unknown"])

        assert isinstance(result, SuggestedTagsAndIngredientsResponse)
        assert result.suggested_ingredients == []
        assert result.suggested_buckets == []

    @patch("services.RAGTaggingService.genai")
    def test_suggest_handles_llm_call_failure_gracefully(self, mock_genai, db_session):
        """If the LLM call itself throws, returns empty lists rather than crashing."""
        mock_llm = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_llm
        mock_llm.generate_content.side_effect = Exception("API unavailable")

        service = RAGTaggingService()
        result = service.suggest(db_session, "some food", ["ingredient"])

        assert isinstance(result, SuggestedTagsAndIngredientsResponse)
        assert result.suggested_ingredients == []
        assert result.suggested_buckets == []

    @patch("services.RAGTaggingService.genai")
    def test_suggest_handles_markdown_wrapped_json(self, mock_genai, db_session):
        """If LLM wraps JSON in markdown code fences, it should still parse correctly."""
        mock_llm = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_llm
        mock_llm.generate_content.return_value = MagicMock(
            text="```json\n{\"suggested_ingredients\": [{\"name\": \"milk\", \"buckets\": [\"dairy\"]}], \"suggested_buckets\": [{\"name\": \"dairy\", \"description\": \"contains milk\"}]}\n```"
        )

        service = RAGTaggingService()
        result = service.suggest(db_session, "latte", ["milk", "espresso"])

        assert len(result.suggested_ingredients) == 1
        assert result.suggested_ingredients[0].name == "milk"
        assert "dairy" in result.suggested_ingredients[0].buckets
