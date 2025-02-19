"""
Detailed lore and item descriptions for The Last Centaur.

This module contains rich descriptions and background stories for items,
areas, and characters in the game world.
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class LoreEntry:
    """A piece of lore that can be discovered."""
    id: str
    title: str
    short_description: str
    full_description: str
    related_items: List[str]
    discovery_condition: str

# Detailed Item Lore
ITEM_LORE = {
    "ancient_sword": {
        "name": "The Ancient Sword - Blade of the First War",
        "short_desc": "A blade that remembers the first centaur wars.",
        "full_desc": """Forged in the time when centaurs first turned against each other, 
this blade was wielded by the legendary warrior-sage Chiron. Its edge never dulls, 
and the runes along its length pulse with memories of ancient battles. Those who listen 
closely claim to hear whispers of long-forgotten battle tactics in its presence.

The sword's pommel bears the mark of the First Herd, and its crossguard is adorned 
with intricate carvings depicting the great migration that led to the centaur wars.""",
        "usage_note": "The sword's power grows when wielded under moonlight, and its runes 
glow in the presence of other artifacts from the First War."
    },
    "crystal_focus": {
        "name": "Crystal Focus - Eye of the Ancient Druids",
        "short_desc": "Channels magical energies of the land.",
        "full_desc": """A crystalline lens created by the druid circles that once 
served as mediators between warring centaur herds. Within its faceted surface, one can 
see the ebb and flow of natural energies that permeate the land. The crystal seems to 
resonate with the earth itself, humming different tones as it passes over places of power.

The crystal's core contains a swirling essence, said to be a trapped fragment of 
the first dawn that witnessed the birth of the centaur race.""",
        "usage_note": "When held up to sunlight in places of power, the crystal reveals 
hidden paths and ancient secrets etched into the very landscape."
    },
    "stealth_cloak": {
        "name": "Cloak of Shadows - Twilight's Embrace",
        "short_desc": "Renders the wearer nearly invisible.",
        "full_desc": """Woven from the essence of twilight by the legendary Shadow Weavers, 
a secretive group of centaur mystics who believed true power lay in remaining unseen. 
The cloak seems to drink in light, creating a void in the world around its wearer. 
Those who don it speak of hearing the whispers of shadows and feeling the pull of 
hidden pathways.

Its fabric bears patterns that shift and change, never appearing the same way twice.""",
        "usage_note": "Most effective during dawn and dusk, when the boundary between 
light and shadow is at its thinnest."
    }
}

# Area Descriptions and History
AREA_LORE = {
    "awakening_woods": {
        "name": "The Awakening Woods - Cradle of Consciousness",
        "description": """These ancient woods mark where you first awoke, stripped of your 
power by the barrier. The trees here seem to whisper with memories of past conflicts, 
their branches reaching like gnarled fingers toward a sky that shifts between golden 
light and ominous shadow.

Hidden among the roots and hollows are the first hints of the three paths that lie 
before you - martial prowess, mystical knowledge, and shadow's cunning.""",
        "history": """Long ago, these woods served as neutral ground where centaur herds 
would gather for peace talks. The ancient trees absorbed the tensions and promises of 
those meetings, and some say they still hold echoes of oaths both kept and broken."""
    },
    "mystic_mountains": {
        "name": "The Mystic Mountains - Peaks of Power",
        "description": """Jagged peaks pierce the clouds, their surfaces etched with 
glowing runes that pulse with ancient power. Crystal formations dot the cliffs, each 
one singing a different note on the wind. The very air here crackles with magical 
energy, and reality seems to bend in unexpected ways.

Those who walk these paths must learn to read the mountains' moods, for their power 
can either illuminate or destroy.""",
        "history": """These peaks once served as sanctuaries for centaur mystics who 
sought to understand the deeper mysteries of their race. The crystals that grow here 
were used to record their discoveries, though many of their secrets were lost in the 
great wars."""
    },
    "shadow_domain": {
        "name": "The Shadow Domain - Throne of the Rival",
        "description": """A realm of perpetual twilight, where reality itself seems to 
waver like a mirage. The very ground shifts treacherously beneath one's hooves, and 
the air is thick with an oppressive power that seeks to crush all who would challenge 
its master's dominion.

This is where your rival has made their seat of power, transforming what was once 
a place of natural beauty into a twisted reflection of their ambitions.""",
        "history": """Originally the site of the First Herd's greatest city, this place 
fell into darkness during the final days of the centaur wars. The second centaur has 
corrupted its ancient wards, turning defensive magics into weapons against any who 
would approach."""
    }
}

# Character Backstories
CHARACTER_LORE = {
    "hermit_druid": {
        "name": "The Hermit Druid - Keeper of Ancient Wisdom",
        "background": """Once a respected elder among the centaur mystics, they foresaw 
the coming wars but their warnings went unheeded. Now they maintain their vigil in 
these lands, guarding ancient knowledge and waiting for one who might learn from the 
past rather than repeat it.

Their magic is subtle but profound, focused on understanding rather than dominance.""",
        "motivation": """They seek to guide a worthy successor who can restore balance 
to the land and end the cycle of conflict that has plagued the centaur race."""
    },
    "fallen_warrior": {
        "name": "The Fallen Warrior - Last of the Honor Guard",
        "background": """A veteran of countless battles, they once led the elite Honor 
Guard that protected the greatest of the centaur lords. When pride and ambition tore 
their world apart, they chose exile rather than participate in the slaughter of their 
kin.

Their scars tell stories of battles won and lost, but their greatest wounds are those 
that cannot be seen.""",
        "motivation": """They seek redemption by ensuring that the ancient ways of 
honorable combat are not lost, even as they warn against the pride that led to their 
people's downfall."""
    },
    "shadow_scout": {
        "name": "The Shadow Scout - Walker Between Worlds",
        "background": """Neither fully of light nor darkness, they learned to walk the 
hidden paths between worlds during the great wars. Their knowledge of secret ways and 
unseen passages saved many lives during the conflicts, though few know of their deeds.

They move like twilight itself, present yet unseen, known yet mysterious.""",
        "motivation": """They seek to preserve the balance between light and shadow, 
believing that true wisdom lies in understanding both rather than choosing between them."""
    }
}

# Historical Events
HISTORICAL_EVENTS = [
    {
        "name": "The First Sundering",
        "date": "Ancient Times",
        "description": """The moment when pride first divided the centaur herds, leading 
to the creation of distinct territories and the first conflicts over resources and 
power."""
    },
    {
        "name": "The Great Migration",
        "date": "Before the Wars",
        "description": """A time when changing lands forced the herds to move, leading 
to territorial disputes and the first major battles between centaur lords."""
    },
    {
        "name": "The War of Seven Herds",
        "date": "Height of Conflict",
        "description": """The devastating conflict that reduced the centaur population 
to a fraction of its former glory, leaving only the strongest or most cunning alive."""
    }
] 