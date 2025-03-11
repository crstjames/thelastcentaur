"""
Warrior path completion test for The Last Centaur.

This test verifies that a player can complete the game through the Warrior path
using the LLM interpreter to process commands.
"""

import os
import sys
import pytest
import asyncio
from typing import Dict, List, Any
import logging

# Add the project root to the path so we can import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_tests.test_client import TestGameClient, ensure_item_acquired, ensure_enemy_defeated, verify_current_area, verify_inventory_contains
from api_tests.test_runner import TestRunner
from src.engine.core.models import PathType, StoryArea

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("warrior_path_tests")

# Constants
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
USE_LLM = True  # Always use LLM for command interpretation

# Test Fixtures
@pytest.fixture
async def test_client():
    """Create and initialize a test client for the game API."""
    client = TestGameClient(api_base_url=API_BASE_URL)
    await client.login(username=f"warrior_tester_{asyncio.current_task().get_name()}")
    await client.create_game()
    yield client
    await client.cleanup()

@pytest.fixture
async def equipped_warrior(test_client):
    """Setup a warrior with starting equipment."""
    client = test_client
    
    # Get basic starting items
    await ensure_item_acquired(client, "rusty_sword", ["take sword", "get rusty sword", "pick up sword"])
    await ensure_item_acquired(client, "leather_pouch", ["take pouch", "get pouch", "pick up leather pouch"])
    
    # Look at inventory to confirm items
    response = await client.send_command("inventory")
    logger.info(f"Initial inventory: {response}")
    
    yield client

# Helper functions
async def train_warrior_skills(client):
    """Train warrior skills and verify training completion."""
    # Train basic combat skills
    response = await client.send_command("train with sword")
    logger.info(f"Sword training: {response}")
    
    response = await client.send_command("practice combat techniques")
    logger.info(f"Combat practice: {response}")
    
    response = await client.send_command("learn defensive stance")
    logger.info(f"Defense training: {response}")
    
    # Check skills learned
    response = await client.send_command("status")
    logger.info(f"Skills status: {response}")
    
    return "combat training" in response.lower()

async def defeat_training_dummy(client):
    """Defeat the training dummy to progress warrior skills."""
    response = await client.send_command("attack training dummy")
    logger.info(f"Attack training dummy: {response}")
    
    if "defeated" not in response.lower():
        response = await client.send_command("use sword on dummy")
        logger.info(f"Using sword on dummy: {response}")
    
    return "defeated" in response.lower() or "destroyed" in response.lower()

