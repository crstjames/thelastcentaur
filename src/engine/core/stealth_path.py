"""
Stealth Path implementation for The Last Centaur.

This module defines the stealth path quest line and related game mechanics.
The stealth path focuses on subterfuge, evasion, and indirect approaches to problems.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from .models import Item, Enemy, PathType, StoryArea
from .quest_system import Quest, QuestStage, QuestTrigger, QuestTriggerType, QuestStatus

# Stealth path-specific items
SHADOW_CLOAK = Item(
    id="shadow_cloak",
    name="Cloak of Shadows",
    description="A cloak woven from shadow essence that renders the wearer nearly invisible in darkness.",
    type="armor",
    properties={
        "defense": 5,
        "special_ability": "shadow_step",
        "path_type": PathType.STEALTH,
        "effect": "reduces detection chance by 75% in shadows"
    }
)

WHISPER_DAGGER = Item(
    id="whisper_dagger",
    name="Whisper Dagger",
    description="A blade so sharp it cuts without sound, perfect for silent eliminations.",
    type="weapon",
    properties={
        "damage": 8,
        "special_ability": "silent_strike",
        "path_type": PathType.STEALTH,
        "effect": "silent kills have 50% chance to not alert nearby enemies"
    }
)

SHADOW_KEY = Item(
    id="shadow_key",
    name="Shadow Key",
    description="A key made of solidified shadow that can open any lock if used with proper skill.",
    type="tool",
    properties={
        "special_ability": "unlock",
        "path_type": PathType.STEALTH,
        "effect": "can unlock most doors and chests without making noise"
    }
)

# Stealth path-specific enemies
SHADOW_HUNTER = Enemy(
    name="Shadow Hunter",
    description="A skilled tracker who can see through most stealth techniques. Moves silently and strikes with deadly precision.",
    health=80,
    damage=20,
    drops=["hunter_trophy", "detection_charm"]
)

VOID_ASSASSIN = Enemy(
    name="Void Assassin",
    description="An elite assassin who has mastered the arts of shadow and silence. Can disappear and reappear at will.",
    health=150,
    damage=30,
    drops=["void_essence", "assassin_mask"]
)

# Stealth path quest definition
def create_stealth_quest() -> Quest:
    """Create the main stealth path quest."""
    return Quest(
        id="shadows_embrace",
        name="The Shadow's Embrace",
        description="Master the arts of stealth and shadow to find a hidden path to the Second Centaur.",
        hidden_description="The path of stealth will allow you to bypass the Second Centaur's defenses and strike from the shadows.",
        initial_stage="meet_shadow_scout",
        stages={
            "meet_shadow_scout": QuestStage(
                id="meet_shadow_scout",
                description="Find the Shadow Scout hiding in the Awakening Woods.",
                hidden_description="The Shadow Scout is a master of stealth who can teach you the basics of shadow walking.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.NPC_DIALOGUE,
                        target="shadow_scout"
                    )
                ],
                next_stages=["find_shadow_cloak"],
                hint_dialogue={
                    "shadow_scout": "The Second Centaur has eyes everywhere, but not all paths need to be walked in the light. I can show you another way."
                }
            ),
            "find_shadow_cloak": QuestStage(
                id="find_shadow_cloak",
                description="Find the Cloak of Shadows hidden in the abandoned watchtower.",
                hidden_description="The Cloak of Shadows is one of three legendary items that can help defeat the Second Centaur.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ITEM_ACQUIRED,
                        target="shadow_cloak"
                    )
                ],
                next_stages=["evade_shadow_hunter"],
                hint_dialogue={
                    "shadow_scout": "The cloak was hidden in the old watchtower to the north. Be careful, the tower is not as abandoned as it seems."
                }
            ),
            "evade_shadow_hunter": QuestStage(
                id="evade_shadow_hunter",
                description="Evade the Shadow Hunter and escape the watchtower.",
                hidden_description="The Shadow Hunter is testing your stealth abilities. Defeating him is not necessary, but escaping is.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.AREA_VISITED,
                        target="forest_edge",
                        condition="undetected=true"
                    )
                ],
                next_stages=["enter_shadow_path"],
                hint_dialogue={
                    "shadow_scout": "The Hunter is skilled, but not infallible. Use the shadows, move slowly, and time your movements carefully."
                }
            ),
            "enter_shadow_path": QuestStage(
                id="enter_shadow_path",
                description="Find and enter the hidden Shadow Path.",
                hidden_description="The Shadow Path is a secret route that leads to the Whispering Caverns.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.AREA_VISITED,
                        target="shadow_path"
                    )
                ],
                next_stages=["find_whisper_dagger"],
                world_changes=[
                    {"type": "unlock_area", "area": "shadow_path"}
                ],
                hint_dialogue={
                    "shadow_scout": "With the cloak, you can now see the hidden path. Look for the shadow that doesn't move with the sun."
                }
            ),
            "find_whisper_dagger": QuestStage(
                id="find_whisper_dagger",
                description="Find the Whisper Dagger in the Whispering Caverns.",
                hidden_description="The Whisper Dagger allows for silent eliminations and can cut through shadow barriers.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ITEM_ACQUIRED,
                        target="whisper_dagger"
                    )
                ],
                next_stages=["enter_whispering_caverns"],
                hint_dialogue={
                    "cave_whisper": "The dagger lies deep within, where the whispers are loudest. Listen carefully, and you will find your way."
                }
            ),
            "enter_whispering_caverns": QuestStage(
                id="enter_whispering_caverns",
                description="Navigate deeper into the Whispering Caverns.",
                hidden_description="The deeper caverns contain the entrance to the Void Sanctum.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.AREA_VISITED,
                        target="deep_caverns"
                    )
                ],
                next_stages=["find_shadow_key"],
                world_changes=[
                    {"type": "unlock_area", "area": "deep_caverns"}
                ],
                hint_dialogue={
                    "cave_whisper": "The path forward is hidden behind illusions. Use the dagger to cut through the veil of deception."
                }
            ),
            "find_shadow_key": QuestStage(
                id="find_shadow_key",
                description="Find the Shadow Key hidden in the Deep Caverns.",
                hidden_description="The Shadow Key is needed to enter the Void Sanctum.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ITEM_ACQUIRED,
                        target="shadow_key"
                    )
                ],
                next_stages=["enter_void_sanctum"],
                hint_dialogue={
                    "cave_whisper": "The key is hidden where light has never touched. Only in perfect darkness will it reveal itself."
                }
            ),
            "enter_void_sanctum": QuestStage(
                id="enter_void_sanctum",
                description="Use the Shadow Key to enter the Void Sanctum.",
                hidden_description="The Void Sanctum is where the Void Assassin awaits.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.AREA_VISITED,
                        target="void_sanctum"
                    )
                ],
                next_stages=["defeat_void_assassin"],
                world_changes=[
                    {"type": "unlock_area", "area": "void_sanctum"}
                ],
                hint_dialogue={
                    "cave_whisper": "The sanctum door will only open to one who holds the key and walks in shadow. Approach unseen."
                }
            ),
            "defeat_void_assassin": QuestStage(
                id="defeat_void_assassin",
                description="Defeat or outsmart the Void Assassin in the Void Sanctum.",
                hidden_description="The Void Assassin possesses the void essence needed to enter the Shadow Domain undetected.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ENEMY_DEFEATED,
                        target="void_assassin"
                    ),
                    QuestTrigger(
                        type=QuestTriggerType.ITEM_ACQUIRED,
                        target="void_essence"
                    )
                ],
                next_stages=["complete_stealth_path"],
                rewards=["void_essence", "assassin_mask"],
                hint_dialogue={
                    "cave_whisper": "The Assassin is a master of shadow, but even masters have blind spots. Watch, wait, and strike when the moment is perfect."
                }
            ),
            "complete_stealth_path": QuestStage(
                id="complete_stealth_path",
                description="Use the void essence to enter the Shadow Domain undetected.",
                hidden_description="The Stealth Path allows you to infiltrate the Shadow Domain and strike the Second Centaur from the shadows.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.AREA_VISITED,
                        target="shadow_domain"
                    )
                ],
                next_stages=[],  # End of quest
                world_changes=[
                    {"type": "unlock_area", "area": "shadow_domain"}
                ],
                hint_dialogue={
                    "cave_whisper": "You have mastered the path of shadow. Now, infiltrate the domain of the Second Centaur and strike when he least expects it."
                }
            )
        },
        discovery_triggers=[
            QuestTrigger(
                type=QuestTriggerType.AREA_VISITED,
                target="awakening_woods"
            )
        ],
        related_quests=["hermits_wisdom", "warriors_honor"],
        required_items=["shadow_cloak", "whisper_dagger", "shadow_key", "void_essence"],
        affected_npcs=["shadow_scout", "cave_whisper"],
        lore_entries=["shadow_arts", "void_sanctum_history", "first_assassin"]
    )

# Stealth path-specific abilities
STEALTH_ABILITIES = {
    "shadow_step": {
        "name": "Shadow Step",
        "description": "Step into the shadows and move a short distance without being seen.",
        "stamina_cost": 15,
        "cooldown": 4,
        "range": 3,  # Tiles
        "requirements": {
            "item": "shadow_cloak",
            "min_level": 2
        }
    },
    "silent_strike": {
        "name": "Silent Strike",
        "description": "A deadly attack that makes no sound and deals critical damage if the target is unaware.",
        "stamina_cost": 25,
        "cooldown": 3,
        "damage_multiplier": 3.0,  # If target is unaware
        "requirements": {
            "item": "whisper_dagger",
            "min_level": 3
        }
    },
    "shadow_veil": {
        "name": "Shadow Veil",
        "description": "Create a veil of shadows that obscures vision and muffles sound in an area.",
        "stamina_cost": 30,
        "cooldown": 6,
        "duration": 4,  # Turns
        "radius": 2,  # Tiles
        "requirements": {
            "path": PathType.STEALTH,
            "min_level": 4
        }
    },
    "void_whisper": {
        "name": "Void Whisper",
        "description": "Create a sound at a distance to distract enemies.",
        "stamina_cost": 10,
        "cooldown": 2,
        "range": 5,  # Tiles
        "duration": 2,  # Turns
        "requirements": {
            "path": PathType.STEALTH,
            "min_level": 1
        }
    }
}

# Stealth detection system
@dataclass
class StealthState:
    """Tracks a player's stealth state."""
    is_hidden: bool = False
    detection_level: float = 0.0  # 0.0 to 1.0, where 1.0 is fully detected
    last_noise_level: float = 0.0  # 0.0 to 1.0, where 1.0 is very loud
    in_shadow: bool = False
    cooldowns: Dict[str, int] = field(default_factory=dict)
    
    def update_detection(self, light_level: float, movement_speed: float, 
                        carrying_weight: float, in_combat: bool) -> None:
        """
        Update detection level based on environmental and player factors.
        
        Args:
            light_level: Current light level (0.0 to 1.0)
            movement_speed: How fast the player is moving (0.0 to 1.0)
            carrying_weight: How much the player is carrying (0.0 to 1.0)
            in_combat: Whether the player is in combat
        """
        # Base detection change
        detection_change = 0.0
        
        # Light affects detection
        if light_level > 0.7:
            detection_change += 0.1  # Bright light increases detection
        elif light_level < 0.3:
            detection_change -= 0.1  # Darkness decreases detection
            self.in_shadow = True
        else:
            self.in_shadow = False
        
        # Movement affects detection
        detection_change += movement_speed * 0.2
        
        # Weight affects detection
        detection_change += carrying_weight * 0.1
        
        # Combat drastically increases detection
        if in_combat:
            detection_change += 0.3
        
        # Apply change with limits
        self.detection_level = max(0.0, min(1.0, self.detection_level + detection_change))
        
        # Update hidden state
        self.is_hidden = self.detection_level < 0.5
    
    def make_noise(self, noise_level: float) -> None:
        """
        Record that the player made noise.
        
        Args:
            noise_level: Level of noise made (0.0 to 1.0)
        """
        self.last_noise_level = noise_level
        
        # Noise increases detection
        self.detection_level = max(0.0, min(1.0, self.detection_level + (noise_level * 0.3)))
        
        # Update hidden state
        self.is_hidden = self.detection_level < 0.5
    
    def apply_stealth_item_effects(self, items: List[str]) -> None:
        """
        Apply effects from stealth items.
        
        Args:
            items: List of item IDs the player has
        """
        if "shadow_cloak" in items and self.in_shadow:
            # Shadow cloak reduces detection by 75% in shadows
            self.detection_level *= 0.25
        
        # Update hidden state
        self.is_hidden = self.detection_level < 0.5
    
    def update_cooldowns(self) -> None:
        """Update ability cooldowns."""
        for ability, turns in list(self.cooldowns.items()):
            if turns <= 1:
                del self.cooldowns[ability]
            else:
                self.cooldowns[ability] = turns - 1

