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
    # Starting Area
    StoryArea.AWAKENING_WOODS: AreaNode(
        area=StoryArea.AWAKENING_WOODS,
        position=(5, 0),
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
            AreaConnection(
                from_area=StoryArea.AWAKENING_WOODS,
                to_area="druids_grove",
                direction=Direction.WEST,
                requirements=[],
                description="A mystical path leads to a secluded grove."
            )
        ],
        terrain_type=TerrainType.FOREST,
        base_description="Ancient woods where you first awakened, stripped of your power.",
        requirements=[],
        enemies=["wolf_pack", "corrupted_sprite"],
        items=["basic_supplies", "old_map"],
        weather_effects=["spirit_winds"]
    ),
    
    # Hermit Druid's Grove
    "druids_grove": AreaNode(
        area="druids_grove",
        position=(4, 0),
        connections=[
            AreaConnection(
                from_area="druids_grove",
                to_area=StoryArea.AWAKENING_WOODS,
                direction=Direction.EAST,
                requirements=[],
                description="The path leads back to the ancient woods."
            )
        ],
        terrain_type=TerrainType.FOREST,
        base_description="A peaceful grove where the Hermit Druid contemplates the mysteries of the past.",
        requirements=[],
        enemies=[],
        items=["crystal_focus", "ancient_scroll"],
        weather_effects=["spirit_winds"],
        npcs=["hermit_druid"]
    ),
    
    # Fallen Warrior's Camp
    "warriors_camp": AreaNode(
        area="warriors_camp",
        position=(6, 0),
        connections=[
            AreaConnection(
                from_area="warriors_camp",
                to_area=StoryArea.AWAKENING_WOODS,
                direction=Direction.WEST,
                requirements=[],
                description="The path leads back to the ancient woods."
            )
        ],
        terrain_type=TerrainType.CLEARING,
        base_description="A small camp where the Fallen Warrior resides, surrounded by old battle standards.",
        requirements=[],
        enemies=[],
        items=["warrior_map"],
        weather_effects=["spirit_winds"],
        npcs=["fallen_warrior"]
    ),
    
    # New Minor Area: Twilight Glade
    "twilight_glade": AreaNode(
        area="twilight_glade",
        position=(4, 3),
        connections=[
            AreaConnection(
                from_area="twilight_glade",
                to_area=StoryArea.FORGOTTEN_GROVE,
                direction=Direction.NORTH,
                requirements=["shadow_key"],
                description="Shadows coalesce into a hidden path.",
                shortcut=True
            )
        ],
        terrain_type=TerrainType.FOREST,
        base_description="A small clearing where twilight seems to linger eternally.",
        requirements=[],
        enemies=["shadow_hound"],
        items=["shadow_essence_fragment"],
        hazards=[HAZARD_TYPES["shadow_veil"]],
        weather_effects=["shadow_mist"],
        is_minor_area=True
    ),
    
    # New Minor Area: Warrior's Rest
    "warriors_rest": AreaNode(
        area="warriors_rest",
        position=(6, 3),
        connections=[
            AreaConnection(
                from_area="warriors_rest",
                to_area=StoryArea.ANCIENT_RUINS,
                direction=Direction.EAST,
                requirements=["warrior_token"],
                description="A hidden path marked by ancient battle standards.",
                shortcut=True
            )
        ],
        terrain_type=TerrainType.RUINS,
        base_description="A sheltered hollow where ancient warriors once made camp.",
        requirements=[],
        enemies=["spectral_sentinel", "corrupted_centaur_spirit"],
        items=["warrior_token", "ancient_battle_plan"],
        hazards=[HAZARD_TYPES["spectral_winds"]],
        weather_effects=["spirit_winds"],
        is_minor_area=True
    ),
    
    # New Minor Area: Crystal Outpost
    "crystal_outpost": AreaNode(
        area="crystal_outpost",
        position=(2, 5),
        connections=[
            AreaConnection(
                from_area="crystal_outpost",
                to_area=StoryArea.CRYSTAL_CAVES,
                direction=Direction.NORTH,
                requirements=["crystal_key"],
                description="A crystalline archway pulses with stored magical energy.",
                shortcut=True
            )
        ],
        terrain_type=TerrainType.MOUNTAIN,
        base_description="A former research post of the centaur mystics, now overrun by crystal formations.",
        requirements=["crystal_focus"],
        enemies=["crystal_golem", "mana_wraith"],
        items=["crystal_key", "mystic_research_notes"],
        hazards=[HAZARD_TYPES["crystal_storm"]],
        weather_effects=["crystal_rain"],
        is_minor_area=True
    ),
    
    # Central Hub Area
    StoryArea.TRIALS_PATH: AreaNode(
        area=StoryArea.TRIALS_PATH,
        position=(5, 2),
        connections=[
            AreaConnection(
                from_area=StoryArea.TRIALS_PATH,
                to_area=StoryArea.MYSTIC_MOUNTAINS,
                direction=Direction.WEST,
                requirements=["crystal_focus"],
                description="A path spirals up into the misty mountains, crackling with magical energy."
            ),
            AreaConnection(
                from_area=StoryArea.TRIALS_PATH,
                to_area=StoryArea.ANCIENT_RUINS,
                direction=Direction.EAST,
                requirements=["warrior_map"],
                description="Ancient stone steps lead to crumbling ruins of a forgotten stronghold."
            ),
            AreaConnection(
                from_area=StoryArea.TRIALS_PATH,
                to_area="twilight_glade",
                direction=Direction.NORTH,
                requirements=["shadow_key"],
                description="A shadowy path leads to a mysterious glade."
            ),
            AreaConnection(
                from_area=StoryArea.TRIALS_PATH,
                to_area=StoryArea.AWAKENING_WOODS,
                direction=Direction.SOUTH,
                requirements=[],
                description="The path leads back to the awakening woods where your journey began."
            )
        ],
        terrain_type=TerrainType.CLEARING,
        base_description="A crossroads where the three paths diverge, each leading to a different destiny.",
        requirements=[],
        enemies=["wandering_spirit", "lost_warrior"],
        items=["path_marker", "ancient_inscription"],
        npcs=["shadow_scout"]
    ),
    
    # Mystic Path Areas
    StoryArea.MYSTIC_MOUNTAINS: AreaNode(
        area=StoryArea.MYSTIC_MOUNTAINS,
        position=(3, 4),
        connections=[
            AreaConnection(
                from_area=StoryArea.MYSTIC_MOUNTAINS,
                to_area=StoryArea.CRYSTAL_CAVES,
                direction=Direction.NORTH,
                requirements=["crystal_focus"],
                description="Crystal formations mark the entrance to deep, resonating caves.",
                hazards=[HAZARD_TYPES["crystal_storm"]]
            ),
            AreaConnection(
                from_area=StoryArea.MYSTIC_MOUNTAINS,
                to_area="crystal_outpost",
                direction=Direction.WEST,
                requirements=["crystal_focus"],
                description="A narrow path winds down to a crystal-encrusted structure.",
                shortcut=True
            )
        ],
        terrain_type=TerrainType.MOUNTAIN,
        base_description="Jagged peaks pulse with ancient power, their surfaces etched with glowing runes.",
        requirements=["crystal_focus"],
        enemies=["mountain_guardian", "storm_elemental", "crystal_golem"],
        items=["crystal_shard", "runic_inscription"],
        hazards=[HAZARD_TYPES["magic_barrier"]],
        weather_effects=["magical_storm", "crystal_rain"]
    ),
    
    # Crystal Caves Area
    StoryArea.CRYSTAL_CAVES: AreaNode(
        area=StoryArea.CRYSTAL_CAVES,
        position=(3, 6),
        connections=[
            AreaConnection(
                from_area=StoryArea.CRYSTAL_CAVES,
                to_area=StoryArea.SHADOW_DOMAIN,
                direction=Direction.NORTH,
                requirements=["crystal_key", "guardian_essence"],
                description="The crystal-lined tunnel leads to the corrupted domain.",
                hazards=[HAZARD_TYPES["crystal_storm"], HAZARD_TYPES["magic_barrier"]]
            ),
            AreaConnection(
                from_area=StoryArea.CRYSTAL_CAVES,
                to_area=StoryArea.MYSTIC_MOUNTAINS,
                direction=Direction.SOUTH,
                requirements=[],
                description="The path leads back to the mystic mountains."
            )
        ],
        terrain_type=TerrainType.MOUNTAIN,
        base_description="A vast network of crystal-lined caves, humming with ancient magical frequencies.",
        requirements=["crystal_key"],
        enemies=["crystal_guardian", "resonance_spirit"],
        items=["mystic_crystal", "resonance_key", "guardian_essence"],
        hazards=[HAZARD_TYPES["crystal_storm"]],
        weather_effects=["crystal_rain", "magical_storm"]
    ),
    
    # Warrior Path Areas
    StoryArea.ANCIENT_RUINS: AreaNode(
        area=StoryArea.ANCIENT_RUINS,
        position=(7, 4),
        connections=[
            AreaConnection(
                from_area=StoryArea.ANCIENT_RUINS,
                to_area=StoryArea.ENCHANTED_VALLEY,
                direction=Direction.NORTH,
                requirements=["war_horn"],
                description="The path to the valley is guarded by ancient spirits."
            ),
            AreaConnection(
                from_area=StoryArea.ANCIENT_RUINS,
                to_area="warriors_armory",
                direction=Direction.EAST,
                requirements=["ancient_sword"],
                description="A hidden chamber that holds ancient weapons of war."
            )
        ],
        terrain_type=TerrainType.RUINS,
        base_description="Crumbling ruins of a mighty centaur stronghold, echoing with memories of battle.",
        requirements=["warrior_map"],
        enemies=["stone_guardian", "phantom_warrior"],
        items=["ancient_sword", "battle_relic", "warrior_inscription"]
    ),
    
    # New Minor Area: Warrior's Armory
    "warriors_armory": AreaNode(
        area="warriors_armory",
        position=(8, 5),
        connections=[
            AreaConnection(
                from_area="warriors_armory",
                to_area=StoryArea.ANCIENT_RUINS,
                direction=Direction.WEST,
                requirements=[],
                description="The path leads back to the main ruins."
            )
        ],
        terrain_type=TerrainType.RUINS,
        base_description="An ancient armory where the mightiest weapons of the centaur wars were kept.",
        requirements=["ancient_sword"],
        enemies=[],
        items=["war_horn"],
        weather_effects=["spirit_winds"]
    ),
    
    # Stealth Path Areas
    StoryArea.FORGOTTEN_GROVE: AreaNode(
        area=StoryArea.FORGOTTEN_GROVE,
        position=(5, 5),
        connections=[
            AreaConnection(
                from_area=StoryArea.FORGOTTEN_GROVE,
                to_area=StoryArea.SHADOW_DOMAIN,
                direction=Direction.NORTH,
                requirements=["stealth_cloak", "phantom_dagger", "shadow_essence", "shadow_essence_fragment"],
                description="The grove's shadows deepen, leading to the domain of your rival. With both shadow essences combined, you can slip through the veil of reality itself.",
                shortcut=True
            )
        ],
        terrain_type=TerrainType.FOREST,
        base_description="A mysterious grove where shadows move with purpose and secrets hide in plain sight.",
        requirements=["shadow_key"],
        enemies=["shadow_stalker", "phantom_assassin"],
        items=["stealth_cloak", "phantom_dagger", "shadow_essence"],
        weather_effects=["shadow_mist"]
    ),
    
    # Final Area
    StoryArea.SHADOW_DOMAIN: AreaNode(
        area=StoryArea.SHADOW_DOMAIN,
        position=(5, 9),
        connections=[],
        terrain_type=TerrainType.RUINS,
        base_description="The corrupted throne of your rival, where reality itself bends to their will.",
        requirements=[],
        enemies=["shadow_guardian", "second_centaur", "shadow_knight", "void_walker"],
        items=["crown_of_dominion"],
        hazards=[
            HAZARD_TYPES["magic_barrier"],
            HAZARD_TYPES["shadow_veil"],
            HAZARD_TYPES["spectral_winds"]
        ],
        weather_effects=["magical_storm", "shadow_mist", "spirit_winds"]
    ),
    
    # Enchanted Valley Area
    StoryArea.ENCHANTED_VALLEY: AreaNode(
        area=StoryArea.ENCHANTED_VALLEY,
        position=(7, 5),
        connections=[
            AreaConnection(
                from_area=StoryArea.ENCHANTED_VALLEY,
                to_area=StoryArea.SHADOW_DOMAIN,
                direction=Direction.NORTH,
                requirements=["guardian_essence"],
                description="The path to the Shadow Domain lies ahead, guarded by the Shadow Guardian."
            ),
            AreaConnection(
                from_area=StoryArea.ENCHANTED_VALLEY,
                to_area=StoryArea.ANCIENT_RUINS,
                direction=Direction.SOUTH,
                requirements=[],
                description="The ancient ruins lie to the south."
            )
        ],
        terrain_type=TerrainType.VALLEY,
        base_description="A valley of ancient battlefields, where the spirits of fallen warriors still linger.",
        requirements=["war_horn"],
        enemies=["shadow_guardian"],
        items=["guardian_essence"],
        weather_effects=["spirit_winds"]
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
        starting_node.enemies = self._create_enemies(["wolf_pack", "shadow_stalker"])
        
        self.areas = GAME_MAP
        self.position_to_area = {}
        
        # Build a position-to-area lookup
        for area_id, area_node in self.areas.items():
            self.position_to_area[area_node.position] = area_node
    
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
    
    def get_tile_at_position(self, position: Tuple[int, int]) -> Optional[AreaNode]:
        """
        Get the area node at a specific position.
        
        Args:
            position: The (x, y) position to check
            
        Returns:
            The AreaNode at the position, or None if no area exists there
        """
        return self.position_to_area.get(position) 