"""
Map system for The Last Centaur.

This module handles the game's map layout and transition logic
using a coordinate-based movement system on a 10x10 grid.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import random

from .models import Direction, TerrainType, StoryArea, TileState, Enemy

@dataclass
class EnvironmentalHazard:
    """Represents an environmental hazard in an area."""
    type: str
    description: str
    damage: int
    requirements: List[str]  # Items needed to safely pass
    active_times: Optional[List[str]] = None  # Time-based hazards

# Simplified AreaNode without connection dependencies
@dataclass
class AreaNode:
    """Represents an area node in the game map."""
    area: Optional[StoryArea]  # Can be None for generic areas
    position: Tuple[int, int]
    terrain_type: TerrainType
    base_description: str
    requirements: List[str]
    enemies: List[str]
    items: List[str]
    hazards: List[EnvironmentalHazard] = None
    weather_effects: List[str] = None
    is_minor_area: bool = False
    npcs: List[str] = None
    is_passable: bool = True  # Whether the player can move to this area

# Define the named areas on the map
NAMED_AREAS = {
    # Each tuple is (position, area_enum)
    (0, 0): StoryArea.AWAKENING_WOODS,  # Starting area with pouch and rusty sword
    (1, 0): StoryArea.WARRIORS_CAMP,
    (0, 1): StoryArea.TRIALS_PATH,
    (1, 1): StoryArea.MOUNTAIN_BASE,
    (2, 0): StoryArea.TRAINING_GROUNDS,
    (0, 2): StoryArea.SHADOW_DOMAIN,
    (0, 3): StoryArea.SHADOW_TRAINING,
    (1, 2): StoryArea.MYSTIC_MOUNTAINS,
    (2, 2): StoryArea.CRYSTAL_POND,
    (3, 0): StoryArea.HONOR_SHRINE,
    (0, 4): StoryArea.FORGOTTEN_TEMPLE,
    (3, 2): StoryArea.MEDITATION_CIRCLE,
    (1, 3): StoryArea.ENCHANTED_VALLEY,
    (1, 4): StoryArea.CRYSTAL_CAVES,
    (2, 4): StoryArea.FORGOTTEN_GROVE,
    (9, 9): StoryArea.ANCIENT_SANCTUARY,  # Final boss area in the opposite corner
    (8, 8): StoryArea.GUARDIAN_OVERLOOK,  # Pre-boss area
    (5, 5): StoryArea.CROSSROADS,         # Central area connecting different paths
}

# Data for named areas
AREA_DATA = {
    StoryArea.AWAKENING_WOODS: {
        "terrain": TerrainType.FOREST,
        "desc": "You stand in an ancient forest clearing. The air is thick with magic and mystery. A leather pouch lies on the ground, and a rusty sword is embedded in a nearby stump.",
        "enemies": ["forest_guardian"],
        "items": ["rusty_sword", "leather_pouch"],
        "reqs": [],
    },
    StoryArea.WARRIORS_CAMP: {
        "terrain": TerrainType.CLEARING,
        "desc": "A small encampment with training equipment and weapon racks. Warriors hone their skills here.",
        "enemies": ["training_dummy"],
        "items": ["basic_shield"],
        "reqs": [],
    },
    StoryArea.TRIALS_PATH: {
        "terrain": TerrainType.FOREST,
        "desc": "Ancient stone markers line this path, each inscribed with forgotten runes. This is the beginning of the hero's trials.",
        "enemies": ["forest_wolf"],
        "items": ["healing_herb", "trial_map"],
        "reqs": [],
    },
    StoryArea.MOUNTAIN_BASE: {
        "terrain": TerrainType.MOUNTAIN,
        "desc": "The terrain becomes rocky as you approach the mountain base. A cool breeze flows down from the peaks.",
        "enemies": ["mountain_goat"],
        "items": ["climbing_rope"],
        "reqs": [],
    },
    StoryArea.TRAINING_GROUNDS: {
        "terrain": TerrainType.CLEARING,
        "desc": "An open area with practice dummies and weapon racks. Warriors train here for combat.",
        "enemies": ["practice_target"],
        "items": ["training_sword"],
        "reqs": [],
    },
    StoryArea.SHADOW_DOMAIN: {
        "terrain": TerrainType.RUINS,
        "desc": "Ancient ruins shrouded in perpetual shadow. The air feels heavy with dark magic.",
        "enemies": ["shadow_creature"],
        "items": ["shadow_essence"],
        "reqs": [],
    },
    StoryArea.MYSTIC_MOUNTAINS: {
        "terrain": TerrainType.MOUNTAIN,
        "desc": "Towering peaks shrouded in mist. Strange lights sometimes flicker between the crags.",
        "enemies": ["mountain_spirit"],
        "items": ["mystic_crystal"],
        "reqs": [],
    },
    StoryArea.SHADOW_TRAINING: {
        "terrain": TerrainType.RUINS,
        "desc": "A dark arena where shadow warriors practice their deadly arts. The training equipment seems ancient but well-maintained.",
        "enemies": ["phantom_assassin"],
        "items": ["shadow_blade"],
        "reqs": ["shadow_essence"],
    },
    StoryArea.CRYSTAL_POND: {
        "terrain": TerrainType.WATER,
        "desc": "A serene pond where crystals grow from the water's surface. The water glows with a faint blue light.",
        "enemies": ["water_sprite"],
        "items": ["luminous_crystal"],
        "reqs": [],
    },
    StoryArea.HONOR_SHRINE: {
        "terrain": TerrainType.TEMPLE,
        "desc": "A small shrine dedicated to the ancient heroes. The air feels peaceful here.",
        "enemies": [],
        "items": ["honor_medal"],
        "reqs": [],
    },
    StoryArea.FORGOTTEN_TEMPLE: {
        "terrain": TerrainType.TEMPLE,
        "desc": "A crumbling temple, its original purpose long forgotten. Shadows dance across the walls without clear source.",
        "enemies": ["temple_guardian"],
        "items": ["ancient_scroll"],
        "reqs": ["shadow_blade"],
    },
    StoryArea.MEDITATION_CIRCLE: {
        "terrain": TerrainType.CLEARING,
        "desc": "A circle of smooth stones arranged for meditation. The area has a calming effect on all who enter.",
        "enemies": [],
        "items": ["meditation_stone"],
        "reqs": [],
    },
    StoryArea.ENCHANTED_VALLEY: {
        "terrain": TerrainType.FOREST,
        "desc": "A lush valley filled with strange, glowing plants. Magic seems to infuse the very air.",
        "enemies": ["magic_wisp"],
        "items": ["enchanted_seed"],
        "reqs": ["mystic_crystal"],
    },
    StoryArea.CRYSTAL_CAVES: {
        "terrain": TerrainType.CAVE,
        "desc": "A network of caves with walls lined with luminous crystals. The light they emit shifts through a rainbow of colors.",
        "enemies": ["crystal_golem"],
        "items": ["prismatic_shard"],
        "reqs": ["luminous_crystal"],
    },
    StoryArea.FORGOTTEN_GROVE: {
        "terrain": TerrainType.FOREST,
        "desc": "An ancient grove of trees with silver bark and leaves that whisper secrets. The center forms a natural shrine.",
        "enemies": ["grove_spirit"],
        "items": ["silver_leaf"],
        "reqs": ["enchanted_seed"],
    },
    # New areas for game progression
    StoryArea.CROSSROADS: {
        "terrain": TerrainType.CLEARING,
        "desc": "A major crossroads where several paths meet. Stone markers indicate different possible journeys. A worn signpost points to the trials ahead.",
        "enemies": [],
        "items": ["traveler_map", "compass"],
        "reqs": [],
    },
    StoryArea.GUARDIAN_OVERLOOK: {
        "terrain": TerrainType.MOUNTAIN,
        "desc": "A high vantage point overlooking a sacred valley. In the distance, you can see the entrance to the Ancient Sanctuary. A powerful energy emanates from beyond.",
        "enemies": ["guardian_scout"],
        "items": ["ancient_key"],
        "reqs": ["honor_medal", "shadow_blade", "prismatic_shard"],
    },
    StoryArea.ANCIENT_SANCTUARY: {
        "terrain": TerrainType.TEMPLE,
        "desc": "The legendary sanctuary where the last centaur is said to reside. The air vibrates with ancient magic. A massive centaur stands guard, watching your approach with ancient eyes.",
        "enemies": ["centaur_guardian"],
        "items": ["centaur_wisdom"],
        "reqs": ["ancient_key"],
    },
}

# Generic descriptions for undefined areas based on terrain type
GENERIC_DESCRIPTIONS = {
    TerrainType.FOREST: [
        "A dense forest with towering trees. Sunlight filters through the canopy above.",
        "The forest is alive with the sounds of birds and small creatures.",
        "Thick undergrowth makes it difficult to see far in any direction.",
        "Moss-covered trees surround you, their branches creating natural arches overhead.",
    ],
    TerrainType.MOUNTAIN: [
        "Rocky terrain rises steeply here. The air is crisp and clear.",
        "A mountain path winds its way through large boulders.",
        "Sharp rocks and steep drops make this area treacherous to navigate.",
        "The mountain terrain provides a clear view of the surrounding landscape.",
    ],
    TerrainType.CLEARING: [
        "A small clearing offers a break from the dense surroundings.",
        "Tall grass sways gently in the open space.",
        "Wildflowers dot this open area, adding splashes of color.",
        "The clearing provides good visibility in all directions.",
    ],
    TerrainType.WATER: [
        "A small stream flows through this area, the water crystal clear.",
        "The water here is still and reflective like a mirror.",
        "Reeds and water plants grow along the edges of this watery area.",
        "The gentle sound of flowing water fills this peaceful spot.",
    ],
    TerrainType.CAVE: [
        "The rocky walls of this cave are cool to the touch.",
        "Stalactites hang from the ceiling, created over countless years.",
        "The cave offers shelter from the elements but is shrouded in darkness.",
        "Mysterious echoes bounce off the cave walls as you move.",
    ],
    TerrainType.TEMPLE: [
        "Ancient pillars mark what was once a sacred space.",
        "Faded carvings on stone blocks hint at forgotten rituals.",
        "The remains of a temple structure create an atmosphere of reverence.",
        "Though ruined, this temple still maintains an aura of importance.",
    ],
    TerrainType.RUINS: [
        "Crumbling stone structures hint at a civilization long gone.",
        "Broken walls and collapsed roofs tell of a once-great building.",
        "These ruins have been reclaimed by nature over many years.",
        "The silent ruins stand as a testament to a forgotten time.",
    ],
    TerrainType.VALLEY: [
        "The valley floor is rich with vegetation and wildlife.",
        "Sheltered by hills on either side, this valley feels protected.",
        "The valley stretches ahead, its end obscured by distance.",
        "A gentle slope leads deeper into this peaceful valley.",
    ],
}

# Common enemies by terrain type for generic areas
GENERIC_ENEMIES = {
    TerrainType.FOREST: ["forest_sprite", "wild_fox", "forest_beetle"],
    TerrainType.MOUNTAIN: ["rock_crawler", "mountain_hawk", "cliff_jumper"],
    TerrainType.CLEARING: ["field_mouse", "grass_snake", "meadow_rabbit"],
    TerrainType.WATER: ["small_fish", "water_beetle", "tiny_frog"],
    TerrainType.CAVE: ["cave_bat", "blind_worm", "crystal_beetle"],
    TerrainType.TEMPLE: ["temple_sprite", "guardian_wisp", "stone_sentinel"],
    TerrainType.RUINS: ["dust_spirit", "memory_fragment", "ancient_construct"],
    TerrainType.VALLEY: ["valley_deer", "wild_boar", "field_vole"],
}

# Common items by terrain type for generic areas
GENERIC_ITEMS = {
    TerrainType.FOREST: ["forest_berries", "fallen_branch", "strange_mushroom"],
    TerrainType.MOUNTAIN: ["sharp_stone", "alpine_flower", "eagle_feather"],
    TerrainType.CLEARING: ["wildflowers", "tall_grass", "smooth_pebble"],
    TerrainType.WATER: ["water_lily", "smooth_stone", "reed_bundle"],
    TerrainType.CAVE: ["glowing_fungus", "cave_crystal", "bat_guano"],
    TerrainType.TEMPLE: ["prayer_bead", "broken_statue", "ceremonial_coin"],
    TerrainType.RUINS: ["ancient_coin", "mossy_brick", "tarnished_emblem"],
    TerrainType.VALLEY: ["valley_herb", "colorful_flower", "bird_nest"],
}

class MapManager:
    """Manages the game map and player movement."""
    
    def __init__(self):
        """Initialize the map manager with a 10x10 grid."""
        # Create the full grid of areas
        self.areas = {}
        self.position_to_area = {}
        
        # Generate the whole 10x10 grid
        self._generate_world_grid(10, 10)
        
        # Initialize named areas with their special properties
        self._initialize_named_areas()
        
        # Fix the Phantom Assassin location
        self._fix_phantom_assassin_location()
        
    def _generate_world_grid(self, width, height):
        """Generate a grid of areas with appropriate terrain."""
        terrain_distribution = {
            TerrainType.FOREST: 0.3,
            TerrainType.CLEARING: 0.2,
            TerrainType.MOUNTAIN: 0.15,
            TerrainType.RUINS: 0.1,
            TerrainType.WATER: 0.1,
            TerrainType.TEMPLE: 0.05,
            TerrainType.CAVE: 0.05,
            TerrainType.VALLEY: 0.05,
        }
        
        terrain_types = list(terrain_distribution.keys())
        weights = list(terrain_distribution.values())
        
        # Ensure path to the final boss
        path_positions = set()
        current_x, current_y = 0, 0
        target_x, target_y = 9, 9
        
        # Create a zigzag path to the boss
        while current_x < target_x:
            current_x += 1
            path_positions.add((current_x, current_y))
        
        while current_y < target_y:
            current_y += 1
            path_positions.add((current_x, current_y))
        
        # Add central crossroads area
        path_positions.add((5, 5))
        
        # Add diagonal path from crossroads to boss path
        x, y = 5, 5
        while x < 9 and y < 9:
            x += 1
            y += 1
            path_positions.add((x, y))
        
        # Generate a node for each position in the grid
        for x in range(width):
            for y in range(height):
                position = (x, y)
                
                # If this is a named area, skip it for now (will be added later)
                if position in NAMED_AREAS:
                    continue
                
                # Generate a generic area
                if position in path_positions:
                    # Path areas are always passable and mostly clearings
                    terrain = random.choices(
                        [TerrainType.CLEARING, TerrainType.FOREST, TerrainType.VALLEY],
                        weights=[0.6, 0.3, 0.1],
                        k=1
                    )[0]
                    requirements = []
                    is_passable = True
                else:
                    # Off-path areas can be any terrain
                    terrain = random.choices(terrain_types, weights=weights, k=1)[0]
                    
                    # Some areas have requirements or are impassable
                    is_passable = random.random() < 0.8  # 80% chance of being passable
                    
                    # Only add requirements to passable areas
                    requirements = []
                    if is_passable and random.random() < 0.2:  # 20% chance of requirements
                        possible_reqs = ["rusty_sword", "shadow_essence", "mystic_crystal", 
                                        "climbing_rope", "shadow_blade"]
                        requirements = [random.choice(possible_reqs)]
                
                desc = random.choice(GENERIC_DESCRIPTIONS[terrain])
                
                # 50% chance of enemies if area is passable
                enemies = []
                if is_passable and random.random() < 0.5:
                    enemies = [random.choice(GENERIC_ENEMIES[terrain])]
                
                # 30% chance of items if area is passable
                items = []
                if is_passable and random.random() < 0.3:
                    items = [random.choice(GENERIC_ITEMS[terrain])]
                
                # Create the area node
                node = AreaNode(
                    area=None,  # No specific named area
                    position=position,
                    terrain_type=terrain,
                    base_description=desc,
                    requirements=requirements,
                    enemies=enemies,
                    items=items,
                    is_passable=is_passable
                )
                
                # Add to our maps
                self.position_to_area[position] = node
    
    def _initialize_named_areas(self):
        """Initialize named areas with their special properties."""
        for position, area_enum in NAMED_AREAS.items():
            area_data = AREA_DATA[area_enum]
            
            node = AreaNode(
                area=area_enum,
                position=position,
                terrain_type=area_data["terrain"],
                base_description=area_data["desc"],
                requirements=area_data["reqs"],
                enemies=area_data["enemies"],
                items=area_data["items"],
            )
            
            # Add to our maps
            self.position_to_area[position] = node
            self.areas[area_enum] = node
        
        # After initializing all areas, call the diagnostic function
        self._print_map_diagnostics()

    def _print_map_diagnostics(self):
        """Print diagnostic information about the map initialization."""
        print("\n==== MAP INITIALIZATION DIAGNOSTICS ====")
        
        # Check NAMED_AREAS dictionary
        print(f"NAMED_AREAS contains {len(NAMED_AREAS)} entries:")
        for position, area_enum in NAMED_AREAS.items():
            print(f"  Position {position} -> {area_enum.name} ({area_enum.value})")
        
        # Check position_to_area dictionary
        print(f"\nposition_to_area contains {len(self.position_to_area)} entries")
        print("Named areas in position_to_area:")
        for position, node in self.position_to_area.items():
            if node.area and isinstance(node.area, StoryArea):
                print(f"  Position {position} -> {node.area.name} ({node.area.value})")
        
        # Check areas dictionary
        print(f"\nareas dictionary contains {len(self.areas)} entries:")
        for area_enum, node in self.areas.items():
            print(f"  {area_enum.name} -> Position {node.position}")
        
        # Check specifically for Warriors Camp
        warriors_camp_pos = (1, 0)
        if warriors_camp_pos in self.position_to_area:
            node = self.position_to_area[warriors_camp_pos]
            print(f"\nWarriors Camp at (1, 0): {node.area.name if node.area else 'Not found'}")
            print(f"  Is passable: {getattr(node, 'is_passable', True)}")
            print(f"  Requirements: {getattr(node, 'requirements', [])}")
        else:
            print("\nWarriors Camp not found at position (1, 0)")
        
        # Check for StoryArea.WARRIORS_CAMP in areas dictionary
        if StoryArea.WARRIORS_CAMP in self.areas:
            node = self.areas[StoryArea.WARRIORS_CAMP]
            print(f"\nWarriors Camp in areas dictionary: {node.position}")
        else:
            print("\nWarriors Camp not found in areas dictionary")
        
        print("==== END MAP DIAGNOSTICS ====\n")
    
    def _fix_phantom_assassin_location(self):
        """Fix the phantom assassin location to ensure it's at the shadow training area."""
        # Find the shadow training area
        shadow_training = self.get_area_node("shadow_training")
        if shadow_training and "phantom_assassin" not in shadow_training.enemies:
                shadow_training.enemies.append("phantom_assassin")
    
    def _create_enemies(self, enemy_names: List[str]) -> List[str]:
        """Create enemies for an area."""
        return enemy_names
    
    def get_area_node(self, area) -> Optional[AreaNode]:
        """Get an area node by name or enum."""
        if isinstance(area, str):
            # Convert string to enum
            area = getattr(StoryArea, area.upper(), None)
            if area:
                return self.areas.get(area)
            
            # Check if it's a position string like "0,0"
            try:
                if "," in area:
                    x, y = map(int, area.split(","))
                    return self.position_to_area.get((x, y))
            except:
                pass
                
            return None
            
        if isinstance(area, StoryArea):
            return self.areas.get(area)
            
        return None
    
    def get_adjacent_areas(self, current_area: StoryArea, inventory: List[str]) -> List[Tuple[StoryArea, Direction]]:
        """Get available adjacent areas from the current area based on position and inventory."""
        if isinstance(current_area, StoryArea):
            node = self.areas.get(current_area)
        else:
            # Try to get by position if it's not a StoryArea
            node = self.position_to_area.get(current_area)
            
        if not node:
            return []
            
        x, y = node.position
        adjacent_positions = [
            ((x, y + 1), Direction.NORTH),
            ((x, y - 1), Direction.SOUTH),
            ((x + 1, y), Direction.EAST),
            ((x - 1, y), Direction.WEST)
        ]
        
        adjacent_areas = []
        for pos, direction in adjacent_positions:
            # Check if position is in bounds (10x10 grid)
            if 0 <= pos[0] < 10 and 0 <= pos[1] < 10:
                # Check if area exists at this position
                area_node = self.position_to_area.get(pos)
                if area_node and area_node.is_passable:
                    # Check if player has required items
                    if all(req in inventory for req in area_node.requirements):
                        # If it's a named area, return the StoryArea enum
                        if area_node.area:
                            adjacent_areas.append((area_node.area, direction))
                        else:
                            # For generic areas, return the position as a string
                            area_name = f"Area ({pos[0]},{pos[1]})"
                            adjacent_areas.append((area_name, direction))
        
        return adjacent_areas
    
    def move_player(self, current_area, direction: Direction, inventory: List[str]) -> Optional[str]:
        """Move the player in the specified direction if possible."""
        # Get the current position
        if isinstance(current_area, StoryArea):
            node = self.areas.get(current_area)
        else:
            # Handle cases where current_area is a position tuple or string
            if isinstance(current_area, str) and not hasattr(StoryArea, current_area.upper()):
                # It's a generic area name like "Area (1,2)"
                try:
                    import re
                    match = re.search(r'\((\d+),(\d+)\)', current_area)
                    if match:
                        x, y = int(match.group(1)), int(match.group(2))
                        node = self.position_to_area.get((x, y))
                    else:
                        return None
                except:
                    return None
            else:
                node = self.position_to_area.get(current_area)
            
        if not node:
            return None
        
        # Calculate the new position
        x, y = node.position
        if direction == Direction.NORTH:
            new_position = (x, y + 1)
        elif direction == Direction.SOUTH:
            new_position = (x, y - 1)
        elif direction == Direction.EAST:
            new_position = (x + 1, y)
        elif direction == Direction.WEST:
            new_position = (x - 1, y)
        else:
            return None  # Invalid direction
        
        # Check if new position is in bounds (10x10 grid)
        if not (0 <= new_position[0] < 10 and 0 <= new_position[1] < 10):
            return None
        
        # Check if there's an area at the new position
        new_area_node = self.position_to_area.get(new_position)
        if not new_area_node:
            return None  # No area at this position
        
        # Check requirements
        if not all(req in inventory for req in new_area_node.requirements):
            return None  # Requirements not met
        
        # Return the area identifier (StoryArea enum if named, or position string if generic)
        if new_area_node.area:
            return new_area_node.area
        else:
            return f"Area ({new_position[0]},{new_position[1]})"
    
    def get_area_by_position(self, position) -> Optional[AreaNode]:
        """Get an area node by position."""
        return self.position_to_area.get(position)
    
    def get_active_hazards(self, area) -> List[EnvironmentalHazard]:
        """Get currently active hazards in an area."""
        node = None
        if isinstance(area, StoryArea):
            node = self.areas.get(area)
        elif isinstance(area, tuple) and len(area) == 2:
            node = self.position_to_area.get(area)
        
        if not node or not node.hazards:
            return []
            
        return node.hazards
    
    def get_weather_description(self, area) -> str:
        """Get the current weather description for an area."""
        # In a real implementation, this would check time of day, season, etc.
        weather_options = [
            "Clear skies above.",
            "A light breeze rustles the leaves.",
            "Clouds drift lazily overhead.",
            "The air is crisp and clear."
        ]
        return random.choice(weather_options)
        
    def set_current_area(self, area: StoryArea) -> bool:
        """Set the current area for testing purposes.
        
        Args:
            area: The StoryArea to set as current
            
        Returns:
            bool: True if successful, False if the area doesn't exist
        """
        # Check if the area exists in our map
        area_node = self.get_area_node(area)
        if not area_node:
            return False
            
        # In a real implementation, this would update the player's position
        # For testing purposes, we just return success
        return True 