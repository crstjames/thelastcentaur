"""
Warrior Path implementation for The Last Centaur.

This module defines the warrior path quest line and related game mechanics.
The warrior path focuses on combat prowess, honor, and direct confrontation.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .models import Item, Enemy, PathType, StoryArea
from .quest_system import Quest, QuestStage, QuestTrigger, QuestTriggerType, QuestStatus

# Warrior path-specific items
WARRIORS_SWORD = Item(
    id="warriors_sword",
    name="Warrior's Sword",
    description="A well-balanced blade that grows stronger with each honorable victory.",
    type="weapon",
    properties={
        "damage": 10,
        "durability": 100,
        "special_ability": "honor_strike",
        "path_type": PathType.WARRIOR
    }
)

CHAMPIONS_SHIELD = Item(
    id="champions_shield",
    name="Champion's Shield",
    description="A shield that has protected many warriors before you.",
    type="shield",
    properties={
        "defense": 8,
        "durability": 120,
        "special_ability": "block_counter",
        "path_type": PathType.WARRIOR
    }
)

BATTLE_MEDALLION = Item(
    id="battle_medallion",
    name="Battle Medallion",
    description="A medallion that marks you as a warrior of honor.",
    type="accessory",
    properties={
        "honor_bonus": 5,
        "path_type": PathType.WARRIOR
    }
)

# Warrior path-specific enemies
FALLEN_CHAMPION = Enemy(
    name="Fallen Champion",
    description="Once a noble warrior, now corrupted by the Second Centaur's influence. Still fights with skill and precision.",
    health=100,
    damage=15,
    drops=["champions_shield"]
)

CORRUPTED_WARLORD = Enemy(
    name="Corrupted Warlord",
    description="A powerful warlord who has given in to the promise of power. Wields dark magic alongside martial prowess.",
    health=200,
    damage=25,
    drops=["warlords_amulet", "dark_essence"]
)

# Warrior path quest definition
def create_warrior_quest() -> Quest:
    """Create the main warrior path quest."""
    return Quest(
        id="warriors_honor",
        name="The Warrior's Honor",
        description="Prove your worth as a warrior and reclaim the ancient weapons of the First Centaur.",
        hidden_description="The path of the warrior will allow you to directly confront the Second Centaur in combat.",
        initial_stage="meet_fallen_warrior",
        stages={
            "meet_fallen_warrior": QuestStage(
                id="meet_fallen_warrior",
                description="Find the Fallen Warrior in the Awakening Woods.",
                hidden_description="The Fallen Warrior knows the location of the Warrior's Sword.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.NPC_DIALOGUE,
                        target="fallen_warrior"
                    )
                ],
                next_stages=["find_warriors_sword"],
                hint_dialogue={
                    "fallen_warrior": "I was once like you, seeking to challenge the Second Centaur. The path of the warrior is direct but perilous. You'll need the ancient weapons."
                }
            ),
            "find_warriors_sword": QuestStage(
                id="find_warriors_sword",
                description="Find the Warrior's Sword in the ancient battlefield.",
                hidden_description="The Warrior's Sword is one of three legendary weapons forged to defeat the Second Centaur.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ITEM_ACQUIRED,
                        target="warriors_sword"
                    )
                ],
                next_stages=["defeat_fallen_champion"],
                hint_dialogue={
                    "fallen_warrior": "The sword lies in the ancient battlefield to the east. It awaits a worthy wielder."
                }
            ),
            "defeat_fallen_champion": QuestStage(
                id="defeat_fallen_champion",
                description="Defeat the Fallen Champion to prove your worth.",
                hidden_description="The Fallen Champion guards the path to the Battle Plains and tests all who seek to follow the warrior's path.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ENEMY_DEFEATED,
                        target="fallen_champion"
                    )
                ],
                next_stages=["enter_battle_plains"],
                rewards=["champions_shield"],
                hint_dialogue={
                    "fallen_warrior": "The Champion guards the path forward. Defeat him with honor, and his shield shall be yours."
                }
            ),
            "enter_battle_plains": QuestStage(
                id="enter_battle_plains",
                description="Enter the Battle Plains.",
                hidden_description="The Battle Plains are where the First Centaur fought their greatest battles.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.AREA_VISITED,
                        target="battle_plains"
                    )
                ],
                next_stages=["find_battle_medallion"],
                world_changes=[
                    {"type": "unlock_area", "area": "battle_plains"}
                ],
                hint_dialogue={
                    "fallen_warrior": "The Battle Plains lie beyond the Champion. There, you will find the next trial."
                }
            ),
            "find_battle_medallion": QuestStage(
                id="find_battle_medallion",
                description="Find the Battle Medallion hidden in the Battle Plains.",
                hidden_description="The Battle Medallion is needed to enter the War Fortress.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ITEM_ACQUIRED,
                        target="battle_medallion"
                    )
                ],
                next_stages=["enter_war_fortress"],
                hint_dialogue={
                    "battle_spirit": "The medallion lies at the heart of the plains, where the blood of heroes has soaked the earth."
                }
            ),
            "enter_war_fortress": QuestStage(
                id="enter_war_fortress",
                description="Use the Battle Medallion to enter the War Fortress.",
                hidden_description="The War Fortress is where the Corrupted Warlord awaits.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.AREA_VISITED,
                        target="war_fortress"
                    )
                ],
                next_stages=["defeat_corrupted_warlord"],
                world_changes=[
                    {"type": "unlock_area", "area": "war_fortress"}
                ],
                hint_dialogue={
                    "battle_spirit": "The fortress gates will open to one who bears the medallion. Inside awaits your greatest test."
                }
            ),
            "defeat_corrupted_warlord": QuestStage(
                id="defeat_corrupted_warlord",
                description="Defeat the Corrupted Warlord in the War Fortress.",
                hidden_description="The Corrupted Warlord possesses the dark essence needed to enter the Shadow Domain.",
                triggers=[
                    QuestTrigger(
                        type=QuestTriggerType.ENEMY_DEFEATED,
                        target="corrupted_warlord"
                    )
                ],
                next_stages=["complete_warrior_path"],
                rewards=["warlords_amulet", "dark_essence"],
                hint_dialogue={
                    "battle_spirit": "The Warlord was once the greatest of us. Now, he serves the darkness. Defeat him, and take what you need to face the Second Centaur."
                }
            ),
            "complete_warrior_path": QuestStage(
                id="complete_warrior_path",
                description="Use the dark essence to enter the Shadow Domain and confront the Second Centaur.",
                hidden_description="The Warrior Path allows you to challenge the Second Centaur directly in combat.",
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
                    "battle_spirit": "You have proven yourself worthy of the warrior's path. Now, face the Second Centaur with honor and courage."
                }
            )
        },
        discovery_triggers=[
            QuestTrigger(
                type=QuestTriggerType.AREA_VISITED,
                target="awakening_woods"
            )
        ],
        related_quests=["hermits_wisdom", "shadows_embrace"],
        required_items=["warriors_sword", "champions_shield", "battle_medallion", "dark_essence"],
        affected_npcs=["fallen_warrior", "battle_spirit"],
        lore_entries=["first_warrior", "battle_plains_history", "war_fortress_fall"]
    )

# Warrior path-specific abilities
WARRIOR_ABILITIES = {
    "honor_strike": {
        "name": "Honor Strike",
        "description": "A powerful strike that deals extra damage to corrupted enemies.",
        "stamina_cost": 20,
        "cooldown": 3,
        "damage_multiplier": 1.5,
        "requirements": {
            "item": "warriors_sword",
            "min_level": 3
        }
    },
    "stalwart_defense": {
        "name": "Stalwart Defense",
        "description": "Raise your shield to block all incoming damage for 2 turns.",
        "stamina_cost": 30,
        "cooldown": 5,
        "duration": 2,
        "requirements": {
            "item": "champions_shield",
            "min_level": 5
        }
    },
    "battle_cry": {
        "name": "Battle Cry",
        "description": "A mighty shout that intimidates enemies, reducing their damage for 3 turns.",
        "stamina_cost": 15,
        "cooldown": 4,
        "effect": {
            "type": "debuff",
            "target": "all_enemies",
            "stat": "damage",
            "modifier": -0.3,
            "duration": 3
        },
        "requirements": {
            "path": PathType.WARRIOR,
            "min_level": 2
        }
    },
    "adrenaline_rush": {
        "name": "Adrenaline Rush",
        "description": "Channel your battle fury to increase attack speed for 3 turns.",
        "stamina_cost": 25,
        "cooldown": 6,
        "effect": {
            "type": "buff",
            "target": "self",
            "stat": "attack_speed",
            "modifier": 0.5,
            "duration": 3
        },
        "requirements": {
            "path": PathType.WARRIOR,
            "min_level": 4
        }
    }
}

# Warrior path progression system
@dataclass
class WarriorProgression:
    """Tracks a player's progression along the warrior path."""
    level: int = 1
    experience: int = 0
    honorable_kills: int = 0
    abilities_unlocked: List[str] = field(default_factory=list)
    max_health_bonus: int = 0
    max_stamina_bonus: int = 0
    
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
        self.max_health_bonus = self.level * 10
        self.max_stamina_bonus = self.level * 5
        
        # Check for newly unlocked abilities
        new_abilities = []
        for ability_id, ability_data in WARRIOR_ABILITIES.items():
            min_level = ability_data.get("requirements", {}).get("min_level", 1)
            if min_level <= self.level and ability_id not in self.abilities_unlocked:
                self.abilities_unlocked.append(ability_id)
                new_abilities.append(ability_id)
        
        return levels_gained, new_abilities
    
    def record_honorable_kill(self) -> None:
        """Record an honorable kill and update stats if needed."""
        self.honorable_kills += 1
        
        # Every 5 honorable kills provides a small permanent bonus
        if self.honorable_kills % 5 == 0:
            self.max_health_bonus += 5
            self.max_stamina_bonus += 3

