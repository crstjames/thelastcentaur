"""
Map system for The Last Centaur.

This module handles the game's map layout, area connections,
and transition logic between different areas.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from .models import Direction, TerrainType, StoryArea, TileState, Enemy
from .world_design import AREA_REQUIREMENTS, WORLD_ENEMIES

@dataclass
class EnvironmentalHazard:
    """Represents an environmental hazard in an area."""
    type: str
    description: str
    damage: int
    requirements: List[str]  # Items needed to safely pass
    active_times: Optional[List[str]] = None  # Time-based hazards

@dataclass
class AreaConnection:
    """Represents a connection between two areas."""
    from_area: StoryArea
    to_area: StoryArea
    direction: Direction
    requirements: List[str]
    description: str
    is_locked: bool = True
    hazards: List[EnvironmentalHazard] = None
    shortcut: bool = False  # Indicates if this is a hidden shortcut

@dataclass
class AreaNode:
    """Represents an area node in the game map."""
    area: StoryArea
    position: Tuple[int, int]
    connections: List[AreaConnection]
    terrain_type: TerrainType
    base_description: str
    requirements: List[str]
    enemies: List[str]
    items: List[str]
    hazards: List[EnvironmentalHazard] = None
    weather_effects: List[str] = None
    is_minor_area: bool = False
    npcs: List[str] = None

# Environmental Hazards
HAZARD_TYPES = {
    "magic_barrier": EnvironmentalHazard(
        type="magic_barrier",
        description="A shimmering wall of ancient magic blocks the path.",
        damage=50,
        requirements=["crystal_focus", "ancient_sword"]
    ),
    "shadow_veil": EnvironmentalHazard(
        type="shadow_veil",
        description="Impenetrable shadows swirl across the path.",
        damage=30,
        requirements=["stealth_cloak"]
    ),
    "crystal_storm": EnvironmentalHazard(
        type="crystal_storm",
        description="Sharp crystal shards swirl through the air.",
        damage=25,
        requirements=["crystal_shield"],
        active_times=["night"]
    ),
    "spectral_winds": EnvironmentalHazard(
        type="spectral_winds",
        description="Howling winds carry the voices of the fallen.",
        damage=20,
        requirements=["war_horn"],
        active_times=["dusk", "dawn"]
    )
}

# Weather Effects
WEATHER_EFFECTS = {
    "magical_storm": "Reality warps and bends under magical energies.",
    "shadow_mist": "Thick mists obscure vision and muffle sound.",
    "crystal_rain": "Crystalline droplets fall from the sky, resonating with magical frequencies.",
    "spirit_winds": "Ethereal winds carry whispers of the past."
}

# Map Layout Definition
GAME_MAP = {
    # Starting Area - Now at (0,0) for bottom-left starting position
    StoryArea.AWAKENING_WOODS: AreaNode(
        area=StoryArea.AWAKENING_WOODS,
        position=(0, 0),  # Changed from (5, 0) to (0, 0)
        connections=[
            AreaConnection(
                from_area=StoryArea.AWAKENING_WOODS,
                to_area=StoryArea.TRIALS_PATH,
                direction=Direction.NORTH,
                requirements=[],
                description="A well-worn path leads northward, marked by ancient stone markers."
            ),
            AreaConnection(
                from_area=StoryArea.AWAKENING_WOODS,
                to_area="warriors_camp",
                direction=Direction.EAST,
                requirements=[],
                description="A small path leads to a warrior's camp."
            ),
            # Removed south and west connections as this is now the bottom-left starting position
        ],
        terrain_type=TerrainType.FOREST,
        base_description="You stand in a ancient forest clearing. The air is thick with magic and mystery.",
        requirements=[],
        enemies=["forest_guardian"],
        items=["rusty_sword", "leather_pouch"]
    ),

    # Warrior Path area to the east at (1, 0)
    "warriors_camp": AreaNode(
        area="warriors_camp",
        position=(1, 0),
        connections=[
            AreaConnection(
                from_area="warriors_camp",
                to_area=StoryArea.AWAKENING_WOODS,
                direction=Direction.WEST,
                requirements=[],
                description="The path leads back to the forest clearing."
            ),
            AreaConnection(
                from_area="warriors_camp",
                to_area="mountain_base",
                direction=Direction.NORTH,
                requirements=[],
                description="A steep trail winds up into the mountains."
            ),
            AreaConnection(
                from_area="warriors_camp",
                to_area="training_grounds",
                direction=Direction.EAST,
                requirements=[],
                description="You see combat training dummies in the distance."
            ),
        ],
        terrain_type=TerrainType.CLEARING,
        base_description="A small encampment with training equipment and weapon racks. Warriors hone their skills here.",
        requirements=[],
        enemies=["training_dummy"],
        items=["basic_shield"]
    ),

    # Trials path to the north at (0, 1)
    StoryArea.TRIALS_PATH: AreaNode(
        area=StoryArea.TRIALS_PATH,
        position=(0, 1),  # Updated from original position
        connections=[
            AreaConnection(
                from_area=StoryArea.TRIALS_PATH,
                to_area=StoryArea.AWAKENING_WOODS,
                direction=Direction.SOUTH,
                requirements=[],
                description="The path leads back to the forest clearing."
            ),
            AreaConnection(
                from_area=StoryArea.TRIALS_PATH,
                to_area="mountain_base",
                direction=Direction.EAST,
                requirements=[],
                description="A path winds toward the base of the mountains."
            ),
            AreaConnection(
                from_area=StoryArea.TRIALS_PATH,
                to_area=StoryArea.SHADOW_DOMAIN,
                direction=Direction.NORTH,
                requirements=["shadow_key"],
                description="A shimmering portal leads to a shadowy realm."
            ),
        ],
        terrain_type=TerrainType.FOREST,
        base_description="Ancient stone markers line this path, each inscribed with forgotten runes.",
        requirements=[],
        enemies=["forest_wolf"],
        items=["healing_herb"]
    ),

    # Mountain Base area at (1, 1) - connecting warrior and mystic paths
    "mountain_base": AreaNode(
        area="mountain_base",
        position=(1, 1),
        connections=[
            AreaConnection(
                from_area="mountain_base",
                to_area="warriors_camp",
                direction=Direction.SOUTH,
                requirements=[],
                description="The path leads down to the warrior camp."
            ),
            AreaConnection(
                from_area="mountain_base",
                to_area=StoryArea.TRIALS_PATH,
                direction=Direction.WEST,
                requirements=[],
                description="A path leads toward ancient stone markers."
            ),
            AreaConnection(
                from_area="mountain_base",
                to_area="training_grounds",
                direction=Direction.EAST,
                requirements=[],
                description="The path continues eastward to training grounds."
            ),
            AreaConnection(
                from_area="mountain_base",
                to_area=StoryArea.MYSTIC_MOUNTAINS,
                direction=Direction.NORTH,
                requirements=[],
                description="A steep trail winds higher into the mountains."
            ),
        ],
        terrain_type=TerrainType.MOUNTAIN,
        base_description="The terrain becomes rocky as you approach the mountain base. A cool breeze flows down from the peaks.",
        requirements=[],
        enemies=["mountain_goat"],
        items=["climbing_rope"]
    ),

    # Training grounds at (2, 0) - deeper into warrior path
    "training_grounds": AreaNode(
        area="training_grounds",
        position=(2, 0),
        connections=[
            AreaConnection(
                from_area="training_grounds",
                to_area="warriors_camp",
                direction=Direction.WEST,
                requirements=[],
                description="The path leads back to the warrior camp."
            ),
            AreaConnection(
                from_area="training_grounds",
                to_area="mountain_base",
                direction=Direction.NORTH,
                requirements=[],
                description="A path leads to the mountain base."
            ),
            AreaConnection(
                from_area="training_grounds",
                to_area="honor_shrine",
                direction=Direction.EAST,
                requirements=["warrior_token"],
                description="A path to a sacred shrine is visible eastward."
            ),
        ],
        terrain_type=TerrainType.CLEARING,
        base_description="Advanced training equipment and weapon racks. The ground is packed from countless sparring matches.",
        requirements=[],
        enemies=["veteran_warrior"],
        items=["steel_sword"]
    ),

    # Stealth Path - Shadow Domain at (0, 2)
    StoryArea.SHADOW_DOMAIN: AreaNode(
        area=StoryArea.SHADOW_DOMAIN,
        position=(0, 2),
        connections=[
            AreaConnection(
                from_area=StoryArea.SHADOW_DOMAIN,
                to_area=StoryArea.TRIALS_PATH,
                direction=Direction.SOUTH,
                requirements=[],
                description="The shimmering portal leads back to the trials path."
            ),
            AreaConnection(
                from_area=StoryArea.SHADOW_DOMAIN,
                to_area="shadow_training",
                direction=Direction.EAST,
                requirements=[],
                description="A path of shadows extends eastward."
            ),
            AreaConnection(
                from_area=StoryArea.SHADOW_DOMAIN,
                to_area="forgotten_temple",
                direction=Direction.NORTH,
                requirements=["shadow_cloak"],
                description="A nearly invisible path leads to a forgotten temple."
            ),
        ],
        terrain_type=TerrainType.RUINS,
        base_description="Shadows move with a life of their own here. Light seems to be absorbed rather than reflected.",
        requirements=["shadow_key"],
        enemies=["shadow_stalker"],
        items=["phantom_dagger"]
    ),

    # Mystic Mountains at (1, 2) - start of mystic path
    StoryArea.MYSTIC_MOUNTAINS: AreaNode(
        area=StoryArea.MYSTIC_MOUNTAINS,
        position=(1, 2),
        connections=[
            AreaConnection(
                from_area=StoryArea.MYSTIC_MOUNTAINS,
                to_area="mountain_base",
                direction=Direction.SOUTH,
                requirements=[],
                description="The path leads back down the mountain."
            ),
            AreaConnection(
                from_area=StoryArea.MYSTIC_MOUNTAINS,
                to_area="shadow_training",
                direction=Direction.WEST,
                requirements=["shadow_key"],
                description="A nearly invisible path leads westward."
            ),
            AreaConnection(
                from_area=StoryArea.MYSTIC_MOUNTAINS,
                to_area="crystal_pond",
                direction=Direction.EAST,
                requirements=[],
                description="A trail leads toward a shimmering glow."
            ),
            AreaConnection(
                from_area=StoryArea.MYSTIC_MOUNTAINS,
                to_area=StoryArea.ENCHANTED_VALLEY,
                direction=Direction.NORTH,
                requirements=[],
                description="The path continues upward, entering a hidden valley."
            ),
        ],
        terrain_type=TerrainType.MOUNTAIN,
        base_description="The air thins as you climb. Strange energies dance at the edge of perception.",
        requirements=[],
        enemies=["mountain_spirit"],
        items=["crystal_focus"]
    ),

    # Shadow training at (0, 3) - deeper into stealth path
    "shadow_training": AreaNode(
        area="shadow_training",
        position=(0, 3),
        connections=[
            AreaConnection(
                from_area="shadow_training",
                to_area=StoryArea.SHADOW_DOMAIN,
                direction=Direction.WEST,
                requirements=[],
                description="The shadow path leads back to the domain entrance."
            ),
            AreaConnection(
                from_area="shadow_training",
                to_area=StoryArea.MYSTIC_MOUNTAINS,
                direction=Direction.EAST,
                requirements=[],
                description="A faint trail leads toward the mountain."
            ),
            AreaConnection(
                from_area="shadow_training",
                to_area="forgotten_temple",
                direction=Direction.NORTH,
                requirements=["stealth_token"],
                description="A concealed passage leads to an ancient temple."
            ),
        ],
        terrain_type=TerrainType.RUINS,
        base_description="Training dummies made of shadow stand motionless, waiting for practice.",
        requirements=[],
        enemies=["shadow_initiate"],
        items=["smoke_bomb", "stealth_cloak"]
    ),

    # Crystal pond at (2, 2) - deeper into mystic path
    "crystal_pond": AreaNode(
        area="crystal_pond",
        position=(2, 2),
        connections=[
            AreaConnection(
                from_area="crystal_pond",
                to_area=StoryArea.MYSTIC_MOUNTAINS,
                direction=Direction.WEST,
                requirements=[],
                description="The path leads back to the mountains."
            ),
            AreaConnection(
                from_area="crystal_pond",
                to_area=StoryArea.ENCHANTED_VALLEY,
                direction=Direction.NORTH,
                requirements=[],
                description="A serene path leads upward into a valley."
            ),
            AreaConnection(
                from_area="crystal_pond",
                to_area="meditation_circle",
                direction=Direction.EAST,
                requirements=["mystic_token"],
                description="A path of glowing stones leads to a meditation circle."
            ),
        ],
        terrain_type=TerrainType.VALLEY,
        base_description="A small pond whose waters glow with inner light. Crystals grow from the surrounding rocks.",
        requirements=[],
        enemies=["crystal_elemental"],
        items=["mana_crystal", "mystic_herbs"]
    ),

    # Adding the rest of the important areas to complete the paths

    # Honor Shrine (3, 0) - warrior path culmination
    "honor_shrine": AreaNode(
        area="honor_shrine",
        position=(3, 0),
        connections=[
            AreaConnection(
                from_area="honor_shrine",
                to_area="training_grounds",
                direction=Direction.WEST,
                requirements=[],
                description="The path leads back to the training grounds."
            ),
        ],
        terrain_type=TerrainType.RUINS,
        base_description="An ancient shrine dedicated to honor and courage. Weapons of legendary warriors decorate the walls.",
        requirements=["warrior_token"],
        enemies=["honor_guardian"],
        items=["warrior_talisman", "ancient_sword"]
    ),

    # Forgotten Temple (0, 4) - stealth path culmination
    "forgotten_temple": AreaNode(
        area="forgotten_temple",
        position=(0, 4),
        connections=[
            AreaConnection(
                from_area="forgotten_temple",
                to_area="shadow_training",
                direction=Direction.SOUTH,
                requirements=[],
                description="The concealed passage leads back to the training area."
            ),
            AreaConnection(
                from_area="forgotten_temple",
                to_area=StoryArea.SHADOW_DOMAIN,
                direction=Direction.SOUTH,
                requirements=[],
                description="A nearly invisible path leads back to the shadow domain."
            ),
        ],
        terrain_type=TerrainType.RUINS,
        base_description="A temple forgotten by all but the shadows. Ancient assassins once trained here.",
        requirements=["stealth_token", "shadow_cloak"],
        enemies=["shadow_master"],
        items=["shadow_blade", "stealth_talisman"]
    ),

    # Meditation Circle (3, 2) - mystic path culmination
    "meditation_circle": AreaNode(
        area="meditation_circle",
        position=(3, 2),
        connections=[
            AreaConnection(
                from_area="meditation_circle",
                to_area="crystal_pond",
                direction=Direction.WEST,
                requirements=[],
                description="The path of glowing stones leads back to the crystal pond."
            ),
        ],
        terrain_type=TerrainType.VALLEY,
        base_description="A perfect circle of ancient stones, humming with magical energy. The air itself seems to enhance focus.",
        requirements=["mystic_token"],
        enemies=["spirit_guide"],
        items=["mystic_talisman", "spell_focus"]
    ),

    # Enchanted Valley (1, 3) - high-level mystic area
    StoryArea.ENCHANTED_VALLEY: AreaNode(
        area=StoryArea.ENCHANTED_VALLEY,
        position=(1, 3),
        connections=[
            AreaConnection(
                from_area=StoryArea.ENCHANTED_VALLEY,
                to_area=StoryArea.MYSTIC_MOUNTAINS,
                direction=Direction.SOUTH,
                requirements=[],
                description="The path leads back down the mountain."
            ),
            AreaConnection(
                from_area=StoryArea.ENCHANTED_VALLEY,
                to_area="crystal_pond",
                direction=Direction.SOUTH,
                requirements=[],
                description="A path leads down to a glowing pond."
            ),
            AreaConnection(
                from_area=StoryArea.ENCHANTED_VALLEY,
                to_area=StoryArea.CRYSTAL_CAVES,
                direction=Direction.NORTH,
                requirements=["crystal_key"],
                description="A hidden entrance to mysterious caves is visible."
            ),
        ],
        terrain_type=TerrainType.VALLEY,
        base_description="A valley hidden from the world, where magic flows freely and strange plants grow.",
        requirements=[],
        enemies=["fae_guardian"],
        items=["mystic_token", "crystal_key"]
    ),

    # Crystal Caves (1, 4) - end game area
    StoryArea.CRYSTAL_CAVES: AreaNode(
        area=StoryArea.CRYSTAL_CAVES,
        position=(1, 4),
        connections=[
            AreaConnection(
                from_area=StoryArea.CRYSTAL_CAVES,
                to_area=StoryArea.ENCHANTED_VALLEY,
                direction=Direction.SOUTH,
                requirements=[],
                description="The cave exit leads back to the enchanted valley."
            ),
            AreaConnection(
                from_area=StoryArea.CRYSTAL_CAVES,
                to_area=StoryArea.FORGOTTEN_GROVE,
                direction=Direction.EAST,
                requirements=["all_talismans"],
                description="A crystal arch forms a portal to a mysterious grove."
            ),
        ],
        terrain_type=TerrainType.CAVE,
        base_description="Massive crystals grow from floor to ceiling, humming with ancient power.",
        requirements=["crystal_key"],
        enemies=["crystal_guardian"],
        items=["power_crystal"]
    ),

    # Forgotten Grove (2, 4) - final area
    StoryArea.FORGOTTEN_GROVE: AreaNode(
        area=StoryArea.FORGOTTEN_GROVE,
        position=(2, 4),
        connections=[
            AreaConnection(
                from_area=StoryArea.FORGOTTEN_GROVE,
                to_area=StoryArea.CRYSTAL_CAVES,
                direction=Direction.WEST,
                requirements=[],
                description="The crystal portal leads back to the caves."
            ),
        ],
        terrain_type=TerrainType.FOREST,
        base_description="The legendary grove where the last centaurs made their final stand.",
        requirements=["all_talismans"],
        enemies=["ancient_guardian"],
        items=["centaur_relic"]
    ),
}

class MapSystem:
    """Handles map-related operations and transitions."""
    
    def __init__(self):
        self.current_area = StoryArea.AWAKENING_WOODS
        self.discovered_areas: Set[StoryArea] = {StoryArea.AWAKENING_WOODS}
        self.unlocked_connections: Set[Tuple[StoryArea, StoryArea]] = set()
        self.current_time = "day"  # Track time of day for hazards
        
        # Initialize starting area with proper Enemy objects
        starting_node = GAME_MAP[StoryArea.AWAKENING_WOODS]
        starting_node.enemies = self._create_enemies(["forest_guardian"])
        
        # Fix the Phantom Assassin location
        self._fix_phantom_assassin_location()
        
        self.areas = GAME_MAP
        self.position_to_area = {}
        
        # Build a position-to-area lookup
        for area_id, area_node in self.areas.items():
            self.position_to_area[area_node.position] = area_node
    
    def _fix_phantom_assassin_location(self):
        """Fix the phantom assassin location to ensure it's at the shadow training area."""
        # Find the shadow training area
        shadow_training = self.get_area_node("shadow_training")
        if shadow_training:
            # Add phantom assassin to shadow training area
            if "phantom_assassin" not in shadow_training.enemies:
                shadow_training.enemies.append("phantom_assassin")
                print("Added phantom_assassin to shadow_training area")
        else:
            print("Warning: shadow_training area not found")
    
    def _create_enemies(self, enemy_ids: List[str]) -> List[Enemy]:
        """Convert enemy IDs to Enemy objects based on current time."""
        enemies = []
        for enemy_id in enemy_ids:
            enemy_data = next((e for e in WORLD_ENEMIES if e["id"] == enemy_id), None)
            if enemy_data:
                is_night_only = enemy_data.get("night_only", False)
                if not is_night_only or (is_night_only and self.current_time == "night"):
                    enemies.append(Enemy(
                        name=enemy_data["name"],
                        description=enemy_data["description"],
                        health=enemy_data["health"],
                        damage=enemy_data["damage"],
                        drops=enemy_data.get("drops", []),
                        requirements=enemy_data.get("requirements", [])
                    ))
        return enemies
    
    def get_area_node(self, area: StoryArea) -> AreaNode:
        """Get the area node for a given area."""
        return GAME_MAP[area]
    
    def get_available_connections(self, area: StoryArea, inventory: List[str]) -> List[AreaConnection]:
        """Get available connections from the current area based on inventory."""
        node = self.get_area_node(area)
        available = []
        
        for conn in node.connections:
            # Check if player has required items
            has_requirements = all(req in inventory for req in conn.requirements)
            # Check hazard requirements
            can_pass_hazards = True
            if conn.hazards:
                for hazard in conn.hazards:
                    if hazard.active_times and self.current_time not in hazard.active_times:
                        continue
                    if not all(req in inventory for req in hazard.requirements):
                        can_pass_hazards = False
                        break
            
            if has_requirements and can_pass_hazards:
                available.append(conn)
        
        return available
    
    def get_active_hazards(self, area: StoryArea) -> List[EnvironmentalHazard]:
        """Get currently active hazards in an area."""
        node = self.get_area_node(area)
        if not node.hazards:
            return []
            
        return [
            hazard for hazard in node.hazards
            if not hazard.active_times or self.current_time in hazard.active_times
        ]
    
    def get_weather_description(self, area: StoryArea) -> str:
        """Get the current weather effects for an area."""
        node = self.get_area_node(area)
        if not node.weather_effects:
            return "The weather is calm."
            
        effects = [WEATHER_EFFECTS[effect] for effect in node.weather_effects]
        return " ".join(effects)
    
    def can_transition(self, from_area: StoryArea, to_area: StoryArea, 
                      direction: Direction, inventory: List[str]) -> Tuple[bool, str]:
        """Check if transition between areas is possible."""
        # Get the connection if it exists
        node = self.get_area_node(from_area)
        connection = next((c for c in node.connections 
                         if c.to_area == to_area and c.direction == direction), None)
        
        if not connection:
            # Try to find any connection in the requested direction
            connection = next((c for c in node.connections if c.direction == direction), None)
            if connection:
                to_area = connection.to_area
            else:
                return False, "No path exists in that direction."
            
        # Check requirements
        missing_items = [req for req in connection.requirements if req not in inventory]
        if missing_items:
            return False, f"Missing required items: {', '.join(missing_items)}"
            
        # Check if destination area is accessible
        dest_node = self.get_area_node(to_area)
        missing_area_items = [req for req in dest_node.requirements if req not in inventory]
        if missing_area_items:
            return False, f"Cannot enter area. Missing: {', '.join(missing_area_items)}"
            
        return True, connection.description
    
    def transition_area(self, from_area: StoryArea, to_area: StoryArea, 
                       direction: Direction, inventory: List[str]) -> Tuple[bool, str, Optional[TileState]]:
        """Attempt to transition between areas."""
        can_move, message = self.can_transition(from_area, to_area, direction, inventory)
        
        if not can_move:
            return False, message, None
            
        # Create the new area's tile state
        dest_node = self.get_area_node(to_area)
        
        # Convert enemy dictionaries to Enemy objects
        enemies = self._create_enemies(dest_node.enemies)
        
        # Initialize NPCs list from area node
        npcs = dest_node.npcs if dest_node.npcs else []
        
        new_tile = TileState(
            position=dest_node.position,
            terrain_type=dest_node.terrain_type,
            area=to_area,
            description=dest_node.base_description,
            items=dest_node.items.copy(),
            enemies=enemies,
            npcs=npcs,
            is_visited=to_area in self.discovered_areas
        )
        
        # Update discovered areas
        self.discovered_areas.add(to_area)
        self.unlocked_connections.add((from_area, to_area))
        
        return True, message, new_tile
    
    def get_area_description(self, area: StoryArea, is_first_visit: bool) -> str:
        """Get the description for an area, including any special first-visit text."""
        node = self.get_area_node(area)
        description = node.base_description
        
        # Add weather effects
        description += f"\n\n{self.get_weather_description(area)}"
        
        # Add active hazards
        active_hazards = self.get_active_hazards(area)
        if active_hazards:
            description += "\n\nHazards:"
            for hazard in active_hazards:
                description += f"\n- {hazard.description}"
        
        if is_first_visit:
            description += "\n\nYou have discovered a new area!"
            
        # Add connection descriptions
        for conn in node.connections:
            if (area, conn.to_area) in self.unlocked_connections:
                description += f"\n\n{conn.description}"
                if conn.shortcut:
                    description += " (Shortcut)"
                
        return description
    
    def update_time(self, time_of_day: str) -> None:
        """Update the current time and handle time-based changes."""
        self.current_time = time_of_day.lower()
        
        # Update enemies based on time
        for area in self.discovered_areas:
            node = self.get_area_node(area)
            if isinstance(node.enemies, list):
                # Convert enemy IDs to Enemy objects if needed
                if node.enemies and isinstance(node.enemies[0], str):
                    node.enemies = self._create_enemies(node.enemies)
                # Update enemies based on time of day
                tile = TileState(
                    position=node.position,
                    terrain_type=node.terrain_type,
                    area=area,
                    description=node.base_description,
                    items=node.items.copy(),
                    enemies=node.enemies,
                    is_visited=True
                )
                tile.update_enemies(time_of_day)
                node.enemies = tile.enemies
                
                # Update description based on time of day
                if time_of_day.lower() == "night":
                    if "The land lies under a blanket of stars" not in node.base_description:
                        node.base_description += " The land lies under a blanket of stars."
    
    def get_position_for_area(self, area: StoryArea) -> Tuple[int, int]:
        """Get the position coordinates for an area."""
        node = self.get_area_node(area)
        if node:
            return node.position
        return (0, 0)  # Default to starting position
                
    def get_tile_at_position(self, position: Tuple[int, int]) -> Optional[AreaNode]:
        """Get the area node at a specific position."""
        for area, node in GAME_MAP.items():
            if node.position == position:
                return node
        return None 