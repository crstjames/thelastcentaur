"""
Test file for the path system.

This file contains tests for the path system, including path selection,
progression, and ability usage.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import only the models to avoid circular imports
from src.engine.core.models import PathType

# We'll patch the other imports
class TestPathSystem(unittest.TestCase):
    """Test cases for the path system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Import here to avoid circular imports
        from src.engine.core.path_system import PathSystem
        
        # Create a mock QuestSystem
        self.quest_system = MagicMock()
        self.quest_system.start_quest.return_value = (True, "Quest started successfully")
        
        # Create the PathSystem with the mock
        self.path_system = PathSystem(self.quest_system)
    
    def test_path_selection(self):
        """Test path selection functionality."""
        # Test selecting the warrior path
        message = self.path_system.select_path(PathType.WARRIOR)
        self.assertIn("path of the Warrior", message)
        self.assertEqual(self.path_system.path_selection.selected_path, PathType.WARRIOR)
        
        # Test getting path description
        description = self.path_system.get_path_description(PathType.WARRIOR)
        self.assertIn("combat prowess", description)
        
        # Test getting path progress
        progress = self.path_system.get_path_progress()
        self.assertIn("Warrior Path - Level 1", progress)
    
    def test_path_affinity(self):
        """Test path affinity tracking."""
        # Record combat actions
        self.path_system.record_combat_action("direct_attack", "enemy", True)
        self.path_system.record_combat_action("stealth_attack", "enemy", True)
        self.path_system.record_combat_action("spell_cast", "enemy", True)
        
        # Check affinities
        affinities = self.path_system.path_selection.path_affinity
        self.assertAlmostEqual(affinities[PathType.WARRIOR], 0.1, places=5)
        self.assertAlmostEqual(affinities[PathType.STEALTH], 0.1, places=5)
        self.assertAlmostEqual(affinities[PathType.MYSTIC], 0.1, places=5)
        
        # Record exploration actions
        self.path_system.record_exploration_action("search_for_enemies", "forest")
        self.path_system.record_exploration_action("search_for_hidden", "cave")
        self.path_system.record_exploration_action("search_for_knowledge", "library")
        
        # Check updated affinities
        affinities = self.path_system.path_selection.path_affinity
        self.assertAlmostEqual(affinities[PathType.WARRIOR], 0.15, places=5)
        self.assertAlmostEqual(affinities[PathType.STEALTH], 0.15, places=5)
        self.assertAlmostEqual(affinities[PathType.MYSTIC], 0.15, places=5)
        
        # Record dialogue choices
        self.path_system.record_dialogue_choice("guard", "aggressive")
        self.path_system.record_dialogue_choice("merchant", "deceptive")
        self.path_system.record_dialogue_choice("sage", "inquisitive")
        
        # Check final affinities
        affinities = self.path_system.path_selection.path_affinity
        self.assertAlmostEqual(affinities[PathType.WARRIOR], 0.2, places=5)
        self.assertAlmostEqual(affinities[PathType.STEALTH], 0.2, places=5)
        self.assertAlmostEqual(affinities[PathType.MYSTIC], 0.2, places=5)
        
        # Test getting suggested path
        path_type, description = self.path_system.get_suggested_path()
        self.assertIn(path_type, [PathType.WARRIOR, PathType.STEALTH, PathType.MYSTIC])
        self.assertIn("Your actions suggest", description)
    
    def test_path_experience(self):
        """Test path experience and progression."""
        # Select a path
        self.path_system.select_path(PathType.WARRIOR)
        
        # Gain experience
        levels, abilities = self.path_system.gain_path_experience(100)
        self.assertEqual(levels, 1)  # Should level up once
        self.assertTrue(len(abilities) > 0)  # Should unlock at least one ability
        
        # Check progress
        progress = self.path_system.get_path_progress()
        self.assertIn("Warrior Path - Level 2", progress)
        self.assertIn("Experience: 100", progress)
    
    def test_ability_usage(self):
        """Test ability usage."""
        # Select a path
        self.path_system.select_path(PathType.WARRIOR)
        
        # Gain enough experience to unlock abilities
        self.path_system.gain_path_experience(100)
        
        # Get available abilities
        abilities = self.path_system.path_selection.get_available_abilities()
        self.assertTrue(len(abilities) > 0)
        
        # Try to use an ability (should fail due to missing items/stamina)
        ability_id = list(abilities.keys())[0]
        can_use, reason = self.path_system.can_use_ability(ability_id)
        self.assertFalse(can_use)
        
        # Try to use ability with proper parameters
        success, message, effects = self.path_system.use_ability(
            ability_id,
            player_items=["Warrior's Sword"],
            player_stamina=100,
            base_damage=10,
            weapon_damage=5
        )
        
        # This might still fail if the ability has specific requirements
        if success:
            self.assertIn("You use", message)
            self.assertIn("name", effects)
            self.assertIn("description", effects)
        else:
            self.assertIn("need", reason.lower())
    
    def test_path_status(self):
        """Test getting path status."""
        # Select a path and gain experience
        self.path_system.select_path(PathType.WARRIOR)
        self.path_system.gain_path_experience(50)
        
        # Get path status
        status = self.path_system.get_path_status()
        
        # Check status fields
        self.assertEqual(status["selected_path"], PathType.WARRIOR)
        self.assertEqual(status["warrior"]["level"], 1)
        self.assertEqual(status["warrior"]["experience"], 50)
        self.assertTrue("abilities" in status["warrior"])
        self.assertTrue("affinity" in status["warrior"])


if __name__ == "__main__":
    unittest.main() 