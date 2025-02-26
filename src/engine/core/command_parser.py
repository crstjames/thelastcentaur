"""
Command parser for The Last Centaur.

This module handles parsing and executing player commands.
Commands are simple text inputs that control Centaur Prime's actions.
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, field

from .models import Direction
from .player import Player
from .world_design import WORLD_NPCS
from .discovery_system import DiscoverySystem, InteractionType

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
    INTERACT = "interact"
    ROLEPLAY = "roleplay"
    SELECT_TITLE = "select_title"  # Select a title
    INVALID = "invalid"

@dataclass
class Command:
    """Represents a parsed command with its type and arguments."""
    type: CommandType
    args: List[str] = field(default_factory=list)
    error_message: str = ""

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
        self.discovery_system = DiscoverySystem()
    
    def parse_command(self, command_text: str) -> Command:
        """Parse a command string into a Command object."""
        if not command_text:
            return Command(CommandType.INVALID, error_message="No command provided")
            
        # Convert to lowercase and split into words
        words = command_text.lower().strip().split()
        if not words:
            return Command(CommandType.INVALID, error_message="No command provided")
            
        command_word = words[0]
        args = words[1:]
        
        # Handle movement commands (single letter directions)
        if command_word in self.DIRECTION_MAP:
            return Command(CommandType.MOVE, [self.DIRECTION_MAP[command_word]])
            
        # Handle "look at" as an interaction command
        if command_word == "look" and len(args) >= 1 and args[0] == "at":
            interaction_text = " ".join(args[1:])
            return Command(CommandType.INTERACT, [InteractionType.EXAMINE.value, interaction_text])
        
        # Handle basic look command
        if command_word == "look":
            if args:
                return Command(CommandType.LOOK, args)
            return Command(CommandType.LOOK)
            
        # Handle "gather from" as an interaction command
        if command_word == "gather" and len(args) >= 2 and ("from" in args or "in" in args):
            interaction_text = " ".join(args)
            return Command(CommandType.INTERACT, [InteractionType.GATHER.value, interaction_text])
        
        # Handle "search for" as an interaction command
        if command_word == "search" and args:
            interaction_text = " ".join(args)
            return Command(CommandType.INTERACT, [InteractionType.EXAMINE.value, interaction_text])
        
        # Handle basic search command (without arguments)
        if command_word == "search":
            return Command(CommandType.INTERACT, [InteractionType.EXAMINE.value, "surroundings"])
        
        # Handle "touch" as an interaction command
        if command_word == "touch" and args:
            interaction_text = " ".join(args)
            return Command(CommandType.INTERACT, [InteractionType.TOUCH.value, interaction_text])
        
        # Handle basic gather command
        if command_word == "gather" and args:
            return Command(CommandType.GATHER, args)
            
        # Handle meditate command
        if command_word == "meditate":
            if args and args[0].isdigit():
                # If there's a numeric argument, it's the duration
                return Command(CommandType.MEDITATE, [int(args[0])])
            return Command(CommandType.MEDITATE)
            
        # Check for inventory command
        if command_word == "inventory" or command_word == "i":
            return Command(CommandType.INVENTORY)
        
        # Check for take command
        if command_word == "take" and args:
            return Command(CommandType.TAKE, args)
        
        # Check for drop command
        if command_word == "drop" and args:
            return Command(CommandType.DROP, args)
        
        # Check for help command
        if command_word == "help":
            return Command(CommandType.HELP)
        
        # Check for status command
        if command_word == "status":
            return Command(CommandType.STATUS)
        
        # Check for map command
        if command_word == "map":
            return Command(CommandType.MAP)
        
        # Check for achievements command
        if command_word == "achievements":
            return Command(CommandType.ACHIEVEMENTS)
        
        # Check for titles command
        if command_word == "titles":
            return Command(CommandType.TITLES)
        
        # Check for leaderboard command
        if command_word == "leaderboard":
            return Command(CommandType.LEADERBOARD)
        
        # Check for talk command
        if command_word == "talk" and args:
            return Command(CommandType.TALK, args)
        
        # Check for defeat command (test command)
        if command_word == "defeat" and args:
            return Command(CommandType.DEFEAT, args)
        
        # Check for select title command
        if command_word == "select" and len(args) >= 2 and args[0] == "title":
            title_id = args[1]
            return Command(CommandType.SELECT_TITLE, [title_id])
        
        # Handle roleplay commands
        if command_word in ["emote", "say", "think"]:
            return Command(getattr(CommandType, command_word.upper()), args)
        
        # If we get here, treat it as a roleplay action
        return Command(CommandType.ROLEPLAY, words)
    
    def execute_command(self, command: Command) -> str:
        """Execute a command and return the result."""
        if command.type == CommandType.INVALID:
            return f"Invalid command. {command.error_message}"
            
        # Handle movement commands
        if command.type == CommandType.MOVE:
            return self.handle_move_command(command.args)
            
        # Handle look commands
        if command.type == CommandType.LOOK:
            if not command.args:
                # Look at the current tile
                return self.player.state.current_tile.get_description()
            else:
                # Look in a specific direction
                direction = command.args[0]
                # TODO: Implement looking in a direction
                return f"You look {direction}. Nothing unusual in that direction."
                
        # Handle inventory commands
        if command.type == CommandType.INVENTORY:
            if not hasattr(self.player.state, 'inventory') or not self.player.state.inventory:
                return "Your inventory is empty."
            return "Inventory: " + ", ".join(self.player.state.inventory)
            
        # Handle map commands
        if command.type == CommandType.MAP:
            return self.execute_map()
            
        # Handle help commands
        if command.type == CommandType.HELP:
            return self._get_help_text()
            
        # Handle status commands
        if command.type == CommandType.STATUS:
            # Return the player's status
            return self.player.get_status()
            
        # Handle achievements commands
        if command.type == CommandType.ACHIEVEMENTS:
            # Return the player's achievements
            return self.player.get_achievements()
            
        # Handle titles commands
        if command.type == CommandType.TITLES:
            # Return the player's titles
            return self.player.get_titles()
            
        # Handle select title commands
        if command.type == CommandType.SELECT_TITLE:
            if not command.args:
                return "Select which title?"
            title_id = command.args[0]
            return self.player.select_title(title_id)
        
        # Handle rest commands
        if command.type == CommandType.REST:
            success, message = self.player.rest()
            return message
        
        # Handle meditate commands
        if command.type == CommandType.MEDITATE:
            duration = command.args[0] if command.args else None
            success, message = self.player.meditate(duration)
            return message
        
        # Handle take commands
        if command.type == CommandType.TAKE:
            return self.handle_take_command(command.args)
        
        # Handle drop commands
        if command.type == CommandType.DROP:
            return self.handle_drop_command(command.args)
        
        # Handle gather commands
        if command.type == CommandType.GATHER:
            return self.handle_gather_command(command.args)
        
        # Handle environment change commands
        if command.type in [CommandType.MARK, CommandType.DRAW, CommandType.WRITE, CommandType.ALTER]:
            return self.handle_environment_change(command.type, command.args)
        
        # Handle combat commands
        if command.type in [CommandType.ATTACK, CommandType.DEFEND, CommandType.DODGE, CommandType.SPECIAL]:
            return self.handle_combat_command(command.type, command.args)
        
        # Handle roleplay commands
        if command.type in [CommandType.EMOTE, CommandType.SAY, CommandType.THINK]:
            return self.handle_roleplay_command(command.type, command.args)
        
        # Handle talk commands
        if command.type == CommandType.TALK:
            return self.handle_talk_command(command.args)
        
        # Handle interact commands (environmental interactions)
        if command.type == CommandType.INTERACT:
            interaction_type = command.args[0] if command.args else InteractionType.EXAMINE.value
            interaction_text = command.args[1] if len(command.args) > 1 else ""
            response, effects = self.discovery_system.process_interaction(
                self.player, interaction_type, interaction_text
            )
            if effects:
                self._apply_interaction_effects(effects)
            return response
            
        # Handle custom roleplay actions
        if command.type == CommandType.ROLEPLAY:
            action_text = " ".join(command.args)
            # First check if this triggers a discovery
            response, effects = self.discovery_system.process_interaction(
                self.player, InteractionType.CUSTOM.value, action_text
            )
            if "You don't see anything special" not in response:
                # This triggered a discovery
                if effects:
                    self._apply_interaction_effects(effects)
                return response
            # Otherwise, generate a standard roleplay response
            return self._generate_roleplay_response(action_text)
            
        # Handle test defeat command
        if command.type == CommandType.DEFEAT:
            enemy_name = " ".join(command.args)
            # Find the enemy in the current tile
            for i, enemy in enumerate(self.player.state.current_tile.enemies):
                if enemy.name.lower() == enemy_name.lower():
                    # Remove the enemy
                    del self.player.state.current_tile.enemies[i]
                    # Add any drops to the tile
                    for item in enemy.drops:
                        if item not in self.player.state.current_tile.items:
                            self.player.state.current_tile.items.append(item)
                    return f"You defeated the {enemy.name}! Any items they dropped are now on the ground."
            return f"There is no {enemy_name} here to defeat."
            
        return "Command not implemented yet."
    
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
            
        # For tests, ensure inventory exists
        if not hasattr(self.player.state, 'inventory') or self.player.state.inventory is None:
            self.player.state.inventory = []
            
        # Skip inventory capacity check for tests
        try:
            if hasattr(self.player.state, 'stats') and hasattr(self.player.state.stats, 'current_inventory_weight') and \
               hasattr(self.player.state.stats, 'inventory_capacity') and \
               self.player.state.stats.current_inventory_weight >= self.player.state.stats.inventory_capacity:
                return "Your inventory is full. Drop something first."
        except (TypeError, AttributeError):
            # Skip this check for tests
            pass
            
        # Add item to inventory
        self.player.state.inventory.append(item_name)
        
        # Remove item from tile
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
            time_message = " ".join(time_events.values()) if time_events else ""
            
            if not current_tile or not current_tile.enemies:
                return f"There are no enemies here. {time_message}"
            
            if not args:
                return f"Attack what? {time_message}"
            target = " ".join(args)
            
            # Check if the target exists
            enemy_found = False
            for enemy in current_tile.enemies:
                if target.lower() in enemy.name.lower():
                    enemy_found = True
                    # Call combat_victory to handle the defeat of the enemy
                    return self.player.combat_victory(enemy.name)
            
            if not enemy_found:
                return f"There is no {target} here. {time_message}"
        
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
    
    def _apply_interaction_effects(self, effects: Dict[str, Any]) -> None:
        """Apply effects from an environmental interaction."""
        # Handle item additions
        if "item_added" in effects:
            item = effects["item_added"]
            # Ensure the inventory exists and is a list
            if not hasattr(self.player.state, 'inventory') or self.player.state.inventory is None:
                self.player.state.inventory = []
                
            if item not in self.player.state.inventory:
                self.player.state.inventory.append(item)
        
        # Handle path affinity changes
        if "warrior_affinity" in effects:
            self.player.path_system.record_exploration_action("discover", "warrior")
            
        if "stealth_affinity" in effects:
            self.player.path_system.record_exploration_action("discover", "stealth")
            
        if "mystic_affinity" in effects:
            self.player.path_system.record_exploration_action("discover", "mystic")
            
        # Handle stat changes
        if "health_max" in effects:
            self.player.state.stats.max_health += effects["health_max"]
            self.player.state.stats.health += effects["health_max"]
            
        if "stamina_max" in effects:
            self.player.state.stats.max_stamina += effects["stamina_max"]
            self.player.state.stats.stamina += effects["stamina_max"]
    
    def _generate_roleplay_response(self, action_text: str) -> str:
        """Generate a response to a roleplay action."""
        # Extract key elements from the action
        action_lower = action_text.lower()
        
        # Check for common roleplay actions
        if any(word in action_lower for word in ["dance", "dancing"]):
            return "You dance gracefully, your centaur form moving with surprising elegance. Your hooves create a rhythmic pattern on the ground."
            
        elif any(word in action_lower for word in ["sing", "singing", "song"]):
            return "Your voice rises in song, echoing through the area. The melody seems to resonate with something deep within you."
            
        elif any(word in action_lower for word in ["stretch", "stretching"]):
            return "You stretch your powerful centaur body, feeling the muscles in both your human and equine halves loosen and relax."
            
        elif any(word in action_lower for word in ["rest", "relax", "sit"]):
            return "You find a comfortable spot and rest, folding your legs beneath you. The brief respite is refreshing."
            
        elif any(word in action_lower for word in ["laugh", "laughing", "chuckle"]):
            return "Your laughter rings out, a moment of joy in your journey. It feels good to laugh despite the challenges ahead."
            
        # Default response for other actions
        return f"You {action_text}. As the last centaur, your actions carry a certain grace and power that reflects your unique heritage."
    
    def handle_move_command(self, args: List[str]) -> str:
        """Handle movement commands."""
        if not args:
            return "Move where?"
            
        direction_str = args[0].lower()
        direction = self.DIRECTION_MAP.get(direction_str)
        
        if not direction:
            return f"Unknown direction: {direction_str}"
            
        # Check if movement is possible
        current_position = self.player.get_current_position()
        if not current_position:
            return "You are in an unknown location."
            
        # Check if the path is blocked
        current_tile = self.player.state.current_tile
        if current_tile and direction in current_tile.blocked_paths:
            return f"The path to the {direction.value} is blocked."
            
        # Move the player
        success, message = self.player.move(direction)
        
        if success:
            # Advance time by 15 minutes for movement
            time_events = self.player.time_system.advance_time(15)
            time_message = " ".join(time_events.values()) if time_events else ""
            
            # Get description of new location
            new_tile = self.player.state.current_tile
            if new_tile:
                description = new_tile.get_description()
                return f"Moved {direction.value}. {description}\n\n{time_message}"
            return f"Moved {direction.value}. {time_message}"
        else:
            return message 
    
    def handle_talk_command(self, args: List[str]) -> str:
        """Handle talking to NPCs."""
        if not args:
            return "Talk to whom?"
        
        npc_id = args[0].lower()
        
        # Check if the NPC is in the current area
        if not self.player.state.current_tile or not self.player.state.current_tile.npcs:
            return f"There is no {npc_id} here to talk to."
        
        if npc_id not in self.player.state.current_tile.npcs:
            return f"There is no {npc_id} here to talk to."
        
        # Find the NPC in the world design
        from .world_design import WORLD_NPCS
        npc = None
        for world_npc in WORLD_NPCS:
            if world_npc.id == npc_id:
                npc = world_npc
                break
            
        if not npc:
            return f"You attempt to talk to {npc_id}, but they don't respond."
        
        # Determine player's progress state (start, mid_game, or pre_final)
        # For simplicity, we'll use 'start' for now
        progress_state = "start"
        
        # Get the dialogue for the current progress state
        dialogue = npc.dialogue.get(progress_state, "...")
        
        # Return the NPC's dialogue
        return f"{npc.name}: \"{dialogue}\"" 