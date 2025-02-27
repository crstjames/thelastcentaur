"""
Tests for the elemental combat system.

This module tests the functionality of the combat system, including:
- Elemental affinities
- Status effects
- Damage calculation
- Combat flow
"""

import pytest
from unittest.mock import MagicMock

from src.engine.core.combat_system import (
    CombatSystem, 
    ElementType, 
    StatusEffect, 
    CombatStats,
    CombatAction,
    StatusEffectInstance
)
from src.engine.core.models import TerrainType, Enemy, PathType


class TestCombatSystem:
    """Test suite for the combat system."""
    
    @pytest.fixture
    def combat_system(self):
        """Create a combat system instance for testing."""
        return CombatSystem()
    
    @pytest.fixture
    def player_stats(self):
        """Create player combat stats for testing."""
        return CombatStats(
            health=100,
            max_health=100,
            damage=20,
            defense=5,
            critical_chance=5,
            dodge_chance=5,
            elemental_affinities={
                ElementType.PHYSICAL: 2,
                ElementType.FIRE: 1,
                ElementType.WATER: 1,
                ElementType.EARTH: 0,
                ElementType.AIR: 0,
                ElementType.SHADOW: 0,
                ElementType.LIGHT: 0
            }
        )
    
    @pytest.fixture
    def enemy_stats(self):
        """Create enemy combat stats for testing."""
        return CombatStats(
            health=80,
            max_health=80,
            damage=15,
            defense=3,
            critical_chance=5,
            dodge_chance=5,
            elemental_affinities={
                ElementType.PHYSICAL: 1,
                ElementType.FIRE: 0,
                ElementType.WATER: 0,
                ElementType.EARTH: 2,
                ElementType.AIR: 0,
                ElementType.SHADOW: 0,
                ElementType.LIGHT: 0
            }
        )
    
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
    
    def test_assign_enemy_elements(self, combat_system, enemy):
        """Test assigning elemental affinities to enemies."""
        # Test with shadow enemy
        shadow_enemy = Enemy(
            name="Shadow Stalker",
            description="A shadow creature",
            health=80,
            damage=15,
            drops=[],
            requirements=[]
        )
        
        affinities = combat_system.assign_enemy_elements(shadow_enemy)
        assert affinities[ElementType.SHADOW] > 0
        assert affinities[ElementType.LIGHT] < 0
        
        # Test with wolf enemy
        wolf_enemy = Enemy(
            name="Wolf Pack",
            description="A pack of wolves",
            health=60,
            damage=15,
            drops=[],
            requirements=[]
        )
        
        affinities = combat_system.assign_enemy_elements(wolf_enemy)
        assert affinities[ElementType.PHYSICAL] > 0
        
        # Test with generic enemy
        generic_enemy = Enemy(
            name="Generic Enemy",
            description="A generic enemy",
            health=50,
            damage=10,
            drops=[],
            requirements=[]
        )
        
        affinities = combat_system.assign_enemy_elements(generic_enemy)
        assert affinities[ElementType.PHYSICAL] > 0
    
    def test_get_enemy_combat_stats(self, combat_system, enemy):
        """Test converting an enemy to combat stats."""
        stats = combat_system.get_enemy_combat_stats(enemy)
        
        assert stats.health == enemy.health
        assert stats.max_health == enemy.health
        assert stats.damage == enemy.damage
        assert stats.defense == enemy.health // 20
        assert stats.critical_chance == 5
        assert stats.dodge_chance == 5
        assert ElementType.PHYSICAL in stats.elemental_affinities
    
    def test_calculate_damage(self, combat_system, player_stats, enemy_stats):
        """Test damage calculation with elemental affinities."""
        # Test physical attack (player -> enemy)
        result = combat_system.calculate_damage(
            player_stats,
            enemy_stats,
            ElementType.PHYSICAL,
            TerrainType.FOREST
        )
        
        assert result.damage_dealt > 0
        assert not result.is_critical  # Not guaranteed, but unlikely with 5% chance
        
        # Test fire attack against earth (should be effective)
        result = combat_system.calculate_damage(
            player_stats,
            enemy_stats,
            ElementType.FIRE,
            TerrainType.CAVE  # Cave boosts fire
        )
        
        assert result.damage_dealt > 0
        assert result.elemental_bonus  # Fire is effective against earth
        
        # Test water attack against earth (should be ineffective)
        result = combat_system.calculate_damage(
            player_stats,
            enemy_stats,
            ElementType.WATER,
            TerrainType.FOREST
        )
        
        assert result.damage_dealt > 0
        assert not result.elemental_bonus  # Water is not effective against earth
    
    def test_apply_status_effects(self, combat_system, player_stats):
        """Test applying status effects."""
        # Add a burn effect
        player_stats.status_effects.append(
            StatusEffectInstance(
                effect=StatusEffect.BURN,
                duration=3,
                potency=2,
                source=ElementType.FIRE
            )
        )
        
        # Apply the effect
        damage, messages = combat_system.apply_status_effects(player_stats)
        
        assert damage > 0
        assert len(messages) > 0
        assert player_stats.status_effects[0].duration == 2  # Reduced by 1
        
        # Apply again until expired
        combat_system.apply_status_effects(player_stats)
        damage, messages = combat_system.apply_status_effects(player_stats)
        
        assert len(player_stats.status_effects) == 0  # Effect should be gone
    
    def test_dodge_result(self, combat_system, player_stats, enemy_stats):
        """Test dodge mechanics."""
        # Normal dodge chance
        for _ in range(10):  # Run multiple times to account for randomness
            result = combat_system.get_dodge_result(enemy_stats, player_stats)
            # Can't assert exact result due to randomness, but it should be a boolean
            assert isinstance(result, bool)
        
        # Increased dodge chance
        player_stats.dodge_chance = 75  # Max allowed
        
        # Should dodge more often, but still can't guarantee every time
        dodge_count = 0
        for _ in range(10):
            if combat_system.get_dodge_result(enemy_stats, player_stats):
                dodge_count += 1
        
        # With 75% dodge chance, should dodge most of the time
        assert dodge_count > 5
    
    def test_process_player_turn(self, combat_system, player_stats, enemy_stats):
        """Test processing a player's turn."""
        # Test attack action
        damage, message = combat_system.process_player_turn(
            player_stats,
            enemy_stats,
            CombatAction.ATTACK,
            ElementType.PHYSICAL,
            TerrainType.FOREST
        )
        
        assert damage > 0
        assert message
        
        # Test defend action
        original_defense = player_stats.defense
        damage, message = combat_system.process_player_turn(
            player_stats,
            enemy_stats,
            CombatAction.DEFEND,
            ElementType.PHYSICAL,
            TerrainType.FOREST
        )
        
        assert damage == 0  # Defend doesn't deal damage
        assert player_stats.defense > original_defense
        
        # Test dodge action
        original_dodge = player_stats.dodge_chance
        damage, message = combat_system.process_player_turn(
            player_stats,
            enemy_stats,
            CombatAction.DODGE,
            ElementType.PHYSICAL,
            TerrainType.FOREST
        )
        
        assert damage == 0  # Dodge doesn't deal damage
        assert player_stats.dodge_chance > original_dodge
    
    def test_process_enemy_turn(self, combat_system, player_stats, enemy_stats):
        """Test processing an enemy's turn."""
        # Normal attack
        damage, message = combat_system.process_enemy_turn(
            enemy_stats,
            player_stats,
            TerrainType.FOREST
        )
        
        assert message
        # Damage could be 0 if dodged, so we can't assert it's always > 0
        
        # Stunned enemy
        enemy_stats.status_effects.append(
            StatusEffectInstance(
                effect=StatusEffect.STUN,
                duration=2,
                potency=1,
                source=ElementType.EARTH
            )
        )
        
        damage, message = combat_system.process_enemy_turn(
            enemy_stats,
            player_stats,
            TerrainType.FOREST
        )
        
        assert damage == 0  # Stunned enemy can't attack
        assert "stunned" in message.lower()
    
    def test_format_combat_status(self, combat_system, player_stats, enemy_stats):
        """Test formatting combat status."""
        status = combat_system.format_combat_status(
            player_stats,
            enemy_stats,
            "Test Enemy"
        )
        
        assert "COMBAT STATUS" in status
        assert "Test Enemy" in status
        assert str(player_stats.health) in status
        assert str(enemy_stats.health) in status
    
    def test_get_available_elements(self, combat_system, player_stats):
        """Test getting available elements for a player."""
        elements = combat_system.get_available_elements(player_stats)
        
        assert len(elements) > 0
        assert elements[0][0] == ElementType.PHYSICAL  # Highest affinity
        
        # Test with no affinities
        player_stats.elemental_affinities = {element: 0 for element in ElementType}
        elements = combat_system.get_available_elements(player_stats)
        
        assert len(elements) == 1
        assert elements[0][0] == ElementType.PHYSICAL  # Default fallback 
    
    def test_determine_enemy_strategy(self, combat_system, player_stats, enemy_stats):
        """Test determining enemy combat strategy based on type and health."""
        # Test shadow enemy strategy
        enemy_stats.name = "Shadow Stalker"
        enemy_stats.elemental_affinities[ElementType.SHADOW] = 3
        
        # At full health
        action, element = combat_system.determine_enemy_strategy(enemy_stats, player_stats)
        assert action in [CombatAction.ATTACK, CombatAction.DODGE]
        assert element == ElementType.SHADOW  # Should prefer shadow element
        
        # At low health
        enemy_stats.health = int(enemy_stats.max_health * 0.2)  # 20% health
        action, element = combat_system.determine_enemy_strategy(enemy_stats, player_stats)
        assert action in [CombatAction.ATTACK, CombatAction.DODGE]  # Should be more aggressive
        
        # Test construct enemy strategy
        enemy_stats.health = enemy_stats.max_health  # Reset health
        enemy_stats.name = "Crystal Golem"
        enemy_stats.elemental_affinities[ElementType.EARTH] = 3
        enemy_stats.elemental_affinities[ElementType.SHADOW] = 0
        
        # At full health
        action, element = combat_system.determine_enemy_strategy(enemy_stats, player_stats)
        assert element in [ElementType.EARTH, ElementType.PHYSICAL]  # Should prefer earth or physical
        
        # At low health
        enemy_stats.health = int(enemy_stats.max_health * 0.2)  # 20% health
        for _ in range(10):  # Run multiple times due to randomness
            action, element = combat_system.determine_enemy_strategy(enemy_stats, player_stats)
            if action == CombatAction.DEFEND:
                break  # Found the expected behavior
        # Should have a higher chance to defend at low health
        
        # Test spirit enemy strategy
        enemy_stats.health = enemy_stats.max_health  # Reset health
        enemy_stats.name = "Spectral Sentinel"
        enemy_stats.elemental_affinities = {
            ElementType.PHYSICAL: 0,
            ElementType.FIRE: 0,
            ElementType.WATER: 0,
            ElementType.EARTH: 0,
            ElementType.AIR: 2,
            ElementType.SHADOW: 1,
            ElementType.LIGHT: 2
        }
        
        # Spirits should prefer magical elements
        action, element = combat_system.determine_enemy_strategy(enemy_stats, player_stats)
        assert element in [ElementType.AIR, ElementType.SHADOW, ElementType.LIGHT]
        
        # Test with player having status effects
        player_stats.status_effects = [
            StatusEffectInstance(
                effect=StatusEffect.BURN,
                duration=2,
                potency=1,
                source=ElementType.FIRE
            )
        ]
        
        # Some enemies should adapt to player status
        enemy_stats.name = "Shadow Knight"
        action, element = combat_system.determine_enemy_strategy(enemy_stats, player_stats)
        # Strategy should be affected but can't assert exact behavior due to randomness
    
    def test_shadow_centaur_special(self, combat_system, player_stats, enemy_stats):
        """Test Shadow Centaur special abilities."""
        # Set up Shadow Centaur stats
        enemy_stats.name = "Shadow Centaur"
        enemy_stats.max_health = 300
        enemy_stats.health = 300
        enemy_stats.damage = 60
        enemy_stats.elemental_affinities[ElementType.SHADOW] = 3
        
        # Test Phase 1 (75-100% health)
        damage, message, used = combat_system.handle_shadow_centaur_special(
            enemy_stats, player_stats, 3  # Turn 3
        )
        
        if used:
            assert "shadow wave" in message.lower() or "wave of dark energy" in message.lower()
            assert damage > 0
        
        # Test Phase 2 (50-75% health)
        enemy_stats.health = 200  # ~67% health
        
        damage, message, used = combat_system.handle_shadow_centaur_special(
            enemy_stats, player_stats, 2  # Turn 2
        )
        
        if used:
            assert ("shadow strike" in message.lower() or 
                   "void shield" in message.lower() or
                   "supernatural speed" in message.lower() or
                   "swirling vortex" in message.lower())
            # Can't assert exact damage due to randomness
        
        # Test Phase 3 (25-50% health)
        enemy_stats.health = 100  # ~33% health
        
        damage, message, used = combat_system.handle_shadow_centaur_special(
            enemy_stats, player_stats, 2  # Turn 2
        )
        
        if used:
            assert ("shadow nova" in message.lower() or 
                   "life drain" in message.lower() or
                   "nova of dark energy" in message.lower() or
                   "shadowy tendril" in message.lower())
            # Can't assert exact damage due to randomness
        
        # Test Final Phase (<25% health)
        enemy_stats.health = 50  # ~17% health
        
        damage, message, used = combat_system.handle_shadow_centaur_special(
            enemy_stats, player_stats, 1  # Turn 1
        )
        
        assert used  # Should always use ability in final phase
        assert ("shadow explosion" in message.lower() or 
               "void consumption" in message.lower() or
               "reality tear" in message.lower() or
               "unstable" in message.lower() or
               "rift to the void" in message.lower() or
               "fabric of reality" in message.lower())
        assert damage > 0  # Should deal significant damage
    
    def test_is_boss_enemy(self, combat_system):
        """Test boss enemy detection."""
        assert combat_system.is_boss_enemy("Shadow Centaur")
        assert combat_system.is_boss_enemy("The Second Centaur")
        assert combat_system.is_boss_enemy("shadow guardian")
        assert combat_system.is_boss_enemy("Corrupted Druid")
        assert combat_system.is_boss_enemy("Phantom Assassin")
        
        assert not combat_system.is_boss_enemy("Wolf Pack")
        assert not combat_system.is_boss_enemy("Shadow Hound")
        assert not combat_system.is_boss_enemy("Crystal Golem")
    
    def test_start_combat(self, combat_system):
        """Test combat initialization."""
        player_stats = {
            "health": 100,
            "max_health": 100,
            "attack": 20,
            "defense": 5,
            "dodge_chance": 10,
            "critical_chance": 10,
            "elemental_affinities": {
                ElementType.PHYSICAL: 2,
                ElementType.FIRE: 1,
                ElementType.WATER: 1,
                ElementType.EARTH: 0,
                ElementType.AIR: 0,
                ElementType.SHADOW: 0,
                ElementType.LIGHT: 0
            }
        }
        
        # Test with regular enemy
        regular_enemy = {
            "name": "Wolf Pack",
            "health": 60,
            "damage": 15
        }
        
        message = combat_system.start_combat(player_stats, regular_enemy)
        assert "Wolf Pack" in message
        assert combat_system.in_combat
        assert combat_system.turn_count == 0
        assert combat_system.player_combat_stats.health == 100
        assert combat_system.enemy_combat_stats.health == 60
        
        # Test with Shadow Centaur
        shadow_centaur = {
            "name": "Shadow Centaur",
            "health": 300,
            "damage": 60
        }
        
        message = combat_system.start_combat(player_stats, shadow_centaur)
        assert "Shadow Centaur" in message
        assert "final challenge" in message.lower()
        assert combat_system.in_combat
        assert combat_system.enemy_combat_stats.elemental_affinities[ElementType.SHADOW] == 3
        assert combat_system.enemy_combat_stats.critical_chance > 10  # Should be increased
    
    def test_error_handling_and_edge_cases(self, combat_system, player_stats, enemy_stats):
        """Test error handling and edge cases in the combat system."""
        # Test with zero health enemy
        enemy_stats.health = 0
        damage, message = combat_system.process_enemy_turn(
            enemy_stats,
            player_stats,
            TerrainType.FOREST
        )
        assert damage == 0
        assert "defeated" in message.lower()
        
        # Test with zero health player
        player_stats.health = 0
        damage, message = combat_system.process_player_turn(
            player_stats,
            enemy_stats,
            CombatAction.ATTACK,
            ElementType.PHYSICAL,
            TerrainType.FOREST
        )
        assert damage == 0
        assert "defeated" in message.lower()
        
        # Test with missing elemental affinities
        player_stats.health = 100  # Reset health
        player_stats.elemental_affinities = {}  # Empty affinities
        
        # Should not crash and should default to physical
        elements = combat_system.get_available_elements(player_stats)
        assert len(elements) == 1
        assert elements[0][0] == ElementType.PHYSICAL
        
        # Test with invalid element
        damage, message = combat_system.process_player_turn(
            player_stats,
            enemy_stats,
            CombatAction.ATTACK,
            None,  # Invalid element
            TerrainType.FOREST
        )
        # Should default to physical and not crash
        assert "attack" in message.lower()
        
        # Test with multiple status effects
        player_stats.status_effects = [
            StatusEffectInstance(
                effect=StatusEffect.BURN,
                duration=2,
                potency=2,
                source=ElementType.FIRE
            ),
            StatusEffectInstance(
                effect=StatusEffect.CHILL,
                duration=3,
                potency=1,
                source=ElementType.WATER
            ),
            StatusEffectInstance(
                effect=StatusEffect.STUN,
                duration=1,
                potency=1,
                source=ElementType.EARTH
            )
        ]
        
        # Apply status effects
        damage, messages = combat_system.apply_status_effects(player_stats)
        
        # Should handle multiple effects correctly
        assert damage > 0  # Burn should deal damage
        assert len(messages) >= 2  # Should have messages for each effect
        assert len(player_stats.status_effects) == 2  # Stun should expire
        
        # Test Shadow Centaur special with invalid turn count
        enemy_stats.name = "Shadow Centaur"
        enemy_stats.health = 50  # Final phase
        enemy_stats.max_health = 300
        
        damage, message, used = combat_system.handle_shadow_centaur_special(
            enemy_stats,
            player_stats,
            -1  # Invalid turn count
        )
        
        # Should still work in final phase regardless of turn count
        assert used
        assert damage > 0
        
        # Test with extreme values
        player_stats.damage = 1000  # Very high damage
        result = combat_system.calculate_damage(
            player_stats,
            enemy_stats,
            ElementType.PHYSICAL,
            TerrainType.FOREST
        )
        
        # Should handle extreme values without issues
        assert result.damage_dealt > 0
        
        # Test with negative defense (should be handled gracefully)
        enemy_stats.defense = -10
        result = combat_system.calculate_damage(
            player_stats,
            enemy_stats,
            ElementType.PHYSICAL,
            TerrainType.FOREST
        )
        
        # Should handle negative defense without crashing
        assert result.damage_dealt > 0 