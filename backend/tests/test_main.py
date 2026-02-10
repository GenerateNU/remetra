"""Tests for main application endpoints."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check and root endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Remetra API", "status": "running"}

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_scalar_docs_endpoint(self):
        """Test Scalar API documentation endpoint."""
        response = client.get("/scalar")
        assert response.status_code == 200
        # Scalar returns HTML
        assert "text/html" in response.headers["content-type"]


class TestAppConfiguration:
    """Test FastAPI app configuration."""

    def test_app_title(self):
        """Test app has correct title."""
        assert app.title == "Remetra API"

    def test_app_version(self):
        """Test app has correct version."""
        assert app.version == "0.1.0"
