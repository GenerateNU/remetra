"""Router tests for POST /voice/parse. Gemini is mocked."""

from unittest.mock import MagicMock, patch

from models.food import Food

_AUDIO = {"file": ("meal.m4a", b"fake-audio", "audio/mp4")}
_PARSED = (
    '{"transcript": "pasta with garlic and parmesan", "name": "Pasta", "ingredients": ["pasta", "garlic", "parmesan"]}'
)


class TestVoiceRouter:
    """HTTP tests for voice food parsing."""

    @patch("services.voice_parse_service.genai")
    def test_parse_returns_transcript_name_and_ingredients(self, mock_genai, test_client, authenticated_user):
        """An authenticated upload returns the parsed food fields."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text=_PARSED)

        response = test_client.post("/voice/parse", files=_AUDIO)

        assert response.status_code == 200
        assert response.json() == {
            "transcript": "pasta with garlic and parmesan",
            "name": "Pasta",
            "ingredients": ["pasta", "garlic", "parmesan"],
        }

    @patch("services.voice_parse_service.genai")
    def test_parse_does_not_write_to_db(self, mock_genai, test_client, authenticated_user, db_session):
        """Parsing suggests values and does not create food rows."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text=_PARSED)
        before = db_session.query(Food).count()

        response = test_client.post("/voice/parse", files=_AUDIO)

        assert response.status_code == 200
        assert db_session.query(Food).count() == before

    @patch("services.voice_parse_service.genai")
    def test_gemini_failure_returns_friendly_error(self, mock_genai, test_client, authenticated_user):
        """A Gemini exception becomes a friendly error response."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API unavailable")

        response = test_client.post("/voice/parse", files=_AUDIO)

        assert response.status_code == 502
        assert response.json()["detail"] == "Voice parsing service is unavailable"
        assert "API unavailable" not in response.text

    @patch("services.voice_parse_service.genai")
    def test_invalid_json_returns_friendly_error(self, mock_genai, test_client, authenticated_user):
        """Unparseable model output is a friendly error, not a crash."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="this is not json")

        response = test_client.post("/voice/parse", files=_AUDIO)

        assert response.status_code == 502
        assert response.json()["detail"] == "Could not understand the recording"

    def test_empty_file_returns_400(self, test_client, authenticated_user):
        """An empty upload is rejected before Gemini is called."""
        response = test_client.post("/voice/parse", files={"file": ("meal.m4a", b"", "audio/mp4")})

        assert response.status_code == 400
        assert response.json()["detail"] == "Audio file is empty"

    def test_missing_token_returns_401(self, test_client):
        """A request without a valid token is rejected."""
        response = test_client.post("/voice/parse", files=_AUDIO)

        assert response.status_code == 401

    def test_missing_file_returns_422(self, test_client, authenticated_user):
        """A request with no audio file is rejected by FastAPI."""
        response = test_client.post("/voice/parse")

        assert response.status_code == 422
