from typing import Dict, List, Optional, Set, Tuple, Any
from src.engine.core.map_system import MapSystem
from src.engine.core.models import TileState, StoryArea, TerrainType

class GameMapSystem(MapSystem):
    """
    Extended MapSystem for game state management.
    
    This class extends the engine's MapSystem to add methods needed for
    game state persistence and loading.
    """
    
    def __init__(self):
        """Initialize the game map system."""
        super().__init__()
        self.tiles: Dict[Tuple[int, int], TileState] = {}
        self.visited_tiles: Set[Tuple[int, int]] = set()
    
    def add_tile(self, tile_state: TileState) -> None:
        """Add a tile to the map."""
        self.tiles[tile_state.position] = tile_state
        if tile_state.is_visited:
            self.visited_tiles.add(tile_state.position)
    
    def mark_tile_visited(self, x: int, y: int) -> None:
        """Mark a tile as visited."""
        position = (x, y)
        self.visited_tiles.add(position)
        if position in self.tiles:
            self.tiles[position].is_visited = True
    
    def get_tile(self, x: int, y: int) -> Optional[TileState]:
        """Get a tile by position."""
        return self.tiles.get((x, y))
    
    def get_all_tiles(self) -> List[TileState]:
        """Get all tiles in the map."""
        return list(self.tiles.values()) 