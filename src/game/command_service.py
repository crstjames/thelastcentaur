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
    
    async def process_command(self, command_text: str, game_id: str, db: AsyncSession = None) -> str:
        """Process a command with context awareness and special handling."""
        print(f"Command Service process_command: {command_text}")
        if not command_text:
            return "Please enter a command."
        
        # Normalize the command
        command_text = command_text.strip().lower()
        command_parts = command_text.split()
        
        # Handle special debug commands
        if command_parts and command_parts[0].startswith("debug_"):
            print(f"Processing debug command: {command_text}")
            
            # Debug command to teleport to a specific area
            if command_parts[0] == "debug_teleport" and len(command_parts) > 1:
                return await self._handle_debug_teleport(command_parts[1:], game_id)
            
            # Debug command to set position directly
            if command_parts[0] == "debug_set_position" and len(command_parts) > 1:
                return await self._handle_debug_set_position(command_parts[1:], game_id)
                
            # Debug command to report current location
            if command_parts[0] == "debug_location":
                return await self._handle_debug_location(command_parts[1:], game_id)
        
        # Handle direction shortcuts for movement
        direction_shortcuts = {
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west"
        }
        
        # Handle explicit movement commands
        if command_parts and command_parts[0] == "move" and len(command_parts) > 1:
            direction = command_parts[1]
            # Check if it's a valid direction
            valid_directions = ["north", "south", "east", "west", "n", "s", "e", "w"]
            if direction in valid_directions:
                # Convert shorthand directions to full names
                if direction in direction_shortcuts:
                    direction = direction_shortcuts[direction]
                # Use just the direction as the command
                print(f"Movement command detected: {command_parts[0]} {direction} -> {direction}")
                command_text = direction
        
        # Use the command parser for regular commands
        print(f"Parsing command: {command_text}")
        command = self.command_parser.parse_command(command_text)
        print(f"Parsed command type: {command.type if command else 'None'}")
        
        if not command:
            # If command not recognized, try to suggest alternatives
            print("Command not recognized")
            suggestions = self._suggest_commands(command_text)
            if suggestions:
                return f"Unknown command: '{command_text}'. Did you mean: {', '.join(suggestions)}?"
            return f"Unknown command: '{command_text}'. Type 'help' for a list of commands."
        
        # Execute the command
        result = self.command_parser.execute_command(command)
        
        # Enhance the result with context-aware information
        enhanced_result = await self._enhance_result(result, command, game_id)
        
        # Update player position if this was a movement command
        if command.type == CommandType.MOVE:
            await self._update_player_position(command, game_id)
        
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
        
        # Add combat command aliases
        combat_aliases = {
            "fight": "attack",
            "battle": "attack",
            "strike": "attack"
        }
        
        # Combine all commands
        all_commands = (available_commands + 
                       list(direction_shortcuts.keys()) + 
                       list(direction_shortcuts.values()) + 
                       special_cmds + 
                       list(combat_aliases.keys()))
        
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
    
    async def _update_player_position(self, command, game_id: str):
        """Update the player's position after movement."""
        try:
            # Get the current game state
            async with self.db_session.begin():
                game_query = select(GameInstance).where(GameInstance.id == game_id)
                game_result = await self.db_session.execute(game_query)
                game = game_result.scalar_one_or_none()
                
                if not game:
                    print(f"Game not found: {game_id}")
                    return
                
                # Get the current position
                current_position = game.player_state.get("location", "0,0")
                x, y = map(int, current_position.split(","))
                
                # Update position based on direction
                direction = ""
                if command.args and len(command.args) > 0:
                    direction = str(command.args[0]).lower()
                
                new_x, new_y = x, y
                
                if direction == "north":
                    new_y += 1
                elif direction == "south":
                    new_y -= 1
                elif direction == "east":
                    new_x += 1
                elif direction == "west":
                    new_x -= 1
                
                # Ensure we don't move out of bounds
                new_x = max(0, min(9, new_x))
                new_y = max(0, min(9, new_y))
                
                # Update the player's position
                new_position = f"{new_x},{new_y}"
                game.player_state["location"] = new_position
                
                # Update the game state
                await self.db_session.commit()
                print(f"Updated player position to {new_position}")
                
        except Exception as e:
            print(f"Error updating player position: {e}")
            await self.db_session.rollback()
    
    async def _handle_debug_teleport(self, args: List[str], game_id: str) -> str:
        """Handle the debug_teleport command."""
        if not args:
            return "Debug teleport command requires an area name"
        
        area_name = ' '.join(args).upper()  # Convert to uppercase for matching with StoryArea enums
        
        # Find the area in the map
        try:
            # Get the current game state
            async with self.db_session.begin():
                game_query = select(GameInstance).where(GameInstance.id == game_id)
                game_result = await self.db_session.execute(game_query)
                game = game_result.scalar_one_or_none()
                
                if not game:
                    print(f"Game not found: {game_id}")
                    return "Game not found"
                
                # Find the area position
                from src.engine.core.models import StoryArea
                from src.engine.core.map_system import NAMED_AREAS
                
                # Convert from string to enum value
                try:
                    area_enum = getattr(StoryArea, area_name)
                except AttributeError:
                    return f"Area {area_name} not found. Available areas: {', '.join([a.name for a in StoryArea])}"
                
                # Find the position for this area
                area_position = None
                for pos, area in NAMED_AREAS.items():
                    if area == area_enum:
                        area_position = pos
                        break
                
                if not area_position:
                    return f"Position for area {area_name} not found in map data"
                
                # Update the player's position
                x, y = area_position
                game.current_position = {"x": x, "y": y}
                game.player_state["position"] = {"x": x, "y": y}
                
                if "game_state" not in game.player_state:
                    game.player_state["game_state"] = {}
                
                if "current_area" not in game.player_state["game_state"]:
                    game.player_state["game_state"]["current_area"] = {}
                
                game.player_state["game_state"]["current_area"] = area_enum.value
                
                # Update the game state
                await self.db_session.commit()
                print(f"DEBUG: Teleported player to {area_name} at position {area_position}")
                
                return f"Teleported to {area_name} at position {x},{y}"
        except Exception as e:
            print(f"Error in debug teleport: {str(e)}")
            return f"Error in debug teleport: {str(e)}"
    
    async def _handle_debug_set_position(self, args: List[str], game_id: str) -> str:
        """
        Handle the debug_set_position command, which sets the player's position to a named area.
        
        Args:
            args: List of command arguments (should contain the area name)
            game_id: ID of the current game
            
        Returns:
            Response message
        """
        if not args:
            return "Invalid command. Usage: debug_set_position <area_name>"
            
        area_name = args[0].upper()
        
        try:
            # Load game state
            game_manager = await self._get_game_manager(game_id)
            player = game_manager.get_player()
            map_system = game_manager.get_map_system()
            
            try:
                area_enum = getattr(StoryArea, area_name)
            except AttributeError:
                return f"Invalid command. Unknown area: {area_name.lower()}"
            
            # Find the position for this area
            area_position = None
            for pos, area in NAMED_AREAS.items():
                if area == area_enum:
                    area_position = pos
                    break
                    
            if not area_position:
                return f"Could not find coordinates for area {area_name}"
                
            # Set player position and mark as visited
            player.state.position = area_position
            player.state.current_area = area_enum
            player.state.visited_tiles.add(area_position)
            
            # Update the current_tile if we have the method
            if hasattr(player, 'update_current_tile') and callable(getattr(player, 'update_current_tile')):
                player.update_current_tile()
                print(f"DEBUG: Player tile updated via update_current_tile")
            else:
                # Try to get the tile from map system directly
                area_node = map_system.get_area_by_position(area_position)
                if area_node and hasattr(player.state, 'current_tile'):
                    player.state.current_tile = area_node
                    print(f"DEBUG: Player tile updated manually: {area_node.area}")
            
            # Save the game state
            await game_manager.save_game_state()
            
            print(f"DEBUG: Set player position to {area_name} at position {area_position}")
            
            # Return a more detailed message
            return f"Teleported to {area_name} at position {area_position[0]},{area_position[1]}. Current area updated to {area_enum.name}."
        except Exception as e:
            print(f"Error in debug set_position: {str(e)}")
            return f"Error: {str(e)}"

    async def _handle_debug_location(self, args: List[str], game_id: str) -> str:
        """
        Handle the debug_location command, which reports the player's current area name and coordinates.
        
        Args:
            args: List of command arguments (not used)
            game_id: ID of the current game
            
        Returns:
            Response message with current location details
        """
        try:
            # Load game state
            game_manager = await self._get_game_manager(game_id)
            player = game_manager.get_player()
            map_system = game_manager.get_map_system()
            
            # Get current position and area
            current_position = player.state.position
            current_area = player.state.current_area
            
            # Get tile info
            current_tile = None
            x, y = current_position
            try:
                current_tile = map_system.get_tile(x, y)
            except Exception as e:
                print(f"Error getting tile: {e}")
            
            # Check if position is in NAMED_AREAS
            from src.engine.core.map_system import NAMED_AREAS
            area_name = "Unnamed Area"
            if current_position in NAMED_AREAS:
                area_name = NAMED_AREAS[current_position].name
            
            # Build the response with detailed information
            response = [
                f"DEBUG LOCATION INFO:",
                f"Current position: {current_position[0]},{current_position[1]}",
                f"Current area: {current_area.name if current_area else 'Unknown'}"
            ]
            
            # Add named area info
            response.append(f"Named area: {area_name}")
            
            # Add tile info if available
            if current_tile:
                tile_type = getattr(current_tile, 'type', 'Unknown')
                tile_area = getattr(current_tile, 'area', None)
                response.append(f"Tile type: {tile_type}")
                if tile_area:
                    response.append(f"Tile area: {tile_area.name}")
            
            # Add visited tiles count
            visited_tiles_count = len(player.state.visited_tiles) if hasattr(player.state, 'visited_tiles') else 0
            response.append(f"Visited tiles: {visited_tiles_count}")
            
            return "\n".join(response)
        except Exception as e:
            print(f"Error in debug_location: {str(e)}")
            return f"Error in debug_location: {str(e)}" 