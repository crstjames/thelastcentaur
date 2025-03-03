"""
Warrior Path Test for The Last Centaur.

This test follows the path of martial prowess:
Start → Trials Path → Ancient Ruins → Warriors Armory → Enchanted Valley → Shadow Domain
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any

# Import base test classes
from api_tests.base_path_test import BasePathTest
from api_tests.test_client import ensure_enemy_defeated

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("warrior_path_test")

class WarriorPathTest(BasePathTest):
    """Test for the warrior path through the game via API calls."""
    
    def __init__(self, **kwargs):
        """Initialize the warrior path test."""
        required_items = [
            "warrior_map", 
            "ancient_sword", 
            "war_horn", 
            "guardian_essence"
        ]
        super().__init__("warrior", required_items, **kwargs)
        
    async def step_awakening_woods(self) -> None:
        """Step 1: Start in Awakening Woods and gather basic supplies."""
        # Look around to get our bearings
        await self.execute_command("look", "ancient woods", case_sensitive=False)
        
        # Pick up initial items
        await self.ensure_item("old_map", ["take old_map", "pick up map", "grab map"])
        await self.ensure_item("basic_supplies", ["take basic_supplies", "gather supplies", "pick up supplies"])
        
        # Defeat any wolves if present
        await self.execute_command("look")
        await ensure_enemy_defeated(self.client, "Wolf Pack")
        
    async def step_meet_fallen_warrior(self) -> None:
        """Step 2: Meet with the Fallen Warrior to get the warrior map."""
        # Move east to the Fallen Warrior's camp
        await self.execute_command("e", ignore_failure=True)
        
        # Check we're in the right place
        await self.ensure_location("warriors_camp")
        
        # Look around
        await self.execute_command("look", "camp")
        
        # Talk to the Fallen Warrior
        await self.execute_command("talk fallen_warrior", "Strength alone won't save you", ignore_failure=True)
        
        # Ensure we have the warrior_map
        await self.ensure_item("warrior_map", [
            "take warrior_map", 
            "grab warrior_map",
            "pick up warrior_map",
            "search"
        ])
        
        # Go back to Awakening Woods
        await self.execute_command("w", ignore_failure=True)
        await self.ensure_location("AWAKENING_WOODS")
        
    async def step_move_to_trials_path(self) -> None:
        """Step 3: Move to Trials Path."""
        # Move north to Trials Path
        await self.execute_command("n", "crossroads")
        
        # Check we're in the right place
        await self.ensure_location("TRIALS_PATH")
        
        # Look around
        await self.execute_command("look", "paths diverge")
        
    async def step_move_to_ancient_ruins(self) -> None:
        """Step 4: Move to Ancient Ruins and get the ancient sword."""
        # Move east to Ancient Ruins
        await self.execute_command("e", ignore_failure=True)
        
        # Check we're in the right place
        await self.ensure_location("ANCIENT_RUINS")
        
        # Look around
        await self.execute_command("look", "ruins")
        
        # Get the ancient sword
        await self.ensure_item("ancient_sword", [
            "take ancient_sword", 
            "grab ancient_sword",
            "search"
        ])
        
    async def step_move_to_warriors_armory(self) -> None:
        """Step 5: Move to Warrior's Armory and get the war horn."""
        # Move east to Warrior's Armory
        await self.execute_command("e", ignore_failure=True)
        
        # Check we're in the right place
        await self.ensure_location("warriors_armory")
        
        # Look around
        await self.execute_command("look", "armory")
        
        # Get the war horn
        await self.ensure_item("war_horn", [
            "take war_horn", 
            "grab war_horn",
            "search"
        ])
        
        # Go back to Ancient Ruins
        await self.execute_command("w", ignore_failure=True)
        await self.ensure_location("ANCIENT_RUINS")
        
        # Defeat the Stone Guardian if present
        await ensure_enemy_defeated(self.client, "Stone Guardian")
        
    async def step_move_to_enchanted_valley(self) -> None:
        """Step 6: Move to Enchanted Valley and defeat the Shadow Guardian."""
        # Move north to Enchanted Valley
        await self.execute_command("n", ignore_failure=True)
        
        # Check we're in the right place
        await self.ensure_location("ENCHANTED_VALLEY")
        
        # Look around
        await self.execute_command("look", "valley")
        
        # Defeat the Shadow Guardian
        await ensure_enemy_defeated(self.client, "Shadow Guardian")
        
        # Get the guardian essence
        await self.ensure_item("guardian_essence", [
            "take guardian_essence", 
            "grab guardian_essence",
            "search"
        ])
        
    async def step_move_to_shadow_domain(self) -> None:
        """Step 7: Move to Shadow Domain and complete the path."""
        # Verify we have all required items for the path
        inventory_response = await self.execute_command("inventory")
        for item in ["ancient_sword", "war_horn", "guardian_essence"]:
            if item not in inventory_response:
                logger.warning(f"Required item {item} not in inventory, attempting to add")
                await self.ensure_item(item, [f"take {item}", "search"])
        
        # Move north to Shadow Domain
        await self.execute_command("n", ignore_failure=True)
        
        # Verify we're in Shadow Domain
        await self.ensure_location("SHADOW_DOMAIN")
        
        # Look around
        await self.execute_command("look", "shadow")
        
        # Defeat the Second Centaur if present
        await ensure_enemy_defeated(self.client, "Second Centaur")
        await ensure_enemy_defeated(self.client, "Shadow Centaur")
        
        # Get the crown of dominion if present
        await self.ensure_item("crown_of_dominion", [
            "take crown_of_dominion", 
            "grab crown_of_dominion",
            "search"
        ])
        
    async def run_test(self) -> None:
        """Run the warrior path test steps in sequence."""
        steps = [
            ("awakening_woods", self.step_awakening_woods),
            ("meet_fallen_warrior", self.step_meet_fallen_warrior),
            ("move_to_trials_path", self.step_move_to_trials_path),
            ("move_to_ancient_ruins", self.step_move_to_ancient_ruins),
            ("move_to_warriors_armory", self.step_move_to_warriors_armory),
            ("move_to_enchanted_valley", self.step_move_to_enchanted_valley),
            ("move_to_shadow_domain", self.step_move_to_shadow_domain)
        ]
        
        for step_name, step_func in steps:
            success = await self.try_step(step_name, step_func)
            if not success:
                raise AssertionError(f"Step {step_name} failed")
                
        # Final verification
        await self.verify_completion()
        logger.info("Warrior path test completed successfully")

async def test_warrior_path_api():
    """Run the warrior path test."""
    test = WarriorPathTest()
    await test()
    
if __name__ == "__main__":
    asyncio.run(test_warrior_path_api()) 