import pytest
import pytest_asyncio
from fastapi import Depends, APIRouter, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.core.config import settings
from src.main import app

# pytestmark = pytest.mark.asyncio

# Create a test router with an endpoint that uses the database session
test_router = APIRouter()

@test_router.get("/test-db-session", status_code=status.HTTP_200_OK)
async def test_db_session_route(db: AsyncSession = Depends(get_db)):
    """Test route that requires a database session."""
    # Just check if the session is available
    return {"status": "success", "message": "Database session is available"}

# Add the test router to the app in the fixture
@pytest_asyncio.fixture
async def app_with_db_route():
    """Add test route to the app."""
    app.include_router(
        test_router, prefix=f"{settings.API_V1_STR}/test", tags=["test-db"]
    )
    return app

class TestDatabaseSession:
    def test_db_session_dependency(self, client: TestClient, app_with_db_route):
        """Test that the database session dependency works correctly."""
        response = client.get(f"{settings.API_V1_STR}/test/test-db-session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Database session is available" 