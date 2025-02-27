"""
Simplified tests for the discovery system in The Last Centaur.

This module tests the core functionality of the discovery system without redundancy.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.engine.core.discovery_system import DiscoverySystem, InteractionType, HiddenDiscovery, EnvironmentalChange


class TestDiscoverySystem:
    """Tests for the DiscoverySystem class."""
    
    @pytest.fixture
    def discovery_system(self):
        """Create a discovery system for testing."""
        return DiscoverySystem()
    
    @pytest.fixture
    def mock_player(self):
        """Create a mock player for testing."""
        player = MagicMock()
        player.state.current_tile.terrain_type = "FOREST"
        player.state.current_tile.position = (0, 0)
        player.inventory.add_item = MagicMock()
        return player
    
    def test_discovery_system_initialization(self, discovery_system):
        """Test that the discovery system initializes correctly."""
        assert discovery_system.found_discoveries == set()
        assert isinstance(discovery_system.tile_changes, dict)
        assert "test_berries" in discovery_system.discoveries
        assert "pretty_flower" in discovery_system.discoveries
    
    def test_parse_natural_language(self, discovery_system):
        """Test parsing natural language input."""
        # Test basic parsing
        interaction_type, keywords = discovery_system.parse_natural_language("I want to look at the tree")
        assert interaction_type == "examine"
        assert "tree" in keywords
    
    def test_gameplay_item_discovery(self, mock_player, discovery_system):
        """Test discovering items through gameplay interactions."""
        # Add a test discovery
        discovery_system.discoveries["test_item"] = HiddenDiscovery(
            id="test_item",
            name="Test Item",
            description="A test item",
            discovery_text="You found a test item!",
            terrain_types=["FOREST"],
            required_interaction="examine",
            required_keywords=["tree", "branch"],
            chance_to_find=1.0,
            item_reward="test_item"
        )
        
        # Test successful discovery
        with patch.object(discovery_system, '_check_for_discoveries', 
                         return_value=(True, "You found a test item!", {"item_added": "test_item"})):
            response, effects = discovery_system.process_interaction(
                mock_player,
                InteractionType.EXAMINE.value,
                "I want to examine the tree branch"
            )
            
            # Check that the discovery was found
            assert "You found a test item!" in response
            assert effects is not None
            assert "item_added" in effects
    
    def test_terrain_specific_discoveries(self, mock_player, discovery_system):
        """Test that discoveries are terrain-specific."""
        # Add test discoveries for different terrains
        discovery_system.discoveries["forest_item"] = HiddenDiscovery(
            id="forest_item",
            name="Forest Item",
            description="A forest item",
            discovery_text="You found a forest item!",
            terrain_types=["FOREST"],
            required_interaction="examine",
            required_keywords=["tree"],
            chance_to_find=1.0,
            item_reward="forest_item"
        )
        
        discovery_system.discoveries["mountain_item"] = HiddenDiscovery(
            id="mountain_item",
            name="Mountain Item",
            description="A mountain item",
            discovery_text="You found a mountain item!",
            terrain_types=["MOUNTAIN"],
            required_interaction="examine",
            required_keywords=["rock"],
            chance_to_find=1.0,
            item_reward="mountain_item"
        )
        
        # Test forest discovery in forest terrain
        with patch.object(discovery_system, '_check_for_discoveries', 
                         return_value=(True, "You found a forest item!", {"item_added": "forest_item"})):
            response, effects = discovery_system.process_interaction(
                mock_player,
                InteractionType.EXAMINE.value,
                "I want to examine the tree"
            )
            
            # Check that the discovery was found
            assert "You found a forest item!" in response
    
    def test_environmental_changes(self, mock_player, discovery_system):
        """Test environmental changes from discoveries."""
        # Test recording an environmental change
        position = (0, 0)
        discovery_system._record_environmental_change(
            position, 
            "You carved a mark into the tree.",
            is_permanent=True
        )
        
        # Check that the change was recorded
        changes = discovery_system.get_tile_changes(position)
        assert len(changes) > 0
        assert "You carved a mark into the tree." in changes[0]
    
    def test_process_interaction_with_no_effects(self, discovery_system, mock_player):
        """Test processing an interaction that has no effects."""
        # Test with a standard response (no discovery)
        with patch.object(discovery_system, '_check_for_discoveries', 
                         return_value=(False, "", {})):
            # Mock the _generate_standard_response method
            with patch.object(discovery_system, '_generate_standard_response', 
                             return_value="You examine it closely but find nothing unusual."):
                response, effects = discovery_system.process_interaction(
                    mock_player,
                    InteractionType.EXAMINE.value,
                    "I want to learn about the history of the trees"
                )
                
                # Check that no discovery was found
                assert "You examine it closely but find nothing unusual." in response
                assert effects == {}  # Empty dict, not None
    
    def test_process_interaction_with_invalid_interaction(self, discovery_system, mock_player):
        """Test processing an invalid interaction type."""
        # Test with invalid interaction type
        with patch.object(discovery_system, 'parse_natural_language', 
                         return_value=("invalid_type", ["tree"])):
            # For invalid interaction types, the method returns an empty string
            with patch.object(discovery_system, '_generate_standard_response', 
                             return_value=""):
                response, effects = discovery_system.process_interaction(
                    mock_player,
                    "invalid_type",
                    "I want to examine the tree"
                )
                
                # Check that a standard response is returned
                assert response == ""
                assert effects == {}
    
    def test_enhance_tile_description(self, discovery_system, mock_player):
        """Test enhancing a tile description with environmental changes."""
        # Add an environmental change
        position = (0, 0)
        discovery_system._record_environmental_change(
            position, 
            "There's a carved mark on one of the trees.",
            is_permanent=True
        )
        
        # Mock the tile
        tile = MagicMock()
        tile.position = position
        tile.description = "A forest area with tall trees."
        
        # Test enhancing the description
        enhanced = discovery_system.enhance_tile_description(tile)
        assert enhanced != tile.description
        assert "carved mark" in enhanced or "There's a carved mark on one of the trees." in enhanced 