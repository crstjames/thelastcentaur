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
def test_process_interaction_with_no_player(discovery_system):
    """Test that the process_interaction method returns no effects when no player is provided."""
    # Process an interaction with no player
    response, effects = discovery_system.process_interaction(
        None,
        InteractionType.GATHER.value,
        "berries bush"
    )
    
    # Check that the response and effects are empty
    assert not response
    assert not effects

def test_process_interaction_with_no_tile(discovery_system):
    """Test that the process_interaction method returns no effects when no tile is provided."""
    # Create a mock player with no tile
    mock_player = MagicMock()
    mock_player.state = MagicMock()
    mock_player.state.current_tile = None
    
    # Process an interaction with no tile
    response, effects = discovery_system.process_interaction(
        mock_player,
        InteractionType.GATHER.value,
        "berries bush"
    )
    
    # Check that the response and effects are empty
    assert not response
    assert not effects

def test_process_interaction_with_no_terrain_type(discovery_system, mock_player):
    """Test that the process_interaction method returns no effects when no terrain type is provided."""
    # Process an interaction with no terrain type
    response, effects = discovery_system.process_interaction(
        mock_player,
        InteractionType.GATHER.value,
        "berries bush"
        )
    
    # Check that the response and effects are empty
    assert not response
    assert not effects

def test_process_interaction_with_no_interaction_type(discovery_system, mock_player):
    """Test that the process_interaction method returns no effects when no interaction type is provided."""
    # Process an interaction with no interaction type
    response, effects = discovery_system.process_interaction(
        mock_player,
        None,
        "berries bush"
    )
    
    # Check that the response and effects are empty
    assert not response
    assert not effects

def test_process_interaction_with_no_text(discovery_system, mock_player):
    """Test that the process_interaction method returns no effects when no text is provided."""
    # Process an interaction with no text
    response, effects = discovery_system.process_interaction(
        mock_player,
        InteractionType.GATHER.value,
        ""
    )
    
    # Check that the response and effects are empty
    assert not response
    assert not effects