# The Warrior's Journey Test
@pytest.mark.asyncio
async def test_warrior_path_complete_journey(equipped_warrior):
    """Test the complete warrior path journey from start to finish."""
    client = equipped_warrior
    logger.info("=== STARTING WARRIOR PATH JOURNEY ===")
    
    # PHASE 1: Initial Exploration & Training
    # ----------------------------------------
    
    # Initial exploration
    response = await client.send_command("look around")
    logger.info(f"Initial exploration: {response}")
    
    # Move to Warrior's Camp
    response = await client.send_command("move east")
    logger.info(f"Moving to Warrior's Camp: {response}")
    
    # Verify we're in the right place
    assert await verify_current_area(client, "warriors_camp")
    
    # Talk to the warrior mentor
    response = await client.send_command("talk to mentor")
    logger.info(f"Talking to mentor: {response}")
    
    # Get warrior path quest
    response = await client.send_command("accept warrior training")
    logger.info(f"Accepting warrior quest: {response}")
    
    # Move to Training Grounds
    response = await client.send_command("move east")
    logger.info(f"Moving to Training Grounds: {response}")
    
    assert await verify_current_area(client, "training_grounds")
    
    # Train warrior skills
    trained = await train_warrior_skills(client)
    assert trained, "Failed to complete warrior training"
    
    # Defeat training dummy
    dummy_defeated = await defeat_training_dummy(client)
    assert dummy_defeated, "Failed to defeat training dummy"
    
    # PHASE 2: Equipment Upgrade
    # --------------------------
    
    # Move to Honor Shrine
    response = await client.send_command("move east")
    logger.info(f"Moving to Honor Shrine: {response}")
    
    assert await verify_current_area(client, "honor_shrine")
    
    # Pray at the shrine
    response = await client.send_command("pray at shrine")
    logger.info(f"Praying at shrine: {response}")
    
    # Get warrior's steel sword
    await ensure_item_acquired(client, "steel_sword", [
        "take sword from altar", 
        "get steel sword", 
        "accept sword offering"
    ])
    
    # Verify inventory has the new sword
    missing_items = await verify_inventory_contains(client, ["steel_sword"])
    assert not missing_items, f"Missing required items: {missing_items}"
    
    # PHASE 3: First Combat Trial
    # ---------------------------
    
    # Return to Warrior's Camp
    response = await client.send_command("move west")
    logger.info(f"Moving back to Training Grounds: {response}")
    
    response = await client.send_command("move west")
    logger.info(f"Moving back to Warrior's Camp: {response}")
    
    # Move north to Mountain Base
    response = await client.send_command("move north")
    logger.info(f"Moving to Mountain Base: {response}")
    
    assert await verify_current_area(client, "mountain_base")
    
    # Engage with first trial enemy
    enemy_defeated = await ensure_enemy_defeated(client, "mountain_wolf")
    assert enemy_defeated, "Failed to defeat mountain wolf"
    
    # PHASE 4: Advanced Training
    # --------------------------
    
    # Move to Crossroads
    response = await client.send_command("move northeast")  # Assuming this is the direction to Crossroads
    logger.info(f"Moving to Crossroads: {response}")
    
    assert await verify_current_area(client, "crossroads")
    
    # Learn advanced combat technique
    response = await client.send_command("train advanced combat")
    logger.info(f"Learning advanced technique: {response}")
    
    # PHASE 5: Warrior's Challenge
    # ----------------------------
    
    # Move to Guardian Overlook
    response = await client.send_command("follow warrior's path")
    logger.info(f"Following warrior's path: {response}")
    
    # Navigate to Guardian Overlook (multiple steps)
    response = await client.send_command("move forward")
    logger.info(f"Moving toward Guardian Overlook: {response}")
    
    response = await client.send_command("climb mountain path")
    logger.info(f"Climbing mountain path: {response}")
    
    # Ensure we reach Guardian Overlook
    assert await verify_current_area(client, "guardian_overlook")
    
    # Defeat the guardian
    enemy_defeated = await ensure_enemy_defeated(client, "honor_guardian")
    assert enemy_defeated, "Failed to defeat the Honor Guardian"
    
    # PHASE 6: Final Battle
    # ---------------------
    
    # Move to Ancient Sanctuary
    response = await client.send_command("enter sanctuary")
    logger.info(f"Entering Ancient Sanctuary: {response}")
    
    assert await verify_current_area(client, "ancient_sanctuary")
    
    # Prepare for final battle
    response = await client.send_command("ready weapon")
    logger.info(f"Preparing for battle: {response}")
    
    # Defeat the final boss using warrior techniques
    response = await client.send_command("challenge the guardian")
    logger.info(f"Challenging final guardian: {response}")
    
    # Final battle sequence
    response = await client.send_command("use overhead strike")
    logger.info(f"Using overhead strike: {response}")
    
    response = await client.send_command("defend against attack")
    logger.info(f"Defending: {response}")
    
    response = await client.send_command("use powerful thrust")
    logger.info(f"Using powerful thrust: {response}")
    
    # Final strike to defeat the boss
    response = await client.send_command("deliver final blow")
    logger.info(f"Delivering final blow: {response}")
    
    # Verify game completion
    response = await client.send_command("look around")
    
    # Check for victory conditions in the response
    assert any(phrase in response.lower() for phrase in [
        "you have completed", 
        "victory", 
        "triumphant", 
        "congratulations"
    ]), "Could not verify game completion"
    
    logger.info("=== WARRIOR PATH COMPLETED SUCCESSFULLY ===")

# Run tests directly
if __name__ == "__main__":
    asyncio.run(TestRunner(stop_on_failure=True).run_tests({
        "warrior_path_journey": test_warrior_path_complete_journey,
    })) 