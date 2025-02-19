"""
Command parser for The Last Centaur.

This module handles parsing and executing player commands.
Commands are simple text inputs that control Centaur Prime's actions.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from .models import Direction
from .player import Player
from .world_design import WORLD_NPCS

class CommandType(str, Enum):
    """Types of commands available to the player."""
    # Movement Commands
    MOVE = "move"
    MEDITATE = "meditate"
    
    # Information Commands
    LOOK = "look"
    STATUS = "status"
    HELP = "help"
    INVENTORY = "inventory"
    MAP = "map"
    
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
    """Represents a parsed command."""
    type: CommandType
    args: List[str]
    raw_input: str

class CommandParser:
    """Handles parsing and executing player commands."""
    
    # Command aliases for easier input
    MOVE_ALIASES = {
        "n": "north",
        "s": "south",
        "e": "east",
        "w": "west",
        "north": "north",
        "south": "south",
        "east": "east",
        "west": "west",
        "go north": "north",
        "go south": "south",
        "go east": "east",
        "go west": "west"
    }
    
    DIRECTION_MAP = {
        "north": Direction.NORTH,
        "south": Direction.SOUTH,
        "east": Direction.EAST,
        "west": Direction.WEST
    }
    
    # New command aliases
    ITEM_ALIASES = {
        "take": ["get", "pick", "grab", "pickup"],
        "drop": ["put", "place", "discard"],
        "gather": ["collect", "harvest", "forage"]
    }
    
    ENVIRONMENT_ALIASES = {
        "mark": ["sign", "symbol"],
        "draw": ["sketch", "trace"],
        "write": ["inscribe", "carve"],
        "alter": ["change", "modify", "arrange"]
    }
    
    COMBAT_ALIASES = {
        "attack": ["strike", "hit", "slash"],
        "defend": ["block", "guard", "shield"],
        "dodge": ["evade", "avoid", "roll"],
        "special": ["skill", "ability", "power"]
    }
    
    ROLEPLAY_ALIASES = {
        "emote": ["me", "action", "act"],
        "say": ["speak", "tell", "talk"],
        "think": ["ponder", "contemplate"]
    }
    
    # Add test command aliases
    TEST_ALIASES = {
        "defeat": ["vanquish", "remove", "test_kill"]
    }
    
    # Add NPC interaction aliases
    NPC_ALIASES = {
        "talk": ["speak", "chat", "converse", "interact"]
    }
    
    def __init__(self, player: Player):
        self.player = player
    
    def parse_command(self, user_input: str) -> Optional[Command]:
        """Parse user input into a command."""
        if not user_input:
            return None
            
        # Convert to lowercase and split into words
        words = user_input.lower().strip().split()
        if not words:
            return None
            
        # Handle NPC interaction first
        if words[0] in self.NPC_ALIASES["talk"] or words[0] == "talk":
            return Command(CommandType.TALK, words[1:], user_input)
            
        # Handle movement commands
        if words[0] in ["move", "go", "n", "s", "e", "w"] or words[0] in self.MOVE_ALIASES:
            if words[0] in ["n", "s", "e", "w"]:
                direction = self.MOVE_ALIASES[words[0]]
                return Command(CommandType.MOVE, [direction], user_input)
            elif words[0] in self.MOVE_ALIASES:
                return Command(CommandType.MOVE, [self.MOVE_ALIASES[words[0]]], user_input)
            elif len(words) > 1 and words[1] in self.MOVE_ALIASES:
                return Command(CommandType.MOVE, [self.MOVE_ALIASES[words[1]]], user_input)
        
        # Handle meditation
        if words[0] in ["meditate", "rest", "recover"]:
            return Command(CommandType.MEDITATE, [], user_input)
        
        # Handle look command
        if words[0] in ["look", "examine", "l"]:
            direction = None
            if len(words) > 1 and words[1] in self.MOVE_ALIASES:
                direction = self.MOVE_ALIASES[words[1]]
            return Command(CommandType.LOOK, [direction] if direction else [], user_input)
        
        # Handle status command
        if words[0] in ["status", "stat", "stats"]:
            return Command(CommandType.STATUS, [], user_input)
        
        # Handle inventory command
        if words[0] in ["inventory", "inv", "i"]:
            return Command(CommandType.INVENTORY, [], user_input)
        
        # Handle map command
        if words[0] in ["map", "m"]:
            return Command(CommandType.MAP, [], user_input)
        
        # Handle help command
        if words[0] in ["help", "h", "?"]:
            return Command(CommandType.HELP, [], user_input)
        
        # Handle item commands
        if words[0] in self.ITEM_ALIASES["take"] or words[0] == "take":
            return Command(CommandType.TAKE, words[1:], user_input)
        if words[0] in self.ITEM_ALIASES["drop"] or words[0] == "drop":
            return Command(CommandType.DROP, words[1:], user_input)
        if words[0] in self.ITEM_ALIASES["gather"] or words[0] == "gather":
            return Command(CommandType.GATHER, words[1:], user_input)
        
        # Handle environment commands
        if words[0] in self.ENVIRONMENT_ALIASES["mark"] or words[0] == "mark":
            return Command(CommandType.MARK, words[1:], user_input)
        if words[0] in self.ENVIRONMENT_ALIASES["draw"] or words[0] == "draw":
            return Command(CommandType.DRAW, words[1:], user_input)
        if words[0] in self.ENVIRONMENT_ALIASES["write"] or words[0] == "write":
            return Command(CommandType.WRITE, words[1:], user_input)
        if words[0] in self.ENVIRONMENT_ALIASES["alter"] or words[0] == "alter":
            return Command(CommandType.ALTER, words[1:], user_input)
        
        # Handle combat commands
        if words[0] in self.COMBAT_ALIASES["attack"] or words[0] == "attack":
            return Command(CommandType.ATTACK, words[1:], user_input)
        if words[0] in self.COMBAT_ALIASES["defend"] or words[0] == "defend":
            return Command(CommandType.DEFEND, words[1:], user_input)
        if words[0] in self.COMBAT_ALIASES["dodge"] or words[0] == "dodge":
            return Command(CommandType.DODGE, words[1:], user_input)
        if words[0] in self.COMBAT_ALIASES["special"] or words[0] == "special":
            return Command(CommandType.SPECIAL, words[1:], user_input)
        
        # Handle roleplay commands
        if words[0] in self.ROLEPLAY_ALIASES["emote"] or words[0] == "emote":
            return Command(CommandType.EMOTE, words[1:], user_input)
        if words[0] in self.ROLEPLAY_ALIASES["say"] or words[0] == "say":
            return Command(CommandType.SAY, words[1:], user_input)
        if words[0] in self.ROLEPLAY_ALIASES["think"] or words[0] == "think":
            return Command(CommandType.THINK, words[1:], user_input)
        
        # Handle test commands
        if words[0] in self.TEST_ALIASES["defeat"] or words[0] == "defeat":
            return Command(CommandType.DEFEAT, words[1:], user_input)
        
        return None
    
    def execute_command(self, command: Command) -> str:
        """Execute a parsed command and return the result message."""
        if command.type == CommandType.MOVE:
            if not command.args:
                return "Move in which direction?"
            direction = self.DIRECTION_MAP.get(command.args[0])
            if not direction:
                return f"Unknown direction: {command.args[0]}"
            success, message = self.player.move(direction)
            return message
        
        elif command.type == CommandType.MEDITATE:
            success, message = self.player.meditate()
            return message
        
        elif command.type == CommandType.LOOK:
            if not command.args:
                # Look at current tile
                return self.get_current_tile_description()
            # Look in direction
            direction = self.DIRECTION_MAP.get(command.args[0])
            if not direction:
                return f"Cannot look {command.args[0]}"
            return self.look_in_direction(direction)
        
        elif command.type == CommandType.STATUS:
            return self.get_player_status()
        
        elif command.type == CommandType.INVENTORY:
            return self.get_inventory_status()
        
        elif command.type == CommandType.MAP:
            return self.get_map_view()
        
        elif command.type == CommandType.HELP:
            return self.get_help_text()
        
        # Item Commands
        elif command.type == CommandType.TAKE:
            if not command.args:
                return "Take what?"
            return self.handle_take_command(command.args)
            
        elif command.type == CommandType.DROP:
            if not command.args:
                return "Drop what?"
            return self.handle_drop_command(command.args)
            
        elif command.type == CommandType.GATHER:
            if not command.args:
                return "Gather what?"
            return self.handle_gather_command(command.args)
        
        # Environment Commands
        elif command.type == CommandType.MARK:
            if not command.args:
                return "Mark what?"
            return self.handle_environment_change(command.type, command.args)
            
        elif command.type == CommandType.DRAW:
            if not command.args:
                return "Draw what?"
            return self.handle_environment_change(command.type, command.args)
            
        elif command.type == CommandType.WRITE:
            if not command.args:
                return "Write what?"
            return self.handle_environment_change(command.type, command.args)
            
        elif command.type == CommandType.ALTER:
            if not command.args:
                return "Alter what?"
            return self.handle_environment_change(command.type, command.args)
        
        # Combat Commands
        elif command.type in [CommandType.ATTACK, CommandType.DEFEND, 
                            CommandType.DODGE, CommandType.SPECIAL]:
            return self.handle_combat_command(command.type, command.args)
        
        # Roleplay Commands
        elif command.type in [CommandType.EMOTE, CommandType.SAY, CommandType.THINK]:
            if not command.args:
                return f"{command.type.value} what?"
            return self.handle_roleplay_command(command.type, command.args)
        
        # Handle test defeat command
        elif command.type == CommandType.DEFEAT:
            if not command.args:
                return "Defeat which enemy?"
            return self.handle_defeat_command(command.args)
        
        # Handle NPC interaction
        elif command.type == CommandType.TALK:
            if not command.args:
                return "Talk to whom?"
            return self.handle_talk_command(command.args)
        
        return "Unknown command."
    
    def get_current_tile_description(self) -> str:
        """Get description of current tile and surroundings."""
        current_tile = self.player.state.current_tile
        if not current_tile:
            return "You are in an unknown area."
            
        description = [current_tile.description]
        
        # Add available directions
        possible_moves = self.player.get_possible_moves()
        directions = []
        for direction, status in possible_moves.items():
            if status == "Clear path.":
                directions.append(direction.value)
        
        if directions:
            description.append(f"\nYou can move: {', '.join(directions)}")
        
        # Add enemies if present
        if current_tile.enemies:
            enemy_names = [enemy.name for enemy in current_tile.enemies]
            description.append(f"\nEnemies present: {', '.join(enemy_names)}")
        
        # Add items if present
        if current_tile.items:
            description.append(f"\nItems visible: {', '.join(current_tile.items)}")
        
        return "\n".join(description)
    
    def look_in_direction(self, direction: Direction) -> str:
        """Look in a specific direction and describe what's there."""
        new_x, new_y = self.player._get_new_position(direction)
        
        # Check if position is off map
        if not (0 <= new_x < 10 and 0 <= new_y < 10):
            return "A shimmering magical barrier stretches into the distance."
        
        # Check if tile has been visited
        tile_info = self.player.get_tile_info((new_x, new_y))
        if tile_info:
            return tile_info
        else:
            return "You can see something in that direction, but can't make out details from here."
    
    def get_player_status(self) -> str:
        """Get player's current status."""
        stats = self.player.state.stats
        return (
            f"Health: {stats.health}/{stats.max_health}\n"
            f"Stamina: {stats.stamina}/{stats.max_stamina}\n"
            f"Inventory: {stats.current_inventory_weight}/{stats.inventory_capacity}"
        )
    
    def get_inventory_status(self) -> str:
        """Get inventory contents."""
        if not self.player.state.inventory:
            return "Your inventory is empty."
        return "Inventory:\n" + "\n".join(f"- {item}" for item in self.player.state.inventory)
    
    def get_map_view(self) -> str:
        """Get ASCII representation of discovered map."""
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
    
    def get_help_text(self) -> str:
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
        
        if not current_tile or not current_tile.enemies:
            return "There are no enemies here."
        
        target = " ".join(args) if args else None
        if target and not any(enemy["name"].lower() == target.lower() 
                            for enemy in current_tile.enemies):
            return f"There is no {target} here."
        
        # Basic combat system - can be expanded later
        combat_messages = {
            CommandType.ATTACK: "You attack the enemy!",
            CommandType.DEFEND: "You take a defensive stance.",
            CommandType.DODGE: "You prepare to dodge the next attack.",
            CommandType.SPECIAL: "You prepare to use a special ability."
        }
        
        return combat_messages.get(action, "Invalid combat action.")
    
    def handle_roleplay_command(self, action: CommandType, args: List[str]) -> str:
        """Handle roleplay actions."""
        message = " ".join(args)
        
        roleplay_formats = {
            CommandType.EMOTE: f"* Centaur Prime {message}",
            CommandType.SAY: f'Centaur Prime says: "{message}"',
            CommandType.THINK: f"* Centaur Prime ponders: {message}"
        }
        
        return roleplay_formats.get(action, message)
    
    def handle_defeat_command(self, args: List[str]) -> str:
        """Handle instantly defeating an enemy for testing."""
        target_name = " ".join(args)
        current_tile = self.player.state.current_tile
        
        if not current_tile:
            return "You are in an unknown area."
        
        if not current_tile.enemies:
            return "There are no enemies here."
        
        # Find the target enemy
        target_enemy = None
        remaining_enemies = []
        
        for enemy in current_tile.enemies:
            if enemy.name.lower() == target_name.lower():
                target_enemy = enemy
            else:
                remaining_enemies.append(enemy)
        
        if not target_enemy:
            return f"There is no {target_name} here."
        
        # Remove the enemy and collect its drops
        current_tile.enemies = remaining_enemies
        
        # Add drops to the tile's items
        if target_enemy.drops:
            current_tile.items.extend(target_enemy.drops)
            drops_message = f"\nThe enemy dropped: {', '.join(target_enemy.drops)}"
        else:
            drops_message = ""
        
        # Update blocked paths if this was the last enemy
        if not remaining_enemies:
            if self.player.state.position in self.player.state.blocked_paths:
                self.player.state.blocked_paths.pop(self.player.state.position)
        
        return f"TEST: Instantly defeated {target_enemy.name}.{drops_message}"
    
    def handle_talk_command(self, args: List[str]) -> str:
        """Handle talking to NPCs."""
        npc_name = " ".join(args).lower()
        current_tile = self.player.state.current_tile
        
        if not current_tile:
            return "You are in an unknown area."
            
        if not current_tile.npcs:
            return f"There is no one here to talk to."
            
        # Find the NPC in the world design
        npc = next((n for n in WORLD_NPCS if n.id.lower() == npc_name.replace(" ", "_") 
                   or n.name.lower() == npc_name), None)
                   
        if not npc or npc.id not in current_tile.npcs:
            return f"There is no {npc_name} here to talk to."
            
        # Get appropriate dialogue based on game progress
        # For now, just use "start" dialogue
        dialogue = npc.dialogue.get("start", "...")
        
        # Add quest items to the current tile if they exist
        if npc.quest_items:
            for item in npc.quest_items:
                if item not in current_tile.items:
                    current_tile.items.append(item)
        
        return f"{npc.name} says: '{dialogue}'" 