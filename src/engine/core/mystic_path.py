"""
Mystic Path implementation for The Last Centaur.

This module defines the mystic path quest line and related game mechanics.
The mystic path focuses on magical abilities, wisdom, and understanding the deeper nature of reality.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from .models import Item, Enemy, PathType, StoryArea
from .quest_system import Quest, QuestStage, QuestTrigger, QuestTriggerType, QuestStatus

# Mystic path-specific items
CRYSTAL_FOCUS = Item(
    id="crystal_focus",
    name="Crystal Focus",
    description="A crystal that channels magical energies and reveals hidden truths.",
    type="focus",
    properties={
        "magic_power": 15,
        "special_ability": "truth_sight",
        "path_type": PathType.MYSTIC,
        "effect": "reveals hidden paths and secrets"
    }
)

ANCIENT_SCROLL = Item(
    id="ancient_scroll",
    name="Ancient Scroll",
    description="A scroll containing ancient spells and wisdom from a forgotten age.",
    type="scroll",
    properties={
        "spell_1": "arcane_bolt",
        "spell_2": "healing_light",
        "spell_3": "mind_shield",
        "special_ability": "spell_mastery",
        "path_type": PathType.MYSTIC,
        "effect": "learn spells faster and with less mana cost"
    }
)

GUARDIAN_ESSENCE = Item(
    id="guardian_essence",
    name="Guardian Essence",
    description="The crystallized essence of a defeated Crystal Guardian, pulsing with magical energy.",
    type="material",
    properties={
        "magic_power": 20,
        "special_ability": "mana_surge",
        "path_type": PathType.MYSTIC,
        "effect": "temporarily doubles mana regeneration"
    }
)

# Mystic path-specific enemies
CRYSTAL_GUARDIAN = Enemy(
    name="Crystal Guardian",
    description="A sentient crystalline entity that guards the deepest secrets of the Crystal Caves. Its body shimmers with arcane energy.",
    health=180,
    damage=15,
    drops=["guardian_essence", "crystal_fragments"]
)

CORRUPTED_SAGE = Enemy(
    name="Corrupted Sage",
    description="Once a wise mystic, now twisted by the Second Centaur's influence. Wields powerful but unstable magic.",
    health=120,
    damage=25,
    drops=["sage_tome", "corrupted_focus"]
)

# Mystic path quest definition
def create_mystic_quest() -> Quest:
    """Create the main mystic path quest."""
    return Quest(
        id="hermits_wisdom",
        name="The Hermit's Wisdom",
        description="Seek the ancient knowledge of the Hermit Druid.",
        hidden_description="The Hermit Druid holds secrets about the true nature of the Second Centaur.",
        initial_stage="find_hermit",
        stages={
            "find_hermit": QuestStage(
                id="find_hermit",
                description="Find the Hermit Druid in the western woods.",
                hidden_description="The Hermit Druid is hiding from the Second Centaur's agents.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.NPC_DIALOGUE,
                        target="hermit_druid"
                    )
                ],
                next_stages=["retrieve_scroll"],
                hint_dialogue={
                    "fallen_warrior": "I've heard whispers of an old druid who lives to the west. They say he knows things about our past that most have forgotten."
                }
            ),
            "retrieve_scroll": QuestStage(
                id="retrieve_scroll",
                description="The Hermit Druid has asked you to retrieve an ancient scroll from his meditation spot.",
                hidden_description="The scroll contains a ritual that can weaken the Second Centaur.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ITEM_ACQUIRED,
                        target="ancient_scroll"
                    )
                ],
                next_stages=["return_scroll", "study_scroll"],
                hint_dialogue={
                    "hermit_druid": "My meditation spot lies deeper in the grove. The scroll should still be there, unless... No, I'm sure it's safe."
                }
            ),
            "study_scroll": QuestStage(
                id="study_scroll",
                description="Study the ancient scroll to learn its secrets.",
                hidden_description="The scroll reveals the location of the Crystal Focus.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ITEM_USED,
                        target="ancient_scroll"
                    )
                ],
                next_stages=["find_crystal"],
                world_changes=[
                    {"type": "reveal_item", "item_id": "crystal_focus", "location": (3, 4)}
                ]
            ),
            "return_scroll": QuestStage(
                id="return_scroll",
                description="Return the scroll to the Hermit Druid.",
                hidden_description="The Hermit will reveal more about your quest if you return the scroll.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ITEM_GIVEN,
                        target="ancient_scroll",
                        condition="recipient=hermit_druid"
                    )
                ],
                next_stages=["find_crystal"],
                rewards=["hermit_blessing"],
                hint_dialogue={
                    "hermit_druid": "You've found it! Now, let me show you what it means..."
                }
            ),
            "find_crystal": QuestStage(
                id="find_crystal",
                description="Find the Crystal Focus in the Mystic Mountains.",
                hidden_description="The Crystal Focus is needed to see through the Second Centaur's illusions.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ITEM_ACQUIRED,
                        target="crystal_focus"
                    )
                ],
                next_stages=["enter_crystal_caves"],
                hint_dialogue={
                    "hermit_druid": "The Crystal Focus lies in the mountains to the north. It will reveal paths hidden to the naked eye."
                }
            ),
            "enter_crystal_caves": QuestStage(
                id="enter_crystal_caves",
                description="Use the Crystal Focus to enter the Crystal Caves.",
                hidden_description="The Crystal Caves contain the essence needed to challenge the Second Centaur.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.AREA_VISITED,
                        target="crystal_caves"
                    )
                ],
                next_stages=["defeat_guardian"],
                world_changes=[
                    {"type": "unlock_area", "area": "crystal_caves"}
                ],
                hint_dialogue={
                    "hermit_druid": "The caves are hidden from ordinary sight. Use the Crystal Focus to reveal the entrance."
                }
            ),
            "defeat_guardian": QuestStage(
                id="defeat_guardian",
                description="Defeat the Crystal Guardian to obtain its essence.",
                hidden_description="The Guardian's essence contains the power of the original centaur lords.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ENEMY_DEFEATED,
                        target="crystal_guardian"
                    )
                ],
                next_stages=["complete_mystic_path"],
                rewards=["guardian_essence"],
                hint_dialogue={
                    "hermit_druid": "The Guardian will not yield easily, but its essence is crucial for your journey."
                }
            ),
            "complete_mystic_path": QuestStage(
                id="complete_mystic_path",
                description="Use the knowledge and power you've gathered to confront the Second Centaur.",
                hidden_description="The Mystic Path allows you to counter the Second Centaur's magical abilities.",
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
                    "hermit_druid": "You now possess the knowledge and power to face the Second Centaur. Remember, true strength comes from understanding, not just power."
                }
            )
        },
        discovery_triggers=[
            QuestTrigger(
                type=QuestTriggerType.AREA_VISITED,
                target="awakening_woods"
            )
        ],
        related_quests=["warriors_honor", "shadows_embrace"],
        required_items=["ancient_scroll", "crystal_focus", "guardian_essence"],
        affected_npcs=["hermit_druid", "fallen_warrior"],
        lore_entries=["centaur_wars", "crystal_magic", "first_centaur"]
    )

# Mystic path-specific abilities
MYSTIC_ABILITIES = {
    "truth_sight": {
        "name": "Truth Sight",
        "description": "See through illusions and reveal hidden paths and objects.",
        "mana_cost": 20,
        "cooldown": 5,
        "duration": 3,  # Turns
        "requirements": {
            "item": "crystal_focus",
            "min_level": 2
        }
    },
    "arcane_bolt": {
        "name": "Arcane Bolt",
        "description": "Fire a bolt of pure magical energy that bypasses physical defenses.",
        "mana_cost": 15,
        "cooldown": 2,
        "damage": 25,
        "requirements": {
            "path": PathType.MYSTIC,
            "min_level": 1
        }
    },
    "mind_shield": {
        "name": "Mind Shield",
        "description": "Create a barrier that protects against mental attacks and corruption.",
        "mana_cost": 30,
        "cooldown": 6,
        "duration": 4,  # Turns
        "requirements": {
            "path": PathType.MYSTIC,
            "min_level": 3
        }
    },
    "essence_drain": {
        "name": "Essence Drain",
        "description": "Drain magical essence from an enemy to restore your own mana.",
        "mana_cost": 10,
        "cooldown": 4,
        "drain_amount": 20,
        "requirements": {
            "path": PathType.MYSTIC,
            "min_level": 4
        }
    },
    "reality_shift": {
        "name": "Reality Shift",
        "description": "Briefly alter reality to teleport a short distance.",
        "mana_cost": 35,
        "cooldown": 7,
        "range": 4,  # Tiles
        "requirements": {
            "item": "guardian_essence",
            "min_level": 5
        }
    }
}

# Mystic path progression system
@dataclass
class MysticProgression:
    """Tracks a player's progression along the mystic path."""
    level: int = 1
    experience: int = 0
    spells_learned: List[str] = field(default_factory=list)
    abilities_unlocked: List[str] = field(default_factory=list)
    max_mana: int = 100
    mana_regen: float = 5.0
    
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
        self.max_mana = 100 + (self.level * 20)
        self.mana_regen = 5.0 + (self.level * 0.5)
        
        # Check for newly unlocked abilities
        new_abilities = []
        for ability_id, ability_data in MYSTIC_ABILITIES.items():
            min_level = ability_data.get("requirements", {}).get("min_level", 1)
            if min_level <= self.level and ability_id not in self.abilities_unlocked:
                self.abilities_unlocked.append(ability_id)
                new_abilities.append(ability_id)
        
        return levels_gained, new_abilities
    
    def learn_spell(self, spell_id: str) -> bool:
        """
        Learn a new spell.
        
        Args:
            spell_id: ID of the spell to learn
            
        Returns:
            Whether the spell was successfully learned
        """
        if spell_id in self.spells_learned:
            return False
        
        self.spells_learned.append(spell_id)
        return True

