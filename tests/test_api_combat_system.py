"""
Test script for the Combat System API in The Last Centaur.

This test verifies that the combat mechanics work correctly when accessed through the API:
1. Basic combat functionality
2. Different combat situations and enemy types
3. Combat outcomes and consequences
4. Combat item interactions
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
from src.engine.core.models import StoryArea, EnemyType
from src.auth.security import create_access_token


class TestAPICombatSystem:
    """Test suite for combat mechanics in the game through the API."""
    
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
                "name": f"Combat Test Game {uuid.uuid4().hex[:8]}",
                "max_players": 1,
                "description": "A game for testing the combat API"
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
            
            # Helper function to add an enemy to the current area
            async def add_enemy(enemy_id: str, enemy_type: EnemyType) -> bool:
                """Add an enemy to the current area through a debug command."""
                response = await execute(f"debug_add_enemy {enemy_id} {enemy_type.name}")
                return "added" in response.lower() or "spawned" in response.lower()
            
            # Yield the necessary objects for testing
            yield game_instance, execute, set_current_area, add_enemy
    
    @pytest.mark.asyncio
    async def test_basic_combat(self, game_setup):
        """Test basic combat functionality via API."""
        _, execute, set_current_area, add_enemy = game_setup
        
        # Move to a suitable area for combat
        await set_current_area(StoryArea.AWAKENING_WOODS)
        
        # Add a basic enemy
        await add_enemy("test_wolf", EnemyType.BEAST)
        
        # Check that the enemy is present
        look_response = await execute("look")
        assert "test_wolf" in look_response.lower()
        
        # Attack the enemy
        attack_response = await execute("attack test_wolf")
        assert "you attack the test_wolf" in attack_response.lower()
        
        # Combat should continue until enemy is defeated or player retreats
        # For testing purposes, we'll just defeat the enemy quickly using a debug command
        await execute("debug_defeat_enemy test_wolf")
        
        # Verify the enemy is no longer present
        final_look = await execute("look")
        assert "test_wolf" not in final_look.lower()
    
    @pytest.mark.asyncio
    async def test_combat_with_weapon(self, game_setup):
        """Test combat using a weapon via API."""
        _, execute, set_current_area, add_enemy = game_setup
        
        # Move to a suitable area for combat
        await set_current_area(StoryArea.FORGOTTEN_RUINS)
        
        # Add a weapon to the player's inventory
        await execute("debug_add_item steel_sword")
        
        # Verify the weapon is in inventory
        inventory = await execute("inventory")
        assert "steel_sword" in inventory
        
        # Add an enemy
        await add_enemy("ancient_guardian", EnemyType.CONSTRUCT)
        
        # Check that the enemy is present
        look_response = await execute("look")
        assert "ancient_guardian" in look_response.lower()
        
        # Equip the weapon
        equip_response = await execute("equip steel_sword")
        assert "you equip the steel_sword" in equip_response.lower()
        
        # Attack the enemy with the equipped weapon
        attack_response = await execute("attack ancient_guardian")
        assert "you attack the ancient_guardian" in attack_response.lower()
        assert "steel_sword" in attack_response.lower()
        
        # For testing purposes, defeat the enemy
        await execute("debug_defeat_enemy ancient_guardian")
        
        # Verify the enemy is defeated
        final_look = await execute("look")
        assert "ancient_guardian" not in final_look.lower()
    
    @pytest.mark.asyncio
    async def test_combat_with_magic(self, game_setup):
        """Test combat using magic via API."""
        _, execute, set_current_area, add_enemy = game_setup
        
        # Move to a suitable area
        await set_current_area(StoryArea.CRYSTAL_CAVES)
        
        # Add magic ability to player
        await execute("debug_add_spell fireball")
        
        # Add an enemy vulnerable to magic
        await add_enemy("frost_elemental", EnemyType.ELEMENTAL)
        
        # Check that the enemy is present
        look_response = await execute("look")
        assert "frost_elemental" in look_response.lower()
        
        # Cast spell at the enemy
        cast_response = await execute("cast fireball at frost_elemental")
        assert "you cast fireball" in cast_response.lower()
        assert "frost_elemental" in cast_response.lower()
        
        # For testing purposes, defeat the enemy
        await execute("debug_defeat_enemy frost_elemental")
        
        # Verify the enemy is defeated
        final_look = await execute("look")
        assert "frost_elemental" not in final_look.lower()
    
    @pytest.mark.asyncio
    async def test_combat_retreat(self, game_setup):
        """Test retreating from combat via API."""
        _, execute, set_current_area, add_enemy = game_setup
        
        # Move to a suitable area
        await set_current_area(StoryArea.SHADOW_MARSH)
        
        # Add a strong enemy
        await add_enemy("marsh_troll", EnemyType.GIANT)
        
        # Check that the enemy is present
        look_response = await execute("look")
        assert "marsh_troll" in look_response.lower()
        
        # Start combat
        attack_response = await execute("attack marsh_troll")
        assert "you attack the marsh_troll" in attack_response.lower()
        
        # Retreat from combat
        retreat_response = await execute("retreat")
        assert "you retreat" in retreat_response.lower()
        
        # Player should still be in the same area, but combat should have ended
        area_check = await execute("look")
        assert "shadow_marsh" in area_check.lower()
        
        # The enemy should still be there
        assert "marsh_troll" in area_check.lower()
    
    @pytest.mark.asyncio
    async def test_combat_with_potion(self, game_setup):
        """Test using potions during combat via API."""
        _, execute, set_current_area, add_enemy = game_setup
        
        # Move to a suitable area
        await set_current_area(StoryArea.ANCIENT_BATTLEFIELD)
        
        # Add a healing potion to inventory
        await execute("debug_add_item healing_potion")
        
        # Add an enemy
        await add_enemy("skeletal_warrior", EnemyType.UNDEAD)
        
        # Check inventory and enemy presence
        inventory = await execute("inventory")
        assert "healing_potion" in inventory
        
        look_response = await execute("look")
        assert "skeletal_warrior" in look_response.lower()
        
        # Start combat
        await execute("attack skeletal_warrior")
        
        # Use the potion during combat
        potion_response = await execute("use healing_potion")
        assert "you use the healing_potion" in potion_response.lower()
        assert "health" in potion_response.lower()
        
        # Check that the potion was consumed
        new_inventory = await execute("inventory")
        assert "healing_potion" not in new_inventory
        
        # End combat for test cleanup
        await execute("debug_defeat_enemy skeletal_warrior")
        
        # Verify enemy is defeated
        final_look = await execute("look")
        assert "skeletal_warrior" not in final_look.lower()
    
    @pytest.mark.asyncio
    async def test_combat_loot(self, game_setup):
        """Test looting after combat via API."""
        _, execute, set_current_area, add_enemy = game_setup
        
        # Move to a suitable area
        await set_current_area(StoryArea.FORGOTTEN_TEMPLE)
        
        # Add an enemy with loot
        await add_enemy("temple_guardian", EnemyType.CONSTRUCT)
        
        # Add loot to the enemy
        await execute("debug_add_enemy_loot temple_guardian ancient_key")
        
        # Check that the enemy is present
        look_response = await execute("look")
        assert "temple_guardian" in look_response.lower()
        
        # Defeat the enemy
        await execute("attack temple_guardian")
        await execute("debug_defeat_enemy temple_guardian")
        
        # Check for loot drop message
        loot_response = await execute("look")
        assert "ancient_key" in loot_response.lower()
        
        # Take the loot
        take_response = await execute("take ancient_key")
        assert "you take the ancient_key" in take_response.lower()
        
        # Verify item is in inventory
        inventory = await execute("inventory")
        assert "ancient_key" in inventory 