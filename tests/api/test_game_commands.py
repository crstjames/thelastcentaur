"""
API tests for game command execution endpoints.

This module tests the API endpoints for game command execution,
focusing on handling problematic commands identified in gameplay logs.
"""

import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch, MagicMock

from src.main import app


@pytest.fixture
def authenticated_client(client, mocker):
    """Create an authenticated client for testing."""
    # Mock the get_current_user dependency
    mocker.patch(
        "src.auth.deps.get_current_user",
        return_value={
            "id": "test_user_id",
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True,
            "is_superuser": False
        }
    )
    return client


@pytest.fixture
def game_instance(mocker):
    """Create a mock game instance."""
    mock_game = MagicMock()
    mock_game.id = "test_game_id"
    mock_game.user_id = "test_user_id"
    mock_game.name = "Test Game"
    mock_game.game_state = {
        "inventory": ["basic_supplies", "old_map"],
        "player_position": [0, 0],
        "visited_tiles": [[0, 0]],
        "player_stats": {
            "health": 100,
            "max_health": 100
        }
    }

    # Mock the get_game_instance function
    mocker.patch(
        "src.game.router.get_game_instance",
        return_value=mock_game
    )
    
    return mock_game


class TestGameCommandAPI:
    """Test suite for game command API endpoints."""
    
    def test_item_pickup_commands(self, authenticated_client, game_instance, mocker):
        """Test that item pickup commands are properly handled by the API."""
        # Mock the command service to simulate successful pickup
        mocker.patch(
            "src.game.command_service.process_command",
            return_value=("You picked up the shadow_essence_fragment.", game_instance)
        )
        
        # Test different pickup command variations
        pickup_variations = [
            "pick up fragment",
            "pick up the fragment",
            "grab fragment",
            "take fragment",
            "get fragment",
            "pick up shadow_essence_fragment",
            "grab the shadow_essence_fragment"
        ]
        
        for command in pickup_variations:
            response = authenticated_client.post(
                f"/api/v1/game/{game_instance.id}/command",
                json={"command": command}
            )
            
            # Verify the API response
            assert response.status_code == 200
            data = response.json()
            assert data["command"] == command
            assert "You picked up" in data["response"]
    
    def test_combat_commands(self, authenticated_client, game_instance, mocker):
        """Test that combat commands are properly handled by the API."""
        # Mock the command service to simulate successful combat initiation
        mocker.patch(
            "src.game.command_service.process_command",
            return_value=("You attack the Phantom Assassin!", game_instance)
        )
        
        # Test different combat command variations
        combat_variations = [
            "fight phantom",
            "attack phantom",
            "battle phantom",
            "fight assassin",
            "attack phantom assassin",
            "fight the phantom assassin"
        ]
        
        for command in combat_variations:
            response = authenticated_client.post(
                f"/api/v1/game/{game_instance.id}/command",
                json={"command": command}
            )
            
            # Verify the API response
            assert response.status_code == 200
            data = response.json()
            assert data["command"] == command
            assert "attack" in data["response"].lower()
    
    def test_item_interaction_persistence(self, authenticated_client, game_instance, mocker):
        """Test that item state persistence is handled correctly through API."""
        # Mock command responses for a sequence of commands
        command_responses = [
            # Initial look command showing item
            ("You see a shadow_essence_fragment nearby.", game_instance),
            # Pickup command
            ("You picked up the shadow_essence_fragment.", {
                **game_instance,
                "game_state": {
                    **game_instance.game_state,
                    "inventory": [*game_instance.game_state["inventory"], "shadow_essence_fragment"]
                }
            }),
            # Look again - item should be gone
            ("The area is now empty of items.", {
                **game_instance,
                "game_state": {
                    **game_instance.game_state,
                    "inventory": [*game_instance.game_state["inventory"], "shadow_essence_fragment"]
                }
            })
        ]
        
        # Create a side effect that returns responses in sequence
        mock_process = mocker.patch("src.game.command_service.process_command")
        mock_process.side_effect = command_responses
        
        # Execute the sequence of commands
        commands = ["look", "take shadow_essence_fragment", "look"]
        
        for i, command in enumerate(commands):
            response = authenticated_client.post(
                f"/api/v1/game/{game_instance.id}/command",
                json={"command": command}
            )
            
            # Verify the API response
            assert response.status_code == 200
            data = response.json()
            assert data["command"] == command
            
            # Check specific response patterns
            if i == 0:  # First look
                assert "shadow_essence_fragment" in data["response"]
            elif i == 1:  # Pickup
                assert "picked up" in data["response"].lower()
            elif i == 2:  # Second look
                assert "shadow_essence_fragment" not in data["response"]


class TestAdminCommandAPI:
    """Test suite for admin command API endpoints to assist with in-game issue debug/resolution."""
    
    @pytest.fixture
    def admin_client(self, client, mocker):
        """Create an admin client for testing."""
        # Mock the verify_admin_access dependency
        mocker.patch(
            "src.game.admin_routes.verify_admin_access",
            return_value={
                "id": "admin_user_id",
                "username": "admin",
                "email": "admin@example.com",
                "is_active": True,
                "is_superuser": True
            }
        )
        return client
    
    def test_force_add_item(self, admin_client, game_instance, mocker):
        """Test that the force_add_item endpoint can resolve item pickup issues."""
        # Mock get_game_instance for admin routes
        mocker.patch(
            "src.game.admin_routes.get_game_instance",
            return_value=game_instance
        )
        
        # Test adding the problematic item
        response = admin_client.post(
            f"/api/v1/admin/game/{game_instance.id}/force_item",
            json={"item_name": "shadow_essence_fragment"}
        )
        
        # Verify the API response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "shadow_essence_fragment" in data["inventory"]
    
    def test_defeat_enemy(self, admin_client, game_instance, mocker):
        """Test that the defeat_enemy endpoint can resolve combat issues."""
        # Mock get_game_instance for admin routes
        mocker.patch(
            "src.game.admin_routes.get_game_instance",
            return_value=game_instance
        )
        
        # Mock execute_command to simulate successful command execution
        command_response = "The Phantom Assassin has been defeated!"
        mocker.patch(
            "src.game.admin_routes.execute_command",
            return_value=command_response
        )
        
        # Test defeating the problematic enemy
        response = admin_client.post(
            f"/api/v1/admin/game/{game_instance.id}/defeat_enemy",
            json={"enemy_name": "Phantom Assassin"}
        )
        
        # Verify the API response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "defeated" in data["message"].lower() 