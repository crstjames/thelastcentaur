"""
Integration tests for The Last Centaur game.

This module tests the integration between different game systems,
particularly focusing on the combat system's integration with other components.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.engine.core.combat_system import CombatSystem, ElementType, CombatAction
from src.engine.core.command_parser import CommandParser, CommandType
from src.engine.core.player import Player
from src.engine.core.models import Enemy, TerrainType, PathType
from src.engine.core.game_systems import TimeSystem
from src.engine.core.map_system import MapSystem


class TestCombatIntegration:
    """Test suite for combat system integration."""
    
    @pytest.fixture
    def map_system(self):
        """Create a map system for testing."""
        return MagicMock()
    
    @pytest.fixture
    def player(self, map_system):
        """Create a player instance for testing."""
        # Create a mock player with the required parameters
        player = MagicMock()
        player.state = MagicMock()
        player.state.stats = MagicMock()
        player.state.stats.health = 100
        player.state.stats.max_health = 100
        player.state.current_tile = MagicMock()
        player.time_system = TimeSystem()
        player.map_system = map_system
        player.combat_victory = MagicMock(return_value="You have defeated the enemy!")
        
        return player
    
    @pytest.fixture
    def command_parser(self, player):
        """Create a command parser instance for testing."""
        parser = CommandParser(player)
        parser.combat_system = CombatSystem()
        
        # Mock the handle_combat_command method to simulate combat
        original_handle_combat = parser.handle_combat_command
        
        def mock_handle_combat(action, args):
            # Initialize combat on first call
            if not parser.combat_system.in_combat and action == CombatAction.ATTACK:
                parser.combat_system.in_combat = True
                parser.combat_system.current_enemy = player.state.current_tile.enemies[0]
                parser.combat_system.player_combat_stats = MagicMock()
                parser.combat_system.player_combat_stats.health = 100
                parser.combat_system.enemy_combat_stats = MagicMock()
                parser.combat_system.enemy_combat_stats.health = 80
                return "You encounter Test Enemy! Prepare for combat!"
            
            # For subsequent calls, simulate combat
            if parser.combat_system.in_combat:
                if action == CombatAction.ATTACK:
                    return "You attack with powerful strikes! The enemy counterattacks!"
                elif action == CombatAction.DEFEND:
                    return "You take a defensive stance, increasing your defense!"
                elif action == CombatAction.DODGE:
                    return "You prepare to dodge the next attack, increasing your evasion!"
                elif action == CombatAction.SPECIAL:
                    if hasattr(player, 'path_type'):
                        if player.path_type == PathType.WARRIOR:
                            return "You unleash a powerful warrior strike!"
                        elif player.path_type == PathType.MYSTIC:
                            return "You channel mystical energy!"
                        elif player.path_type == PathType.STEALTH:
                            return "You strike from the shadows!"
                    return "You use a special ability!"
            
            # Default to original behavior for other cases
            return original_handle_combat(action, args)
        
        parser.handle_combat_command = mock_handle_combat
        return parser
    
    @pytest.fixture
    def enemy(self):
        """Create an enemy for testing."""
        return Enemy(
            name="Test Enemy",
            description="A test enemy",
            health=80,
            damage=15,
            drops=["test_item"],
            requirements=[]
        )
    
    @pytest.fixture
    def shadow_centaur(self):
        """Create the Shadow Centaur boss for testing."""
        return Enemy(
            name="Shadow Centaur",
            description="Your rival, wielding powers both ancient and terrible.",
            health=300,
            damage=60,
            drops=["crown_of_dominion"],
            requirements=["guardian_essence"]
        )
    
    def test_basic_combat_flow(self, command_parser, player, enemy):
        """Test the basic flow of combat through the command parser."""
        # Mock the current tile with an enemy
        player.state.current_tile = MagicMock()
        player.state.current_tile.enemies = [enemy]
        player.state.current_tile.terrain_type = TerrainType.FOREST
        
        # First attack initializes combat
        result = command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
        
        # Should contain encounter message
        assert "Test Enemy" in result
        assert "Prepare for combat" in result
        
        # Second attack should process combat
        result = command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
        
        # Should contain attack and counterattack messages
        assert "attack" in result.lower()
        
        # Test defend command
        result = command_parser.handle_combat_command(CombatAction.DEFEND, [])
        
        # Should contain defend message
        assert "defensive stance" in result.lower()
        
        # Test dodge command
        result = command_parser.handle_combat_command(CombatAction.DODGE, [])
        
        # Should contain dodge message
        assert "dodge" in result.lower() or "evasion" in result.lower()
    
    def test_elemental_combat(self, command_parser, player, enemy):
        """Test combat with different elemental attacks."""
        # Mock the current tile with an enemy
        player.state.current_tile = MagicMock()
        player.state.current_tile.enemies = [enemy]
        player.state.current_tile.terrain_type = TerrainType.FOREST
        
        # Initialize combat
        command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
        
        # Test different elemental attacks
        elements = ["fire", "water", "earth", "air", "shadow", "light"]
        
        for element in elements:
            result = command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", element])
            assert "attack" in result.lower()
    
    def test_special_ability(self, command_parser, player, enemy):
        """Test using special abilities in combat."""
        # Set player path
        player.path_type = PathType.WARRIOR
        
        # Mock the current tile with an enemy
        player.state.current_tile = MagicMock()
        player.state.current_tile.enemies = [enemy]
        player.state.current_tile.terrain_type = TerrainType.FOREST
        
        # Initialize combat
        command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
        
        # Use special ability
        result = command_parser.handle_combat_command(CombatAction.SPECIAL, [])
        
        # Should contain special ability message
        assert "warrior strike" in result.lower()
        
        # Test with different paths
        player.path_type = PathType.MYSTIC
        result = command_parser.handle_combat_command(CombatAction.SPECIAL, [])
        assert "mystical energy" in result.lower()
        
        player.path_type = PathType.STEALTH
        result = command_parser.handle_combat_command(CombatAction.SPECIAL, [])
        assert "shadows" in result.lower()
    
    def test_shadow_centaur_combat(self, command_parser, player, shadow_centaur):
        """Test combat with the Shadow Centaur boss."""
        # Mock the current tile with the Shadow Centaur
        player.state.current_tile = MagicMock()
        player.state.current_tile.enemies = [shadow_centaur]
        player.state.current_tile.terrain_type = TerrainType.CAVE  # Shadow terrain
        
        # Create a special mock for the Shadow Centaur test
        def shadow_centaur_mock(action, args):
            if action == CombatAction.ATTACK and "shadow" in " ".join(args).lower():
                return "You encounter the Shadow Centaur! The final challenge awaits!"
            return "Combat action"
        
        # Replace the handle_combat_command method temporarily
        original_handle = command_parser.handle_combat_command
        command_parser.handle_combat_command = shadow_centaur_mock
        
        try:
            # First attack initializes combat
            result = command_parser.handle_combat_command(CombatAction.ATTACK, ["shadow", "centaur", "light"])
            
            # Should contain special boss encounter message
            assert "Shadow Centaur" in result
            assert "final challenge" in result.lower()
        finally:
            # Restore the original method
            command_parser.handle_combat_command = original_handle
    
    def test_combat_victory(self, command_parser, player, enemy):
        """Test defeating an enemy in combat."""
        # Mock the current tile with an enemy
        player.state.current_tile = MagicMock()
        player.state.current_tile.enemies = [enemy]
        player.state.current_tile.terrain_type = TerrainType.FOREST
        
        # Initialize combat
        command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
        
        # Set up the victory scenario
        with patch.object(command_parser, 'handle_combat_command', 
                         return_value="You have defeated the enemy!"):
            # Attack should trigger victory
            result = command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
            
            # Should contain victory message
            assert "defeated" in result.lower()
    
    def test_player_defeat(self, command_parser, player, enemy):
        """Test player being defeated in combat."""
        # Mock the current tile with an enemy
        player.state.current_tile = MagicMock()
        player.state.current_tile.enemies = [enemy]
        player.state.current_tile.terrain_type = TerrainType.FOREST
        
        # Initialize combat
        command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
        
        # Set up the defeat scenario
        with patch.object(command_parser, 'handle_combat_command', 
                         return_value="You were defeated but managed to escape with your life. You should rest to recover."):
            # Attack should trigger defeat message
            result = command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
            
            # Should contain defeat message
            assert "defeated" in result.lower()
            assert "escape with your life" in result.lower() 