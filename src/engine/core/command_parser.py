"""
Command parser for The Last Centaur.

This module handles parsing and executing player commands.
Commands are simple text inputs that control Centaur Prime's actions.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

from .models import Direction
from .player import Player
from .world_design import WORLD_NPCS

class CommandType(str, Enum):
    """Types of commands available to the player."""
    # Movement Commands
    MOVE = "move"
    MEDITATE = "meditate"
    REST = "rest"
    
    # Information Commands
    LOOK = "look"
    STATUS = "status"
    HELP = "help"
    INVENTORY = "inventory"
    MAP = "map"
    ACHIEVEMENTS = "achievements"
    TITLES = "titles"
    LEADERBOARD = "leaderboard"
    
    # Item Commands
    TAKE = "take"      # Take item from ground
    DROP = "drop"      # Drop item to ground
    GATHER = "gather"  # Gather environmental resources
    
    # Environment Commands
    MARK = "mark"      # Leave a mark/sign
    DRAW = "draw"      # Draw something
    WRITE = "write"    # Write a message
    ALTER = "alter"    # Change environment
    
    # Combat Commands
    ATTACK = "attack"
    DEFEND = "defend"
    DODGE = "dodge"
    SPECIAL = "special"
    
    # Roleplay Commands
    EMOTE = "emote"
    SAY = "say"
    THINK = "think"
    TALK = "talk"      # Talk to NPCs
    
    # Test Commands
    DEFEAT = "defeat"  # Instantly defeat an enemy

@dataclass
class Command:
    """Represents a parsed command with its type and arguments."""
    type: CommandType
    args: List[str] = field(default_factory=list)

class CommandParser:
    """Handles parsing and executing player commands."""
    
    # Command type to function mapping
    DIRECTION_MAP = {
        "n": Direction.NORTH,
        "north": Direction.NORTH,
        "s": Direction.SOUTH,
        "south": Direction.SOUTH,
        "e": Direction.EAST,
        "east": Direction.EAST,
        "w": Direction.WEST,
        "west": Direction.WEST
    }
    
    # NPC interaction aliases
    NPC_ALIASES = ["talk", "speak", "converse"]
    
    def __init__(self, player: Player):
        self.player = player
    
    def parse_command(self, command: str) -> Optional[Command]:
        """Parse a command string into a Command object."""
        if not command:
            return None
            
        # Split command into parts
        parts = command.lower().split()
        if not parts:
            return None
            
        # Check for movement commands
        if parts[0] in self.DIRECTION_MAP:
            return Command(type=CommandType.MOVE, args=[parts[0]])
            
        # Check for look command
        if parts[0] == "look":
            if len(parts) > 1:
                return Command(type=CommandType.LOOK, args=parts[1:])
            return Command(type=CommandType.LOOK)
            
        # Check for inventory command
        if parts[0] == "inventory" or parts[0] == "i":
            return Command(type=CommandType.INVENTORY)
            
        # Check for take command
        if parts[0] == "take" and len(parts) > 1:
            return Command(type=CommandType.TAKE, args=parts[1:])
            
        # Check for drop command
        if parts[0] == "drop" and len(parts) > 1:
            return Command(type=CommandType.DROP, args=parts[1:])
            
        # Check for gather command
        if parts[0] == "gather" and len(parts) > 1:
            return Command(type=CommandType.GATHER, args=parts[1:])
            
        # Check for defeat command
        if parts[0] == "defeat" and len(parts) > 1:
            return Command(type=CommandType.DEFEAT, args=parts[1:])
            
        # Check for rest command
        if parts[0] == "rest":
            return Command(type=CommandType.REST)
            
        # Check for meditate command
        if parts[0] == "meditate":
            duration = int(parts[1]) if len(parts) > 1 else None
            return Command(type=CommandType.MEDITATE, args=[str(duration)] if duration else [])
            
        # Check for achievements command
        if parts[0] == "achievements":
            return Command(type=CommandType.ACHIEVEMENTS)
            
        # Check for titles command
        if parts[0] == "titles":
            return Command(type=CommandType.TITLES, args=parts[1:] if len(parts) > 1 else [])
            
        # Check for select title command
        if parts[0] == "select" and len(parts) > 2 and parts[1] == "title":
            return Command(type=CommandType.TITLES, args=["select", " ".join(parts[2:])])
            
        # Check for status command
        if parts[0] == "status" or parts[0] == "stats":
            return Command(type=CommandType.STATUS)
            
        # Check for attack command
        if parts[0] == "attack" and len(parts) > 1:
            return Command(type=CommandType.ATTACK, args=parts[1:])
            
        # Check for NPC interactions
        if parts[0] in self.NPC_ALIASES and len(parts) > 1:
            npc_name = " ".join(parts[1:])
            if self.player.state.current_tile and npc_name in self.player.state.current_tile.npcs:
                return Command(type=CommandType.TALK, args=[npc_name])
            return None
            
        return None
    
    def execute_command(self, command: Command) -> str:
        """Execute a parsed command."""
        try:
            if command.type == CommandType.MOVE:
                # Get direction from first argument
                direction_str = command.args[0] if command.args else None
                if not direction_str:
                    return "Which direction?"
                
                # Convert to Direction enum
                try:
                    direction = self.DIRECTION_MAP[direction_str.lower()]
                except KeyError:
                    return f"Unknown direction: {direction_str}"
                
                # Try to move
                success, message = self.player.move(direction)
                return message
                
            elif command.type == CommandType.LOOK:
                current_tile = self.player.state.current_tile
                if not current_tile:
                    return "Nothing to see here."
                description = current_tile.get_description()
                time_desc = self.player.time_system.time.get_time_description()
                return f"{description}\n\n{time_desc}"
                
            elif command.type == CommandType.TALK:
                if not self.player.state.current_tile:
                    return "You are in an unknown area."
                    
                npc_name = command.args[0] if command.args else None
                if not npc_name:
                    return "Talk to whom?"
                    
                if npc_name not in self.player.state.current_tile.npcs:
                    return "There is no one here to talk to."
                    
                # Get NPC dialogue from world design
                from .world_design import WORLD_NPCS
                npc_data = next((npc for npc in WORLD_NPCS if npc.id == npc_name), None)
                if not npc_data:
                    return "That person seems unable to talk right now."
                
                # Give quest items to player
                for item in npc_data.quest_items:
                    if item not in self.player.state.inventory:
                        self.player.state.inventory.append(item)
                    
                return npc_data.dialogue["start"]
                
            elif command.type == CommandType.STATUS:
                return self.player.get_status()
            
            elif command.type == CommandType.HELP:
                return self._get_help_text()
            
            elif command.type == CommandType.INVENTORY:
                return "Inventory: " + ", ".join(self.player.state.inventory)
            
            elif command.type == CommandType.MAP:
                return self.execute_map()
            
            elif command.type == CommandType.ACHIEVEMENTS:
                return self.player.get_achievements()
            
            elif command.type == CommandType.LEADERBOARD:
                category = command.args[0] if command.args else None
                return self.player.get_leaderboard(category)
            
            elif command.type == CommandType.REST:
                success, message = self.player.rest()
                return message
            
            elif command.type == CommandType.TAKE:
                return self.handle_take_command(command.args)
            
            elif command.type == CommandType.DROP:
                return self.handle_drop_command(command.args)
            
            elif command.type == CommandType.GATHER:
                return self.handle_gather_command(command.args)
            
            elif command.type in [CommandType.MARK, CommandType.DRAW, CommandType.WRITE, CommandType.ALTER]:
                return self.handle_environment_change(command.type, command.args)
            
            elif command.type in [CommandType.ATTACK, CommandType.DEFEND, CommandType.DODGE, CommandType.SPECIAL]:
                return self.handle_combat_command(command.type, command.args)
            
            elif command.type in [CommandType.EMOTE, CommandType.SAY, CommandType.THINK]:
                return self.handle_roleplay_command(command.type, command.args)
            
            elif command.type == CommandType.DEFEAT:
                if not command.args:
                    return "Defeat what?"
                target = " ".join(command.args)
                return self.player.combat_victory(target)
            
            elif command.type == CommandType.MEDITATE:
                # Check if a duration was provided
                if command.args and command.args[0].isdigit():
                    duration = int(command.args[0])
                    success, message = self.player.meditate(duration)
                else:
                    success, message = self.player.meditate()
                return message
            
            elif command.type == CommandType.TITLES:
                if not command.args:
                    return self.player.title_system.get_title_status()
                if command.args[0] == "select" and len(command.args) > 1:
                    success, message = self.player.title_system.equip_title(command.args[1])
                    return message
                return self.player.title_system.get_title_status()
            
            return "Unknown command."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    def execute_map(self) -> str:
        """Execute the map command."""
        # This would be implemented to show visited areas
        visited = self.player.get_movement_history()
        map_view = []
        for y in range(9, -1, -1):  # 9 to 0 for y axis
            row = []
            for x in range(10):  # 0 to 9 for x axis
                if (x, y) == self.player.get_current_position():
                    row.append("@")  # Player position
                elif (x, y) in visited:
                    row.append("·")  # Visited tile
                else:
                    row.append(" ")  # Undiscovered
            map_view.append("".join(row))
        return "\n".join(map_view)
    
    def _get_help_text(self) -> str:
        """Get help text with available commands."""
        help_text = """
