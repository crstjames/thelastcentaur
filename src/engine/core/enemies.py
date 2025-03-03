"""
Enemy definitions for The Last Centaur.

This module defines all enemies in the game, including their stats,
behaviors, and special abilities.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class EnemyType(str, Enum):
    """Types of enemies in the game."""
    BEAST = "beast"
    SPIRIT = "spirit"
    CONSTRUCT = "construct"
    CORRUPTED = "corrupted"
    SHADOW = "shadow"
    BOSS = "boss"

class CombatStyle(str, Enum):
    """Different combat styles enemies can use."""
    AGGRESSIVE = "aggressive"  # Direct attacks
    DEFENSIVE = "defensive"   # Counter-attacks
    TACTICAL = "tactical"    # Uses environment
    MAGICAL = "magical"      # Spell-based
    STEALTH = "stealth"     # Ambush attacks

@dataclass
class SpecialAbility:
    """Represents a special ability an enemy can use."""
    name: str
    description: str
    damage: int
    cooldown: int
    requirements: List[str]  # Conditions needed to use ability

@dataclass
class Enemy:
    """Detailed enemy definition."""
    id: str
    name: str
    type: EnemyType
    description: str
    combat_style: CombatStyle
    health: int
    damage: int
    abilities: List[SpecialAbility]
    drops: List[str]
    requirements: List[str]
    weakness: List[str]
    behavior_notes: str

# Special Abilities
ABILITIES = {
    "shadow_strike": SpecialAbility(
        name="Shadow Strike",
        description="Emerges from shadows for a powerful surprise attack",
        damage=40,
        cooldown=3,
        requirements=["darkness"]
    ),
    "crystal_burst": SpecialAbility(
        name="Crystal Burst",
        description="Explodes into damaging crystal shards",
        damage=30,
        cooldown=4,
        requirements=[]
    ),
    "spirit_drain": SpecialAbility(
        name="Spirit Drain",
        description="Drains energy, healing itself",
        damage=20,
        cooldown=5,
        requirements=["damaged"]
    ),
    "war_cry": SpecialAbility(
        name="War Cry",
        description="Empowers nearby allies and intimidates foes",
        damage=0,
        cooldown=6,
        requirements=["allies_present"]
    )
}

# Enemy Definitions
ENEMIES = {
    # Original Enemies (Enhanced)
    "wolf_pack": Enemy(
        id="wolf_pack",
        name="Twilight Wolf Pack",
        type=EnemyType.BEAST,
        description="A pack of wolves touched by shadow magic, hunting in perfect coordination.",
        combat_style=CombatStyle.TACTICAL,
        health=60,
        damage=15,
        abilities=[ABILITIES["shadow_strike"]],
        drops=["wolf_fang", "shadow_touched_pelt"],
        requirements=[],
        weakness=["fire", "light_magic"],
        behavior_notes="Coordinates attacks, flanking and surrounding their prey."
    ),
    
    # New Minor Enemies
    "shadow_hound": Enemy(
        id="shadow_hound",
        name="Shadow Hound",
        type=EnemyType.SHADOW,
        description="A creature of pure shadow, barely visible until it strikes.",
        combat_style=CombatStyle.STEALTH,
        health=45,
        damage=25,
        abilities=[ABILITIES["shadow_strike"]],
        drops=["shadow_essence", "void_fang"],
        requirements=[],
        weakness=["light_magic", "crystal_focus"],
        behavior_notes="Invisible in shadows, revealed by light sources."
    ),
    
    "crystal_golem": Enemy(
        id="crystal_golem",
        name="Crystal Golem",
        type=EnemyType.CONSTRUCT,
        description="A massive construct of living crystal, pulsing with stored magical energy.",
        combat_style=CombatStyle.DEFENSIVE,
        health=120,
        damage=30,
        abilities=[ABILITIES["crystal_burst"]],
        drops=["perfect_crystal", "golem_core"],
        requirements=["crystal_focus"],
        weakness=["sonic_attacks", "earth_magic"],
        behavior_notes="Reflects magical attacks. Must be shattered to defeat."
    ),
    
    "spectral_sentinel": Enemy(
        id="spectral_sentinel",
        name="Spectral Sentinel",
        type=EnemyType.SPIRIT,
        description="The vigilant spirit of an ancient guard, still patrolling its post.",
        combat_style=CombatStyle.TACTICAL,
        health=80,
        damage=35,
        abilities=[ABILITIES["war_cry"]],
        drops=["spectral_essence", "ancient_weapon"],
        requirements=["spirit_sight"],
        weakness=["holy_magic", "ancient_sword"],
        behavior_notes="Calls reinforcements when threatened. Can phase through walls."
    ),
    
    "corrupted_centaur_spirit": Enemy(
        id="corrupted_centaur_spirit",
        name="Corrupted Centaur Spirit",
        type=EnemyType.CORRUPTED,
        description="The twisted remnant of a fallen centaur warrior, consumed by darkness.",
        combat_style=CombatStyle.AGGRESSIVE,
        health=90,
        damage=40,
        abilities=[ABILITIES["spirit_drain"]],
        drops=["corrupted_essence", "warrior_memory"],
        requirements=["spirit_sight"],
        weakness=["purifying_magic", "war_horn"],
        behavior_notes="Uses corrupted versions of centaur battle techniques."
    ),
    
    "twilight_wisp": Enemy(
        id="twilight_wisp",
        name="Twilight Wisp",
        type=EnemyType.SPIRIT,
        description="A mischievous spirit that leads travelers astray.",
        combat_style=CombatStyle.MAGICAL,
        health=30,
        damage=15,
        abilities=[],
        drops=["wisp_essence", "twilight_shard"],
        requirements=[],
        weakness=["crystal_focus", "true_sight"],
        behavior_notes="Creates illusions and false paths. Cannot be harmed by physical attacks."
    ),
    
    "mana_wraith": Enemy(
        id="mana_wraith",
        name="Mana Wraith",
        type=EnemyType.SPIRIT,
        description="A spirit that feeds on magical energy, drawn to sources of power.",
        combat_style=CombatStyle.MAGICAL,
        health=70,
        damage=25,
        abilities=[ABILITIES["spirit_drain"]],
        drops=["wraith_essence", "crystallized_mana"],
        requirements=["magic_resistance"],
        weakness=["physical_attacks", "ancient_sword"],
        behavior_notes="Drains magical items and abilities. Stronger near sources of magic."
    ),
    
    # New Elite Enemies
    "shadow_knight": Enemy(
        id="shadow_knight",
        name="Shadow Knight",
        type=EnemyType.SHADOW,
        description="An elite warrior in service to the second centaur, wielding both blade and shadow.",
        combat_style=CombatStyle.TACTICAL,
        health=150,
        damage=45,
        abilities=[ABILITIES["shadow_strike"], ABILITIES["war_cry"]],
        drops=["shadow_steel", "void_essence"],
        requirements=["ancient_sword", "stealth_cloak"],
        weakness=["light_magic", "crystal_focus"],
        behavior_notes="Combines martial prowess with shadow magic. Can command lesser shadows."
    ),
    
    "void_walker": Enemy(
        id="void_walker",
        name="Void Walker",
        type=EnemyType.SHADOW,
        description="A being of pure void, barely held together by the second centaur's will.",
        combat_style=CombatStyle.MAGICAL,
        health=120,
        damage=50,
        abilities=[ABILITIES["shadow_strike"], ABILITIES["spirit_drain"]],
        drops=["void_crystal", "null_essence"],
        requirements=["crystal_focus", "phantom_dagger"],
        weakness=["light_magic", "holy_magic"],
        behavior_notes="Can create areas of absolute darkness. Immune to physical damage."
    ),
    
    # Add Phantom Assassin definition
    "phantom_assassin": Enemy(
        id="phantom_assassin",
        name="Phantom Assassin",
        type=EnemyType.SHADOW,
        description="A deadly spirit that guards the secret paths. Masters of shadow and stealth, they strike without warning.",
        combat_style=CombatStyle.STEALTH,
        health=80,
        damage=50,
        abilities=[ABILITIES["shadow_strike"]],
        drops=["shadow_essence", "phantom_dagger"],
        requirements=["stealth_cloak"],
        weakness=["light_magic", "mystic_abilities"],
        behavior_notes="Uses stealth tactics, disappearing and reappearing to attack from unexpected angles."
    ),
    
    # Add Shadow Stalker definition
    "shadow_stalker": Enemy(
        id="shadow_stalker",
        name="Shadow Stalker",
        type=EnemyType.SHADOW,
        description="A creature of pure darkness that hunts at night. Nearly invisible in shadows.",
        combat_style=CombatStyle.STEALTH,
        health=80,
        damage=25,
        abilities=[ABILITIES["shadow_strike"]],
        drops=["shadow_essence", "stealth_cloak"],
        requirements=[],
        weakness=["light_magic", "fire"],
        behavior_notes="Prefers to ambush from darkness. More powerful at night or in dark areas."
    )
} 