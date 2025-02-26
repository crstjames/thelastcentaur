"""
Tests for the main application.
"""

import pytest
from fastapi.testclient import TestClient

from src.core.config import settings

# Remove the asyncio mark since we're using TestClient now
# pytestmark = pytest.mark.asyncio

class TestMainApplication:
    """Tests for the main application."""

    def test_health_check(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_api_docs_available(self, client: TestClient):
        """Test that the API documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_api_v1_prefix(self, client: TestClient):
        """Test that the API v1 prefix is working."""
        # This should return 405 Method Not Allowed, but it confirms the route exists
        response = client.get(f"{settings.API_V1_STR}/auth/login")
        assert response.status_code == 405  # Method Not Allowed for GET on login endpoint

    def test_api_v1_prefix_additional(self, client: TestClient):
        """Test additional API v1 prefix functionality."""
        # This should return 405 Method Not Allowed, but it confirms the route exists
        response = client.get(f"{settings.API_V1_STR}/auth/login")
        
        assert response.status_code == 405  # Method Not Allowed (login requires POST)
        
        # Try a non-existent endpoint
        response = client.get(f"{settings.API_V1_STR}/non-existent-endpoint")
        
        assert response.status_code == 404  # Not found