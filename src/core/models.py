"""
Core models for The Last Centaur.

This module re-exports models from src.engine.core.models for backward compatibility.
All new code should import directly from src.engine.core.models.
"""

# Re-export all models from src.engine.core.models
from src.engine.core.models import (
    Direction,
    CommandType,
    TerrainType,
    PathType,
    StoryArea,
    EventType,
    GameEvent,
    EnvironmentalChange,
    Item,
    Enemy,
    GameState
)

# TileState in core.models was a BaseModel while in engine.core.models it's an Enum
# Import both with explicit naming to avoid conflicts
from src.engine.core.models import TileState as TileStateEnum

# For backward compatibility, we'll keep the BaseModel version with a different name
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime

class TileState(BaseModel):
    """Model for tile state. For compatibility with code expecting the BaseModel version."""
    position: Tuple[int, int]
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
    blocked_paths: List[Direction] = Field(default_factory=list)
    npcs: List[Any] = Field(default_factory=list)
    
    def get_description(self) -> str:
        """Return the tile description."""
        return self.description

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