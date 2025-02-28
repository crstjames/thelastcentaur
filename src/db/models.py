from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, JSON, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base, TimestampMixin, GameInstanceMixin
from src.core.models import Direction, TerrainType
from src.game.schemas import GameStatus
import uuid

def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())

class User(TimestampMixin, Base):
    """User model for authentication and game ownership."""
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    game_instances: Mapped[List["GameInstance"]] = relationship(back_populates="user")

class GameInstance(TimestampMixin, Base):
    """Game instance model representing a single game session."""
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"))
    name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    current_position: Mapped[dict] = mapped_column(JSON, default=lambda: {"x": 0, "y": 0})
    game_state: Mapped[dict] = mapped_column(JSON, default={})
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="game_instances")
    tiles: Mapped[List["Tile"]] = relationship(back_populates="game_instance")

class Tile(TimestampMixin, GameInstanceMixin, Base):
    """Tile model representing a single tile in the game map."""
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    position_x: Mapped[int] = mapped_column(nullable=False)
    position_y: Mapped[int] = mapped_column(nullable=False)
    terrain_type: Mapped[TerrainType] = mapped_column(SQLEnum(TerrainType))
    description: Mapped[str] = mapped_column(String(500))
    is_visited: Mapped[bool] = mapped_column(Boolean, default=False)
    game_instance_id: Mapped[str] = mapped_column(ForeignKey("gameinstance.id"), nullable=False)
    
    # Relationships
    game_instance: Mapped["GameInstance"] = relationship(back_populates="tiles")
    
    # JSON fields for complex data
    items: Mapped[dict] = mapped_column(JSON, default={})
    enemies: Mapped[dict] = mapped_column(JSON, default={})
    requirements: Mapped[dict] = mapped_column(JSON, default={})
    environmental_changes: Mapped[dict] = mapped_column(JSON, default={})
    
    # Available exits
    exits: Mapped[List[Direction]] = mapped_column(JSON, default=[])
    
    # Relationships
    history: Mapped[List["TileHistory"]] = relationship(back_populates="tile")

class TileHistory(TimestampMixin, GameInstanceMixin, Base):
    """History model for tracking events on a tile."""
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tile_id: Mapped[str] = mapped_column(ForeignKey("tile.id"))
    event_type: Mapped[str] = mapped_column(String(50))
    event_data: Mapped[dict] = mapped_column(JSON)
    
    # Relationships
    tile: Mapped["Tile"] = relationship(back_populates="history") 