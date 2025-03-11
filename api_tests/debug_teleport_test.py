#!/usr/bin/env python3
"""
Debug Teleport Test for The Last Centaur.

This test verifies that we can use debug teleport commands to manually
place the player at specific areas for testing purposes.
"""

import os
import sys
import asyncio
import logging
import uuid
import json
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("debug_teleport_test")

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test client
from api_tests.test_client import TestGameClient, verify_current_area

API_URL = os.getenv("API_URL", "http://localhost:8000")

async def run_debug_teleport_test():
    """Run the debug teleport test."""
    client = TestGameClient(api_base_url=API_URL)
    
    logger.info("=== STARTING DEBUG TELEPORT TEST ===")
    
    # Generate unique username
    unique_id = str(uuid.uuid4())[:8]
    username = f"teleport_test_user_{unique_id}"
    email = f"test_{unique_id}@example.com"
    
    try:
        # Use the login method as it handles registration for new users
        logger.info(f"Registering and logging in as: {username}")
        await client.login(username)
        logger.info("Login successful")
        
        # Create new game
        logger.info("Creating game...")
        game_id = await client.create_game(game_name=f"Debug Test Game {unique_id}")
        logger.info(f"Game created with ID: {game_id}")
        
        # Check starting area (should be AWAKENING_WOODS)
        response = await client.send_command("look")
        logger.info(f"Initial look response: {response}")
        
        is_in_awakening = await verify_current_area(client, "AWAKENING_WOODS")
        logger.info(f"Verify in AWAKENING_WOODS: {is_in_awakening}")
        
        # Try debug teleport to WARRIORS_CAMP
        logger.info("Attempting debug teleport to WARRIORS_CAMP...")
        response = await client.send_command("debug_set_position WARRIORS_CAMP")
        logger.info(f"Debug teleport response: {response}")
        
        # Verify we're now in WARRIORS_CAMP
        logger.info("Checking current area after teleport...")
        is_in_warriors = await verify_current_area(client, "WARRIORS_CAMP")
        logger.info(f"Verify in WARRIORS_CAMP: {is_in_warriors}")
        
        if is_in_warriors:
            logger.info("TELEPORT TEST PASSED: Successfully teleported to WARRIORS_CAMP")
        else:
            logger.error("TELEPORT TEST FAILED: Could not teleport to WARRIORS_CAMP")
            
        # Try teleporting to another area (TRAINING_GROUNDS)
        logger.info("Attempting debug teleport to TRAINING_GROUNDS...")
        response = await client.send_command("debug_set_position TRAINING_GROUNDS")
        logger.info(f"Debug teleport response: {response}")
        
        # Verify we're now in TRAINING_GROUNDS
        logger.info("Checking current area after second teleport...")
        is_in_training = await verify_current_area(client, "TRAINING_GROUNDS")
        logger.info(f"Verify in TRAINING_GROUNDS: {is_in_training}")
        
        if is_in_training:
            logger.info("TELEPORT TEST PASSED: Successfully teleported to TRAINING_GROUNDS")
        else:
            logger.error("TELEPORT TEST FAILED: Could not teleport to TRAINING_GROUNDS")
        
        # Try invalid area name
        logger.info("Testing invalid area name...")
        response = await client.send_command("debug_set_position INVALID_AREA")
        logger.info(f"Invalid area response: {response}")
        
        # Clean up
        logger.info("Cleaning up test resources...")
        await client.cleanup()
        
        logger.info("=== DEBUG TELEPORT TEST COMPLETED ===")
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        raise
    finally:
        # Ensure client is cleaned up
        if hasattr(client, 'cleanup'):
            await client.cleanup()

if __name__ == "__main__":
    asyncio.run(run_debug_teleport_test()) 