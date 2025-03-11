"""
Core models for The Last Centaur game engine.

This module defines the fundamental data structures used throughout the game.
All models use Pydantic for validation and serialization.
"""

from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from pydantic import BaseModel, Field, validator, ConfigDict, model_serializer

class Direction(str, Enum):
    """Direction enum for movement."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"

class CommandType(Enum):
    """Command types for user input."""
    MOVE = auto()
    LOOK = auto()
    INVENTORY = auto()
    GET = auto()
    DROP = auto()
    EXAMINE = auto()
    USE = auto()
    HELP = auto()
    QUIT = auto()
    ATTACK = auto()
    TALK = auto()
    UNKNOWN = auto()

class TerrainType(str, Enum):
    """Terrain types for area nodes."""
    FOREST = "forest"
    MOUNTAIN = "mountain"
    CLEARING = "clearing"
    WATER = "water"
    CAVE = "cave"
    TEMPLE = "temple"
    RUINS = "ruins"
    VALLEY = "valley"

class PathType(str, Enum):
    """The three possible paths to victory."""
    WARRIOR = "warrior"  # Direct combat path
    MYSTIC = "mystic"   # Magic and knowledge path
    STEALTH = "stealth" # Cunning and deception path

class StoryArea(str, Enum):
    """Enumeration of story areas in the game."""
    AWAKENING_WOODS = "awakening_woods"
    WARRIORS_CAMP = "warriors_camp"
    TRIALS_PATH = "trials_path"
    MOUNTAIN_BASE = "mountain_base"
    TRAINING_GROUNDS = "training_grounds"
    SHADOW_DOMAIN = "shadow_domain"
    SHADOW_TRAINING = "shadow_training"
    MYSTIC_MOUNTAINS = "mystic_mountains"
    CRYSTAL_POND = "crystal_pond"
    HONOR_SHRINE = "honor_shrine"
    FORGOTTEN_TEMPLE = "forgotten_temple"
    MEDITATION_CIRCLE = "meditation_circle"
    ENCHANTED_VALLEY = "enchanted_valley"
    CRYSTAL_CAVES = "crystal_caves"
    FORGOTTEN_GROVE = "forgotten_grove"
    CROSSROADS = "crossroads"
    GUARDIAN_OVERLOOK = "guardian_overlook"
    ANCIENT_SANCTUARY = "ancient_sanctuary"

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
    drops: List[str] = None
    requirements: List[str] = None  # Items needed to defeat this enemy

class TileState(Enum):
    """State of a game tile."""
    UNEXPLORED = auto()
    VISIBLE = auto()
    EXPLORED = auto()

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