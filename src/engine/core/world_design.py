"""
World design for The Last Centaur.

This module defines the game world structure, including:
- Areas and their connections
- Key NPCs and their stories
- Enemies and their drops
- Items and their requirements
- Three distinct paths to victory
"""

from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass

class PathType(str, Enum):
    """The three possible paths to victory."""
    WARRIOR = "warrior"  # Direct combat path
    MYSTIC = "mystic"   # Magic and knowledge path
    STEALTH = "stealth" # Cunning and deception path

@dataclass
class NPC:
    """Represents a friendly NPC in the game."""
    id: str
    name: str
    description: str
    location: Tuple[int, int]
    dialogue: Dict[str, str]  # Keyed by player's progress state
    quest_items: List[str]
    requirements: List[str]
    path_alignment: Optional[PathType] = None

@dataclass
class KeyItem:
    """Represents a key item needed for progression."""
    id: str
    name: str
    description: str
    location: Optional[Tuple[int, int]]
    required_for: List[str]  # List of areas or enemies that require this item
    path_type: Optional[PathType]
    acquisition_requirements: List[str]

# World Structure Constants
STARTING_POSITION = (5, 0)  # Bottom center of the map
FINAL_BOSS_POSITION = (5, 9)  # Top center of the map

# Key NPCs
WORLD_NPCS = [
    NPC(
        id="hermit_druid",
        name="The Hermit Druid",
        description="An ancient druid who remembers the age of centaur wars.",
        location=(4, 1),
        dialogue={
            "start": "Ah, another proud centaur. Will you learn from our past, or repeat it?",
            "mid_game": "The shadow grows stronger with each passing day...",
            "pre_final": "Three paths lie before you. Choose wisely."
        },
        quest_items=["ancient_scroll"],
        requirements=[],
        path_alignment=PathType.MYSTIC
    ),
    NPC(
        id="fallen_warrior",
        name="The Fallen Warrior",
        description="A battle-scarred veteran of the centaur wars, now seeking redemption.",
        location=(6, 1),
        dialogue={
            "start": "Strength alone won't save you. Trust me, I learned that the hard way.",
            "mid_game": "The old weapons still sing with power, if you know where to look.",
            "pre_final": "Face him with honor, but don't let pride blind you."
        },
        quest_items=["warrior_map"],
        requirements=[],
        path_alignment=PathType.WARRIOR
    ),
    NPC(
        id="shadow_scout",
        name="The Shadow Scout",
        description="A mysterious figure who knows the secret paths.",
        location=(5, 2),
        dialogue={
            "start": "Not all victories require bloodshed, clever one.",
            "mid_game": "The shadows whisper of hidden passages...",
            "pre_final": "Sometimes the best path is the one least traveled."
        },
        quest_items=["shadow_key"],
        requirements=["stealth_cloak"],
        path_alignment=PathType.STEALTH
    )
]

# Key Items for Each Path
PATH_ITEMS = {
    PathType.WARRIOR: [
        KeyItem(
            id="ancient_sword",
            name="The Ancient Sword",
            description="A blade that remembers the first centaur wars.",
            location=(7, 3),
            required_for=["shadow_guardian"],
            path_type=PathType.WARRIOR,
            acquisition_requirements=["warrior_map"]
        ),
        KeyItem(
            id="war_horn",
            name="Horn of the Fallen",
            description="Its call can rally ancient spirits to your aid.",
            location=(8, 5),
            required_for=["spirit_gate"],
            path_type=PathType.WARRIOR,
            acquisition_requirements=["ancient_sword"]
        )
    ],
    PathType.MYSTIC: [
        KeyItem(
            id="crystal_focus",
            name="Crystal Focus",
            description="Channels magical energies of the land.",
            location=(3, 4),
            required_for=["magic_barrier"],
            path_type=PathType.MYSTIC,
            acquisition_requirements=["ancient_scroll"]
        ),
        KeyItem(
            id="druid_staff",
            name="Staff of Nature's Wrath",
            description="Holds power over the natural world.",
            location=(2, 6),
            required_for=["nature_gate"],
            path_type=PathType.MYSTIC,
            acquisition_requirements=["crystal_focus"]
        )
    ],
    PathType.STEALTH: [
        KeyItem(
            id="stealth_cloak",
            name="Cloak of Shadows",
            description="Renders the wearer nearly invisible.",
            location=(4, 3),
            required_for=["shadow_gate"],
            path_type=PathType.STEALTH,
            acquisition_requirements=["shadow_key"]
        ),
        KeyItem(
            id="phantom_dagger",
            name="Phantom's Edge",
            description="A blade that can cut through magical barriers.",
            location=(3, 7),
            required_for=["final_barrier"],
            path_type=PathType.STEALTH,
            acquisition_requirements=["stealth_cloak"]
        )
    ]
}

# Major Enemies
WORLD_ENEMIES = [
    {
        "id": "shadow_guardian",
        "name": "Shadow Guardian",
        "description": "A manifestation of the second centaur's power.",
        "health": 150,
        "damage": 40,
        "position": (5, 7),
        "drops": ["guardian_essence"],
        "requirements": ["ancient_sword", "druid_staff", "phantom_dagger"]
    },
    {
        "id": "corrupted_druid",
        "name": "Corrupted Druid",
        "description": "Once a protector of these lands, now twisted by dark magic.",
        "health": 100,
        "damage": 30,
        "position": (2, 5),
        "drops": ["nature_key"],
        "requirements": ["crystal_focus"]
    },
    {
        "id": "phantom_assassin",
        "name": "Phantom Assassin",
        "description": "A deadly spirit that guards the secret paths.",
        "health": 80,
        "damage": 50,
        "position": (7, 6),
        "drops": ["shadow_essence"],
        "requirements": ["stealth_cloak"]
    },
    {
        "id": "second_centaur",
        "name": "The Shadow Centaur",
        "description": "Your rival, wielding powers both ancient and terrible.",
        "health": 300,
        "damage": 60,
        "position": FINAL_BOSS_POSITION,
        "drops": ["crown_of_dominion"],
        "requirements": ["guardian_essence"]  # Need to defeat the guardian first
    }
]

# Area Requirements (what's needed to enter each area)
AREA_REQUIREMENTS = {
    "mystic_mountains": ["crystal_focus"],
    "shadow_domain": ["guardian_essence"],
    "crystal_caves": ["druid_staff"],
    "forgotten_grove": ["stealth_cloak"],
    "ancient_ruins": ["war_horn"],
    "enchanted_valley": ["nature_key"]
}

# Victory Conditions for Each Path
VICTORY_CONDITIONS = {
    PathType.WARRIOR: {
        "required_items": ["ancient_sword", "war_horn", "guardian_essence"],
        "required_kills": ["shadow_guardian", "second_centaur"],
        "description": "The path of direct confrontation. Gather the ancient weapons and face your rival in honorable combat."
    },
    PathType.MYSTIC: {
        "required_items": ["crystal_focus", "druid_staff", "nature_key"],
        "required_kills": ["corrupted_druid", "second_centaur"],
        "description": "The path of magical mastery. Learn the land's secrets and turn its power against your rival."
    },
    PathType.STEALTH: {
        "required_items": ["stealth_cloak", "phantom_dagger", "shadow_essence"],
        "required_kills": ["phantom_assassin", "second_centaur"],
        "description": "The path of cunning. Use stealth and deception to reach your rival when they least expect it."
    }
} 