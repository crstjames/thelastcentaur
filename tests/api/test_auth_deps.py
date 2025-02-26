from typing import Annotated, Dict

import pytest
import pytest_asyncio
from fastapi import Depends, status
from fastapi.routing import APIRouter
from fastapi.testclient import TestClient

from src.auth.deps import get_current_user
from src.core.config import settings
from src.db.models import User
from src.main import app

# Create a test router
test_router = APIRouter()

@test_router.get("/test-auth", status_code=status.HTTP_200_OK)
def auth_route_handler(current_user: Annotated[User, Depends(get_current_user)]):
    """Test route that requires authentication."""
    return {"user_id": current_user.id, "username": current_user.username}

@pytest.fixture
def app_with_test_route():
    """Add the test route to the app."""
    # Include the test router in the app
    app.include_router(
        test_router, prefix=f"{settings.API_V1_STR}/test", tags=["test"]
    )
    return app

class TestAuthDependencies:
    """Test authentication dependencies."""

    def test_protected_route_with_token(self, client: TestClient, token_headers: Dict[str, str], test_user: User, app_with_test_route):
        """Test accessing a protected route with a valid token."""
        response = client.get(
            f"{settings.API_V1_STR}/test/test-auth",
            headers=token_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["username"] == test_user.username

    def test_protected_route_without_token(self, client: TestClient, app_with_test_route):
        """Test accessing a protected route without a token."""
        response = client.get(
            f"{settings.API_V1_STR}/test/test-auth",
        )
        assert response.status_code == 401

    def test_protected_route_with_invalid_token(self, client: TestClient, app_with_test_route):
        """Test accessing a protected route with an invalid token."""
        headers = {"Authorization": "Bearer invalidtoken123"}

        response = client.get(
            f"{settings.API_V1_STR}/test/test-auth",
            headers=headers,
        )
        assert response.status_code == 401 