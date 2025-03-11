"""
Test script for the Movement System API in The Last Centaur.

This test verifies that the movement mechanics work correctly when accessed through the API:
1. Basic directional movement
2. Movement constraints (blocked paths)
3. Area transitions and discovery
4. Map exploration and tracking
"""

import pytest
import sys
import os
import asyncio
import uuid
from datetime import datetime
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from src.db.models import User, GameInstance
from src.engine.core.models import StoryArea, Direction
from src.auth.security import create_access_token


class TestAPIMovementSystem:
    """Test suite for movement mechanics in the game through the API."""
    
    @pytest.fixture
    async def test_user(self, db_session):
        """Create a test user for authentication."""
        # Generate a unique username for this test run
        test_username = f"test_user_{uuid.uuid4().hex[:8]}"
        
        # Create a test user
        test_user = User(
            username=test_username,
            email=f"{test_username}@example.com",
            hashed_password="$2b$12$T7eUHK5IfH5wjLd/KGQvx.x8d6OUGfM8t.fVQjHbP5JsJkrZBXa82",  # hashed 'password'
            is_active=True,
            is_superuser=False
        )
        
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)
        
        # Create a token for this user
        token = create_access_token(subject=test_user.username)
        
        return {"user": test_user, "token": token}
    
    @pytest.fixture
    async def game_setup(self, db_session, test_user):
        """Set up a game instance and client for API testing."""
        # Create an AsyncClient for async tests
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Set headers with authentication token
            headers = {"Authorization": f"Bearer {test_user['token']}"}
            
            # Create a game instance for testing
            game_data = {
                "name": f"Movement Test Game {uuid.uuid4().hex[:8]}",
                "max_players": 1,
                "description": "A game for testing the movement API"
            }
            
            response = await client.post("/game", json=game_data, headers=headers)
            assert response.status_code == 200
            game_instance = response.json()
            
            # Helper function to execute commands through the API
            async def execute(command: str) -> str:
                """Execute a command through the API and return the response."""
                print(f"> {command}")
                
                # Call the command API endpoint
                command_data = {
                    "command": command,
                    "use_llm": False  # Bypass LLM processing
                }
                
                response = await client.post(
                    f"/game/{game_instance['id']}/command", 
                    json=command_data,
                    headers=headers
                )
                
                assert response.status_code == 200, f"API call failed with status {response.status_code}: {response.text}"
                result = response.json()
                return result["response"]
            
            # Helper function to set player's position
            async def set_position(x: int, y: int) -> bool:
                """Set the player's position through a debug command."""
                response = await execute(f"debug_set_position {x} {y}")
                return f"position set to {x}, {y}" in response.lower()
            
            # Helper function to get current area information
            async def get_map_info() -> dict:
                """Get map information through the API."""
                response = await client.get(
                    f"/game/{game_instance['id']}/map",
                    headers=headers
                )
                
                assert response.status_code == 200, f"Map API call failed with status {response.status_code}: {response.text}"
                return response.json()
            
            # Helper function to check if movement is possible
            async def can_move(direction: Direction) -> bool:
                """Check if movement in the specified direction is possible."""
                # First check current position
                map_info = await get_map_info()
                current_x = map_info["current_position"]["x"]
                current_y = map_info["current_position"]["y"]
                
                # Try to move
                response = await execute(direction.name.lower())
                
                # Check if position changed
                new_map_info = await get_map_info()
                new_x = new_map_info["current_position"]["x"]
                new_y = new_map_info["current_position"]["y"]
                
                # If position changed, movement was successful
                return (current_x != new_x) or (current_y != new_y)
            
            # Yield the necessary objects for testing
            yield game_instance, execute, set_position, get_map_info, can_move
    
    @pytest.mark.asyncio
    async def test_basic_movement(self, game_setup):
        """Test basic directional movement via API."""
        _, execute, set_position, get_map_info, _ = game_setup
        
        # Start at a known position
        await set_position(5, 5)
        
        # Get initial position
        initial_map = await get_map_info()
        initial_x = initial_map["current_position"]["x"]
        initial_y = initial_map["current_position"]["y"]
        
        assert initial_x == 5
        assert initial_y == 5
        
        # Test moving north
        north_response = await execute("north")
        assert "north" in north_response.lower()
        
        north_map = await get_map_info()
        assert north_map["current_position"]["x"] == 5
        assert north_map["current_position"]["y"] == 4  # Y decreases when moving north
        
        # Test moving east
        east_response = await execute("east")
        assert "east" in east_response.lower()
        
        east_map = await get_map_info()
        assert east_map["current_position"]["x"] == 6  # X increases when moving east
        assert east_map["current_position"]["y"] == 4
        
        # Test moving south
        south_response = await execute("south")
        assert "south" in south_response.lower()
        
        south_map = await get_map_info()
        assert south_map["current_position"]["x"] == 6
        assert south_map["current_position"]["y"] == 5  # Y increases when moving south
        
        # Test moving west
        west_response = await execute("west")
        assert "west" in west_response.lower()
        
        west_map = await get_map_info()
        assert west_map["current_position"]["x"] == 5  # X decreases when moving west
        assert west_map["current_position"]["y"] == 5
        
        # Should be back at the starting position
        assert west_map["current_position"]["x"] == initial_x
        assert west_map["current_position"]["y"] == initial_y
    
    @pytest.mark.asyncio
    async def test_movement_shortcuts(self, game_setup):
        """Test movement using shorthand directions via API."""
        _, execute, set_position, get_map_info, _ = game_setup
        
        # Start at a known position
        await set_position(5, 5)
        
        # Test shorthand directions
        # North shorthand (n)
        n_response = await execute("n")
        assert "north" in n_response.lower()
        
        n_map = await get_map_info()
        assert n_map["current_position"]["x"] == 5
        assert n_map["current_position"]["y"] == 4
        
        # East shorthand (e)
        e_response = await execute("e")
        assert "east" in e_response.lower()
        
        e_map = await get_map_info()
        assert e_map["current_position"]["x"] == 6
        assert e_map["current_position"]["y"] == 4
        
        # South shorthand (s)
        s_response = await execute("s")
        assert "south" in s_response.lower()
        
        s_map = await get_map_info()
        assert s_map["current_position"]["x"] == 6
        assert s_map["current_position"]["y"] == 5
        
        # West shorthand (w)
        w_response = await execute("w")
        assert "west" in w_response.lower()
        
        w_map = await get_map_info()
        assert w_map["current_position"]["x"] == 5
        assert w_map["current_position"]["y"] == 5
    
    @pytest.mark.asyncio
    async def test_blocked_movement(self, game_setup):
        """Test movement restrictions via API."""
        _, execute, set_position, get_map_info, _ = game_setup
        
        # Teleport to a location near a map boundary or blocked path
        await set_position(1, 1)
        
        # Try to move beyond the boundary
        boundary_response = await execute("north")
        
        # Position should not change
        boundary_map = await get_map_info()
        assert boundary_map["current_position"]["x"] == 1
        assert boundary_map["current_position"]["y"] == 1
        
        # Response should indicate the path is blocked
        assert "cannot" in boundary_response.lower() or "blocked" in boundary_response.lower() or "unable" in boundary_response.lower()
    
    @pytest.mark.asyncio
    async def test_area_discovery(self, game_setup):
        """Test discovering new areas via API."""
        _, execute, set_position, get_map_info, _ = game_setup
        
        # Move to a special known area (Awakening Woods)
        await execute("debug_teleport AWAKENING_WOODS")
        
        # Get initial number of visited tiles
        initial_map = await get_map_info()
        initial_visited = len([tile for tile in initial_map["tiles"] if tile["is_visited"]])
        
        # Look around to mark current tile as visited
        await execute("look")
        
        # Move in each direction to discover new areas
        await execute("north")
        await execute("east")
        await execute("south")
        await execute("west")
        
        # Check how many tiles are now visited
        final_map = await get_map_info()
        final_visited = len([tile for tile in final_map["tiles"] if tile["is_visited"]])
        
        # We should have discovered more tiles
        assert final_visited > initial_visited, "No new areas were discovered after movement"
    
    @pytest.mark.asyncio
    async def test_area_transition(self, game_setup):
        """Test transitioning between named areas via API."""
        _, execute, set_position, _ = game_setup
        
        # Start in Awakening Woods
        await execute("debug_teleport AWAKENING_WOODS")
        
        # Confirm current location
        initial_look = await execute("look")
        assert "awakening woods" in initial_look.lower()
        
        # Move to an adjacent area (requires game knowledge)
        # First, find which direction to move (this might need adjustment based on the actual map)
        compass_directions = ["north", "east", "south", "west"]
        
        # Try each direction until we find a transition
        transitioned = False
        for direction in compass_directions:
            response = await execute(direction)
            # Check if we're in a different area now
            new_look = await execute("look")
            if "awakening woods" not in new_look.lower():
                transitioned = True
                break
            # If no transition, go back
            if direction == "north":
                await execute("south")
            elif direction == "east":
                await execute("west")
            elif direction == "south":
                await execute("north")
            elif direction == "west":
                await execute("east")
        
        assert transitioned, "Could not transition to a new area from Awakening Woods"
    
    @pytest.mark.asyncio
    async def test_exploration_commands(self, game_setup):
        """Test commands related to exploration via API."""
        _, execute, set_position, _ = game_setup
        
        # Start at a known position
        await set_position(5, 5)
        
        # Test the look command
        look_response = await execute("look")
        assert len(look_response) > 0, "Look command returned an empty response"
        
        # Test the map command
        map_response = await execute("map")
        assert "map" in map_response.lower()
        
        # Test examine surroundings
        examine_response = await execute("examine surroundings")
        assert len(examine_response) > 0, "Examine surroundings returned an empty response"
        
        # Test the weather command if available
        weather_response = await execute("weather")
        assert len(weather_response) > 0, "Weather command returned an empty response" 