# Meditation system for mystic path
@dataclass
class MeditationState:
    """Tracks a player's meditation state."""
    is_meditating: bool = False
    meditation_level: int = 0  # 0 to 5, where 5 is deepest meditation
    turns_meditating: int = 0
    mana_restored_per_turn: float = 0.0
    insight_chance: float = 0.0
    
    def start_meditation(self, mystic_level: int) -> None:
        """
        Begin meditation.
        
        Args:
            mystic_level: Current mystic level
        """
        self.is_meditating = True
        self.meditation_level = 0
        self.turns_meditating = 0
        self.mana_restored_per_turn = 5.0 + (mystic_level * 0.5)
        self.insight_chance = 0.05 + (mystic_level * 0.01)
    
    def continue_meditation(self) -> Tuple[float, bool]:
        """
        Continue meditating for another turn.
        
        Returns:
            Tuple of (mana restored, whether gained insight)
        """
        if not self.is_meditating:
            return 0.0, False
        
        self.turns_meditating += 1
        
        # Meditation deepens over time
        if self.turns_meditating % 3 == 0 and self.meditation_level < 5:
            self.meditation_level += 1
            self.mana_restored_per_turn += 2.0
            self.insight_chance += 0.02
        
        # Check for insight
        gained_insight = False
        import random
        if random.random() < self.insight_chance:
            gained_insight = True
        
        return self.mana_restored_per_turn, gained_insight
    
    def end_meditation(self) -> None:
        """End meditation."""
        self.is_meditating = False
        self.meditation_level = 0
        self.turns_meditating = 0
        self.mana_restored_per_turn = 0.0
        self.insight_chance = 0.0

