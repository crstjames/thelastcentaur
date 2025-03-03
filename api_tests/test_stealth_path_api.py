"""
Stealth Path Test for The Last Centaur.

This test follows the path of cunning and deception:
Start → Ancient Ruins → Trials Path → Enchanted Valley → Shadow Domain
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
logger = logging.getLogger("stealth_path_test")

class StealthPathTest(BasePathTest):
    """Test for the stealth path through the game via API calls."""
    
    def __init__(self, **kwargs):
        """Initialize the stealth path test."""
        required_items = [
            "shadow_key", 
            "stealth_cloak", 
            "phantom_dagger", 
            "shadow_essence", 
            "shadow_essence_fragment"
        ]
        super().__init__("stealth", required_items, **kwargs)
        
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
        
    async def step_move_to_trials_path(self) -> None:
        """Step 2: Move from Awakening Woods to Trials Path and interact with Shadow Scout."""
        # Move north to Trials Path
        await self.execute_command("n", "crossroads")
        
        # Check we're in the right place
        await self.ensure_location("TRIALS_PATH")
        
        # Look around to ensure the Shadow Scout is present
        await self.execute_command("look")
        await self.execute_command("look north")
        await self.execute_command("look east")
        await self.execute_command("look west")
        
        # Talk to Shadow Scout to get the shadow_key
        await self.execute_command("talk shadow_scout", "Not all victories require bloodshed", ignore_failure=True)
        
        # Ensure we have the shadow_key
        await self.ensure_item("shadow_key", [
            "take shadow_key", 
            "examine shadow scout", 
            "search", 
            "look at shadow_scout"
        ])
        
    async def step_move_to_twilight_glade(self) -> None:
        """Step 3: Move to Twilight Glade and get the shadow essence fragment."""
        # Prepare for the hidden path
        await self.execute_command("look north")
        
        # Move north to Twilight Glade
        await self.execute_command("n", ignore_failure=True)
        
        # Verify we're in Twilight Glade
        await self.ensure_location("twilight_glade")
        
        # Look around
        await self.execute_command("look", "twilight")
        
        # Defeat any shadow hound if present
        await ensure_enemy_defeated(self.client, "Shadow Hound")
        
        # Get the shadow essence fragment
        await self.ensure_item("shadow_essence_fragment", [
            "take shadow_essence_fragment", 
            "grab shadow_essence_fragment",
            "examine shadow_essence_fragment",
            "search"
        ])
        
    async def step_move_to_forgotten_grove(self) -> None:
        """Step 4: Move to Forgotten Grove and get the stealth cloak."""
        # Look around in sequence to reveal the path
        await self.execute_command("look")
        await self.execute_command("look north")
        await self.execute_command("look east")
        await self.execute_command("look west")
        await self.execute_command("look north")
        
        # Move north to Forgotten Grove
        await self.execute_command("n", ignore_failure=True)
        
        # Verify we're in Forgotten Grove
        await self.ensure_location("FORGOTTEN_GROVE")
        
        # Look around
        await self.execute_command("look", "grove")
        
        # Defeat Shadow Stalker if present
        await ensure_enemy_defeated(self.client, "Shadow Stalker")
        
        # Get the stealth cloak
        await self.ensure_item("stealth_cloak", [
            "take stealth_cloak", 
            "grab stealth_cloak",
            "pick up stealth_cloak",
            "search"
        ])
        
    async def step_defeat_phantom_assassin(self) -> None:
        """Step 5: Find and defeat the Phantom Assassin to get the phantom dagger and shadow essence."""
        # Look around in sequence to make the Phantom Assassin appear
        await self.execute_command("look")
        await self.execute_command("look north")
        await self.execute_command("look east")
        await self.execute_command("look west")
        
        # Check for the Phantom Assassin
        response = await self.execute_command("look")
        
        # Defeat the Phantom Assassin if present
        await ensure_enemy_defeated(self.client, "Phantom Assassin")
        
        # Get the phantom dagger
        await self.ensure_item("phantom_dagger", [
            "take phantom_dagger", 
            "grab phantom_dagger",
            "search"
        ])
        
        # Get the shadow essence
        await self.ensure_item("shadow_essence", [
            "take shadow_essence", 
            "grab shadow_essence",
            "search"
        ])
        
    async def step_move_to_shadow_domain(self) -> None:
        """Step 6: Move to Shadow Domain and complete the path."""
        # Look around to prepare for the move
        await self.execute_command("look")
        
        # Verify we have all required items for the path
        inventory_response = await self.execute_command("inventory")
        for item in ["stealth_cloak", "phantom_dagger", "shadow_essence", "shadow_essence_fragment"]:
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
        """Run the stealth path test steps in sequence."""
        steps = [
            ("awakening_woods", self.step_awakening_woods),
            ("move_to_trials_path", self.step_move_to_trials_path),
            ("move_to_twilight_glade", self.step_move_to_twilight_glade),
            ("move_to_forgotten_grove", self.step_move_to_forgotten_grove),
            ("defeat_phantom_assassin", self.step_defeat_phantom_assassin),
            ("move_to_shadow_domain", self.step_move_to_shadow_domain)
        ]
        
        for step_name, step_func in steps:
            success = await self.try_step(step_name, step_func)
            if not success:
                raise AssertionError(f"Step {step_name} failed")
                
        # Final verification
        await self.verify_completion()
        logger.info("Stealth path test completed successfully")

async def test_stealth_path_api():
    """Run the stealth path test."""
    test = StealthPathTest()
    await test()
    
if __name__ == "__main__":
    asyncio.run(test_stealth_path_api()) 