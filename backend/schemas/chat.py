"""Chatbot Pydantic schemas for request/response validation."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """A question from the signed-in user about their own logs."""

    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(
        ...,
        description="The user's question for the chatbot",
        min_length=1,
        max_length=1000,
    )


class ChatResponse(BaseModel):
    """
    The chatbot's reply.

    kind is "emergency" for the fixed safety reply (the model is never called),
    and "refused" when the model's answer broke a rule and was replaced.
    """

    model_config = ConfigDict(from_attributes=True)

    answer: str = Field(..., description="Reply text to show the user")
    kind: Literal["answer", "emergency", "refused"] = Field(default="answer", description="Type of reply")


class ChatModelOutput(BaseModel):
    """
    The JSON shape Gemini must return. Internal only, never sent to the client.

    triggers_mentioned has no default so the model can't skip it.
    """

    answer: str = Field(..., min_length=1)
    triggers_mentioned: list[str]
