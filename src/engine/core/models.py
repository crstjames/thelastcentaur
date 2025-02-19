"""
Core models for The Last Centaur game engine.

This module defines the fundamental data structures used throughout the game.
All models use Pydantic for validation and serialization.
"""

from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Union
from pydantic import BaseModel, Field, validator

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

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

@dataclass
class EnvironmentalChange:
    """Represents a change to the environment."""
    type: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
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

class TileState(BaseModel):
    """Represents the current state of a tile."""
    
    position: Tuple[int, int]
    terrain_type: TerrainType
    area: Union[StoryArea, str]  # Allow both StoryArea enum and string values
    description: str
    items: List[str] = Field(default_factory=list)
    enemies: List[Enemy] = Field(default_factory=list)
    npcs: List[str] = Field(default_factory=list)  # Add NPCs field
    is_visited: bool = False
    blocked_directions: List[Direction] = Field(default_factory=list)
    requirements: Dict[Direction, str] = Field(default_factory=dict)
    events: List[GameEvent] = Field(default_factory=list)
    changes: List[EnvironmentalChange] = Field(default_factory=list)
    environmental_changes: List[Dict[str, str]] = Field(default_factory=list)  # For storing player-made changes
    gatherable_resources: Dict[str, int] = Field(default_factory=dict)  # Resource name -> quantity

    @validator('position')
    def validate_position(cls, v):
        """Ensure position is within 10x10 grid."""
        x, y = v
        if not (0 <= x < 10 and 0 <= y < 10):
            raise ValueError("Position must be within 10x10 grid")
        return v
    
    def get_full_description(self) -> str:
        """Get the full description including environmental changes."""
        description = [self.description]
        
        # Add environmental changes
        if self.environmental_changes:
            description.append("\nYou notice:")
            for change in self.environmental_changes:
                if change["type"] == "mark":
                    description.append(f"- There are marks here: {change['description']}")
                elif change["type"] == "draw":
                    description.append(f"- Someone drew: {change['description']}")
                elif change["type"] == "write":
                    description.append(f"- Written here: {change['description']}")
                elif change["type"] == "alter":
                    description.append(f"- The environment shows signs of change: {change['description']}")
        
        # Add gatherable resources if any are visible
        visible_resources = [f"{quantity} {resource}" 
                           for resource, quantity in self.gatherable_resources.items() 
                           if quantity > 0]
        if visible_resources:
            description.append("\nYou can gather:")
            description.extend(f"- {resource}" for resource in visible_resources)
        
        return "\n".join(description)
    
    def add_environmental_change(self, change_type: str, description: str) -> None:
        """Add a new environmental change to the tile."""
        self.environmental_changes.append({
            "type": change_type,
            "description": description,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def update_resources(self, resource: str, quantity: int) -> None:
        """Update the quantity of a gatherable resource."""
        current_quantity = self.gatherable_resources.get(resource, 0)
        new_quantity = max(0, current_quantity + quantity)  # Ensure non-negative
        
        if new_quantity > 0:
            self.gatherable_resources[resource] = new_quantity
        elif resource in self.gatherable_resources:
            del self.gatherable_resources[resource]

class GameState(BaseModel):
    """Represents the complete state of the game."""
    
    player_position: Tuple[int, int]
    inventory: List[str] = Field(default_factory=list)
    visited_tiles: Set[Tuple[int, int]] = Field(default_factory=set)
    current_area: StoryArea
    tiles: Dict[Tuple[int, int], TileState] = Field(default_factory=dict)
    events: List[GameEvent] = Field(default_factory=list)
    game_time: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            set: lambda v: list(v)
        } 