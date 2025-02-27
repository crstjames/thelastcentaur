"""
Tests for the movement system in The Last Centaur.

This module tests the functionality of player movement, including:
- Basic movement in all directions
- Backtracking (returning to previous locations)
- Area transitions
- Blocked paths
"""

import pytest
from unittest.mock import MagicMock, patch

from src.engine.core.models import Direction, TileState, TerrainType, StoryArea
from src.engine.core.player import Player
from src.engine.core.map_system import MapSystem, AreaNode, AreaConnection
from src.engine.core.command_parser import CommandParser


class TestMovementSystem:
    """Test suite for the movement system."""
    
    @pytest.fixture
    def map_system(self):
        """Create a map system with a simple 3x3 grid for testing."""
        map_system = MapSystem()
        
        # Create a simple 3x3 grid of areas
        positions = {
            (1, 0): StoryArea.AWAKENING_WOODS,
            (1, 1): StoryArea.TRIALS_PATH,
            (1, 2): StoryArea.ANCIENT_RUINS,
            (0, 1): StoryArea.MYSTIC_MOUNTAINS,
            (2, 1): StoryArea.SHADOW_DOMAIN,
        }
        
        # Create area nodes for each position
        for position, area in positions.items():
            node = AreaNode(
                area=area,
                position=position,
                terrain_type=TerrainType.FOREST,
                base_description=f"Test area at {position}",
                requirements=[],
                enemies=[],
                items=[],
                npcs=[],
                connections=[]  # Add empty connections list, we'll populate it later
            )
            map_system.position_to_area[position] = node
            map_system.areas[area] = node  # Use areas instead of area_to_node
        
        # Add connections between areas
        connections = [
            # Vertical connections
            (StoryArea.AWAKENING_WOODS, Direction.NORTH, StoryArea.TRIALS_PATH),
            (StoryArea.TRIALS_PATH, Direction.SOUTH, StoryArea.AWAKENING_WOODS),
            (StoryArea.TRIALS_PATH, Direction.NORTH, StoryArea.ANCIENT_RUINS),
            (StoryArea.ANCIENT_RUINS, Direction.SOUTH, StoryArea.TRIALS_PATH),
            
            # Horizontal connections
            (StoryArea.MYSTIC_MOUNTAINS, Direction.EAST, StoryArea.TRIALS_PATH),
            (StoryArea.TRIALS_PATH, Direction.WEST, StoryArea.MYSTIC_MOUNTAINS),
            (StoryArea.TRIALS_PATH, Direction.EAST, StoryArea.SHADOW_DOMAIN),
            (StoryArea.SHADOW_DOMAIN, Direction.WEST, StoryArea.TRIALS_PATH),
        ]
        
        for from_area, direction, to_area in connections:
            from_node = map_system.areas[from_area]  # Use areas instead of area_to_node
            connection = AreaConnection(
                from_area=from_area,
                to_area=to_area,
                direction=direction,
                requirements=[],
                description=f"Path from {from_area} to {to_area}"
            )
            from_node.connections.append(connection)
        
        return map_system
    
    @pytest.fixture
    def player(self, map_system):
        """Create a player for testing."""
        player = MagicMock()
        player.state = MagicMock()
        player.state.position = (1, 0)  # Start at AWAKENING_WOODS
        player.state.current_area = StoryArea.AWAKENING_WOODS
        player.state.current_tile = TileState(
            position=(1, 0),
            terrain_type=TerrainType.FOREST,
            area=StoryArea.AWAKENING_WOODS,
            description="Test area at (1, 0)",
            items=[],
            enemies=[],
            npcs=[],
            is_visited=True
        )
        player.state.inventory = []
        player.state.visited_tiles = {(1, 0)}
        player.state.blocked_paths = {}
        player.map_system = map_system
        player.get_current_position.return_value = (1, 0)
        
        # Set up the move method to use the actual implementation
        player.move = lambda direction: Player.move(player, direction)
        
        return player
    
    @pytest.fixture
    def command_parser(self, player):
        """Create a command parser for testing."""
        parser = CommandParser(player)
        return parser
    
    def test_basic_movement(self, player, map_system):
        """Test basic movement in all four directions."""
        # Move north from starting position
        success, message = player.move(Direction.NORTH)
        assert success
        assert "Moved north" in message
        assert player.state.position == (1, 1)
        assert player.state.current_area == StoryArea.TRIALS_PATH
        
        # Move south back to starting position
        success, message = player.move(Direction.SOUTH)
        assert success
        assert "Moved south" in message
        assert player.state.position == (1, 0)
        assert player.state.current_area == StoryArea.AWAKENING_WOODS
        
        # Move north again
        success, message = player.move(Direction.NORTH)
        assert success
        assert player.state.position == (1, 1)
        
        # Move east
        success, message = player.move(Direction.EAST)
        assert success
        assert "Moved east" in message
        assert player.state.position == (2, 1)
        assert player.state.current_area == StoryArea.SHADOW_DOMAIN
        
        # Move west back
        success, message = player.move(Direction.WEST)
        assert success
        assert "Moved west" in message
        assert player.state.position == (1, 1)
        assert player.state.current_area == StoryArea.TRIALS_PATH
    
    def test_backtracking(self, player, map_system):
        """Test that the player can backtrack along previously traveled paths."""
        # Move north from starting position
        success, message = player.move(Direction.NORTH)
        assert success
        assert player.state.position == (1, 1)
        
        # Move north again
        success, message = player.move(Direction.NORTH)
        assert success
        assert player.state.position == (1, 2)
        
        # Backtrack south
        success, message = player.move(Direction.SOUTH)
        assert success
        assert player.state.position == (1, 1)
        
        # Backtrack south again to starting position
        success, message = player.move(Direction.SOUTH)
        assert success
        assert player.state.position == (1, 0)
        assert player.state.current_area == StoryArea.AWAKENING_WOODS
    
    def test_command_parser_movement(self, command_parser, player):
        """Test movement through the command parser."""
        # Move north using command parser
        result = command_parser.handle_move_command(["north"])
        assert "Moved north" in result
        assert player.state.position == (1, 1)
        
        # Move south back to starting position
        result = command_parser.handle_move_command(["south"])
        assert "Moved south" in result
        assert player.state.position == (1, 0)
        
        # Try invalid direction
        result = command_parser.handle_move_command(["invalid"])
        assert "Unknown direction" in result
        assert player.state.position == (1, 0)  # Position unchanged
    
    def test_blocked_paths(self, player):
        """Test that blocked paths prevent movement."""
        # Block the north path
        player.state.blocked_paths[(1, 0)] = [Direction.NORTH]
        
        # Try to move north
        success, message = player.move(Direction.NORTH)
        assert not success
        assert "blocked" in message
        assert player.state.position == (1, 0)  # Position unchanged
        
        # Unblock the path
        player.state.blocked_paths = {}
        
        # Try again
        success, message = player.move(Direction.NORTH)
        assert success
        assert player.state.position == (1, 1)
    
    def test_boundary_limits(self, player):
        """Test that the player cannot move beyond map boundaries."""
        # Move to the western edge
        player.state.position = (0, 1)
        player.get_current_position.return_value = (0, 1)
        
        # Try to move further west (off the map)
        success, message = player.move(Direction.WEST)
        assert not success
        assert "cannot go that way" in message.lower()
        assert player.state.position == (0, 1)  # Position unchanged 