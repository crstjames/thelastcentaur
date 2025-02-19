"""
Player state and movement mechanics for The Last Centaur.

This module handles Centaur Prime's state, movement, and related mechanics.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .models import Direction, TileState
from .map_system import MapSystem, GAME_MAP
from .models import StoryArea

@dataclass
class PlayerStats:
    """Core stats for Centaur Prime."""
    health: int = 100
    max_health: int = 100
    stamina: int = 100
    max_stamina: int = 100
    inventory_capacity: int = 100
    current_inventory_weight: int = 0

@dataclass
class PlayerState:
    """Represents the complete state of Centaur Prime."""
    position: Tuple[int, int]
    current_area: StoryArea = StoryArea.AWAKENING_WOODS
    stats: PlayerStats = field(default_factory=PlayerStats)
    inventory: List[str] = field(default_factory=list)
    visited_tiles: Set[Tuple[int, int]] = field(default_factory=set)
    blocked_paths: Dict[Tuple[int, int], List[Direction]] = field(default_factory=dict)
    current_tile: Optional[TileState] = None

class MovementError(Exception):
    """Custom exception for movement-related errors."""
    pass

class Player:
    """Handles player state and movement."""
    
    def __init__(self, map_system: MapSystem):
        self.state = PlayerState(position=(5, 0))  # Starting position
        self.map_system = map_system
        self.state.visited_tiles.add((5, 0))  # Mark starting tile as visited
        
        # Initialize current tile as TileState
        starting_node = self.map_system.get_area_node(StoryArea.AWAKENING_WOODS)
        self.state.current_tile = TileState(
            position=starting_node.position,
            terrain_type=starting_node.terrain_type,
            area=starting_node.area,
            description=starting_node.base_description,
            items=starting_node.items.copy(),
            enemies=starting_node.enemies,
            is_visited=True
        )
    
    def get_current_position(self) -> Tuple[int, int]:
        """Get the player's current position."""
        return self.state.position
    
    def get_possible_moves(self) -> Dict[Direction, str]:
        """Get all possible moves from current position with descriptions."""
        x, y = self.state.position
        possible = {}
        
        # Check each direction
        for direction in Direction:
            new_x, new_y = self._get_new_position(direction)
            
            # Check if move would be off map
            if not (0 <= new_x < 10 and 0 <= new_y < 10):
                possible[direction] = "A shimmering magical barrier blocks your path."
                continue
            
            # Check if path is blocked by enemy
            if self._is_path_blocked(direction):
                enemy = self._get_blocking_enemy(direction)
                possible[direction] = f"Path blocked by {enemy}. Defeat it to proceed."
                continue
            
            # Check if player has enough stamina
            if self.state.stats.stamina < 5:
                possible[direction] = "Not enough stamina to move."
                continue
            
            # Path is available
            possible[direction] = "Clear path."
        
        return possible
    
    def move(self, direction: Direction) -> Tuple[bool, str]:
        """
        Attempt to move in the specified direction.
        Returns (success, message).
        """
        try:
            # Validate movement
            self._validate_movement(direction)
            
            # Get new position
            new_x, new_y = self._get_new_position(direction)
            
            # Get new area
            new_area = self._get_area_for_position((new_x, new_y))
            
            # If we're staying in the same area, use that for the transition
            if new_area == self.state.current_area:
                # Try to find a connection in the requested direction
                node = self.map_system.get_area_node(self.state.current_area)
                connection = next((c for c in node.connections if c.direction == direction), None)
                if connection:
                    new_area = connection.to_area
            
            # Attempt to transition to new area
            success, message, new_tile = self.map_system.transition_area(
                self.state.current_area,
                new_area,
                direction,
                self.state.inventory
            )
            
            if not success:
                return False, message
            
            # Update position and stats
            self.state.position = (new_x, new_y)
            self.state.stats.stamina -= 5
            self.state.visited_tiles.add((new_x, new_y))
            
            # Update current area and tile
            self.state.current_area = new_area
            self.state.current_tile = new_tile
            
            return True, f"Moved {direction.value}. Stamina: {self.state.stats.stamina}"
            
        except MovementError as e:
            return False, str(e)
    
    def _validate_movement(self, direction: Direction) -> None:
        """Validate if movement is possible."""
        new_x, new_y = self._get_new_position(direction)
        
        # Check map boundaries
        if not (0 <= new_x < 10 and 0 <= new_y < 10):
            raise MovementError("A shimmering magical barrier blocks your path.")
        
        # Check stamina
        if self.state.stats.stamina < 5:
            raise MovementError("Not enough stamina to move.")
        
        # Check if path is blocked by enemy
        if self.state.current_tile and self.state.current_tile.enemies:
            raise MovementError(f"Path blocked by {self.state.current_tile.enemies[0].name}. Defeat it to proceed.")
        
        # Check if the new position is a valid area
        new_area = self._get_area_for_position((new_x, new_y))
        if new_area not in GAME_MAP:
            raise MovementError("A magical barrier prevents you from going that way.")
    
    def _get_new_position(self, direction: Direction) -> Tuple[int, int]:
        """Calculate new position based on direction."""
        x, y = self.state.position
        
        if direction == Direction.NORTH:
            return (x, y + 1)
        elif direction == Direction.SOUTH:
            return (x, y - 1)
        elif direction == Direction.EAST:
            return (x + 1, y)
        else:  # WEST
            return (x - 1, y)
    
    def _is_path_blocked(self, direction: Direction) -> bool:
        """Check if path is blocked by enemy."""
        if self.state.position not in self.state.blocked_paths:
            return False
        return direction in self.state.blocked_paths[self.state.position]
    
    def _get_blocking_enemy(self, direction: Direction) -> str:
        """Get the name of enemy blocking the path."""
        current_tile = self.state.current_tile
        if not current_tile or not current_tile.enemies:
            return "unknown entity"
        
        # In a real implementation, you'd want to track which enemy is blocking which direction
        return current_tile.enemies[0]["name"]
    
    def _get_area_for_position(self, position: Tuple[int, int]) -> StoryArea:
        """Get the area for a given position."""
        # First try to find the area in the GAME_MAP
        for area, node in GAME_MAP.items():
            if isinstance(area, str):
                continue  # Skip string-based area names
            if node.position == position:
                return area
        return self.state.current_area  # Stay in current area if position not found
    
    def get_movement_history(self) -> List[Tuple[int, int]]:
        """Get list of visited tiles in order of visit."""
        return list(self.state.visited_tiles)
    
    def get_tile_info(self, position: Tuple[int, int]) -> Optional[str]:
        """Get information about a tile if it has been visited."""
        if position not in self.state.visited_tiles:
            return None
            
        area = self._get_area_for_position(position)
        node = self.map_system.get_area_node(area)
        return node.base_description
    
    def meditate(self) -> Tuple[bool, str]:
        """
        Meditate to recover stamina. More effective than resting but requires
        concentration and can be interrupted by enemies.
        Returns (success, message).
        """
        if self.state.current_tile and self.state.current_tile.enemies:
            return False, "Cannot meditate while enemies are present. The air is too thick with hostile intent."
            
        # Meditation is more effective than resting
        base_recovery = 40  # Base stamina recovery
        
        # Bonus recovery in mystical areas
        if self.state.current_tile and self.state.current_tile.terrain_type in [TerrainType.RUINS, TerrainType.CAVE]:
            bonus = 10
            recovery_message = "The ancient energies enhance your meditation."
        else:
            bonus = 0
            recovery_message = "You find your center and recover your strength."
        
        total_recovery = min(base_recovery + bonus, 
                           self.state.stats.max_stamina - self.state.stats.stamina)
        
        self.state.stats.stamina += total_recovery
        
        if bonus > 0:
            return True, f"{recovery_message} Recovered {total_recovery} stamina."
        return True, f"{recovery_message} Recovered {total_recovery} stamina."

    def rest(self) -> Tuple[bool, str]:
        """
        Rest to recover a small amount of stamina. Faster but less effective than meditation.
        Returns (success, message).
        """
        if self.state.current_tile and self.state.current_tile.enemies:
            return False, "Cannot rest while enemies are present."
            
        recovery = min(20, self.state.stats.max_stamina - self.state.stats.stamina)
        self.state.stats.stamina += recovery
        return True, f"You take a quick rest and recover {recovery} stamina."
    
    def update_blocked_paths(self, enemy_id: str, direction: Direction, is_blocked: bool) -> None:
        """Update which paths are blocked by enemies."""
        if is_blocked:
            if self.state.position not in self.state.blocked_paths:
                self.state.blocked_paths[self.state.position] = []
            self.state.blocked_paths[self.state.position].append(direction)
        else:
            if self.state.position in self.state.blocked_paths:
                self.state.blocked_paths[self.state.position].remove(direction) 