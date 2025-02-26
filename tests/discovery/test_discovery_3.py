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
def test_process_interaction_with_effects(discovery_system):
    """Test that the process_interaction method returns effects correctly."""
    # Create a mock player
    mock_player = MagicMock()
    mock_player.state.current_tile.terrain_type = "FOREST"
    
    # Process an interaction
    response, effects = discovery_system.process_interaction(
        mock_player,
        InteractionType.GATHER.value,
        "berries bush"
    )
    
    # Check that the response and effects are not empty
    assert response
    assert effects

def test_process_interaction_with_no_effects(discovery_system):
    """Test that the process_interaction method returns no effects when no change occurs."""
    # Create a mock player
    mock_player = MagicMock()
    mock_player.state.current_tile.terrain_type = "FOREST"
    
    # Temporarily remove the test_berries discovery to ensure no effects
    test_berries = None
    if "test_berries" in discovery_system.discoveries:
        test_berries = discovery_system.discoveries["test_berries"]
        del discovery_system.discoveries["test_berries"]
    
    try:
        # Process an interaction
        response, effects = discovery_system.process_interaction(
            mock_player,
            InteractionType.GATHER.value,
            "berries bush"
        )
        
        # Check that the response and effects are empty
        assert not response
        assert not effects
    finally:
        # Restore the test_berries discovery
        if test_berries:
            discovery_system.discoveries["test_berries"] = test_berries

def test_process_interaction_with_invalid_interaction(discovery_system):
    """Test that the process_interaction method returns no effects when an invalid interaction is provided."""
    # Create a mock player
    mock_player = MagicMock()
    mock_player.state.current_tile.terrain_type = "FOREST"
    
    # Process an invalid interaction
    response, effects = discovery_system.process_interaction(
        mock_player,
        "invalid_interaction",
        "berries bush"
    )
    
    # Check that the response and effects are empty
    assert not response
    assert not effects

def test_process_interaction_with_invalid_text(discovery_system):
    """Test that the process_interaction method returns no effects when an invalid text is provided."""
    # Create a mock player
    mock_player = MagicMock()
    mock_player.state.current_tile.terrain_type = "FOREST"
    
    # Process an invalid text
    response, effects = discovery_system.process_interaction(
        mock_player,
        InteractionType.GATHER.value,
        "invalid text"
    )
    
    # Check that the response and effects are empty
    assert not response
    assert not effects

def test_process_interaction_with_empty_text(discovery_system):
    """Test that the process_interaction method returns no effects when an empty text is provided."""
    # Create a mock player
    mock_player = MagicMock()
    mock_player.state.current_tile.terrain_type = "FOREST"
    
    # Process an empty text
    response, effects = discovery_system.process_interaction(
        mock_player,
        InteractionType.GATHER.value,
        ""
    )
    
    # Check that the response and effects are empty
    assert not response
    assert not effects

