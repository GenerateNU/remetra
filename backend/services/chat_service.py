"""Chatbot service: answers a question about the signed-in user's own logs."""

import json
import logging
import os

from google import genai
from sqlalchemy.orm import Session

from chatbot import prompts, safety
from chatbot.context_builder import ContextBuilder
from schemas.chat import ChatModelOutput, ChatResponse


class ChatError(Exception):
    """Raises when Gemini fails, or returns a response that's unusable."""


class ChatService:
    """Service that sends the user's summary and question to Gemini and enforces the chat rules."""

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.context_builder = ContextBuilder()

    def ask(self, db: Session, question: str) -> ChatResponse:
        """
        Answer a question for the signed-in user.

        Args:
            db: Database session
            question: The user's question

        Returns:
            ChatResponse. kind is "emergency" for the fixed safety reply,
            "refused" if the model named a trigger the report doesn't have.

        Raises:
            ChatError: only if the Gemini call fails, or the response is invalid/unusable
        """
        if safety.is_emergency(question):
            return ChatResponse(answer=safety.EMERGENCY_REPLY, kind="emergency")

        summary = self._build_summary(db)
        output = self._call_model(summary, question)

        if not safety.check_triggers(output.triggers_mentioned, summary["reported_triggers"]):
            logging.warning(f"Chat answer named unreported triggers: {output.triggers_mentioned}")
            return ChatResponse(answer=safety.REFUSED_REPLY, kind="refused")

        return ChatResponse(answer=output.answer, kind="answer")

    def _build_summary(self, db: Session) -> dict:
        """The data block the model answers from. Built on the server, never taken from the client."""
        logs = self.context_builder.get_logs(db)

        return {
            "trends": self.context_builder.get_trends(db),
            "food_logs": [prompts.truncate_note(log) for log in logs["food_logs"]],
            "symptom_logs": [prompts.truncate_note(log) for log in logs["symptom_logs"]],
            "reported_triggers": self._get_reported_triggers(db),
        }

    def _get_reported_triggers(self, db: Session) -> list[str]:
        """
        Food or ingredient names the user's report already flags as triggers.

        An empty list means the bot never calls anything a trigger.
        """
        # TODO: blocked on ContextBuilder.get_revealed_insights (still NotImplementedError).
        # Once it lands, return the revealed food/ingredient names from it here, e.g.
        #   insights = self.context_builder.get_revealed_insights(db, ...)
        #   return [insight["label"] for insight in insights]
        # Until then the list stays empty, so every trigger claim is refused.
        return []

    def _call_model(self, summary: dict, question: str) -> ChatModelOutput:
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompts.build_contents(summary, question),
                config={
                    "system_instruction": prompts.SYSTEM_PROMPT,
                    "response_mime_type": "application/json",
                },
            )

            data = json.loads(response.text)
            return ChatModelOutput(**data)

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logging.error(f"Failed to parse LLM response: {e}")
            raise ChatError("Could not understand the chatbot response") from e
        except Exception as e:
            logging.error(f"LLM call failed: {e}")
            raise ChatError("Chatbot service is unavailable") from e