# Helper functions for warrior path gameplay
def calculate_warrior_damage(base_damage: int, player_level: int, weapon_damage: int, 
                            is_honorable_strike: bool = False, 
                            target_is_corrupted: bool = False) -> int:
    """
    Calculate damage for a warrior attack.
    
    Args:
        base_damage: Base damage value
        player_level: Current warrior level
        weapon_damage: Weapon damage value
        is_honorable_strike: Whether using the Honor Strike ability
        target_is_corrupted: Whether the target is corrupted
        
    Returns:
        Final damage value
    """
    damage = base_damage + weapon_damage + (player_level * 2)
    
    if is_honorable_strike:
        damage *= 1.5
    
    if target_is_corrupted and is_honorable_strike:
        damage *= 1.2
    
    return int(damage)

def can_use_warrior_ability(ability_id: str, player_level: int, 
                           player_items: List[str], 
                           player_stamina: int) -> Tuple[bool, str]:
    """
    Check if a player can use a warrior ability.
    
    Args:
        ability_id: ID of the ability to check
        player_level: Current warrior level
        player_items: List of item IDs the player has
        player_stamina: Current stamina value
        
    Returns:
        Tuple of (can use ability, reason if cannot)
    """
    if ability_id not in WARRIOR_ABILITIES:
        return False, f"Unknown ability: {ability_id}"
    
    ability = WARRIOR_ABILITIES[ability_id]
    
    # Check stamina cost
    if player_stamina < ability["stamina_cost"]:
        return False, f"Not enough stamina. Requires {ability['stamina_cost']} stamina."
    
    # Check level requirement
    min_level = ability.get("requirements", {}).get("min_level", 1)
    if player_level < min_level:
        return False, f"Requires warrior level {min_level}."
    
    # Check item requirement
    required_item = ability.get("requirements", {}).get("item")
    if required_item and required_item not in player_items:
        return False, f"Requires item: {required_item}."
    
    return True, "" 