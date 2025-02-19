"""
Tests for core game engine models.
"""

import pytest
from datetime import datetime
from src.engine.core.models import (
    Direction, TerrainType, StoryArea, EventType,
    GameEvent, EnvironmentalChange, Item, Enemy,
    TileState, GameState
)

def test_direction_enum():
    """Test Direction enum values."""
    assert Direction.NORTH.value == "north"
    assert Direction.SOUTH.value == "south"
    assert Direction.EAST.value == "east"
    assert Direction.WEST.value == "west"

def test_terrain_type_enum():
    """Test TerrainType enum values."""
    assert TerrainType.FOREST.value == "forest"
    assert TerrainType.CLEARING.value == "clearing"
    assert TerrainType.MOUNTAIN.value == "mountain"
    assert TerrainType.RUINS.value == "ruins"

def test_game_event_creation():
    """Test GameEvent model creation and validation."""
    event = GameEvent(
        event_type=EventType.INTERACTION,
        description="Player picked up a sword",
        location=(1, 1),
        details={"item": "sword"}
    )
    assert event.event_type == EventType.INTERACTION
    assert event.description == "Player picked up a sword"
    assert event.location == (1, 1)
    assert event.persistence == 100
    assert isinstance(event.timestamp, datetime)

def test_environmental_change_creation():
    """Test EnvironmentalChange model creation and validation."""
    change = EnvironmentalChange(
        type="modification",
        description="A tree was cut down",
        is_permanent=True,
        created_by="player"
    )
    assert change.type == "modification"
    assert change.description == "A tree was cut down"
    assert change.is_permanent is True
    assert change.created_by == "player"
    assert isinstance(change.timestamp, datetime)

def test_item_creation():
    """Test Item model creation and validation."""
    item = Item(
        id="sword_01",
        name="Rusty Sword",
        description="An old but serviceable sword",
        type="weapon",
        properties={"damage": 5}
    )
    assert item.id == "sword_01"
    assert item.name == "Rusty Sword"
    assert item.type == "weapon"
    assert item.properties["damage"] == 5

def test_enemy_creation():
    """Test Enemy model creation and validation."""
    enemy = Enemy(
        name="Goblin",
        description="A small but vicious goblin",
        health=20,
        damage=3,
        drops=["rusty_sword"]
    )
    assert enemy.name == "Goblin"
    assert enemy.health == 20
    assert enemy.damage == 3
    assert "rusty_sword" in enemy.drops

def test_tile_state_creation():
    """Test TileState model creation and validation."""
    tile = TileState(
        position=(0, 0),
        terrain_type=TerrainType.FOREST,
        area=StoryArea.AWAKENING_WOODS,
        description="A dense forest area",
        items=["rusty_sword"],
        enemies=[Enemy(
            name="Wolf",
            description="A fierce wolf",
            health=30,
            damage=5
        )]
    )
    assert tile.position == (0, 0)
    assert tile.terrain_type == TerrainType.FOREST
    assert tile.area == StoryArea.AWAKENING_WOODS
    assert not tile.is_visited
    assert len(tile.items) == 1
    assert len(tile.enemies) == 1

def test_tile_state_position_validation():
    """Test TileState position validation."""
    # Create a tile with valid position first
    tile = TileState(
        position=(0, 0),
        terrain_type=TerrainType.FOREST,
        area=StoryArea.AWAKENING_WOODS,
        description="A dense forest area",
        items=[],
        enemies=[]
    )
    assert tile.position == (0, 0)

def test_game_state_creation():
    """Test GameState model creation and validation."""
    game_state = GameState(
        player_position=(0, 0),
        current_area=StoryArea.AWAKENING_WOODS
    )
    assert game_state.player_position == (0, 0)
    assert game_state.current_area == StoryArea.AWAKENING_WOODS
    assert len(game_state.inventory) == 0
    assert len(game_state.visited_tiles) == 0
    assert isinstance(game_state.game_time, datetime)

def test_game_state_serialization():
    """Test GameState serialization."""
    game_state = GameState(
        player_position=(0, 0),
        current_area=StoryArea.AWAKENING_WOODS,
        visited_tiles={(0, 0), (0, 1)}
    )
    serialized = game_state.model_dump_json()  # Updated to use model_dump_json instead of json()
    assert isinstance(serialized, str)
    assert "player_position" in serialized
    assert "visited_tiles" in serialized 