# Helper functions for mystic path gameplay
def calculate_spell_damage(base_damage: int, player_level: int, focus_power: int,
                          target_is_corrupted: bool = False) -> int:
    """
    Calculate damage for a mystic spell.
    
    Args:
        base_damage: Base damage value
        player_level: Current mystic level
        focus_power: Power of the focus item
        target_is_corrupted: Whether the target is corrupted
        
    Returns:
        Final damage value
    """
    damage = base_damage + (player_level * 3) + (focus_power * 0.5)
    
    if target_is_corrupted:
        damage *= 1.5  # Mystic spells are more effective against corruption
    
    return int(damage)

def can_cast_spell(spell_id: str, player_level: int, player_items: List[str],
                  player_mana: int, meditation_state: MeditationState) -> Tuple[bool, str]:
    """
    Check if a player can cast a mystic spell.
    
    Args:
        spell_id: ID of the spell to check
        player_level: Current mystic level
        player_items: List of item IDs the player has
        player_mana: Current mana value
        meditation_state: Current meditation state
        
    Returns:
        Tuple of (can cast spell, reason if cannot)
    """
    if spell_id not in MYSTIC_ABILITIES:
        return False, f"Unknown spell: {spell_id}"
    
    spell = MYSTIC_ABILITIES[spell_id]
    
    # Check mana cost
    if player_mana < spell["mana_cost"]:
        return False, f"Not enough mana. Requires {spell['mana_cost']} mana."
    
    # Check level requirement
    min_level = spell.get("requirements", {}).get("min_level", 1)
    if player_level < min_level:
        return False, f"Requires mystic level {min_level}."
    
    # Check item requirement
    required_item = spell.get("requirements", {}).get("item")
    if required_item and required_item not in player_items:
        return False, f"Requires item: {required_item}."
    
    # Meditation bonus: some spells are more powerful during meditation
    if meditation_state.is_meditating and meditation_state.meditation_level >= 3:
        # This would be used in the actual spell casting logic
        pass
    
    return True, "" 