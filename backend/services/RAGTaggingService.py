"""RAG-powered tagging service for suggesting trigger ingredients and buckets."""

import json
import logging
import os
from typing import Optional

import google.generativeai as genai
from sqlalchemy.orm import Session

from schemas.tag import (
    SuggestedBucketResponse,
    SuggestedIngredientResponse,
    SuggestedTagsAndIngredientsResponse,
)
from services.ingest import similarity_search


class RAGTaggingService:
    """
    Service that combines vector similarity search with an LLM to suggest
    trigger ingredients and bucket tags for a given food item.

    Suggestions are never persisted — they are returned in the response only.
    """

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.llm = genai.GenerativeModel("gemini-1.5-flash")

    def suggest(
        self,
        db: Session,
        food_name: str,
        ingredients: Optional[list],
    ) -> SuggestedTagsAndIngredientsResponse:
        """
        Given a food name and its ingredients, run a similarity search to retrieve
        relevant nutritional context, then call an LLM to suggest trigger ingredients
        and classify them into buckets.

        Args:
            db: Database session for vector search
            food_name: Name of the food item
            ingredients: List of known ingredients (may be None)

        Returns:
            SuggestedTagsAndIngredientsResponse with suggested_ingredients and suggested_buckets
        """
        # 1. Retrieve relevant RAG context chunks via similarity search
        chunks = similarity_search(food_name, db, n=5)
        context = "\n\n".join(chunk.content for chunk in chunks) if chunks else ""

        # 2. Build prompt
        ingredients_str = ", ".join(str(i) for i in ingredients) if ingredients else "not specified"

        prompt = f"""You are a nutrition and food sensitivity expert.
Given a food item and its ingredients, identify which ingredients are likely trigger ingredients
and classify them into digestive/allergy trigger buckets.

Food name: {food_name}
Ingredients: {ingredients_str}

Relevant nutritional context:
{context if context else "No additional context available."}

Trigger buckets to consider: gluten, FODMAPs, nightshades, histamines, added sugar,
artificial additives, dairy, FDA Big 9 allergens (milk, eggs, fish, shellfish, tree nuts,
peanuts, wheat, soybeans, sesame).

Return ONLY valid JSON with no markdown or explanation:
{{
  "suggested_ingredients": [
    {{"name": "ingredient name", "buckets": ["bucket1", "bucket2"]}}
  ],
  "suggested_buckets": [
    {{"name": "bucket name", "description": "brief reason why this bucket is relevant"}}
  ]
}}

Rules:
- Only include ingredients that are realistically present based on the food name and ingredient list.
- Do NOT hallucinate ingredients with no basis in the provided information.
- If ingredients are not specified, make conservative suggestions from the food name only.
- Only assign a bucket if there is clear evidence for it."""

        # 3. Call LLM
        try:
            response = self.llm.generate_content(prompt)
            raw_text = response.text.strip()

            # Strip markdown code fences if the model wraps the JSON
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()

            data = json.loads(raw_text)

            return SuggestedTagsAndIngredientsResponse(
                suggested_ingredients=[
                    SuggestedIngredientResponse(**item) for item in data.get("suggested_ingredients", [])
                ],
                suggested_buckets=[SuggestedBucketResponse(**item) for item in data.get("suggested_buckets", [])],
            )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logging.error(f"Failed to parse LLM response for food '{food_name}': {e}")
            return SuggestedTagsAndIngredientsResponse(suggested_ingredients=[], suggested_buckets=[])
        except Exception as e:
            logging.error(f"LLM call failed for food '{food_name}': {e}")
            return SuggestedTagsAndIngredientsResponse(suggested_ingredients=[], suggested_buckets=[])
