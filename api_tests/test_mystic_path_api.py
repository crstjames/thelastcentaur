"""
Mystic Path Test for The Last Centaur.

This test follows the path of magical knowledge:
Start → Druid's Grove → Trials Path → Mystic Mountains → Crystal Outpost → Crystal Caves → Shadow Domain
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
logger = logging.getLogger("mystic_path_test")

class MysticPathTest(BasePathTest):
    """Test for the mystic path through the game via API calls."""
    
    def __init__(self, **kwargs):
        """Initialize the mystic path test."""
        required_items = [
            "ancient_scroll", 
            "crystal_focus", 
            "crystal_key", 
            "mystic_crystal", 
            "resonance_key", 
            "guardian_essence"
        ]
        super().__init__("mystic", required_items, **kwargs)
        
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
        
    async def step_move_to_druids_grove(self) -> None:
        """Step 2: Move to Druid's Grove and interact with Hermit Druid."""
        # Move west to Druid's Grove
        await self.execute_command("w", ignore_failure=True)
        
        # Verify we're in Druid's Grove
        await self.ensure_location("druids_grove")
        
        # Look around
        await self.execute_command("look", "grove")
        
        # Talk to the Hermit Druid
        await self.execute_command("talk hermit_druid", "Ah, another proud centaur", ignore_failure=True)
        
        # Get the ancient scroll
        await self.ensure_item("ancient_scroll", [
            "take ancient_scroll", 
            "grab ancient_scroll",
            "pick up ancient_scroll",
            "search"
        ])
        
        # Get the crystal focus
        await self.ensure_item("crystal_focus", [
            "take crystal_focus", 
            "grab crystal_focus",
            "pick up crystal_focus",
            "search"
        ])
        
        # Go back to Awakening Woods
        await self.execute_command("e", ignore_failure=True)
        await self.ensure_location("AWAKENING_WOODS")
        
    async def step_move_to_trials_path(self) -> None:
        """Step 3: Move to Trials Path."""
        # Move north to Trials Path
        await self.execute_command("n", "crossroads")
        
        # Verify we're in Trials Path
        await self.ensure_location("TRIALS_PATH")
        
        # Look around
        await self.execute_command("look", "paths diverge")
        
    async def step_move_to_mystic_mountains(self) -> None:
        """Step 4: Move to Mystic Mountains."""
        # Move west to Mystic Mountains
        await self.execute_command("w", ignore_failure=True)
        
        # Verify we're in Mystic Mountains
        await self.ensure_location("MYSTIC_MOUNTAINS")
        
        # Look around
        await self.execute_command("look", "peaks")
        
        # Defeat any enemies
        await ensure_enemy_defeated(self.client, "Mountain Guardian")
        await ensure_enemy_defeated(self.client, "Storm Elemental")
        await ensure_enemy_defeated(self.client, "Crystal Golem")
        
    async def step_move_to_crystal_outpost(self) -> None:
        """Step 5: Move to Crystal Outpost and get the crystal key."""
        # Move west to Crystal Outpost
        await self.execute_command("w", ignore_failure=True)
        
        # Verify we're in Crystal Outpost
        await self.ensure_location("crystal_outpost")
        
        # Look around
        await self.execute_command("look", "outpost")
        
        # Defeat any enemies
        await ensure_enemy_defeated(self.client, "Crystal Golem")
        await ensure_enemy_defeated(self.client, "Mana Wraith")
        
        # Get the crystal key
        await self.ensure_item("crystal_key", [
            "take crystal_key", 
            "grab crystal_key",
            "pick up crystal_key",
            "search"
        ])
        
        # Go back to Mystic Mountains
        await self.execute_command("e", ignore_failure=True)
        await self.ensure_location("MYSTIC_MOUNTAINS")
        
    async def step_move_to_crystal_caves(self) -> None:
        """Step 6: Move to Crystal Caves and collect key items."""
        # Move north to Crystal Caves
        await self.execute_command("n", ignore_failure=True)
        
        # Verify we're in Crystal Caves
        await self.ensure_location("CRYSTAL_CAVES")
        
        # Look around
        await self.execute_command("look", "caves")
        
        # Get the mystic crystal
        await self.ensure_item("mystic_crystal", [
            "take mystic_crystal", 
            "grab mystic_crystal",
            "pick up mystic_crystal",
            "search"
        ])
        
        # Get the resonance key
        await self.ensure_item("resonance_key", [
            "take resonance_key", 
            "grab resonance_key",
            "pick up resonance_key",
            "search"
        ])
        
        # Defeat the Crystal Guardian if present
        await ensure_enemy_defeated(self.client, "Crystal Guardian")
        
        # Get the guardian essence
        await self.ensure_item("guardian_essence", [
            "take guardian_essence", 
            "grab guardian_essence",
            "pick up guardian_essence",
            "search"
        ])
        
    async def step_move_to_shadow_domain(self) -> None:
        """Step 7: Move to Shadow Domain and complete the path."""
        # Verify we have all required items for the path
        inventory_response = await self.execute_command("inventory")
        for item in self.required_items:
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
        """Run the mystic path test steps in sequence."""
        steps = [
            ("awakening_woods", self.step_awakening_woods),
            ("move_to_druids_grove", self.step_move_to_druids_grove),
            ("move_to_trials_path", self.step_move_to_trials_path),
            ("move_to_mystic_mountains", self.step_move_to_mystic_mountains),
            ("move_to_crystal_outpost", self.step_move_to_crystal_outpost),
            ("move_to_crystal_caves", self.step_move_to_crystal_caves),
            ("move_to_shadow_domain", self.step_move_to_shadow_domain)
        ]
        
        for step_name, step_func in steps:
            success = await self.try_step(step_name, step_func)
            if not success:
                raise AssertionError(f"Step {step_name} failed")
                
        # Final verification
        await self.verify_completion()
        logger.info("Mystic path test completed successfully")

async def test_mystic_path_api():
    """Run the mystic path test."""
    test = MysticPathTest()
    await test()
    
if __name__ == "__main__":
    asyncio.run(test_mystic_path_api()) 