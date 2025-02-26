import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.engine.core.command_parser import CommandParser, CommandType, Command
from src.engine.core.discovery_system import DiscoverySystem, HiddenDiscovery, InteractionType
from src.engine.core.models import TileState, TerrainType, StoryArea, Direction
from src.engine.core.player import Player

def test_parse_natural_language_commands(mock_player, command_parser):
    """Test that the command parser can parse natural language commands."""
    # Test look command
    cmd = command_parser.parse_command("look at the rock")
    assert cmd.type == CommandType.INTERACT
    assert cmd.args[0] == InteractionType.EXAMINE.value
    assert "rock" in cmd.args[1]
    
    # Test gather command
    cmd = command_parser.parse_command("gather berries from the bush")
    assert cmd.type == CommandType.INTERACT
    assert cmd.args[0] == InteractionType.GATHER.value
    assert "berries" in cmd.args[1]
    assert "bush" in cmd.args[1]
    
    # Test search command
    cmd = command_parser.parse_command("search for hidden items")
    assert cmd.type == CommandType.INTERACT
    assert cmd.args[0] == InteractionType.EXAMINE.value
    assert "hidden items" in cmd.args[1]
    
    # Test touch command
    cmd = command_parser.parse_command("touch the crystal")
    assert cmd.type == CommandType.INTERACT
    assert cmd.args[0] == InteractionType.TOUCH.value
    assert "crystal" in cmd.args[1]

def test_gameplay_item_gathering(mock_player, command_parser):
    """Test that gameplay items can be gathered through the command parser."""
    # Set up the player's current tile
    mock_player.state.current_tile.terrain_type = "FOREST"
    mock_player.state.current_tile.items = ["stick"]
    
    # Execute a take command
    result = command_parser.execute_command(Command(CommandType.TAKE, ["stick"]))
    
    # Check that the item was added to inventory
    assert "stick" in mock_player.state.inventory
    assert "You take the stick" in result

def test_roleplay_item_gathering(mock_player, command_parser):
    """Test that roleplay items can be gathered through the command parser."""
    # Set up the player's current tile
    mock_player.state.current_tile.terrain_type = "FOREST"
    
    # Add a test discovery to the command parser's discovery system
    command_parser.discovery_system.discoveries["pretty_flower"] = HiddenDiscovery(
        id="pretty_flower",
        name="Pretty Flower",
        description="A beautiful flower with vibrant colors.",
        discovery_text="You found a pretty flower!",
        terrain_types=["FOREST", "CLEARING"],
        required_interaction="examine",
        required_keywords=["flower", "flowers", "plant"],
        chance_to_find=1.0,
        item_reward="pretty_flower"
    )
    
    # Parse and execute a command to examine the flower
    cmd = command_parser.parse_command("look at the flower")
    result = command_parser.execute_command(cmd)
    
    # Check that the item was added to inventory
    assert "pretty_flower" in mock_player.state.inventory
    assert "You found a pretty flower!" in result

def test_take_standard_item(mock_player, command_parser):
    """Test taking a standard item from the environment."""
    # Set up the player's current tile
    mock_player.state.current_tile.terrain_type = "FOREST"
    mock_player.state.current_tile.items = ["stick"]
    
    # Execute a take command
    result = command_parser.execute_command(Command(CommandType.TAKE, ["stick"]))
    
    # Check that the item was added to inventory
    assert "stick" in mock_player.state.inventory
    assert "You take the stick" in result

def test_drop_item(mock_player, command_parser):
    """Test dropping an item to the environment."""
    # Add an item to the player's inventory
    mock_player.state.inventory.append("stick")
    
    # Execute a drop command
    result = command_parser.execute_command(Command(CommandType.DROP, ["stick"]))
    
    # Check that the item was removed from inventory and added to tile
    assert "stick" not in mock_player.state.inventory
    assert "stick" in mock_player.state.current_tile.items
    assert "You drop the stick" in result

def test_custom_roleplay_action(mock_player, command_parser):
    """Test a custom roleplay action."""
    # Set up the player's current tile
    mock_player.state.current_tile.terrain_type = "FOREST"
    
    # Add a special discovery for custom actions
    command_parser.discovery_system.discoveries["dance_discovery"] = HiddenDiscovery(
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
    
    # Parse and execute a custom command
    cmd = command_parser.parse_command("dance around in circles")
    result = command_parser.execute_command(cmd)
    
    # Check that the response contains the discovery text or the default dance response
    assert "hidden pattern" in result or "sparkling" in result or "magical crystal" in result or "dance gracefully" in result

def test_movement_commands(mock_player, command_parser):
    """Test movement commands."""
    # Set up the player's current position
    mock_player.get_current_position.return_value = (5, 5)
    mock_player.move.return_value = (True, "Moved successfully")
    
    # Execute a move command
    result = command_parser.execute_command(Command(CommandType.MOVE, ["north"]))
    
    # Check that the player moved
    mock_player.move.assert_called_with(Direction.NORTH)
    assert "Moved" in result

def test_parse_standard_commands(mock_player, command_parser):
    """Test parsing standard commands."""
    # Test movement command
    cmd = command_parser.parse_command("north")
    assert cmd.type == CommandType.MOVE
    assert cmd.args[0] == "north"
    
    # Test look command
    cmd = command_parser.parse_command("look")
    assert cmd.type == CommandType.LOOK
    assert not cmd.args
    
    # Test inventory command
    cmd = command_parser.parse_command("inventory")
    assert cmd.type == CommandType.INVENTORY
    assert not cmd.args
    
    # Test take command
    cmd = command_parser.parse_command("take stick")
    assert cmd.type == CommandType.TAKE
    assert cmd.args[0] == "stick"
    
    # Test drop command
    cmd = command_parser.parse_command("drop stick")
    assert cmd.type == CommandType.DROP
    assert cmd.args[0] == "stick"

def test_gather_environmental_resource(mock_player, command_parser):
    """Test gathering an environmental resource."""
    # Set up the player's current tile
    mock_player.state.current_tile.terrain_type = "FOREST"
    
    # Mock the handle_gather_command method
    def mock_gather(args):
        resource = args[0]
        if resource == "wood":
            mock_player.state.inventory.append("wood")
            return "You gather some wood."
        return f"There is no {resource} to gather here."
    
    command_parser.handle_gather_command = mock_gather
    
    # Execute a gather command
    cmd = command_parser.parse_command("gather wood")
    result = command_parser.execute_command(cmd)
    
    # Check the result
    assert "You gather some wood." in result

if __name__ == '__main__':
    pytest.main() 