import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.engine.core.discovery_system import DiscoverySystem, HiddenDiscovery, InteractionType
from src.engine.core.models import TileState, TerrainType, StoryArea
from src.engine.core.player import Player

# Test for discovery system functionality
def test_discovery_system_initialization(discovery_system):
    """Test that the discovery system initializes correctly."""
    assert isinstance(discovery_system, DiscoverySystem)
    assert "test_berries" in discovery_system.discoveries
    assert "pretty_flower" in discovery_system.discoveries

def test_parse_natural_language(discovery_system):
    """Test that the discovery system can parse natural language commands."""
    # Test gather interaction
    interaction_type, cleaned_text = discovery_system.parse_natural_language("gather berries from the bush")
    assert interaction_type == InteractionType.GATHER.value
    assert cleaned_text == "berries bush"
    
    # Test examine interaction
    interaction_type, cleaned_text = discovery_system.parse_natural_language("look at the flower")
    assert interaction_type == InteractionType.EXAMINE.value
    assert cleaned_text == "flower"
    
    # Test search interaction (should map to examine)
    interaction_type, cleaned_text = discovery_system.parse_natural_language("search for hidden items")
    assert interaction_type == InteractionType.EXAMINE.value
    assert cleaned_text == "hidden items"
    
    # Test touch interaction
    interaction_type, cleaned_text = discovery_system.parse_natural_language("touch the crystal")
    assert interaction_type == InteractionType.TOUCH.value
    assert cleaned_text == "crystal"
    
    # Test custom interaction (not matching any pattern)
    interaction_type, cleaned_text = discovery_system.parse_natural_language("dance around wildly")
    assert interaction_type == InteractionType.CUSTOM.value
    assert cleaned_text == "dance around wildly"

def test_gameplay_item_discovery(mock_player, discovery_system):
    """Test that gameplay items can be discovered."""
    # Set up the player's current tile
    mock_player.state.current_tile.terrain_type = "FOREST"
    
    # Process a gather interaction for berries
    response, effects = discovery_system.process_interaction(
        mock_player, 
        InteractionType.GATHER.value, 
        "berries bush"
    )
    
    # Check the response and effects
    assert "You found some test berries!" in response
    assert effects["item_added"] == "test_berries"

def test_roleplay_item_discovery(mock_player, discovery_system):
    """Test that roleplay items can be discovered."""
    # Set up the player's current tile
    mock_player.state.current_tile.terrain_type = "FOREST"
    
    # Process an examine interaction for flowers
    response, effects = discovery_system.process_interaction(
        mock_player, 
        InteractionType.EXAMINE.value, 
        "flower"
    )
    
    # Check the response and effects
    assert "You found a pretty flower!" in response
    assert effects["item_added"] == "pretty_flower"

def test_terrain_specific_discoveries(mock_player, discovery_system):
    """Test that discoveries are terrain-specific."""
    # Set up the player's current tile as MOUNTAIN
    mock_player.state.current_tile.terrain_type = "MOUNTAIN"
    
    # Try to find berries (should fail in mountains)
    response, effects = discovery_system.process_interaction(
        mock_player,
        InteractionType.GATHER.value,
        "berries bush"
    )
    
    # Check that nothing was found (either empty response or "don't find anything" message)
    assert not response or "don't find anything" in response
    assert not effects or not effects.get("item_added")

