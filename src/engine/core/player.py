"""
Player state and movement mechanics for The Last Centaur.

This module handles Centaur Prime's state, movement, and related mechanics.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .models import Direction, TileState, TerrainType
from .map_system import MapSystem, GAME_MAP
from .models import StoryArea
from .game_systems import TimeSystem, TimeOfDay, AchievementSystem, TitleSystem, LeaderboardSystem, LeaderboardEntry

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
    player_id: str  # Add player_id field
    player_name: str  # Add player_name field
    position: Tuple[int, int]
    current_area: StoryArea = StoryArea.AWAKENING_WOODS
    stats: PlayerStats = field(default_factory=PlayerStats)
    inventory: List[str] = field(default_factory=list)
    visited_tiles: Set[Tuple[int, int]] = field(default_factory=set)
    blocked_paths: Dict[Tuple[int, int], List[Direction]] = field(default_factory=dict)
    current_tile: Optional[TileState] = None
    rest_count: int = 0  # Track number of rest attempts

class MovementError(Exception):
    """Custom exception for movement-related errors."""
    pass

class Player:
    """Handles player state and movement."""
    
    def __init__(self, map_system: MapSystem, player_id: str, player_name: str):
        self.state = PlayerState(
            player_id=player_id,
            player_name=player_name,
            position=(5, 0)
        )
        self.map_system = map_system
        self.time_system = TimeSystem(map_system=map_system)
        self.achievement_system = AchievementSystem()
        self.title_system = TitleSystem()
        self.leaderboard_system = LeaderboardSystem()  # Initialize leaderboard system
        self.state.visited_tiles.add((5, 0))
        
        # Initialize current tile as TileState
        starting_node = self.map_system.get_area_node(StoryArea.AWAKENING_WOODS)
        self.state.current_tile = TileState(
            position=starting_node.position,
            terrain_type=starting_node.terrain_type,
            area=starting_node.area,
            description=starting_node.base_description,
            items=starting_node.items.copy(),
            enemies=starting_node.enemies,
            npcs=starting_node.npcs if starting_node.npcs else [],
            is_visited=True
        )
    
    def get_current_position(self) -> Tuple[int, int]:
        """Get the player's current position."""
        return self.state.position
    
    @property
    def x(self) -> int:
        """Get the player's x coordinate."""
        return self.state.position[0]
    
    @property
    def y(self) -> int:
        """Get the player's y coordinate."""
        return self.state.position[1]
    
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
            
            # Advance time by 5 minutes for movement
            time_events = self.time_system.advance_time(5)
            time_message = " ".join(time_events.values())
            
            # Check for exploration achievements
            achievement_msg = self.achievement_system.check_exploration_achievement(str(new_area))
            if achievement_msg:
                time_message = f"{time_message} {achievement_msg}"
            
            return True, f"Moved {direction.value}. Stamina: {self.state.stats.stamina}. {time_message}"
            
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
        return current_tile.enemies[0].name
    
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
        
        # Add time of day description
        time_desc = self.time_system.time.get_time_description()
        return f"{node.base_description}\n\n{time_desc}"
    
    def meditate(self, duration: Optional[int] = None) -> Tuple[bool, str]:
        """
        Meditate to recover stamina. More effective than resting but requires
        concentration and can be interrupted by enemies.
        
        Args:
            duration: Optional number of minutes to meditate. If not provided, defaults to 30 minutes.
            
        Returns:
            (success, message) tuple
        """
        if self.state.current_tile and self.state.current_tile.enemies:
            return False, "Cannot meditate while enemies are present. The air is too thick with hostile intent."
            
        # Use provided duration or default to 30 minutes
        meditation_time = duration if duration is not None else 30
        
        # Get time-based multipliers
        multipliers = self.time_system.get_time_multipliers()
        
        # Base recovery modified by time of day and duration
        base_recovery = int((40 * (meditation_time / 30)) * multipliers["stamina_recovery"])
        
        # Bonus recovery in mystical areas
        if self.state.current_tile and self.state.current_tile.terrain_type in [TerrainType.RUINS, TerrainType.CAVE]:
            bonus = int(10 * (meditation_time / 30))
            recovery_message = "The ancient energies enhance your meditation."
        else:
            bonus = 0
            recovery_message = "You find your center and recover your strength."
        
        total_recovery = min(base_recovery + bonus, 
                           self.state.stats.max_stamina - self.state.stats.stamina)
        
        self.state.stats.stamina += total_recovery
        
        # Advance time by the meditation duration
        time_events = self.time_system.advance_time(meditation_time)
        time_message = " ".join(time_events.values())
        
        # Update current tile's enemies based on new time
        if self.state.current_tile:
            self.state.current_tile.update_enemies(self.time_system.time.get_time_of_day().value)
        
        if bonus > 0:
            return True, f"{recovery_message} Recovered {total_recovery} stamina. {time_message}"
        return True, f"{recovery_message} Recovered {total_recovery} stamina. {time_message}"

    def rest(self) -> Tuple[bool, str]:
        """Attempt to rest and recover stamina."""
        # Check if there are enemies in the current tile
        if self.state.current_tile and self.state.current_tile.enemies:
            self.state.rest_count += 1  # Increment rest attempts with enemies present
            achievement_msg = self.achievement_system.check_rest_achievement(self.state.rest_count)
            return False, f"Cannot rest while enemies are present. {achievement_msg if achievement_msg else ''}"
        
        # Try to rest using time system
        success, message = self.time_system.rest()
        if success:
            # Recover stamina
            recovery = min(20, self.state.stats.max_stamina - self.state.stats.stamina)
            self.state.stats.stamina += recovery
            return True, f"{message} Recovered {recovery} stamina."
        
        return False, message
    
    def combat_victory(self, enemy_name: str) -> str:
        """Handle victory over an enemy."""
        # Check for combat achievements
        achievement_msg = self.achievement_system.check_combat_achievement(enemy_name, True)
        
        # Remove enemy from current tile
        if self.state.current_tile and self.state.current_tile.enemies:
            # Find the enemy by name (case-insensitive)
            for enemy in self.state.current_tile.enemies[:]:  # Create a copy to modify during iteration
                if enemy.name.lower() == enemy_name.lower():
                    self.state.current_tile.enemies.remove(enemy)
                    break
        
        # Clear blocked paths
        if self.state.position in self.state.blocked_paths:
            self.state.blocked_paths.pop(self.state.position)
        
        # Advance time by 30 minutes for combat
        time_events = self.time_system.advance_time(30)
        time_message = " ".join(time_events.values())
        
        victory_msg = f"Victory! Defeated {enemy_name}."
        if achievement_msg:
            victory_msg = f"{victory_msg} {achievement_msg}"
        if time_message:
            victory_msg = f"{victory_msg} {time_message}"
        
        return victory_msg
    
    def get_achievements(self) -> str:
        """Get the current achievement status."""
        return self.achievement_system.get_achievement_status()
    
    def update_blocked_paths(self, enemy_id: str, direction: Direction, is_blocked: bool) -> None:
        """Update which paths are blocked by enemies."""
        if is_blocked:
            if self.state.position not in self.state.blocked_paths:
                self.state.blocked_paths[self.state.position] = []
            self.state.blocked_paths[self.state.position].append(direction)
        else:
            if self.state.position in self.state.blocked_paths:
                self.state.blocked_paths[self.state.position].remove(direction)
    
    def get_status(self) -> str:
        """Get the player's current status including time."""
        time_desc = self.time_system.time.get_time_description()
        current_time = self.time_system.time.get_formatted_time()
        
        # Get equipped title
        title_info = ""
        if self.title_system.equipped_title:
            title = self.title_system.titles[self.title_system.equipped_title]
            title_info = f"\nTitle: {title.name}"
        
        return (
            f"Time: {current_time}\n"
            f"{time_desc}\n\n"
            f"Health: {self.state.stats.health}/{self.state.stats.max_health}\n"
            f"Stamina: {self.state.stats.stamina}/{self.state.stats.max_stamina}\n"
            f"Position: {self.state.position}\n"
            f"Current Area: {self.state.current_area.value}"
            f"{title_info}\n"
            f"Inventory: {len(self.state.inventory)}/{self.state.stats.inventory_capacity} items"
        )

    def get_titles(self) -> str:
        """Get the current title status."""
        return self.title_system.get_title_status()
    
    def select_title(self, title_id: str) -> str:
        """Attempt to equip a title."""
        success, message = self.title_system.equip_title(title_id)
        return message

    def complete_game(self, path_type: str) -> str:
        """
        Record game completion in the leaderboard.
        
        Args:
            path_type: The path taken to victory (warrior/mystic/stealth)
            
        Returns:
            Completion message with rankings
        """
        # Get current achievement count
        achievement_count = len(self.achievement_system.unlocked_achievements)
        
        # Create leaderboard entry
        entry = LeaderboardEntry(
            player_id=self.state.player_id,
            player_name=self.state.player_name,
            completion_time=self.time_system.time.get_formatted_time(),
            achievements=achievement_count,
            path_type=path_type.lower(),  # Ensure path type is lowercase
            date=datetime.now()  # Ensure we set the date
        )
        
        # Add entry to leaderboard
        self.leaderboard_system.add_entry(entry)
        
        # Check for title unlocks
        title_msg = ""
        if self.time_system.time.days <= 2:  # Completed in 2 days or less
            unlock_msg = self.title_system.unlock_title("the_swift")
            if unlock_msg:
                title_msg = f"\n{unlock_msg}"
        
        # Get player's rankings
        overall_rank = self.leaderboard_system.get_player_ranking(self.state.player_id)
        achievement_rank = self.leaderboard_system.get_player_ranking(
            self.state.player_id, "achievements"
        )
        
        # Format completion message
        message = [
            f"Congratulations, {self.state.player_name}!",
            f"You have completed the game via the {path_type.title()} path.",
            f"Time: {entry.completion_time}",
            f"Achievements: {achievement_count}",
            "",
            "Rankings:",
            f"Overall: #{overall_rank}" if overall_rank else "Overall: Not ranked",
            f"Achievements: #{achievement_rank}" if achievement_rank else "Achievements: Not ranked"
        ]
        
        if title_msg:
            message.append(title_msg)
        
        return "\n".join(message)

    def get_leaderboard(self, category: Optional[str] = None) -> str:
        """Get the current leaderboard standings."""
        return self.leaderboard_system.get_leaderboard(category)
    
    def get_personal_records(self) -> str:
        """Get the player's personal records and rankings."""
        entries = self.leaderboard_system.get_player_entries(self.state.player_id)
        if not entries:
            return "No records yet"
        
        # Get best times for each path
        records = []
        records.append("Personal Records:")
        
        for path_type in self.leaderboard_system.path_types:
            best_time = self.leaderboard_system.get_player_best_time(
                self.state.player_id, path_type
            )
            if best_time:
                records.append(f"{path_type.title()} Path: {best_time}")
        
        # Get rankings
        overall_rank = self.leaderboard_system.get_player_ranking(self.state.player_id)
        achievement_rank = self.leaderboard_system.get_player_ranking(
            self.state.player_id, "achievements"
        )
        
        records.extend([
            "",
            "Current Rankings:",
            f"Overall: #{overall_rank}" if overall_rank else "Overall: Not ranked",
            f"Achievements: #{achievement_rank}" if achievement_rank else "Achievements: Not ranked"
        ])
        
        return "\n".join(records) 