"""Voice parsing service for food input."""

import json
import logging
import os

from google import genai
from google.genai import types

from schemas.voice import VoiceParseResponse

prompt = """You will receieve a short audio recording of someone describing the food they ate. 
            
            1) Transcribe exactly what they said. 
            2) Identify the food as a short, title-cased name (e.g. "Pasta").
            3) List the ingredients they mentioned, lowercase.
            Include the base food if it is implied by the name (e.g. "pasta"), 
            but do not invent ingredients they didn't say. 
    
        Return JSON in exactly this shape:
        {"transcript": "...", "name": "...", "ingredients": ["...", "..."]}

        If no food is described, return the transcript with "name": "" and "ingredients": []."""


class VoiceParseError(Exception):
    """Raises when Gemini fails, or returns a response that's unusable."""


class VoiceParseService:
    """Service that parses a meal recording into suggested food fields."""

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def parse(self, audio_bytes: bytes, mime_type: str) -> VoiceParseResponse:
        """
        Transcribe a short recording from a user and extract the ingredients & food name.

        Args:
            audio_bytes: Raw audio file contents
            mime_type: MIME type of the audio (e.g. "audio/mp4")

        Returns:
            VoiceParseResponse with transcript, name, and ingredients

        Raises:
            VoiceParseError: only if Gemini call fails, or the response is invalid/unusable
        """

        # Call LLM
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                    prompt,
                ],
                config={"response_mime_type": "application/json"},
            )

            data = json.loads(response.text)
            return VoiceParseResponse(**data)

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logging.error(f"Failed to parse LLM response: {e}")
            raise VoiceParseError("Could not understand the recording") from e
        except Exception as e:
            logging.error(f"LLM call failed: {e}")
            raise VoiceParseError("Voice parsing service is unavailable") from e
