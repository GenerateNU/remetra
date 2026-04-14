"""Tests for main application endpoints."""

from unittest.mock import MagicMock, patch

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

    def test_custom_openapi_schema(self):
        """custom_openapi returns a schema with BearerAuth security scheme."""
        schema = app.openapi()
        assert "BearerAuth" in schema["components"]["securitySchemes"]
        assert schema["components"]["securitySchemes"]["BearerAuth"]["scheme"] == "bearer"

    def test_custom_openapi_schema_cached(self):
        """custom_openapi returns the cached schema on subsequent calls."""
        schema1 = app.openapi()
        schema2 = app.openapi()
        assert schema1 is schema2


class TestSyncSchema:
    """Tests for _sync_schema drift detection."""

    def test_sync_schema_no_drift(self):
        """_sync_schema logs info when all model columns exist in the live DB."""
        from database import Base
        from main import _sync_schema

        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        # Return all column names from the actual model so no drift is detected
        mock_inspector.get_columns.side_effect = lambda table_name: [
            {"name": col.name} for col in Base.metadata.tables[table_name].columns
        ]

        with patch("main.sa_inspect", return_value=mock_inspector):
            _sync_schema()  # Covers the no-drift branch (line 53)
