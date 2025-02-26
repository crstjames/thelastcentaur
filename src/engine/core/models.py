"""
Core models for The Last Centaur game engine.

This module defines the fundamental data structures used throughout the game.
All models use Pydantic for validation and serialization.
"""

from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from pydantic import BaseModel, Field, validator, ConfigDict, model_serializer

class Direction(str, Enum):
    """Cardinal directions for movement."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

class TerrainType(str, Enum):
    """Types of terrain in the game."""
    FOREST = "forest"
    MOUNTAIN = "mountain"
    RUINS = "ruins"
    CLEARING = "clearing"
    VALLEY = "valley"
    CAVE = "cave"

class PathType(str, Enum):
    """The three possible paths to victory."""
    WARRIOR = "warrior"  # Direct combat path
    MYSTIC = "mystic"   # Magic and knowledge path
    STEALTH = "stealth" # Cunning and deception path

class StoryArea(str, Enum):
    """Story-specific areas of the map."""
    AWAKENING_WOODS = "awakening_woods"
    TRIALS_PATH = "trials_path"
    ANCIENT_RUINS = "ancient_ruins"
    MYSTIC_MOUNTAINS = "mystic_mountains"
    SHADOW_DOMAIN = "shadow_domain"
    ENCHANTED_VALLEY = "enchanted_valley"
    FORGOTTEN_GROVE = "forgotten_grove"
    CRYSTAL_CAVES = "crystal_caves"

class EventType(str, Enum):
    """Types of events that can occur in the game."""
    INTERACTION = "interaction"      # Player directly interacts with environment
    MODIFICATION = "modification"    # Environment is modified
    STATE_CHANGE = "state_change"   # Something changes state over time
    COMBAT = "combat"               # Combat-related events
    DISCOVERY = "discovery"         # Player discovers something
    NATURAL = "natural"             # Natural events (weather, time passage, etc)

class GameEvent(BaseModel):
    """Represents a single event in the game."""
    
    event_type: EventType
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location: Tuple[int, int]
    details: Dict[str, str] = Field(default_factory=dict)
    persistence: int = Field(100, ge=0, le=100)  # How long event effects last

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "event_type": "interaction",
                "description": "Player picked up a sword",
                "location": (1, 1),
                "details": {"item": "sword"},
                "persistence": 100
            }
        }
    )

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "location": self.location,
            "details": self.details,
            "persistence": self.persistence
        }

@dataclass
class EnvironmentalChange:
    """Represents a change to the environment."""
    type: str
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    is_permanent: bool = False
    created_by: Optional[str] = None

class Item(BaseModel):
    """Represents an item in the game."""
    
    id: str
    name: str
    description: str
    type: str
    properties: Dict[str, Union[str, int, bool]] = Field(default_factory=dict)
    requirements: List[str] = Field(default_factory=list)

@dataclass
class Enemy:
    """Represents an enemy in the game."""
    name: str
    description: str
    health: int
    damage: int
    drops: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)

@dataclass
class TileState:
    """Represents the current state of a tile."""
    position: Tuple[int, int]
    terrain_type: TerrainType
    area: StoryArea
    description: str
    items: List[str]
    enemies: List[Enemy]
    npcs: List[str] = field(default_factory=list)
    is_visited: bool = False
    environmental_changes: List[Dict[str, Any]] = field(default_factory=list)
    blocked_paths: List[Direction] = field(default_factory=list)
    
    def get_description(self) -> str:
        """Get a full description of the tile's current state."""
        desc = [self.description]
        
        # Add environmental changes if present
        if self.environmental_changes:
            permanent_changes = [change for change in self.environmental_changes if change.get("is_permanent", False)]
            if permanent_changes:
                desc.append("")  # Empty line
                desc.append("You notice changes to the environment:")
                for change in permanent_changes:
                    desc.append(f"- {change['description']}")
        
        desc.append("")  # Empty line
        
        # Add movement options
        desc.append("You can move: north, south, east, west")
        desc.append("")  # Empty line
        
        # Add enemies if present
        if self.enemies:
            desc.append("Enemies present: " + ", ".join(enemy.name for enemy in self.enemies))
            desc.append("")  # Empty line
        
        # Add NPCs if present
        if self.npcs:
            desc.append("NPCs present: " + ", ".join(self.npcs))
            desc.append("")  # Empty line
        
        # Add items if present
        if self.items:
            desc.append("Items visible: " + ", ".join(self.items))
            desc.append("")  # Empty line
        
        return "\n".join(desc)
    
    def update_enemies(self, time_of_day: str) -> None:
        """Update enemies based on time of day."""
        # Keep track of original enemy IDs
        enemy_ids = [enemy.name.lower().replace(" ", "_") for enemy in self.enemies]
        
        # Add Shadow Stalker at night if in starting area
        if time_of_day.lower() == "night" and self.area == StoryArea.AWAKENING_WOODS:
            if "shadow_stalker" not in enemy_ids:
                enemy_ids.append("shadow_stalker")
        
        # Convert IDs back to Enemy objects
        from .world_design import WORLD_ENEMIES
        new_enemies = []
        for enemy_id in enemy_ids:
            enemy_data = next((e for e in WORLD_ENEMIES if e["id"] == enemy_id), None)
            if enemy_data:
                is_night_only = enemy_data.get("night_only", False)
                if not is_night_only or (is_night_only and time_of_day.lower() == "night"):
                    new_enemies.append(Enemy(
                        name=enemy_data["name"],
                        description=enemy_data["description"],
                        health=enemy_data["health"],
                        damage=enemy_data["damage"],
                        drops=enemy_data.get("drops", []),
                        requirements=enemy_data.get("requirements", [])
                    ))
        self.enemies = new_enemies

class GameState(BaseModel):
    """Represents the complete state of the game."""
    
    player_position: Tuple[int, int]
    inventory: List[str] = Field(default_factory=list)
    visited_tiles: Set[Tuple[int, int]] = Field(default_factory=set)
    current_area: StoryArea
    tiles: Dict[Tuple[int, int], TileState] = Field(default_factory=dict)
    events: List[GameEvent] = Field(default_factory=list)
    game_time: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "player_position": (0, 0),
                "inventory": [],
                "visited_tiles": [(0, 0)],
                "current_area": "awakening_woods"
            }
        }
    )

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        return {
            "player_position": self.player_position,
            "inventory": self.inventory,
            "visited_tiles": list(self.visited_tiles),
            "current_area": self.current_area,
            "tiles": {str(k): v for k, v in self.tiles.items()},
            "events": self.events,
            "game_time": self.game_time.isoformat()
        } 