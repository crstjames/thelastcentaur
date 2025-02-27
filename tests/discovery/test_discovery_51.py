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
def test_roleplay_item_discovery(mock_player, discovery_system):
    """Test discovering a roleplay item."""
    # Process an interaction that should find the pretty flower
    response, effects = discovery_system.process_interaction(
        mock_player,
        "gather",
        "I want to pick some flowers"
    )
    
    # Check that the discovery was found
    assert "You pick a beautiful flower" in response
    assert "pretty_flower" in discovery_system.found_discoveries
    
    # Check that the item was added to inventory
    assert "pretty_flower" in mock_player.state.inventory
    assert effects.get("item_added") == "pretty_flower"

def test_natural_language_parsing(mock_player, discovery_system):
    """Test the natural language parsing functionality."""
    # Test various natural language inputs
    test_cases = [
        ("look at the tree", InteractionType.EXAMINE.value),
        ("examine the rock", InteractionType.EXAMINE.value),
        ("touch the statue", InteractionType.TOUCH.value),
        ("feel the bark", InteractionType.TOUCH.value),
        ("gather some berries", InteractionType.GATHER.value),
        ("pick up the stick", InteractionType.GATHER.value),
        ("break the branch", InteractionType.BREAK.value),
        ("smash the pot", InteractionType.BREAK.value),
        ("move the rock", InteractionType.MOVE.value),
        ("push the boulder", InteractionType.MOVE.value),
        ("climb the tree", InteractionType.CLIMB.value),
        ("dig in the dirt", InteractionType.DIG.value),
        ("listen to the birds", InteractionType.LISTEN.value),
        ("smell the flowers", InteractionType.SMELL.value),
        ("taste the berry", InteractionType.TASTE.value),
        ("do a dance", InteractionType.CUSTOM.value)  # Should default to custom
    ]
    
    for input_text, expected_type in test_cases:
        interaction_type, _ = discovery_system.parse_natural_language(input_text)
        assert interaction_type == expected_type, f"Failed for input: {input_text}"

def test_custom_roleplay_interaction(mock_player, discovery_system):
    """Test a completely custom roleplay interaction."""
    # Create a special discovery for custom actions
    discovery_system.discoveries["dance_discovery"] = HiddenDiscovery(
        id="dance_discovery",
        name="Dance Discovery",
        description="Something discovered by dancing.",
        discovery_text="As you dance, you notice a hidden pattern in the forest floor!",
        terrain_types=["FOREST"],
        required_interaction="custom",
        required_keywords=["dance", "dancing"],
        chance_to_find=1.0,
        item_reward="dance_token"
    )
    
    # Process a custom interaction
    response, effects = discovery_system.process_interaction(
        mock_player,
        "custom",
        "I want to dance around in circles"
    )
    
    # Check that the discovery was found
    assert "As you dance" in response
    assert "dance_discovery" in discovery_system.found_discoveries
    
    # Check that the item was added to inventory
    assert "dance_token" in mock_player.state.inventory

def test_multiple_roleplay_items(mock_player, discovery_system):
    """Test gathering multiple roleplay items."""
    # Add more roleplay items
    discovery_system.discoveries["smooth_stone"] = HiddenDiscovery(
        id="smooth_stone",
        name="Smooth Stone",
        description="A perfectly smooth stone.",
        discovery_text="You find a perfectly smooth stone. It feels nice in your hand.",
        terrain_types=["FOREST", "MOUNTAIN"],
        required_interaction="gather",
        required_keywords=["stone", "rock"],
        chance_to_find=1.0,
        item_reward="smooth_stone",
        unique=False
    )
    
    discovery_system.discoveries["fallen_leaf"] = HiddenDiscovery(
        id="fallen_leaf",
        name="Colorful Leaf",
        description="A beautifully colored leaf.",
        discovery_text="You pick up a leaf with stunning autumn colors.",
        terrain_types=["FOREST"],
        required_interaction="gather",
        required_keywords=["leaf", "leaves"],
        chance_to_find=1.0,
        item_reward="colorful_leaf",
        unique=False
    )
    
    # Gather the first item
    response1, _ = discovery_system.process_interaction(
        mock_player,
        "gather",
        "I want to gather a smooth stone"
    )
    
    # Gather the second item
    response2, _ = discovery_system.process_interaction(
        mock_player,
        "gather",
        "I want to pick up a colorful leaf"
    )
    
    # Check that both items were found
    assert "smooth_stone" in mock_player.state.inventory
    assert "colorful_leaf" in mock_player.state.inventory
    
    # Check that both discoveries were recorded
    assert "smooth_stone" in discovery_system.found_discoveries
    assert "fallen_leaf" in discovery_system.found_discoveries

def test_environmental_changes(mock_player, discovery_system):
    """Test that environmental changes are recorded."""
    # Process an interaction that should create an environmental change
    discovery_system.process_interaction(
        mock_player,
        "break",
        "I want to break a branch off the tree"
    )
    
    # Check that the change was recorded
    changes = discovery_system.get_tile_changes((5, 5))
    assert len(changes) == 1
    assert "break" in changes[0].lower()
    
    # Check that the change affects the tile description
    enhanced_desc = discovery_system.enhance_tile_description(mock_player.state.current_tile)
    assert enhanced_desc != mock_player.state.current_tile.description

if __name__ == '__main__':
    unittest.main() 