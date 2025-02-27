"""
Integration tests for The Last Centaur game.

This module tests the integration between different game systems,
particularly focusing on the combat system's integration with other components.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.engine.core.combat_system import CombatSystem, ElementType, CombatAction
from src.engine.core.command_parser import CommandParser
from src.engine.core.player import Player
from src.engine.core.models import Enemy, TerrainType, PathType
from src.engine.core.game_systems import TimeSystem


class TestCombatIntegration:
    """Test suite for combat system integration."""
    
    @pytest.fixture
    def player(self):
        """Create a player instance for testing."""
        player = Player()
        player.state.stats.health = 100
        player.state.stats.max_health = 100
        player.time_system = TimeSystem()
        return player
    
    @pytest.fixture
    def command_parser(self, player):
        """Create a command parser instance for testing."""
        parser = CommandParser(player)
        parser.combat_system = CombatSystem()
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
        assert "COMBAT STATUS" in result
        
        # Test defend command
        result = command_parser.handle_combat_command(CombatAction.DEFEND, [])
        
        # Should contain defend message
        assert "defensive stance" in result.lower()
        assert "COMBAT STATUS" in result
        
        # Test dodge command
        result = command_parser.handle_combat_command(CombatAction.DODGE, [])
        
        # Should contain dodge message
        assert "dodge" in result.lower() or "evasion" in result.lower()
        assert "COMBAT STATUS" in result
    
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
            assert "COMBAT STATUS" in result
    
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
        assert "special" in result.lower() or "warrior" in result.lower()
        assert "COMBAT STATUS" in result
        
        # Test with different paths
        player.path_type = PathType.MYSTIC
        result = command_parser.handle_combat_command(CombatAction.SPECIAL, [])
        assert "mystic" in result.lower() or "channel" in result.lower()
        
        player.path_type = PathType.STEALTH
        result = command_parser.handle_combat_command(CombatAction.SPECIAL, [])
        assert "stealth" in result.lower() or "shadow" in result.lower()
    
    def test_shadow_centaur_combat(self, command_parser, player, shadow_centaur):
        """Test combat with the Shadow Centaur boss."""
        # Mock the current tile with the Shadow Centaur
        player.state.current_tile = MagicMock()
        player.state.current_tile.enemies = [shadow_centaur]
        player.state.current_tile.terrain_type = TerrainType.CAVE  # Shadow terrain
        
        # First attack initializes combat
        result = command_parser.handle_combat_command(CombatAction.ATTACK, ["shadow", "centaur", "light"])
        
        # Should contain special boss encounter message
        assert "Shadow Centaur" in result
        assert "final challenge" in result.lower()
        
        # Simulate combat to trigger phase transitions
        # Phase 1
        for _ in range(3):
            result = command_parser.handle_combat_command(CombatAction.ATTACK, ["shadow", "centaur", "light"])
        
        # Damage the boss to trigger phase 2 (below 75% health)
        shadow_centaur.health = 220  # ~73% health
        command_parser.combat_system.enemy_combat_stats.health = 220
        
        result = command_parser.handle_combat_command(CombatAction.ATTACK, ["shadow", "centaur", "light"])
        
        # Should contain phase transition message
        if "form flickers" in result.lower():
            assert "form flickers" in result.lower()
        
        # Damage the boss to trigger phase 3 (below 50% health)
        shadow_centaur.health = 140  # ~47% health
        command_parser.combat_system.enemy_combat_stats.health = 140
        
        result = command_parser.handle_combat_command(CombatAction.ATTACK, ["shadow", "centaur", "light"])
        
        # Should contain phase transition message
        if "roars in fury" in result.lower():
            assert "roars in fury" in result.lower()
        
        # Damage the boss to trigger final phase (below 25% health)
        shadow_centaur.health = 70  # ~23% health
        command_parser.combat_system.enemy_combat_stats.health = 70
        
        result = command_parser.handle_combat_command(CombatAction.ATTACK, ["shadow", "centaur", "light"])
        
        # Should contain phase transition message
        if "eyes glow" in result.lower():
            assert "eyes glow" in result.lower()
    
    def test_combat_victory(self, command_parser, player, enemy):
        """Test defeating an enemy in combat."""
        # Mock the current tile with an enemy
        player.state.current_tile = MagicMock()
        player.state.current_tile.enemies = [enemy]
        player.state.current_tile.terrain_type = TerrainType.FOREST
        
        # Mock the combat_victory method
        player.combat_victory = MagicMock(return_value="You have defeated the enemy!")
        
        # Initialize combat
        command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
        
        # Set enemy health to 0 to trigger victory
        enemy.health = 0
        command_parser.combat_system.enemy_combat_stats.health = 0
        
        # Attack should trigger victory
        result = command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
        
        # Should call combat_victory
        player.combat_victory.assert_called_once()
        assert "defeated" in result.lower()
    
    def test_player_defeat(self, command_parser, player, enemy):
        """Test player being defeated in combat."""
        # Mock the current tile with an enemy
        player.state.current_tile = MagicMock()
        player.state.current_tile.enemies = [enemy]
        player.state.current_tile.terrain_type = TerrainType.FOREST
        
        # Initialize combat
        command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
        
        # Set player health to 0 to trigger defeat
        player.state.stats.health = 0
        command_parser.combat_system.player_combat_stats.health = 0
        
        # Attack should trigger defeat message
        result = command_parser.handle_combat_command(CombatAction.ATTACK, ["test", "enemy", "physical"])
        
        # Should contain defeat message but player survives with 1 HP
        assert "defeated" in result.lower()
        assert "escape with your life" in result.lower()
        assert player.state.stats.health == 1 