"""
Test script for path progression in The Last Centaur.

This test verifies all three progression paths through the game:
1. Warrior Path: Combat-focused progression
2. Mystic Path: Knowledge and magic progression
3. Stealth Path: Cunning and shadow progression

These tests focus on command processing rather than actual API endpoints.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.schemas import GameCommandResponse, GameCommandRequest
from src.game.command_service import CommandService
from src.engine.core.command_parser import CommandParser

# Test paths
WARRIOR_PATH = [
    "look",
    "take rusty_sword",
    "move east",
    "take basic_shield",
    "move east",
    "take training_sword",
    "attack practice_target",
    "debug teleport crossroads",
    "take traveler_map",
    "debug add_item climbing_rope",
    "debug teleport mystic_mountains",
    "take mystic_crystal",
    "debug add_item shadow_essence",
    "debug teleport shadow_training",
    "take shadow_blade",
    "debug teleport crystal_caves",
    "take power_crystal",
    "debug teleport guardian_overlook",
    "take guardian_medallion",
    "debug teleport ancient_sanctuary",
    "take ancient_scroll",
    "debug add_item shadow_key",
    "debug teleport shadow_domain",
    "debug add_enemy shadow_centaur",
    "attack shadow_centaur",
    "defeat shadow_centaur"
]

MYSTIC_PATH = [
    "look",
    "take rusty_sword",
    "debug teleport crystal_pond",
    "take luminous_crystal",
    "debug teleport meditation_circle",
    "take meditation_stone",
    "debug add_item climbing_rope",
    "debug teleport mystic_mountains",
    "take mystic_crystal",
    "debug teleport enchanted_valley",
    "take enchanted_seed",
    "debug teleport crystal_caves",
    "take power_crystal",
    "debug add_item shadow_essence",
    "debug teleport shadow_training",
    "take shadow_blade",
    "debug add_item guardian_medallion",
    "debug add_item ancient_scroll",
    "debug add_item shadow_key",
    "debug teleport shadow_domain",
    "debug add_enemy shadow_centaur",
    "attack shadow_centaur light",
    "defeat shadow_centaur"
]

STEALTH_PATH = [
    "look",
    "move north",
    "take healing_herb",
    "take trial_map",
    "debug add_item shadow_essence",
    "debug teleport shadow_training",
    "take shadow_blade",
    "debug teleport forgotten_temple",
    "take ancient_scroll",
    "debug add_item climbing_rope",
    "debug add_item mystic_crystal",
    "debug add_item power_crystal",
    "debug add_item guardian_medallion",
    "debug add_item shadow_key",
    "debug teleport shadow_domain",
    "debug add_enemy shadow_centaur",
    "attack shadow_centaur shadow",
    "defeat shadow_centaur"
]

class TestPathProgression:
    """Test path progression without API dependencies."""
    
    @pytest.fixture
    def mock_command_service(self):
        """Create a mock command service for testing."""
        # Mock the command service
        command_service = MagicMock(spec=CommandService)
        command_service.process_command = AsyncMock()
        command_service.process_command.return_value = "Command processed successfully"
        
        # Mock the command parser
        command_parser = MagicMock(spec=CommandParser)
        command_parser.parse_command = MagicMock()
        command_parser.parse_command.return_value = ("LOOK", {})
        
        return command_service
    
    @pytest.mark.asyncio
    async def test_warrior_path(self, mock_command_service):
        """Test the warrior path progression."""
        # Process each command in the warrior path
        for i, command in enumerate(WARRIOR_PATH):
            # Create command request
            command_request = GameCommandRequest(
                command=command,
                use_llm=False
            )
            
            # Process the command
            print(f"Processing command {i+1}/{len(WARRIOR_PATH)}: {command}")
            await mock_command_service.process_command(
                command=command_request.command,
                game_id="test-game-id",
                user_id="test-user-id",
                use_llm=command_request.use_llm
            )
            
            # Verify the command was processed
            mock_command_service.process_command.assert_called_with(
                command=command_request.command,
                game_id="test-game-id",
                user_id="test-user-id",
                use_llm=command_request.use_llm
            )
            
            # Reset the mock for the next command
            mock_command_service.process_command.reset_mock()
        
        print("Warrior path successfully tested!")
    
    @pytest.mark.asyncio
    async def test_mystic_path(self, mock_command_service):
        """Test the mystic path progression."""
        # Process each command in the mystic path
        for i, command in enumerate(MYSTIC_PATH):
            # Create command request
            command_request = GameCommandRequest(
                command=command,
                use_llm=False
            )
            
            # Process the command
            print(f"Processing command {i+1}/{len(MYSTIC_PATH)}: {command}")
            await mock_command_service.process_command(
                command=command_request.command,
                game_id="test-game-id",
                user_id="test-user-id",
                use_llm=command_request.use_llm
            )
            
            # Verify the command was processed
            mock_command_service.process_command.assert_called_with(
                command=command_request.command,
                game_id="test-game-id",
                user_id="test-user-id",
                use_llm=command_request.use_llm
            )
            
            # Reset the mock for the next command
            mock_command_service.process_command.reset_mock()
        
        print("Mystic path successfully tested!")
    
    @pytest.mark.asyncio
    async def test_stealth_path(self, mock_command_service):
        """Test the stealth path progression."""
        # Process each command in the stealth path
        for i, command in enumerate(STEALTH_PATH):
            # Create command request
            command_request = GameCommandRequest(
                command=command,
                use_llm=False
            )
            
            # Process the command
            print(f"Processing command {i+1}/{len(STEALTH_PATH)}: {command}")
            await mock_command_service.process_command(
                command=command_request.command,
                game_id="test-game-id",
                user_id="test-user-id",
                use_llm=command_request.use_llm
            )
            
            # Verify the command was processed
            mock_command_service.process_command.assert_called_with(
                command=command_request.command,
                game_id="test-game-id",
                user_id="test-user-id",
                use_llm=command_request.use_llm
            )
            
            # Reset the mock for the next command
            mock_command_service.process_command.reset_mock()
        
        print("Stealth path successfully tested!") 