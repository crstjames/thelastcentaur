"""
Test script for Diverse Combat Scenarios in The Last Centaur.

This test verifies that combat is varied and engaging:
1. Different enemy types with unique abilities
2. Environmental effects that influence combat
3. Special combat scenarios (ambushes, rituals)
4. Scaling difficulty throughout the game
5. Varied combat rewards and consequences
"""

import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.core.models import Direction, StoryArea, ElementType, CombatAction, StatusEffect
from src.engine.core.player import Player
from src.engine.core.map_system import MapManager
from src.engine.core.command_parser import CommandParser
from src.engine.core.combat_system import CombatSystem


class TestCombatDiversity:
    """Test suite for diverse combat scenarios in the game."""
    
    @pytest.fixture
    def game_setup(self):
        """Set up the game systems for testing combat diversity."""
        # Initialize game systems
        map_system = MapManager()
        player = Player(map_system, player_id="test_combat", player_name="Test Fighter")
        command_parser = CommandParser(player)
        combat_system = CombatSystem()
        
        # Add some combat items to player inventory
        player.add_item_to_inventory("steel_sword")
        player.add_item_to_inventory("mystic_amulet")
        player.add_item_to_inventory("fire_essence")
        
        # Helper function to execute commands
        def execute(command: str) -> str:
            """Execute a command and return the response."""
            response = command_parser.parse_command(command)
            print(f"\n> {command}")
            print(response)
            return response
            
        return map_system, player, command_parser, execute, combat_system
    
    def test_enemy_type_diversity(self, game_setup):
        """Test different enemy types with unique abilities."""
        map_system, player, _, execute, combat_system = game_setup
        
        # Test wolf pack - fast, pack tactics
        map_system.set_current_area(StoryArea.TRIALS_PATH)
        wolf_encounter = execute("look")
        assert "wolf pack" in wolf_encounter.lower()
        
        # Initiate combat
        wolf_fight = execute("engage wolf pack")
        assert "wolves circle around you" in wolf_fight.lower()
        assert "pack tactics" in wolf_fight.lower()
        
        # Wolf special ability - flanking attack
        wolf_ability = execute("attack leader")
        assert "flanking maneuver" in wolf_ability.lower()
        
        # Test shadow wraith - elemental vulnerabilities
        map_system.set_current_area(StoryArea.SHADOW_DOMAIN)
        wraith_encounter = execute("look")
        assert "shadow wraith" in wraith_encounter.lower()
        
        # Initiate combat
        wraith_fight = execute("engage shadow wraith")
        assert "ethereal form" in wraith_fight.lower()
        
        # Ineffective physical attack
        physical_attack = execute("attack with steel_sword")
        assert "passes through its form" in physical_attack.lower()
        
        # Effective elemental attack
        elemental_attack = execute("use fire_essence on wraith")
        assert "light burns the shadows" in elemental_attack.lower()
        assert "wraith recoils" in elemental_attack.lower()
        
        # Test ancient guardian - armor and pattern attacks
        map_system.set_current_area(StoryArea.GUARDIAN_OVERLOOK)
        guardian_encounter = execute("look")
        assert "ancient guardian" in guardian_encounter.lower()
        
        # Initiate combat
        guardian_fight = execute("engage guardian")
        assert "animated armor" in guardian_fight.lower()
        assert "magical runes" in guardian_fight.lower()
        
        # Pattern-based attack sequence
        pattern_attack = execute("observe pattern")
        assert "attack sequence" in pattern_attack.lower()
        
        counter_attack = execute("counter rune sequence")
        assert "guardian staggers" in counter_attack.lower()

    def test_environmental_combat(self, game_setup):
        """Test how environment affects combat mechanics."""
        map_system, player, _, execute, _ = game_setup
        
        # Crystal Pond - reflective damage
        map_system.set_current_area(StoryArea.CRYSTAL_POND)
        pond_encounter = execute("engage crystal elemental")
        assert "reflective surface" in pond_encounter.lower()
        
        # Reflected attack
        reflect_attack = execute("use powerful attack")
        assert "amplified by crystals" in reflect_attack.lower()
        assert "reflected back" in reflect_attack.lower()
        
        # Shadow Domain - reduced visibility
        map_system.set_current_area(StoryArea.SHADOW_DOMAIN)
        shadow_combat = execute("engage shadow stalker")
        assert "difficult to see" in shadow_combat.lower()
        
        # Attempt normal attack
        blind_attack = execute("attack")
        assert "miss" in blind_attack.lower() or "reduced accuracy" in blind_attack.lower()
        
        # Use environment to advantage
        adapt_attack = execute("use mystic_amulet for light")
        assert "illuminates" in adapt_attack.lower()
        assert "stalker becomes visible" in adapt_attack.lower()
        
        # Meditation Circle - harmonizing energy
        map_system.set_current_area(StoryArea.MEDITATION_CIRCLE)
        circle_combat = execute("engage corrupted spirit")
        assert "harmonizing energy" in circle_combat.lower()
        
        # Use environment for healing
        healing = execute("channel circle energy")
        assert "rejuvenating" in healing.lower()
        assert "health restored" in healing.lower()

    def test_special_combat_scenarios(self, game_setup):
        """Test unique combat scenarios with special mechanics."""
        map_system, player, _, execute, _ = game_setup
        
        # Ambush scenario
        map_system.set_current_area(StoryArea.MOUNTAIN_BASE)
        execute("look")  # Normal look doesn't show enemies
        
        # Trigger ambush
        ambush = execute("take narrow path")
        assert "ambushed" in ambush.lower()
        assert "no time to prepare" in ambush.lower()
        
        # Escape ambush
        escape = execute("throw fire_essence")
        assert "distraction" in escape.lower()
        assert "opportunity to escape" in escape.lower()
        
        # Ritual combat
        map_system.set_current_area(StoryArea.HONOR_SHRINE)
        ritual = execute("engage in ritual combat")
        assert "ceremonial" in ritual.lower()
        assert "test of honor" in ritual.lower()
        
        # Follow ritual rules
        ritual_strike = execute("perform honorable strike")
        assert "traditional form" in ritual_strike.lower()
        
        # Breaking ritual rules
        break_rules = execute("use underhanded tactic")
        assert "dishonorable" in break_rules.lower()
        assert "ritual upset" in break_rules.lower()
        
        # Mounted combat
        map_system.set_current_area(StoryArea.CROSSROADS)
        mounted = execute("engage mounted patrol")
        assert "horseback" in mounted.lower()
        assert "charging" in mounted.lower()
        
        # Counter mounted attack
        counter = execute("dodge and strike at mount")
        assert "horses stumble" in counter.lower()
        assert "rider vulnerable" in counter.lower()

    def test_difficulty_scaling(self, game_setup):
        """Test that combat difficulty scales throughout the game."""
        map_system, player, _, execute, _ = game_setup
        
        # Early game enemy - simple mechanics
        map_system.set_current_area(StoryArea.AWAKENING_WOODS)
        early_combat = execute("engage forest wolf")
        assert "simple attack pattern" in early_combat.lower()
        
        # Early victory should be straightforward
        early_win = execute("attack with steel_sword")
        assert "defeat" in early_win.lower()
        
        # Mid game enemy - more complex
        map_system.set_current_area(StoryArea.CRYSTAL_POND)
        mid_combat = execute("engage crystal guardian")
        assert "elemental resistance" in mid_combat.lower()
        assert "pattern of attacks" in mid_combat.lower()
        
        # Mid game requires strategy
        strategy = execute("use elemental weakness")
        assert "effective" in strategy.lower()
        
        # Late game enemy - complex mechanics
        map_system.set_current_area(StoryArea.GUARDIAN_OVERLOOK)
        late_combat = execute("engage ancient sentinel")
        assert "multiple phases" in late_combat.lower()
        assert "adaptive defenses" in late_combat.lower()
        
        # Simple attacks ineffective
        simple_attack = execute("attack with steel_sword")
        assert "barely scratches" in simple_attack.lower()
        
        # Complex strategy required
        complex_strategy = execute("use combined elemental attack with pattern disruption")
        assert "sentinel weakens" in complex_strategy.lower()

    def test_combat_rewards_and_consequences(self, game_setup):
        """Test varied rewards and consequences from combat."""
        map_system, player, _, execute, _ = game_setup
        
        # Standard combat with item reward
        map_system.set_current_area(StoryArea.TRIALS_PATH)
        standard_fight = execute("engage forest guardian")
        execute("defeat guardian")  # Skip combat for test
        
        # Check for item reward
        reward = execute("search guardian")
        assert "found" in reward.lower()
        assert "item" in reward.lower()
        
        # Combat with skill reward
        map_system.set_current_area(StoryArea.TRAINING_GROUNDS)
        skill_fight = execute("engage master warrior")
        execute("defeat warrior honorably")  # Skip combat for test
        
        # Check for skill reward
        skill_reward = execute("speak with defeated warrior")
        assert "teaches you" in skill_reward.lower()
        assert "new technique" in skill_reward.lower()
        
        # Combat with narrative consequences
        map_system.set_current_area(StoryArea.SHADOW_DOMAIN)
        narrative_fight = execute("engage shadow messenger")
        
        # Different outcome based on combat approach
        execute("defeat messenger")  # Skip combat for test
        
        # Merciful approach
        mercy = execute("spare messenger")
        assert "information" in mercy.lower()
        assert "shadow centaur's weakness" in mercy.lower()
        
        # Reset and try ruthless approach
        map_system.set_current_area(StoryArea.SHADOW_DOMAIN)
        execute("engage shadow messenger")
        execute("defeat messenger")  # Skip combat for test
        
        ruthless = execute("finish messenger")
        assert "dark power" in ruthless.lower()
        assert "shadow essence absorbed" in ruthless.lower()
        
        # Different narratives should result
        assert mercy != ruthless 