"""
Test script for the Puzzle System API in The Last Centaur.

This test verifies that the puzzle mechanics work correctly when accessed through the API:
1. Item combination puzzles
2. Sequential action puzzles
3. Environmental interaction puzzles
4. Riddle/knowledge-based puzzles
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
from src.engine.core.models import StoryArea, ItemType
from src.auth.security import create_access_token


class TestAPIPuzzleSystem:
    """Test suite for puzzle mechanics in the game through the API."""
    
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
                "name": f"Puzzle Test Game {uuid.uuid4().hex[:8]}",
                "max_players": 1,
                "description": "A game for testing the puzzle API"
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
            
            # Helper function to set the current area
            async def set_current_area(area: StoryArea) -> bool:
                """Set the current area through a debug command."""
                response = await execute(f"debug_teleport {area.name}")
                return "teleported" in response.lower() or "entering" in response.lower()
            
            # Yield the necessary objects for testing
            yield game_instance, execute, set_current_area
    
    @pytest.mark.asyncio
    async def test_item_combination_puzzle(self, game_setup):
        """Test combining items to solve puzzles via API."""
        game_instance, execute, _ = game_setup
        
        # Add required items to inventory using debug commands
        await execute("debug_add_item crystal_fragment_1")
        await execute("debug_add_item crystal_fragment_2")
        await execute("debug_add_item crystal_fragment_3")
        
        # Check inventory
        inventory_response = await execute("inventory")
        assert "crystal_fragment_1" in inventory_response
        assert "crystal_fragment_2" in inventory_response
        assert "crystal_fragment_3" in inventory_response
        
        # Combine the fragments
        combine_response = await execute("combine crystal fragments")
        
        # Verify the combination worked
        assert "mystic_crystal" in combine_response
        assert "You have successfully combined the crystal fragments" in combine_response
        
        # Check the new item is in inventory
        new_inventory = await execute("inventory")
        assert "mystic_crystal" in new_inventory
        assert "crystal_fragment_1" not in new_inventory  # Items should be consumed
    
    @pytest.mark.asyncio
    async def test_sequential_action_puzzle(self, game_setup):
        """Test puzzles that require actions in a specific sequence via API."""
        _, execute, set_current_area = game_setup
        
        # Move to the meditation circle area
        await set_current_area(StoryArea.MEDITATION_CIRCLE)
        
        # Perform the sequence of actions
        response1 = await execute("light north torch")
        assert "You light the torch on the north side" in response1
        
        response2 = await execute("light east torch")
        assert "You light the torch on the east side" in response2
        
        response3 = await execute("light south torch")
        assert "You light the torch on the south side" in response3
        
        response4 = await execute("light west torch")
        assert "You light the torch on the west side" in response4
        
        # Check the result of completing the sequence
        final_response = await execute("look")
        assert "The circle begins to glow" in final_response
        assert "A hidden passage has opened" in final_response
    
    @pytest.mark.asyncio
    async def test_environmental_puzzle(self, game_setup):
        """Test puzzles that involve interacting with the environment via API."""
        _, execute, set_current_area = game_setup
        
        # Move to the crystal pond
        await set_current_area(StoryArea.CRYSTAL_POND)
        
        # Initial observation
        look_response = await execute("look")
        assert "crystal pond" in look_response.lower()
        assert "strange patterns" in look_response.lower()
        
        # Interact with the environment
        response1 = await execute("touch water")
        assert "The water ripples" in response1
        
        response2 = await execute("examine patterns")
        assert "The patterns seem to form a map" in response2
        
        # Add the required item
        await execute("debug_add_item crystal_lens")
        
        # Use an item with the environment
        response3 = await execute("use crystal_lens on patterns")
        
        # Verify puzzle solution
        assert "The lens reveals hidden markings" in response3
        assert "You've discovered the location of the Ancient Sanctuary" in response3
        assert "The knowledge has been added to your map" in response3
    
    @pytest.mark.asyncio
    async def test_riddle_puzzle(self, game_setup):
        """Test knowledge-based riddle puzzles via API."""
        _, execute, set_current_area = game_setup
        
        # Move to the forgotten temple
        await set_current_area(StoryArea.FORGOTTEN_TEMPLE)
        
        # Read the riddle
        riddle_response = await execute("read inscription")
        assert "What walks on four legs in the morning" in riddle_response
        
        # Answer the riddle
        answer_response = await execute("answer is man")
        assert "The stone door rumbles and slides open" in answer_response
        assert "You have solved the ancient riddle" in answer_response
    
    @pytest.mark.asyncio
    async def test_item_key_puzzle(self, game_setup):
        """Test puzzles that require specific items to unlock progress via API."""
        _, execute, set_current_area = game_setup
        
        # Move to the crystal caves
        await set_current_area(StoryArea.CRYSTAL_CAVES)
        
        # Try to go north without the key
        blocked_response = await execute("go north")
        assert "The path to the north is blocked by an ancient door" in blocked_response
        assert "It appears to require a special key" in blocked_response
        
        # Add the mystical key to inventory
        await execute("debug_add_item mystical_key")
        
        # Use the key on the door
        unlock_response = await execute("use mystical_key on door")
        assert "You unlock the ancient door with the mystical key" in unlock_response
        assert "The door swings open, revealing a path to the north" in unlock_response
        
        # Now we should be able to go north
        north_response = await execute("go north")
        assert "You proceed through the now unlocked door to the north" in north_response
        assert "Guardian Overlook" in north_response 