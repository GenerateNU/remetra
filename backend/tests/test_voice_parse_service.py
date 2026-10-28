"""Tests for VoiceParseService. Gemini is mocked."""

from unittest.mock import MagicMock, patch

import pytest

from schemas.voice import VoiceParseResponse
from services.voice_parse_service import VoiceParseError, VoiceParseService


class TestVoiceParseService:
    """Tests for VoiceParseService."""

    @patch("services.voice_parse_service.genai")
    def test_valid_response_parses_name_and_ingredients(self, mock_genai):
        """A normal Gemini JSON payload becomes a food name and ingredient list."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(
            text='{"transcript": "pasta with garlic and parmesan", "name": "Pasta", '
            '"ingredients": ["pasta", "garlic", "parmesan"]}'
        )

        result = VoiceParseService().parse(b"fake-audio", "audio/mp4")

        assert isinstance(result, VoiceParseResponse)
        assert result.transcript == "pasta with garlic and parmesan"
        assert result.name == "Pasta"
        assert result.ingredients == ["pasta", "garlic", "parmesan"]

    @patch("services.voice_parse_service.genai")
    def test_unclear_audio_returns_empty_fields_and_transcript(self, mock_genai):
        """Silent or unclear audio keeps the transcript and leaves name and ingredients empty."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(
            text='{"transcript": "um", "name": "", "ingredients": []}'
        )

        result = VoiceParseService().parse(b"silence", "audio/mp4")

        assert result.transcript == "um"
        assert result.name == ""
        assert result.ingredients == []

    @patch("services.voice_parse_service.genai")
    def test_missing_fields_default_to_empty(self, mock_genai):
        """Omitted name and ingredients come back empty, with the transcript kept."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text='{"transcript": "um"}')

        result = VoiceParseService().parse(b"silence", "audio/mp4")

        assert result.transcript == "um"
        assert result.name == ""
        assert result.ingredients == []

    @patch("services.voice_parse_service.genai")
    def test_gemini_error_raises_friendly_message(self, mock_genai):
        """A Gemini failure becomes VoiceParseError and does not leak the underlying error."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API unavailable")

        with pytest.raises(VoiceParseError) as exc_info:
            VoiceParseService().parse(b"fake-audio", "audio/mp4")

        assert str(exc_info.value) == "Voice parsing service is unavailable"
        assert "API unavailable" not in str(exc_info.value)

    @patch("services.voice_parse_service.genai")
    def test_invalid_json_raises_friendly_message(self, mock_genai):
        """Unparseable model output is a clean error, not a crash."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="this is not json")

        with pytest.raises(VoiceParseError) as exc_info:
            VoiceParseService().parse(b"fake-audio", "audio/mp4")

        assert str(exc_info.value) == "Could not understand the recording"