# Stealth path progression system
@dataclass
class StealthProgression:
    """Tracks a player's progression along the stealth path."""
    level: int = 1
    experience: int = 0
    silent_kills: int = 0
    abilities_unlocked: List[str] = field(default_factory=list)
    detection_reduction: float = 0.0
    
    def gain_experience(self, amount: int) -> Tuple[int, List[str]]:
        """
        Add experience and return level ups and newly unlocked abilities.
        
        Args:
            amount: Amount of experience to add
            
        Returns:
            Tuple of (levels gained, newly unlocked abilities)
        """
        self.experience += amount
        
        # Calculate level ups
        old_level = self.level
        self.level = 1 + (self.experience // 100)  # Simple leveling formula
        levels_gained = self.level - old_level
        
        # Update stats based on new level
        self.detection_reduction = self.level * 0.05  # 5% per level
        
        # Check for newly unlocked abilities
        new_abilities = []
        for ability_id, ability_data in STEALTH_ABILITIES.items():
            min_level = ability_data.get("requirements", {}).get("min_level", 1)
            if min_level <= self.level and ability_id not in self.abilities_unlocked:
                self.abilities_unlocked.append(ability_id)
                new_abilities.append(ability_id)
        
        return levels_gained, new_abilities
    
    def record_silent_kill(self) -> None:
        """Record a silent kill and update stats if needed."""
        self.silent_kills += 1
        
        # Every 3 silent kills improves stealth
        if self.silent_kills % 3 == 0:
            self.detection_reduction += 0.02  # Additional 2% reduction

# Helper functions for stealth path gameplay
def calculate_stealth_damage(base_damage: int, player_level: int, weapon_damage: int,
                            is_silent_strike: bool = False,
                            target_is_unaware: bool = False) -> int:
    """
    Calculate damage for a stealth attack.
    
    Args:
        base_damage: Base damage value
        player_level: Current stealth level
        weapon_damage: Weapon damage value
        is_silent_strike: Whether using the Silent Strike ability
        target_is_unaware: Whether the target is unaware of the player
        
    Returns:
        Final damage value
    """
    damage = base_damage + weapon_damage + (player_level * 1.5)
    
    if is_silent_strike and target_is_unaware:
        damage *= 3.0
    elif target_is_unaware:
        damage *= 2.0
    elif is_silent_strike:
        damage *= 1.5
    
    return int(damage)

def can_use_stealth_ability(ability_id: str, player_level: int,
                           player_items: List[str],
                           player_stamina: int,
                           stealth_state: StealthState) -> Tuple[bool, str]:
    """
    Check if a player can use a stealth ability.
    
    Args:
        ability_id: ID of the ability to check
        player_level: Current stealth level
        player_items: List of item IDs the player has
        player_stamina: Current stamina value
        stealth_state: Current stealth state
        
    Returns:
        Tuple of (can use ability, reason if cannot)
    """
    if ability_id not in STEALTH_ABILITIES:
        return False, f"Unknown ability: {ability_id}"
    
    ability = STEALTH_ABILITIES[ability_id]
    
    # Check cooldown
    if ability_id in stealth_state.cooldowns:
        return False, f"Ability on cooldown for {stealth_state.cooldowns[ability_id]} more turns."
    
    # Check stamina cost
    if player_stamina < ability["stamina_cost"]:
        return False, f"Not enough stamina. Requires {ability['stamina_cost']} stamina."
    
    # Check level requirement
    min_level = ability.get("requirements", {}).get("min_level", 1)
    if player_level < min_level:
        return False, f"Requires stealth level {min_level}."
    
    # Check item requirement
    required_item = ability.get("requirements", {}).get("item")
    if required_item and required_item not in player_items:
        return False, f"Requires item: {required_item}."
    
    return True, "" 