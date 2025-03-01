from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import re

from src.db.models import GameInstance, Tile, TileHistory
from src.core.models import Direction, TerrainType, StoryArea
from src.engine.core.command_parser import CommandParser, CommandType

class CommandService:
    """
    Service for processing and enhancing game commands.
    
    This service extends the functionality of the command parser by:
    1. Adding context-aware command suggestions
    2. Providing help text based on the current game state
    3. Handling special commands that interact with the database
    """
    
    def __init__(self, command_parser: CommandParser, db_session: AsyncSession):
        """Initialize the command service."""
        self.command_parser = command_parser
        self.db_session = db_session
        self.special_commands = {
            "save": self._handle_save_command,
            "help": self._handle_help_command,
            "hint": self._handle_hint_command,
            "map": self._handle_map_command,
        }
    
    async def process_command(self, command_text: str, game_id: str) -> str:
        """Process a command with context awareness and special handling."""
        # Check for special commands first
        command_parts = command_text.strip().lower().split()
        if command_parts and command_parts[0] in self.special_commands:
            return await self.special_commands[command_parts[0]](command_parts[1:], game_id)
        
        # Use the command parser for regular commands
        command = self.command_parser.parse_command(command_text)
        if not command:
            # If command not recognized, try to suggest alternatives
            suggestions = self._suggest_commands(command_text)
            if suggestions:
                return f"Unknown command: '{command_text}'. Did you mean: {', '.join(suggestions)}?"
            return f"Unknown command: '{command_text}'. Type 'help' for a list of commands."
        
        # Execute the command
        result = self.command_parser.execute_command(command)
        
        # Enhance the result with context-aware information
        enhanced_result = await self._enhance_result(result, command, game_id)
        
        return enhanced_result
    
    def _suggest_commands(self, command_text: str) -> List[str]:
        """Suggest similar commands based on input."""
        command_text = command_text.strip().lower()
        
        # Get all available commands
        available_commands = [cmd.value for cmd in CommandType]
        
        # Add direction shortcuts
        direction_shortcuts = {
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
        }
        
        # Add special commands
        special_cmds = list(self.special_commands.keys())
        
        # Combine all commands
        all_commands = available_commands + list(direction_shortcuts.keys()) + list(direction_shortcuts.values()) + special_cmds
        
        # Find similar commands (simple string matching)
        suggestions = []
        for cmd in all_commands:
            # Exact match for first word
            if command_text == cmd:
                return [cmd]  # Exact match, but command parser didn't recognize it
            
            # First few characters match
            if cmd.startswith(command_text):
                suggestions.append(cmd)
            
            # Levenshtein distance would be better here, but this is simpler
            if len(command_text) > 2 and command_text in cmd:
                suggestions.append(cmd)
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    async def _enhance_result(self, result: str, command: Any, game_id: str) -> str:
        """Enhance command result with context-aware information."""
        # Get current tile information
        player = self.command_parser.player
        current_pos = (player.x, player.y)
        
        try:
            stmt = select(Tile).where(
                Tile.game_instance_id == game_id,
                Tile.position_x == current_pos[0],
                Tile.position_y == current_pos[1]
            )
            tile_result = await self.db_session.execute(stmt)
            current_tile = tile_result.scalar_one_or_none()
            
            if not current_tile:
                return result
            
            # Enhance result based on command type
            command_type = getattr(command, "command_type", None)
            
            if command_type == CommandType.LOOK:
                # Enhance look command with tile details
                enhanced = result
                
                # Add information about items if present
                if current_tile.items and len(current_tile.items) > 0:
                    items_desc = self._format_items(current_tile.items)
                    if items_desc:
                        enhanced += f"\n\nYou see: {items_desc}"
                
                # Add information about enemies if present
                if current_tile.enemies and len(current_tile.enemies) > 0:
                    enemies_desc = self._format_enemies(current_tile.enemies)
                    if enemies_desc:
                        enhanced += f"\n\nBeware: {enemies_desc}"
                
                # Add information about exits
                exits_desc = self._format_exits(current_tile.exits)
                if exits_desc:
                    enhanced += f"\n\nExits: {exits_desc}"
                
                return enhanced
            
            elif command_type == CommandType.MOVE:
                # Update tile visited status
                if current_tile and not current_tile.is_visited:
                    current_tile.is_visited = True
                    await self.db_session.commit()
                
                return result
            
            # Default: return original result
            return result
        except Exception as e:
            # Log the error but don't break the game flow
            print(f"Error enhancing result: {str(e)}")
            return result  # Return the original result if enhancement fails
    
    def _format_items(self, items_data: Dict[str, Any]) -> str:
        """Format items data for display."""
        if not items_data or "items" not in items_data or not items_data["items"]:
            return ""
        
        items = items_data["items"]
        if isinstance(items, list) and items:
            return ", ".join([f"{item.get('name', 'Unknown Item')}" for item in items])
        
        return ""
    
    def _format_enemies(self, enemies_data: Dict[str, Any]) -> str:
        """Format enemies data for display."""
        if not enemies_data or "enemies" not in enemies_data or not enemies_data["enemies"]:
            return ""
        
        enemies = enemies_data["enemies"]
        if isinstance(enemies, list) and enemies:
            return ", ".join([f"{enemy.get('name', 'Unknown Enemy')}" for enemy in enemies])
        
        return ""
    
    def _format_exits(self, exits: List[str]) -> str:
        """Format exits for display."""
        if not exits:
            return "No visible exits"
        
        return ", ".join([exit_dir.capitalize() for exit_dir in exits])
    
    async def _handle_save_command(self, args: List[str], game_id: str) -> str:
        """Handle the save command."""
        # Update game instance with current state
        player = self.command_parser.player
        
        stmt = (
            update(GameInstance)
            .where(GameInstance.id == game_id)
            .values(
                current_position={"x": player.x, "y": player.y}
            )
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()
        
        return "Game saved successfully."
    
    async def _handle_help_command(self, args: List[str], game_id: str) -> str:
        """Handle the help command with context-aware help text."""
        # Basic help text
        help_text = """
Available Commands:
------------------
Movement: north (n), south (s), east (e), west (w)
Look: look, examine [object]
Inventory: inventory, take [item], drop [item]
Combat: attack [enemy], defend, dodge
Game: save, help, hint, map

Type 'help [command]' for more information on a specific command.
        """
        
        # Specific command help
        if args:
            specific_cmd = args[0].lower()
            if specific_cmd in ["north", "south", "east", "west", "n", "s", "e", "w"]:
                return "Move in the specified direction if an exit exists."
            elif specific_cmd in ["look", "examine"]:
                return "Look around or examine a specific object. Usage: 'look' or 'examine [object]'"
            elif specific_cmd == "inventory":
                return "Show your current inventory."
            elif specific_cmd in ["take", "get"]:
                return "Take an item from the current location. Usage: 'take [item]'"
            elif specific_cmd == "drop":
                return "Drop an item from your inventory. Usage: 'drop [item]'"
            elif specific_cmd == "attack":
                return "Attack an enemy. Usage: 'attack [enemy]'"
            elif specific_cmd == "save":
                return "Save your current game progress."
            elif specific_cmd == "hint":
                return "Get a hint about what to do next."
            elif specific_cmd == "map":
                return "Display a map of the explored areas."
        
        # Get current tile for context-aware help
        player = self.command_parser.player
        current_pos = (player.x, player.y)
        
        stmt = select(Tile).where(
            Tile.game_instance_id == game_id,
            Tile.position_x == current_pos[0],
            Tile.position_y == current_pos[1]
        )
        tile_result = await self.db_session.execute(stmt)
        current_tile = tile_result.scalar_one_or_none()
        
        if current_tile:
            # Add context-aware suggestions
            context_help = "\nSuggested Actions:\n------------------\n"
            
            # Suggest movement based on available exits
            if current_tile.exits:
                exits_str = ", ".join([f"'{exit_dir}'" for exit_dir in current_tile.exits])
                context_help += f"You can move: {exits_str}\n"
            
            # Suggest examining items if present
            if current_tile.items and "items" in current_tile.items and current_tile.items["items"]:
                items = current_tile.items["items"]
                if items:
                    items_str = ", ".join([f"'{item.get('name', 'item')}'" for item in items])
                    context_help += f"You can examine or take: {items_str}\n"
            
            # Suggest combat if enemies present
            if current_tile.enemies and "enemies" in current_tile.enemies and current_tile.enemies["enemies"]:
                enemies = current_tile.enemies["enemies"]
                if enemies:
                    enemies_str = ", ".join([f"'{enemy.get('name', 'enemy')}'" for enemy in enemies])
                    context_help += f"You can attack: {enemies_str}\n"
            
            help_text += context_help
        
        return help_text
    
    async def _handle_hint_command(self, args: List[str], game_id: str) -> str:
        """Handle the hint command."""
        # Get current game state
        stmt = select(GameInstance).where(GameInstance.id == game_id)
        result = await self.db_session.execute(stmt)
        game_instance = result.scalar_one_or_none()
        
        if not game_instance:
            return "Error: Game instance not found."
        
        # Get current tile
        player = self.command_parser.player
        current_pos = (player.x, player.y)
        
        stmt = select(Tile).where(
            Tile.game_instance_id == game_id,
            Tile.position_x == current_pos[0],
            Tile.position_y == current_pos[1]
        )
        tile_result = await self.db_session.execute(stmt)
        current_tile = tile_result.scalar_one_or_none()
        
        if not current_tile:
            return "I'm not sure where you are. Try looking around."
        
        # Generate hint based on current state
        hint = "Hmm, let me think..."
        
        # Hint based on unexplored exits
        if current_tile.exits:
            hint = f"You might want to explore one of the exits: {', '.join(current_tile.exits)}."
        
        # Hint based on items
        if current_tile.items and "items" in current_tile.items and current_tile.items["items"]:
            items = current_tile.items["items"]
            if items:
                hint = f"There are items here that might be useful: {', '.join([item.get('name', 'item') for item in items])}."
        
        # Hint based on enemies
        if current_tile.enemies and "enemies" in current_tile.enemies and current_tile.enemies["enemies"]:
            enemies = current_tile.enemies["enemies"]
            if enemies:
                hint = f"Be careful! There are enemies nearby: {', '.join([enemy.get('name', 'enemy') for enemy in enemies])}."
        
        return f"Hint: {hint}"
    
    async def _handle_map_command(self, args: List[str], game_id: str) -> str:
        """Handle the map command."""
        # Get all visited tiles for this game
        stmt = select(Tile).where(
            Tile.game_instance_id == game_id,
            Tile.is_visited == True
        )
        result = await self.db_session.execute(stmt)
        visited_tiles = result.scalars().all()
        
        if not visited_tiles:
            return "You haven't explored any areas yet."
        
        # Get current position
        player = self.command_parser.player
        current_pos = (player.x, player.y)
        
        # Find map boundaries
        min_x = min(tile.position_x for tile in visited_tiles)
        max_x = max(tile.position_x for tile in visited_tiles)
        min_y = min(tile.position_y for tile in visited_tiles)
        max_y = max(tile.position_y for tile in visited_tiles)
        
        # Add some padding
        min_x -= 1
        max_x += 1
        min_y -= 1
        max_y += 1
        
        # Create map grid
        map_width = max_x - min_x + 1
        map_height = max_y - min_y + 1
        
        # Create a map representation
        map_grid = []
        for y in range(max_y, min_y - 1, -1):  # Reverse Y to match coordinate system
            row = []
            for x in range(min_x, max_x + 1):
                # Find tile at this position
                tile = next((t for t in visited_tiles if t.position_x == x and t.position_y == y), None)
                
                if (x, y) == current_pos:
                    # Current position
                    row.append("@")
                elif tile:
                    # Visited tile
                    if tile.terrain_type == TerrainType.FOREST:
                        row.append("F")
                    elif tile.terrain_type == TerrainType.CLEARING:
                        row.append("C")
                    elif tile.terrain_type == TerrainType.MOUNTAIN:
                        row.append("M")
                    elif tile.terrain_type == TerrainType.RUINS:
                        row.append("R")
                    elif tile.terrain_type == TerrainType.GRASS:
                        row.append("G")
                    else:
                        row.append(".")
                else:
                    # Unknown tile
                    row.append(" ")
            map_grid.append("".join(row))
        
        # Create map legend
        legend = """
Map Legend:
@ - Your position
F - Forest
C - Clearing
M - Mountain
R - Ruins
G - Grass
        """
        
        # Combine map and legend
        map_display = "\n".join(map_grid) + legend
        
        return f"```\n{map_display}\n```" 