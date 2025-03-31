"""
Database Integration API tests for The Last Centaur.

This test uses FastAPI's TestClient with a real database connection to test the API endpoints.
"""

import pytest
import sys
import os
import uuid
import asyncio
from fastapi.testclient import TestClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from src.db.models import User, GameInstance
from src.auth.security import create_access_token, get_password_hash
from src.core.config import settings

# Create a test client
client = TestClient(app)

class TestAPIDbIntegration:
    """Test suite for API functionality with real database."""
    
    @pytest_asyncio.fixture(scope="function")
    async def test_user(self, db_session: AsyncSession):
        """Create a test user in the database."""
        # Generate a unique username for this test
        test_username = f"testuser_{uuid.uuid4().hex[:8]}"
        test_email = f"{test_username}@example.com"
        
        # Create a new user
        user = User(
            id=str(uuid.uuid4()),
            username=test_username,
            email=test_email,
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Return the user and token
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        yield {
            "user": user,
            "token": access_token
        }
        
        # Clean up - delete the user after the test
        await db_session.delete(user)
        await db_session.commit()
    
    @pytest_asyncio.fixture(scope="function")
    async def test_game(self, test_user, db_session: AsyncSession):
        """Create a test game instance in the database."""
        # Create a new game instance
        game_instance = GameInstance(
            id=str(uuid.uuid4()),
            user_id=test_user["user"].id,
            name=f"Test Game {uuid.uuid4().hex[:8]}",
            status="ACTIVE",
            max_players=1,
            current_players=1,
            description="A test game instance",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(game_instance)
        await db_session.commit()
        await db_session.refresh(game_instance)
        
        yield {
            "game_instance": game_instance,
            "user": test_user["user"],
            "token": test_user["token"]
        }
        
        # Clean up - delete the game instance after the test
        await db_session.delete(game_instance)
        await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_create_and_list_games(self, test_user, db_session: AsyncSession):
        """Test creating and listing games with a real database."""
        # Set up authentication
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # Create a new game
        game_data = {
            "name": f"New Test Game {uuid.uuid4().hex[:8]}",
            "max_players": 1,
            "description": "A new test game created via API"
        }
        
        response = client.post("/api/v1/game", json=game_data, headers=headers)
        
        # Print response for debugging
        print(f"Create game response status: {response.status_code}")
        print(f"Create game response body: {response.text}")
        
        # Check the response
        assert response.status_code == 200
        created_game = response.json()
        assert created_game["name"] == game_data["name"]
        assert created_game["description"] == game_data["description"]
        assert created_game["user_id"] == test_user["user"].id
        
        # List games
        list_response = client.get("/api/v1/game", headers=headers)
        
        # Print response for debugging
        print(f"List games response status: {list_response.status_code}")
        print(f"List games response body: {list_response.text}")
        
        # Check the response
        assert list_response.status_code == 200
        games = list_response.json()
        assert len(games) >= 1  # There should be at least one game (the one we just created)
        
        # Clean up - delete the game
        # This is handled automatically by the database session teardown
    
    @pytest.mark.asyncio
    async def test_command_execution(self, test_game, db_session: AsyncSession):
        """Test executing commands with a real database connection."""
        # Set up authentication
        headers = {"Authorization": f"Bearer {test_game['token']}"}
        
        # Execute a 'look' command
        command_data = {
            "command": "look",
            "use_llm": False  # Bypass LLM processing
        }
        
        # Execute the command with the fixed path
        response = client.post(
            f"/api/v1/game/{test_game['game_instance'].id}/command", 
            json=command_data, 
            headers=headers
        )
        
        # Print response for debugging
        print(f"Command execution response status: {response.status_code}")
        print(f"Command execution response body: {response.text}")
        
        # Check the response
        assert response.status_code == 200
        result = response.json()
        assert result["command"] == "look"
        assert "response" in result
        assert result["game_id"] == test_game["game_instance"].id
        
        # Execute a 'move' command
        move_command_data = {
            "command": "move north",
            "use_llm": False
        }
        
        move_response = client.post(
            f"/api/v1/game/{test_game['game_instance'].id}/command", 
            json=move_command_data, 
            headers=headers
        )
        
        # Print response for debugging
        print(f"Move command response status: {move_response.status_code}")
        print(f"Move command response body: {move_response.text}")
        
        # Check the response
        assert move_response.status_code == 200
        move_result = move_response.json()
        assert move_result["command"] == "move north"
        assert "response" in move_result 