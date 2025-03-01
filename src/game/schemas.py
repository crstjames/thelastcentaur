from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class GameStatus(str, Enum):
    """Game status enum."""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class GameInstanceCreate(BaseModel):
    """Schema for creating a game instance."""
    name: str
    max_players: int = 1
    description: Optional[str] = None

class GameInstanceUpdate(BaseModel):
    """Schema for updating a game instance."""
    name: Optional[str] = None
    status: Optional[GameStatus] = None
    max_players: Optional[int] = None
    description: Optional[str] = None

class GameInstanceResponse(BaseModel):
    """Schema for game instance response."""
    id: str
    user_id: str
    name: str
    status: GameStatus
    max_players: int
    current_players: int
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GameStateCreate(BaseModel):
    """Schema for creating a game state."""
    instance_id: str
    state_data: Dict[str, Any] = Field(default_factory=dict)

class GameStateUpdate(BaseModel):
    """Schema for updating a game state."""
    state_data: Dict[str, Any]

class GameStateResponse(BaseModel):
    """Schema for game state response."""
    id: str
    instance_id: str
    state_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GameCommandRequest(BaseModel):
    """Schema for game command request."""
    command: str
    use_llm: bool = True

class GameCommandResponse(BaseModel):
    """Schema for game command response."""
    command: str
    response: str
    game_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    game_state: Optional[Dict[str, Any]] = None

class TileResponse(BaseModel):
    """Schema for tile response."""
    id: str
    position_x: int
    position_y: int
    terrain_type: str
    description: str
    is_visited: bool
    items: Dict[str, Any] = Field(default_factory=dict)
    enemies: Dict[str, Any] = Field(default_factory=dict)
    exits: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class MapResponse(BaseModel):
    """Schema for map response."""
    tiles: List[TileResponse]
    current_position: Dict[str, int]

    model_config = ConfigDict(from_attributes=True) 