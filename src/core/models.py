from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Direction(str, Enum):
    """Direction enum for movement."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

class TerrainType(str, Enum):
    """Terrain type enum for tiles."""
    FOREST = "forest"
    CLEARING = "clearing"
    MOUNTAIN = "mountain"
    RUINS = "ruins"
    GRASS = "grass"

class StoryArea(str, Enum):
    """Story area enum for game progression."""
    AWAKENING_WOODS = "awakening_woods"
    MYSTIC_VALLEY = "mystic_valley"
    ANCIENT_RUINS = "ancient_ruins"
    FORGOTTEN_PEAKS = "forgotten_peaks"

class EventType(str, Enum):
    """Event type enum for game events."""
    INTERACTION = "interaction"
    COMBAT = "combat"
    DISCOVERY = "discovery"
    ENVIRONMENTAL = "environmental"
    QUEST = "quest"

class GameEvent(BaseModel):
    """Model for game events."""
    event_type: EventType
    description: str
    location: tuple[int, int]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)
    persistence: int = 100  # How long the event persists (0-100)

class EnvironmentalChange(BaseModel):
    """Model for environmental changes."""
    type: str
    description: str
    is_permanent: bool = False
    created_by: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)

class Item(BaseModel):
    """Model for items."""
    id: str
    name: str
    description: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    is_quest_item: bool = False
    can_be_picked_up: bool = True

class Enemy(BaseModel):
    """Model for enemies."""
    name: str
    description: str
    health: int
    damage: int
    drops: List[str] = Field(default_factory=list)
    is_boss: bool = False
    properties: Dict[str, Any] = Field(default_factory=dict)

class TileState(BaseModel):
    """Model for tile state."""
    position: tuple[int, int]
    terrain_type: TerrainType
    area: StoryArea
    description: str
    is_visited: bool = False
    items: List[Item] = Field(default_factory=list)
    enemies: List[Enemy] = Field(default_factory=list)
    environmental_changes: List[EnvironmentalChange] = Field(default_factory=list)
    events: List[GameEvent] = Field(default_factory=list)
    requirements: Dict[str, Any] = Field(default_factory=dict)
    exits: List[Direction] = Field(default_factory=list)

class GameState(BaseModel):
    """Model for game state."""
    player_position: tuple[int, int]
    current_area: StoryArea
    inventory: List[Item] = Field(default_factory=list)
    visited_tiles: set[tuple[int, int]] = Field(default_factory=set)
    game_time: datetime = Field(default_factory=datetime.utcnow)
    active_quests: List[str] = Field(default_factory=list)
    completed_quests: List[str] = Field(default_factory=list)
    player_stats: Dict[str, Any] = Field(default_factory=dict) 