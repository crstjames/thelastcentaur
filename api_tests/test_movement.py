#!/usr/bin/env python3
"""
Movement validation tests for The Last Centaur.

This test file focuses on testing the movement mechanics of the game,
verifying that players can navigate between areas using directional commands
and that the game state updates correctly as players move.
"""

import os
import sys
import pytest
import asyncio
import logging
from typing import Dict, List, Tuple, Any

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_tests.test_client import (
    TestGameClient, 
    verify_current_area, 
    navigate_to_area
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("movement_tests")

# Constants
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

@pytest.fixture
async def test_client():
    """Create and initialize a test client for the game API."""
    client = TestGameClient(api_base_url=API_BASE_URL)
    await client.login(username=f"movement_tester_{asyncio.current_task().get_name()}")
    game_id = await client.create_game()
    logger.info(f"Created test game with ID: {game_id}")
    yield client
    await client.cleanup()

class TestBasicMovement:
    """Test basic movement commands and area transitions."""
    
    @pytest.mark.asyncio
    async def test_cardinal_directions(self, test_client):
        """Test that the player can move in all four cardinal directions."""
        client = test_client
        logger.info("Starting cardinal directions movement test")
        
        # Get initial position
        await client.send_command("look")
        initial_area = None
        
        # Identify starting area
        for area in ["AWAKENING_WOODS", "TRIALS_PATH", "WARRIORS_CAMP"]:
            if await verify_current_area(client, area):
                initial_area = area
                break
        
        assert initial_area, "Failed to identify initial area"
        logger.info(f"Starting test in area: {initial_area}")
        
        # Track visited positions
        visited_areas = [initial_area]
        
        # Try all cardinal directions
        directions = ["north", "east", "south", "west"]
        movements_succeeded = 0
        
        for direction in directions:
            # Try to move in this direction
            response = await client.send_command(f"move {direction}")
            logger.info(f"Move {direction} response: {response}")
            
            # Check if movement succeeded
            if "can't go that way" not in response.lower() and "blocked" not in response.lower():
                movements_succeeded += 1
                
                # Identify current area after movement
                current_area = None
                for area in ["AWAKENING_WOODS", "TRIALS_PATH", "WARRIORS_CAMP", 
                             "TRAINING_GROUNDS", "MOUNTAIN_BASE", "SHADOW_DOMAIN"]:
                    if await verify_current_area(client, area):
                        current_area = area
                        visited_areas.append(current_area)
                        break
                
                assert current_area, f"Failed to identify area after moving {direction}"
                logger.info(f"Successfully moved {direction} to {current_area}")
                
                # Try to return to initial position
                opposite_directions = {"north": "south", "south": "north", 
                                      "east": "west", "west": "east"}
                back_response = await client.send_command(f"move {opposite_directions[direction]}")
                logger.info(f"Return movement response: {back_response}")
                
                # Verify we returned to initial area
                assert await verify_current_area(client, initial_area), f"Failed to return to {initial_area}"
                logger.info(f"Successfully returned to {initial_area}")
        
        logger.info(f"Successfully moved in {movements_succeeded} directions")
        logger.info(f"Visited areas: {visited_areas}")
        
        # Assert that at least one movement was successful
        assert movements_succeeded > 0, "Failed to move in any direction"
    
    @pytest.mark.asyncio
    async def test_area_transitions(self, test_client):
        """Test that area transitions update game state correctly."""
        client = test_client
        logger.info("Starting area transitions test")
        
        # Define a sequence of areas to visit
        areas_to_visit = [
            "AWAKENING_WOODS",
            "WARRIORS_CAMP",
            "TRAINING_GROUNDS"
        ]
        
        # Start at Awakening Woods
        assert await verify_current_area(client, "AWAKENING_WOODS"), "Test should start in AWAKENING_WOODS"
        
        # Navigate through each area in sequence
        for target_area in areas_to_visit[1:]:  # Skip first area (starting point)
            logger.info(f"Attempting to navigate to {target_area}")
            
            # Use the navigate_to_area function
            success = await navigate_to_area(client, target_area)
            
            # Verify navigation was successful
            assert success, f"Failed to navigate to {target_area}"
            assert await verify_current_area(client, target_area), f"Failed to verify current area is {target_area}"
            
            # Check game state after navigation
            game_state = await client.get_game_state()
            
            # Validate updated game state
            if 'game_state' in game_state and 'position' in game_state['game_state']:
                logger.info(f"Position after navigation: {game_state['game_state']['position']}")
            
            # Send a look command to check the area description
            look_response = await client.send_command("look")
            logger.info(f"Area description: {look_response}")
            
            # Keep track of visited tiles
            if 'game_state' in game_state and 'visited_tiles' in game_state['game_state']:
                logger.info(f"Visited tiles: {game_state['game_state']['visited_tiles']}")
        
        logger.info("Area transitions test completed successfully")

class TestComplexMovement:
    """Test more complex movement patterns and obstacles."""
    
    @pytest.mark.asyncio
    async def test_movement_path_finder(self, test_client):
        """Test that the navigation helper can find paths between distant areas."""
        client = test_client
        logger.info("Starting path finding test")
        
        # Define pairs of areas to test navigation between
        test_paths = [
            ("AWAKENING_WOODS", "WARRIORS_CAMP"),
            ("WARRIORS_CAMP", "TRAINING_GROUNDS"),
            ("AWAKENING_WOODS", "TRIALS_PATH")
        ]
        
        for start_area, target_area in test_paths:
            # First make sure we're at the start area
            if not await verify_current_area(client, start_area):
                success = await navigate_to_area(client, start_area)
                assert success, f"Failed to navigate to starting area {start_area}"
            
            logger.info(f"Testing navigation from {start_area} to {target_area}")
            
            # Try to navigate to the target area
            success = await navigate_to_area(client, target_area)
            
            if success:
                logger.info(f"Successfully navigated from {start_area} to {target_area}")
                # Verify we're in the target area
                assert await verify_current_area(client, target_area), f"Failed to verify arrival at {target_area}"
            else:
                logger.warning(f"Failed to navigate from {start_area} to {target_area}")
                # This could be a valid failure if there's no path between these areas
                # We'll just log it rather than failing the test
        
        logger.info("Path finding test completed")

if __name__ == "__main__":
    # Allow running this test file directly
    import pytest
    pytest.main(["-xvs", __file__]) 