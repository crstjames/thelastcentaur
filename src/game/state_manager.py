from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from datetime import datetime

from src.db.models import GameInstance, Tile, TileHistory
from src.core.models import GameState, TileState, Direction, TerrainType, StoryArea
from src.engine.core.command_parser import CommandParser
from src.engine.core.player import Player
from src.game.map_system import GameMapSystem
from src.game.command_service import CommandService

class GameStateManager:
    """
    Manages game state persistence and transitions.
    
    This class serves as the bridge between the game engine and the database,
    handling serialization/deserialization of game state and coordinating
    state transitions based on player actions.
    """
    
    # Dictionary to store loaded game instances
    _loaded_instances = {}
    
    def __init__(self):
        """Initialize the game state manager."""
        pass
    
    async def initialize_game_instance(self, game_id: str, db_session: AsyncSession) -> None:
        """Initialize a new game instance with a basic world."""
        # Initialize the game world for this instance
        await self._initialize_game_world(game_id, db_session)
    
    async def load_game_instance(self, game_id: str, db_session: AsyncSession) -> Optional[GameInstance]:
        """Load a game instance by ID."""
        # Check if already loaded
        if game_id in self._loaded_instances:
            return self._loaded_instances[game_id]["game_instance"]
        
        stmt = select(GameInstance).where(GameInstance.id == game_id)
        result = await db_session.execute(stmt)
        game_instance = result.scalar_one_or_none()
        
        if game_instance:
            # Initialize game engine components
            map_system = GameMapSystem()
            player = Player(
                map_system,
                game_instance.user_id,
                f"Player_{game_instance.user_id[:8]}"
            )
            command_parser = CommandParser(player)
            command_service = CommandService(command_parser, db_session)
            
            # Store in loaded instances
            self._loaded_instances[game_id] = {
                "game_instance": game_instance,
                "map_system": map_system,
                "player": player,
                "command_parser": command_parser,
                "command_service": command_service,
                "db_session": db_session
            }
            
            # Load game state from database
            await self._load_game_state(game_id)
        
        return game_instance
    
    async def save_game_state(self, game_id: str) -> bool:
        """Save the current game state to the database."""
        if game_id not in self._loaded_instances:
            return False
        
        instance_data = self._loaded_instances[game_id]
        player = instance_data["player"]
        map_system = instance_data["map_system"]
        db_session = instance_data["db_session"]
        
        # Get player position
        x, y = player.state.position
        
        # Serialize game state
        game_state = self._serialize_game_state(game_id)
        
        # Update game instance
        stmt = (
            update(GameInstance)
            .where(GameInstance.id == game_id)
            .values(
                current_position={"x": x, "y": y},
                game_state=game_state,
                updated_at=datetime.utcnow()
            )
        )
        await db_session.execute(stmt)
        await db_session.commit()
        
        return True
    
    async def execute_command(self, game_id: str, command_text: str) -> str:
        """Execute a command and update game state."""
        if game_id not in self._loaded_instances:
            return "Game not loaded. Please load a game instance first."
        
        instance_data = self._loaded_instances[game_id]
        command_service = instance_data["command_service"]
        
        # Use the command service to process the command
        result = await command_service.process_command(command_text, game_id)
        
        # Save game state after command execution
        await self.save_game_state(game_id)
        
        # Record relevant events in tile history
        await self._record_tile_history(game_id, command_text, result)
        
        return result
    
    async def get_map(self, game_id: str) -> Dict[str, Any]:
        """Get the current game map."""
        if game_id not in self._loaded_instances:
            return {"error": "Game not loaded"}
        
        instance_data = self._loaded_instances[game_id]
        player = instance_data["player"]
        db_session = instance_data["db_session"]
        
        # Get all tiles for this game instance
        stmt = select(Tile).where(Tile.game_instance_id == game_id)
        result = await db_session.execute(stmt)
        tiles = result.scalars().all()
        
        # Only include visited tiles
        visited_tiles = [tile for tile in tiles if tile.is_visited]
        
        # Create tile data
        tile_data = []
        for tile in visited_tiles:
            tile_data.append({
                "id": tile.id,
                "position_x": tile.position_x,
                "position_y": tile.position_y,
                "terrain_type": tile.terrain_type.value,
                "description": tile.description,
                "is_visited": tile.is_visited,
                "items": tile.items,
                "enemies": tile.enemies,
                "exits": tile.exits
            })
        
        # Get player position from state
        x, y = player.state.position
        
        return {
            "tiles": tile_data,
            "current_position": {"x": x, "y": y}
        }
    
    async def _initialize_game_world(self, game_id: str, db_session: AsyncSession) -> None:
        """Initialize the game world for a new game instance."""
        # Create starting area tiles
        starting_area = StoryArea.AWAKENING_WOODS
        
        # Create a 5x5 starting area
        for x in range(-2, 3):
            for y in range(-2, 3):
                # Determine terrain type based on position
                if x == 0 and y == 0:
                    terrain = TerrainType.CLEARING  # Starting position
                elif abs(x) == 2 or abs(y) == 2:
                    terrain = TerrainType.FOREST    # Border
                else:
                    # Mix of terrain types for inner area
                    if (x + y) % 2 == 0:
                        terrain = TerrainType.GRASS
                    else:
                        terrain = TerrainType.FOREST
                
                # Determine available exits
                exits = []
                if x < 2:  # Can go east if not at eastern edge
                    exits.append(Direction.EAST)
                if x > -2:  # Can go west if not at western edge
                    exits.append(Direction.WEST)
                if y < 2:  # Can go north if not at northern edge
                    exits.append(Direction.NORTH)
                if y > -2:  # Can go south if not at southern edge
                    exits.append(Direction.SOUTH)
                
                # Create tile description
                if x == 0 and y == 0:
                    description = "A small clearing in the forest. Sunlight filters through the canopy above."
                elif terrain == TerrainType.FOREST:
                    description = "Dense forest surrounds you. The trees seem to watch your every move."
                else:
                    description = "A grassy area with scattered trees. The wind rustles through the leaves."
                
                # Create the tile
                tile = Tile(
                    game_instance_id=game_id,
                    position_x=x,
                    position_y=y,
                    terrain_type=terrain,
                    description=description,
                    is_visited=x == 0 and y == 0,  # Only starting tile is visited
                    exits=exits,
                    items={},
                    enemies={},
                    requirements={},
                    environmental_changes={}
                )
                db_session.add(tile)
        
        await db_session.commit()
        
        # Add some items and enemies to make the world more interesting
        await self._populate_world(game_id, db_session)
    
    async def _populate_world(self, game_id: str, db_session: AsyncSession) -> None:
        """Populate the world with items and enemies."""
        # Add a sword in the north tile
        north_tile = await self._get_tile(game_id, 0, 1, db_session)
        if north_tile:
            north_tile.items = {
                "items": [
                    {
                        "id": "sword_01",
                        "name": "Rusty Sword",
                        "description": "An old sword with a rusty blade. Still sharp enough to be useful.",
                        "type": "weapon",
                        "properties": {"damage": 5}
                    }
                ]
            }
        
        # Add a health potion in the east tile
        east_tile = await self._get_tile(game_id, 1, 0, db_session)
        if east_tile:
            east_tile.items = {
                "items": [
                    {
                        "id": "potion_01",
                        "name": "Health Potion",
                        "description": "A small vial containing a red liquid. It smells like herbs and berries.",
                        "type": "consumable",
                        "properties": {"health_restore": 20}
                    }
                ]
            }
        
        # Add a wolf in the west tile
        west_tile = await self._get_tile(game_id, -1, 0, db_session)
        if west_tile:
            west_tile.enemies = {
                "enemies": [
                    {
                        "id": "wolf_01",
                        "name": "Forest Wolf",
                        "description": "A gray wolf with piercing yellow eyes. It growls as you approach.",
                        "health": 15,
                        "damage": 3,
                        "drops": ["wolf_pelt"]
                    }
                ]
            }
        
        # Add a mysterious note in the south tile
        south_tile = await self._get_tile(game_id, 0, -1, db_session)
        if south_tile:
            south_tile.items = {
                "items": [
                    {
                        "id": "note_01",
                        "name": "Mysterious Note",
                        "description": "A weathered piece of parchment with strange symbols.",
                        "type": "quest_item",
                        "properties": {"text": "Beware the ancient ruins to the east. The last of the centaurs guards a powerful artifact."}
                    }
                ]
            }
        
        await db_session.commit()
    
    async def _get_tile(self, game_id: str, x: int, y: int, db_session: AsyncSession) -> Optional[Tile]:
        """Get a tile by position."""
        stmt = select(Tile).where(
            Tile.game_instance_id == game_id,
            Tile.position_x == x,
            Tile.position_y == y
        )
        result = await db_session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _load_game_state(self, game_id: str) -> None:
        """Load game state from database."""
        if game_id not in self._loaded_instances:
            return
        
        instance_data = self._loaded_instances[game_id]
        player = instance_data["player"]
        map_system = instance_data["map_system"]
        db_session = instance_data["db_session"]
        game_instance = instance_data["game_instance"]
        
        # Load player position
        pos = game_instance.current_position
        if pos:
            x = pos.get("x", 0)
            y = pos.get("y", 0)
            player.state.position = (x, y)
        
        # Load game state
        game_state = game_instance.game_state
        if game_state:
            # Load inventory
            if "inventory" in game_state:
                player.state.inventory = game_state["inventory"]
            
            # Load visited tiles
            if "visited_tiles" in game_state:
                for tile_pos in game_state["visited_tiles"]:
                    x, y = tile_pos
                    map_system.mark_tile_visited(x, y)
            
            # Load other player stats
            if "player_stats" in game_state and hasattr(player.state, "stats"):
                for key, value in game_state["player_stats"].items():
                    if hasattr(player.state.stats, key):
                        setattr(player.state.stats, key, value)
        
        # Load tiles from database
        stmt = select(Tile).where(Tile.game_instance_id == game_instance.id)
        result = await db_session.execute(stmt)
        tiles = result.scalars().all()
        
        # Add tiles to map system
        for tile in tiles:
            tile_state = TileState(
                position=(tile.position_x, tile.position_y),
                terrain_type=tile.terrain_type,
                area=StoryArea.AWAKENING_WOODS,  # Default for now, should be stored in tile
                description=tile.description,
                is_visited=tile.is_visited,
                items=tile.items.get("items", []),
                enemies=tile.enemies.get("enemies", []),
                environmental_changes=tile.environmental_changes.get("changes", []),
                events=[],
                requirements=tile.requirements,
                exits=tile.exits
            )
            map_system.add_tile(tile_state)
    
    def _serialize_game_state(self, game_id: str) -> Dict[str, Any]:
        """Serialize the current game state to a dictionary."""
        if game_id not in self._loaded_instances:
            return {}
        
        instance_data = self._loaded_instances[game_id]
        player = instance_data["player"]
        map_system = instance_data["map_system"]
        
        # Convert visited tiles set to list of tuples for JSON serialization
        visited_tiles = [list(pos) for pos in map_system.visited_tiles]
        
        # Get player position from state
        x, y = player.state.position
        
        return {
            "player_position": [x, y],
            "inventory": player.state.inventory,
            "visited_tiles": visited_tiles,
            "player_stats": player.state.stats.__dict__ if hasattr(player.state, "stats") else {},
            "game_time": player.time_system.current_time.isoformat() if hasattr(player, "time_system") and hasattr(player.time_system, "current_time") else None,
            "active_quests": player.state.active_quests if hasattr(player.state, "active_quests") else [],
            "completed_quests": player.state.completed_quests if hasattr(player.state, "completed_quests") else []
        }
    
    async def _record_tile_history(self, game_id: str, command: str, result: str) -> None:
        """Record relevant events in tile history."""
        if game_id not in self._loaded_instances:
            return
        
        instance_data = self._loaded_instances[game_id]
        player = instance_data["player"]
        db_session = instance_data["db_session"]
        
        # Get player position
        x, y = player.state.position
        
        # Only record certain types of commands
        record_types = ["move", "take", "drop", "alter", "mark", "attack"]
        should_record = any(cmd_type in command.lower() for cmd_type in record_types)
        
        if should_record:
            # Get current tile
            stmt = select(Tile).where(
                Tile.game_instance_id == game_id,
                Tile.position_x == x,
                Tile.position_y == y
            )
            result_query = await db_session.execute(stmt)
            tile = result_query.scalar_one_or_none()
            
            if tile:
                # Create history entry
                history = TileHistory(
                    tile_id=tile.id,
                    game_instance_id=game_id,
                    event_type="player_action",
                    event_data={
                        "command": command,
                        "result": result,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                db_session.add(history)
                await db_session.commit() 