Available Commands:

Movement:
- move (n/s/e/w) : Move in a direction
- meditate       : Recover stamina through meditation

Information:
- look [dir]     : Examine current area or look in a direction
- status         : Show your current stats
- inventory      : Show your inventory
- map           : Show discovered areas

Items:
- take/get [item]: Pick up an item
- drop [item]    : Drop an item
- gather [type]  : Gather environmental resources

Environment:
- mark [desc]    : Leave a mark or sign
- draw [desc]    : Draw something
- write [text]   : Write a message
- alter [desc]   : Change the environment

Combat:
- attack [target]: Attack an enemy
- defend         : Take defensive stance
- dodge          : Prepare to dodge
- special        : Use special ability

Roleplay:
- emote [action] : Perform an action
- say [text]     : Say something
- think [text]   : Express thoughts

Test Commands:
- defeat [enemy] : Instantly defeat an enemy (testing only)

Shortcuts:
- Movement: n, s, e, w
- Look: l
- Inventory: i
- Map: m
- Help: h, ?
"""
        return help_text
    
    def handle_take_command(self, args: List[str]) -> str:
        """Handle taking items from the environment."""
        item_name = " ".join(args)
        current_tile = self.player.state.current_tile
        
        if not current_tile:
            return "You are in an unknown area."
        
        # Check if item exists in tile
        if item_name not in current_tile.items:
            return f"There is no {item_name} here."
        
        # Check inventory capacity
        if self.player.state.stats.current_inventory_weight >= self.player.state.stats.inventory_capacity:
            return "Your inventory is full."
        
        # Add to inventory and remove from tile
        self.player.state.inventory.append(item_name)
        current_tile.items.remove(item_name)
        
        return f"You take the {item_name}."
    
    def handle_drop_command(self, args: List[str]) -> str:
        """Handle dropping items to the environment."""
        item_name = " ".join(args)
        
        if item_name not in self.player.state.inventory:
            return f"You don't have a {item_name}."
        
        # Remove from inventory and add to tile
        self.player.state.inventory.remove(item_name)
        self.player.state.current_tile.items.append(item_name)
        
        return f"You drop the {item_name}."
    
    def handle_gather_command(self, args: List[str]) -> str:
        """Handle gathering environmental resources."""
        resource_name = " ".join(args)
        current_tile = self.player.state.current_tile
        
        if not current_tile:
            return "You are in an unknown area."
        
        # Define gatherable resources based on terrain
        TERRAIN_RESOURCES = {
            TerrainType.FOREST: ["leaves", "branches", "herbs", "berries"],
            TerrainType.CLEARING: ["flowers", "grass", "herbs"],
            TerrainType.MOUNTAIN: ["rocks", "crystals", "roots"],
            TerrainType.RUINS: ["rubble", "artifacts", "dust"],
            TerrainType.CAVE: ["mushrooms", "crystals", "moss"]
        }
        
        available_resources = TERRAIN_RESOURCES.get(current_tile.terrain_type, [])
        
        if resource_name not in available_resources:
            return f"There are no {resource_name} to gather here."
        
        # Check inventory capacity
        if self.player.state.stats.current_inventory_weight >= self.player.state.stats.inventory_capacity:
            return "Your inventory is full."
        
        # Add to inventory
        self.player.state.inventory.append(resource_name)
        
        return f"You gather some {resource_name}."
    
    def handle_environment_change(self, action: CommandType, args: List[str]) -> str:
        """Handle changes to the environment."""
        change_description = " ".join(args)
        current_tile = self.player.state.current_tile
        
        if not current_tile:
            return "You are in an unknown area."
        
        # Create environmental change record
        change = {
            "type": action.value,
            "description": change_description,
            "timestamp": "now"  # You'd want to use actual timestamp here
        }
        
        # Add to tile's environmental changes
        if not hasattr(current_tile, "environmental_changes"):
            current_tile.environmental_changes = []
        current_tile.environmental_changes.append(change)
        
        action_messages = {
            CommandType.MARK: f"You leave a mark: {change_description}",
            CommandType.DRAW: f"You draw: {change_description}",
            CommandType.WRITE: f"You write: {change_description}",
            CommandType.ALTER: f"You alter the environment: {change_description}"
        }
        
        return action_messages.get(action, "You change the environment.")
    
    def handle_combat_command(self, action: CommandType, args: List[str]) -> str:
        """Handle combat actions."""
        current_tile = self.player.state.current_tile
        
        # Always advance time for combat actions
        if action == CommandType.ATTACK:
            # Combat takes 30 minutes
            time_events = self.player.time_system.advance_time(30)
            time_message = " ".join(time_events.values())
            
            if not current_tile or not current_tile.enemies:
                return f"There are no enemies here. {time_message}"
            
            if not args:
                return f"Attack what? {time_message}"
            target = " ".join(args)
            enemy_names = [enemy.name.lower() for enemy in current_tile.enemies]
            if target.lower() not in enemy_names:
                return f"There is no {target} here. {time_message}"
            return f"You attack the {target}! {time_message}"
        
        elif action == CommandType.DEFEND:
            # Defending takes 10 minutes
            time_events = self.player.time_system.advance_time(10)
            time_message = " ".join(time_events.values())
            
            if not current_tile or not current_tile.enemies:
                return f"There are no enemies to defend against. {time_message}"
            return f"You take a defensive stance. {time_message}"
        
        elif action == CommandType.DODGE:
            # Dodging takes 5 minutes
            time_events = self.player.time_system.advance_time(5)
            time_message = " ".join(time_events.values())
            
            if not current_tile or not current_tile.enemies:
                return f"There are no attacks to dodge. {time_message}"
            return f"You prepare to dodge. {time_message}"
        
        elif action == CommandType.SPECIAL:
            # Special abilities take 20 minutes
            time_events = self.player.time_system.advance_time(20)
            time_message = " ".join(time_events.values())
            
            if not current_tile or not current_tile.enemies:
                return f"There are no enemies to use special abilities on. {time_message}"
            return f"You prepare to use a special ability. {time_message}"
    
    def handle_roleplay_command(self, action: CommandType, args: List[str]) -> str:
        """Handle roleplay actions."""
        message = " ".join(args)
        
        roleplay_formats = {
            CommandType.EMOTE: f"* Centaur Prime {message}",
            CommandType.SAY: f'Centaur Prime says: "{message}"',
            CommandType.THINK: f"* Centaur Prime ponders: {message}"
        }
        
        return roleplay_formats.get(action, message) 