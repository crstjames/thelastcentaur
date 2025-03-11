from typing import Dict, List, Optional, Set, Tuple
from enum import Enum, auto
from termcolor import colored
import random

from .models import Direction, CommandType, StoryArea, TileState, Enemy
from .map_system import MapManager

class GameEngine:
    """Main game engine for The Last Centaur."""
    
    def __init__(self):
        """Initialize the game engine."""
        self.inventory = []  # Player's inventory
        self.health = 100  # Player's health
        self.max_health = 100  # Maximum player health
        self.current_area = None  # Current area ID (can be a StoryArea enum or a string for generic areas)
        self.discovered_areas = set()  # Discovered areas
        self.map_manager = None  # Will be initialized
        self.active_enemies = {}  # Dictionary of active enemies with their health
        self.weapon = None  # Currently equipped weapon
        self.armor = None  # Currently equipped armor
        self.completed_quests = set()  # Set of completed quests
        self.initialize_map()
    
    def initialize_map(self):
        """Initialize the map and set the current area."""
        # Use the coordinate-based MapManager
        self.map_manager = MapManager()
        self.current_area = StoryArea.AWAKENING_WOODS
        self.discovered_areas = {StoryArea.AWAKENING_WOODS}
    
    def get_current_description(self, include_enemies: bool = True) -> str:
        """Get the description of the current area with available directions."""
        # Handle both named and generic areas
        if isinstance(self.current_area, StoryArea):
            area_node = self.map_manager.get_area_node(self.current_area)
        elif isinstance(self.current_area, str) and self.current_area.startswith("Area ("):
            # Extract coordinates from string like "Area (1,2)"
            import re
            match = re.search(r'\((\d+),(\d+)\)', self.current_area)
            if match:
                pos = (int(match.group(1)), int(match.group(2)))
                area_node = self.map_manager.get_area_by_position(pos)
            else:
                return "ERROR: Invalid area format"
        else:
            return "ERROR: Invalid area type"
        
        if not area_node:
            return "ERROR: Invalid area"
        
        # Get area name
        if area_node.area:
            area_name = area_node.area.name
        else:
            area_name = f"Area ({area_node.position[0]}, {area_node.position[1]})"
        
        # Get base description
        desc = f"You are in {area_name}.\n\n{area_node.base_description}\n"
        
        # Add terrain type
        desc += f"\nTerrain: {area_node.terrain_type.value}"
        
        # Add player status
        desc += f"\nYour health: {self.health}/{self.max_health}"
        if self.weapon:
            desc += f" | Weapon: {self.weapon}"
        if self.armor:
            desc += f" | Armor: {self.armor}"
        
        # Add enemies if present and requested
        if include_enemies and area_node.enemies:
            if isinstance(area_node.enemies[0], str):
                # Handle string enemy IDs
                enemy_list = []
                for enemy in area_node.enemies:
                    if enemy in self.active_enemies:
                        health = self.active_enemies[enemy]
                        enemy_list.append(f"{enemy} (Health: {health})")
                    else:
                        # Initialize enemy health the first time
                        health = self._get_enemy_health(enemy)
                        self.active_enemies[enemy] = health
                        enemy_list.append(f"{enemy} (Health: {health})")
                
                if enemy_list:
                    desc += f"\nEnemies present: {', '.join(enemy_list)}\n"
            else:
                # Handle Enemy objects
                enemy_names = [enemy.name for enemy in area_node.enemies]
                enemy_list = ", ".join(enemy_names)
                desc += f"\nEnemies present: {enemy_list}\n"
        
        # Add items if present
        if area_node.items:
            item_list = ", ".join(area_node.items)
            desc += f"\nYou see: {item_list}\n"
        
        # Get available directions
        available_areas = self.map_manager.get_adjacent_areas(self.current_area, self.inventory)
        if available_areas:
            desc += "\nYou can go:"
            for area, direction in available_areas:
                # Handle both StoryArea enums and string area names
                if isinstance(area, StoryArea):
                    area_name = area.name
                else:
                    area_name = area
                desc += f"\n- {direction.value} to {area_name}"
        else:
            desc += "\nThere are no obvious exits."
        
        # Add coordinates
        if isinstance(self.current_area, StoryArea):
            area_node = self.map_manager.get_area_node(self.current_area)
            if area_node:
                x, y = area_node.position
                desc += f"\n\nCoordinates: ({x}, {y})"
        elif isinstance(self.current_area, str) and self.current_area.startswith("Area ("):
            # Already has coordinates in the name
            desc += f"\n\n{self.current_area}"
        
        return desc
    
    def _get_enemy_health(self, enemy_name):
        """Get the health for an enemy type."""
        # Basic enemies have 20-50 health
        if "guardian" in enemy_name:
            return random.randint(80, 120)  # Guardians are tough
        elif "spirit" in enemy_name or "wisp" in enemy_name:
            return random.randint(30, 50)   # Spirits are moderate
        elif "centaur_guardian" in enemy_name:  # Final boss
            return 200
        else:
            return random.randint(20, 40)   # Regular enemies
    
    def _get_weapon_damage(self, weapon):
        """Get the damage for a weapon."""
        weapon_damage = {
            "rusty_sword": (5, 10),
            "basic_shield": (3, 6),
            "training_sword": (8, 15),
            "shadow_blade": (15, 25),
            "ancient_sword": (20, 30),
            "centaur_spear": (25, 40),
            # Add more weapons as needed
        }
        
        if weapon in weapon_damage:
            min_damage, max_damage = weapon_damage[weapon]
            return random.randint(min_damage, max_damage)
        else:
            # Default damage for unknown weapons
            return random.randint(1, 5)
    
    def move(self, direction: Direction) -> bool:
        """Move the player in the specified direction if possible."""
        new_area = self.map_manager.move_player(self.current_area, direction, self.inventory)
        if new_area:
            self.current_area = new_area
            self.discovered_areas.add(new_area)
            
            # Clear active enemies when moving to a new area
            self.active_enemies = {}
            
            return True
        return False

    def _interpret_command(self, command: str) -> Tuple[CommandType, Optional[str]]:
        """Interpret player command and return command type and target."""
        command = command.lower().strip()
        
        # Check for movement commands first
        movement_prefixes = ["go ", "move ", "walk ", "run ", "head ", "travel "]
        direction_words = {
            "north": Direction.NORTH,
            "south": Direction.SOUTH,
            "east": Direction.EAST,
            "west": Direction.WEST,
            "up": Direction.UP,
            "down": Direction.DOWN,
            "n": Direction.NORTH,
            "s": Direction.SOUTH,
            "e": Direction.EAST,
            "w": Direction.WEST,
            "u": Direction.UP,
            "d": Direction.DOWN,
        }
        
        # Check for direct cardinal directions
        for direction_word, direction in direction_words.items():
            if command == direction_word:
                return CommandType.MOVE, direction.value
        
        # Check for movement with prefix
        for prefix in movement_prefixes:
            if command.startswith(prefix):
                direction_part = command[len(prefix):]
                if direction_part in direction_words:
                    return CommandType.MOVE, direction_words[direction_part].value
        
        # Check if player wants to move to a specific area by name
        available_areas = self.map_manager.get_adjacent_areas(self.current_area, self.inventory)
        for area, direction in available_areas:
            area_str = str(area)
            area_name = area.name.lower() if isinstance(area, StoryArea) else area.lower()
            if (f"go to {area_name}" in command or 
                f"go {area_name}" in command or
                f"move to {area_name}" in command or
                command == area_name):
                return CommandType.MOVE, direction.value
                
        # Handle other command types (inventory, look, etc.)
        if command in ["inventory", "i", "items"]:
            return CommandType.INVENTORY, None
        elif command in ["look", "l", "examine", "x"]:
            return CommandType.LOOK, None
        elif command.startswith("get ") or command.startswith("take "):
            item = command.split(" ", 1)[1]
            return CommandType.GET, item
        elif command.startswith("drop "):
            item = command.split(" ", 1)[1]
            return CommandType.DROP, item
        elif command.startswith("examine ") or command.startswith("look at ") or command.startswith("x "):
            target = command.split(" ", 1)[1]
            if command.startswith("x "):
                target = command[2:]
            elif command.startswith("look at "):
                target = command[8:]
            return CommandType.EXAMINE, target
        elif command in ["help", "h", "?"]:
            return CommandType.HELP, None
        elif command in ["quit", "exit", "q"]:
            return CommandType.QUIT, None
        elif command in ["map", "show map"]:
            return CommandType.LOOK, "map"
        elif command == "where am i":
            return CommandType.LOOK, "position"
        elif command.startswith("attack ") or command.startswith("fight "):
            target = command.split(" ", 1)[1]
            return CommandType.ATTACK, target
        elif command == "status":
            return CommandType.LOOK, "status"
        elif command.startswith("equip "):
            item = command.split(" ", 1)[1]
            return CommandType.USE, item
        elif command.startswith("use "):
            item = command.split(" ", 1)[1]
            return CommandType.USE, item
        
        # If no command is recognized
        return CommandType.UNKNOWN, None
    
    def process_command(self, command: str) -> str:
        """Process player command and return result."""
        command_type, target = self._interpret_command(command)
        
        if command_type == CommandType.MOVE:
            direction = Direction(target)
            if self.move(direction):
                return self.get_current_description()
            else:
                return "You can't go that way."
        
        elif command_type == CommandType.LOOK:
            if target == "map":
                return self._generate_mini_map()
            elif target == "position":
                # Get current position
                if isinstance(self.current_area, StoryArea):
                    area_node = self.map_manager.get_area_node(self.current_area)
                    if area_node:
                        x, y = area_node.position
                        return f"You are at coordinates ({x}, {y}) in area {self.current_area.name}."
                else:
                    return f"You are in {self.current_area}."
            elif target == "status":
                status = f"Health: {self.health}/{self.max_health}\n"
                if self.weapon:
                    status += f"Weapon: {self.weapon}\n"
                if self.armor:
                    status += f"Armor: {self.armor}\n"
                status += f"Inventory: {', '.join(self.inventory) if self.inventory else 'Empty'}\n"
                status += f"Discovered areas: {len(self.discovered_areas)}\n"
                return status
                
            return self.get_current_description()
        
        elif command_type == CommandType.INVENTORY:
            if not self.inventory:
                return "Your inventory is empty."
            
            inv_str = "Inventory:\n"
            for item in self.inventory:
                if item == self.weapon:
                    inv_str += f"- {item} (equipped weapon)\n"
                elif item == self.armor:
                    inv_str += f"- {item} (equipped armor)\n"
                else:
                    inv_str += f"- {item}\n"
            
            return inv_str
        
        elif command_type == CommandType.GET:
            # Get the current area node
            if isinstance(self.current_area, StoryArea):
                area_node = self.map_manager.get_area_node(self.current_area)
            else:
                # Extract coordinates for generic areas
                import re
                match = re.search(r'\((\d+),(\d+)\)', self.current_area)
                if match:
                    pos = (int(match.group(1)), int(match.group(2)))
                    area_node = self.map_manager.get_area_by_position(pos)
                else:
                    return "Error: Cannot determine current area."
            
            # Check for approximate matches
            target_lower = target.lower()
            found_item = None
            
            for item in area_node.items:
                if target_lower in item.lower():
                    found_item = item
                    break
                    
            if found_item:
                area_node.items.remove(found_item)
                self.inventory.append(found_item)
                return f"You pick up the {found_item}."
            
            return f"There is no {target} here."
        
        elif command_type == CommandType.DROP:
            # Check for approximate matches in inventory
            target_lower = target.lower()
            found_item = None
            
            for item in self.inventory:
                if target_lower in item.lower():
                    found_item = item
                    break
                    
            if found_item:
                self.inventory.remove(found_item)
                
                # If dropping equipped items, unequip them
                if found_item == self.weapon:
                    self.weapon = None
                if found_item == self.armor:
                    self.armor = None
                
                # Get the current area node
                if isinstance(self.current_area, StoryArea):
                    area_node = self.map_manager.get_area_node(self.current_area)
                else:
                    # Extract coordinates for generic areas
                    import re
                    match = re.search(r'\((\d+),(\d+)\)', self.current_area)
                    if match:
                        pos = (int(match.group(1)), int(match.group(2)))
                        area_node = self.map_manager.get_area_by_position(pos)
                    else:
                        return "Error: Cannot determine current area."
                        
                area_node.items.append(found_item)
                return f"You drop the {found_item}."
            
            return f"You don't have a {target}."
        
        elif command_type == CommandType.EXAMINE:
            # Check if target is an item in inventory
            target_lower = target.lower()
            
            for item in self.inventory:
                if target_lower in item.lower():
                    item_desc = self._get_item_description(item)
                    return f"You examine the {item}. {item_desc}"
            
            # Get the current area node
            if isinstance(self.current_area, StoryArea):
                area_node = self.map_manager.get_area_node(self.current_area)
            else:
                # Extract coordinates for generic areas
                import re
                match = re.search(r'\((\d+),(\d+)\)', self.current_area)
                if match:
                    pos = (int(match.group(1)), int(match.group(2)))
                    area_node = self.map_manager.get_area_by_position(pos)
                else:
                    return "Error: Cannot determine current area."
            
            # Check if target is an item in the current area
            for item in area_node.items:
                if target_lower in item.lower():
                    item_desc = self._get_item_description(item)
                    return f"You examine the {item}. {item_desc}"
            
            # Check if target is an enemy in the current area
            for enemy in area_node.enemies:
                enemy_name = enemy if isinstance(enemy, str) else enemy.name
                if target_lower in enemy_name.lower():
                    enemy_desc = self._get_enemy_description(enemy_name)
                    if enemy_name in self.active_enemies:
                        health = self.active_enemies[enemy_name]
                        return f"You examine the {enemy_name}. {enemy_desc} It has {health} health remaining."
                    else:
                        return f"You examine the {enemy_name}. {enemy_desc}"
            
            return f"There is no {target} to examine."
        
        elif command_type == CommandType.ATTACK:
            # Get current area node
            if isinstance(self.current_area, StoryArea):
                area_node = self.map_manager.get_area_node(self.current_area)
            else:
                # Extract coordinates for generic areas
                import re
                match = re.search(r'\((\d+),(\d+)\)', self.current_area)
                if match:
                    pos = (int(match.group(1)), int(match.group(2)))
                    area_node = self.map_manager.get_area_by_position(pos)
                else:
                    return "Error: Cannot determine current area."
            
            # Find enemy to attack
            target_lower = target.lower()
            found_enemy = None
            
            for enemy in area_node.enemies:
                enemy_name = enemy if isinstance(enemy, str) else enemy.name
                if target_lower in enemy_name.lower():
                    found_enemy = enemy_name
                    break
            
            if not found_enemy:
                return f"There is no {target} here to attack."
            
            # Check if player has a weapon
            if not self.weapon and "sword" not in self.inventory and "blade" not in self.inventory:
                return "You have no weapon equipped! Try to find a weapon first."
            
            # Calculate player damage
            if self.weapon:
                player_damage = self._get_weapon_damage(self.weapon)
            else:
                # Find any weapon-like item in inventory
                for item in self.inventory:
                    if "sword" in item or "blade" in item:
                        player_damage = self._get_weapon_damage(item)
                        break
                else:
                    player_damage = random.randint(1, 3)  # Bare hands
            
            # Initialize enemy health if not already tracked
            if found_enemy not in self.active_enemies:
                self.active_enemies[found_enemy] = self._get_enemy_health(found_enemy)
            
            # Apply damage to enemy
            self.active_enemies[found_enemy] -= player_damage
            result = f"You attack the {found_enemy} for {player_damage} damage!\n"
            
            # Check if enemy is defeated
            if self.active_enemies[found_enemy] <= 0:
                result += f"The {found_enemy} has been defeated!"
                
                # Remove enemy from the area
                if isinstance(enemy, str):
                    area_node.enemies.remove(found_enemy)
                else:
                    area_node.enemies = [e for e in area_node.enemies if e.name != found_enemy]
                
                # Remove from active enemies
                del self.active_enemies[found_enemy]
                
                # Add special drops for some enemies
                if "guardian" in found_enemy:
                    if random.random() < 0.7:  # 70% chance for guardian drops
                        if "centaur_guardian" == found_enemy:
                            area_node.items.append("centaur_horn")
                            result += "\nThe centaur guardian dropped a magnificent centaur horn!"
                        else:
                            drop = random.choice(["guardian_emblem", "magical_essence", "ancient_coin"])
                            area_node.items.append(drop)
                            result += f"\nThe {found_enemy} dropped a {drop}!"
            else:
                # Enemy attacks back if still alive
                enemy_damage = random.randint(5, 15)
                if "guardian" in found_enemy:
                    enemy_damage = random.randint(10, 20)
                if "centaur_guardian" == found_enemy:
                    enemy_damage = random.randint(15, 30)
                
                # Reduce damage if player has armor
                if self.armor:
                    if "shield" in self.armor:
                        enemy_damage = max(1, enemy_damage - random.randint(3, 8))
                    elif "plate" in self.armor:
                        enemy_damage = max(1, enemy_damage - random.randint(5, 10))
                    else:
                        enemy_damage = max(1, enemy_damage - random.randint(1, 5))
                
                self.health -= enemy_damage
                result += f"The {found_enemy} attacks you for {enemy_damage} damage!"
                result += f"\nThe {found_enemy} has {self.active_enemies[found_enemy]} health remaining."
                result += f"\nYou have {self.health} health remaining."
                
                # Check if player is defeated
                if self.health <= 0:
                    result += "\nYou have been defeated! Game over."
                    # Could add game over logic here
            
            return result
        
        elif command_type == CommandType.USE:
            target_lower = target.lower()
            found_item = None
            
            # Find the item in inventory
            for item in self.inventory:
                if target_lower in item.lower():
                    found_item = item
                    break
            
            if not found_item:
                return f"You don't have a {target}."
            
            # Handle equipping weapons and armor
            if "sword" in found_item or "blade" in found_item or "weapon" in found_item:
                self.weapon = found_item
                return f"You equip the {found_item} as your weapon."
            elif "shield" in found_item or "armor" in found_item or "plate" in found_item:
                self.armor = found_item
                return f"You equip the {found_item} as your armor."
            elif "potion" in found_item or "herb" in found_item:
                # Healing items
                heal_amount = random.randint(20, 40)
                self.health = min(self.max_health, self.health + heal_amount)
                self.inventory.remove(found_item)
                return f"You use the {found_item} and recover {heal_amount} health. You now have {self.health}/{self.max_health} health."
            elif "map" in found_item:
                # Map reveals more of the surrounding area
                return self._generate_mini_map(radius=3)
            else:
                return f"You're not sure how to use the {found_item}."
        
        elif command_type == CommandType.HELP:
            return """Available commands:
- north/south/east/west (or n/s/e/w): Move in that direction
- go [direction]: Move in a direction
- look: Look around
- map: Show a mini-map of the area
- where am i: Show your current coordinates
- status: Show your health and equipment
- inventory (or i): Check your inventory
- get/take [item]: Pick up an item
- drop [item]: Drop an item
- examine [target] (or x [target]): Examine something
- attack/fight [enemy]: Attack an enemy
- use/equip [item]: Use or equip an item
- quit (or q): Quit the game"""
        
        elif command_type == CommandType.QUIT:
            return "Goodbye!"
        
        else:
            return "I don't understand that command."
    
    def _get_item_description(self, item_name):
        """Get a description for an item."""
        item_descriptions = {
            "rusty_sword": "A worn but serviceable sword. It could use some oil and a good sharpening.",
            "leather_pouch": "A small leather pouch that can be worn at the belt. Useful for carrying small items.",
            "basic_shield": "A simple wooden shield reinforced with metal bands.",
            "healing_herb": "A glowing herb with restorative properties. Can be used to heal wounds.",
            "trial_map": "A faded map showing the path of the hero's trials. It marks important locations across the land.",
            "climbing_rope": "A strong rope useful for scaling cliffs and steep terrain.",
            "training_sword": "A balanced practice sword, surprisingly effective in real combat.",
            "shadow_essence": "A swirling vial of shadow energy. It seems to absorb light around it.",
            "shadow_blade": "A deadly blade forged from shadow essence. It seems to whisper dark secrets.",
            "mystic_crystal": "A crystal imbued with magic. It pulses with an inner light.",
            "luminous_crystal": "A crystal that emits a gentle glow. It's warm to the touch.",
            "honor_medal": "A medal awarded to those who have proven their valor.",
            "ancient_scroll": "A scroll containing wisdom from a forgotten age.",
            "meditation_stone": "A smooth stone that calms the mind when held.",
            "enchanted_seed": "A seed that radiates magic. It seems like it could grow into something extraordinary.",
            "prismatic_shard": "A shard that refracts light into a rainbow of colors.",
            "silver_leaf": "A leaf made of pure silver. It never wilts or tarnishes.",
            "traveler_map": "A detailed map of the surrounding lands.",
            "compass": "A magical compass that always points toward your destiny.",
            "ancient_key": "An ornate key that seems to resonate with power. It must unlock something important.",
            "centaur_wisdom": "A crystallized form of ancient centaur knowledge.",
        }
        
        if item_name in item_descriptions:
            return item_descriptions[item_name]
        elif "sword" in item_name:
            return "A weapon designed for combat."
        elif "shield" in item_name:
            return "A defensive item that can protect you in combat."
        elif "potion" in item_name:
            return "A magical liquid with beneficial effects."
        elif "map" in item_name:
            return "A guide to the surrounding areas."
        else:
            return "An item that might be useful on your journey."
    
    def _get_enemy_description(self, enemy_name):
        """Get a description for an enemy."""
        enemy_descriptions = {
            "forest_guardian": "A spectral entity that protects the ancient forest.",
            "training_dummy": "A animated practice target used for combat training.",
            "forest_wolf": "A large wolf with unusually intelligent eyes.",
            "mountain_goat": "A sturdy goat with sharp horns and surprising aggression.",
            "practice_target": "A magical construct designed to test combat skills.",
            "shadow_creature": "A being made of living shadows that shifts and changes form.",
            "mountain_spirit": "An elemental entity born from the ancient rocks of the mountains.",
            "phantom_assassin": "A deadly shadow warrior trained in the art of silent killing.",
            "water_sprite": "A playful but dangerous water elemental.",
            "temple_guardian": "An ancient construct designed to protect sacred places.",
            "magic_wisp": "A small ball of pure magical energy with a mischievous nature.",
            "crystal_golem": "A massive humanoid form composed entirely of living crystal.",
            "grove_spirit": "A guardian of the natural world, capable of commanding plants and animals.",
            "guardian_scout": "An elite warrior tasked with guarding the approach to the Ancient Sanctuary.",
            "centaur_guardian": "The legendary last centaur, a mighty warrior with ancient wisdom.",
        }
        
        if enemy_name in enemy_descriptions:
            return enemy_descriptions[enemy_name]
        elif "guardian" in enemy_name:
            return "A powerful entity tasked with protecting something important."
        elif "spirit" in enemy_name:
            return "A magical entity connected to the natural world."
        elif "golem" in enemy_name:
            return "A construct animated by ancient magic."
        else:
            return "A hostile creature that stands in your way."
    
    def _generate_mini_map(self, radius=10) -> str:
        """Generate a simple ASCII mini-map of the surrounding area."""
        # Determine current position
        if isinstance(self.current_area, StoryArea):
            area_node = self.map_manager.get_area_node(self.current_area)
            if not area_node:
                return "Unable to generate map."
            center_x, center_y = area_node.position
        else:
            # Extract coordinates for generic areas
            import re
            match = re.search(r'\((\d+),(\d+)\)', self.current_area)
            if match:
                center_x, center_y = int(match.group(1)), int(match.group(2))
            else:
                return "Unable to determine current position."
        
        # Generate the map - always show the full 10x10 grid
        map_str = "\nMap (P = Player, # = Explored area, ? = Unexplored area):\n"
        
        # Add coordinate header
        map_str += "   "
        for x in range(10):  # Always show all 10 columns
            map_str += f"{x} "
        map_str += "\n"
        
        for y in range(9, -1, -1):  # Always show all 10 rows
            # Add y-coordinate
            map_str += f"{y:2d} "
            
            for x in range(10):  # Always show all 10 columns
                if x == center_x and y == center_y:
                    map_str += "P "  # Player position
                elif (x, y) in self.map_manager.position_to_area:
                    node = self.map_manager.position_to_area[(x, y)]
                    if node.area and node.area in self.discovered_areas:
                        if node.area == StoryArea.ANCIENT_SANCTUARY:
                            map_str += "! "  # Boss area
                        elif node.area == StoryArea.CROSSROADS:
                            map_str += "X "  # Crossroads
                        else:
                            map_str += "# "  # Discovered named area
                    elif f"Area ({x},{y})" in self.discovered_areas:
                        map_str += "# "  # Discovered generic area
                    else:
                        if node.is_passable:
                            map_str += "? "  # Undiscovered but passable area
                        else:
                            map_str += "■ "  # Impassable area
                else:
                    map_str += ". "  # Empty space
            
            map_str += "\n"
        
        # Add legend
        map_str += "\nLegend: P = Player, # = Explored area, ? = Unexplored area\n"
        map_str += "X = Crossroads, ! = Boss area, ■ = Impassable area\n"
        
        return map_str 