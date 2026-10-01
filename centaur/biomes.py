"""
Biomes for The Last Centaur. Every ordinary (non-landmark) tile takes its name
and description from one of these.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class Biome:
    id: str
    terrain: str
    adjectives: Tuple[str, ...]
    nouns: Tuple[str, ...]
    sights: Tuple[str, ...]             # first sentence of a generated tile description
    details: Tuple[str, ...]            # second sentence


_BIOMES = [
    Biome(
        id="woods", terrain="forest",
        adjectives=("Mossy", "Hushed", "Elder", "Tangled", "Dappled", "Fern-choked", "Old-growth", "Root-bound"),
        nouns=("Hollow", "Thicket", "Stand", "Copse", "Dell", "Glen", "Bracken", "Wood"),
        sights=(
            "Ancient oaks lean together overhead, their branches like gnarled fingers.",
            "Shafts of light fall through the canopy onto a carpet of moss.",
            "Ferns grow chest-high here, hiding the ground entirely.",
            "A fallen giant of a tree lies across the forest floor, furred with lichen.",
            "Birdsong stops the moment you arrive and only slowly returns.",
            "The trees here grow in a near-perfect ring.",
        ),
        details=(
            "Old hoofprints are pressed into the soft earth.",
            "Something has scratched marks into the bark at centaur height.",
            "A cold spring bubbles up between two roots.",
            "Mushrooms glow faintly in the shade.",
            "The wind carries the smell of rain.",
            "A rusted arrowhead is lodged deep in one trunk.",
        ),
    ),
    Biome(
        id="meadow", terrain="clearing",
        adjectives=("Windswept", "Golden", "Rolling", "Quiet", "Sunlit", "Barrow", "Long", "Flowering"),
        nouns=("Meadow", "Field", "Downs", "Lea", "Rise", "Plain", "Heath", "Green"),
        sights=(
            "Tall grass ripples in long waves across open ground.",
            "Wildflowers cover a gentle slope in reds and golds.",
            "An old standing stone leans at the top of a low rise.",
            "The ground here is churned, as if a herd once galloped through.",
            "Grassy mounds dot the field -- barrows, perhaps.",
            "A lone crooked tree stands in the middle of the open plain.",
        ),
        details=(
            "Far off, you can see the dark line of the forest.",
            "Larks rise from the grass as you pass.",
            "A broken spear shaft lies half-buried in the soil.",
            "The wind sounds almost like distant voices.",
            "A ring of trampled grass suggests something rested here recently.",
            "The sky feels very large here.",
        ),
    ),
    Biome(
        id="highlands", terrain="mountain",
        adjectives=("Jagged", "Rune-cut", "Misty", "Windworn", "High", "Storm-scarred", "Echoing", "Pale"),
        nouns=("Ridge", "Crag", "Pass", "Scarp", "Ledge", "Tor", "Saddle", "Spur"),
        sights=(
            "Bare rock climbs steeply on every side, streaked with veins of crystal.",
            "Faded runes are carved into a cliff face, still faintly glowing.",
            "Clouds drift below you through the valleys.",
            "A narrow ledge winds around the mountain's shoulder.",
            "Loose scree shifts under your hooves with every step.",
            "A cairn of stacked stones marks some forgotten traveler.",
        ),
        details=(
            "The air crackles faintly, raising the hair on your arms.",
            "Thin streams of meltwater trickle between the rocks.",
            "An eagle circles overhead.",
            "The cold here bites hard.",
            "Reality seems to bend slightly at the edge of your vision.",
            "You can see a long way from here.",
        ),
    ),
    Biome(
        id="crystal", terrain="cave",
        adjectives=("Glittering", "Humming", "Prismatic", "Sunken", "Resonant", "Shattered", "Glassy", "Deep"),
        nouns=("Grotto", "Hollow", "Vault", "Chasm", "Gallery", "Seam", "Basin", "Pit"),
        sights=(
            "Crystals jut from the rock in every direction, catching what little light there is.",
            "The ground slopes down into a cavern mouth rimmed with quartz.",
            "Crystal formations sing different notes as the air moves past them.",
            "Shards of broken crystal crunch underfoot.",
            "A pool of perfectly still water reflects a ceiling of gemstones.",
            "Crystals have grown over old stone walls, swallowing whatever was built here.",
        ),
        details=(
            "Your own reflection follows you across a hundred facets.",
            "A deep hum vibrates through your hooves.",
            "Tiny lights drift through the air like dust.",
            "Something has carved neat sections out of the crystal.",
            "The temperature drops sharply.",
            "Every sound comes back to you as an echo a moment too late.",
        ),
    ),
    Biome(
        id="ruins", terrain="ruins",
        adjectives=("Fallen", "Broken", "Overgrown", "Silent", "Burnt", "Forgotten", "Crumbling", "Ancient"),
        nouns=("Gate", "Wall", "Courtyard", "Watchtower", "Barracks", "Colonnade", "Stair", "Yard"),
        sights=(
            "Tumbled stone walls trace the outline of what was once a fortress.",
            "Broken columns stand in a row, holding up nothing.",
            "A stone stair climbs to a doorway that opens onto empty air.",
            "Old battle standards hang in tatters from a crumbling wall.",
            "Scorch marks blacken the stones here.",
            "A carved centaur statue lies face-down in the dirt.",
        ),
        details=(
            "Ivy has swallowed half the stonework.",
            "You find old weapons, rusted beyond use.",
            "Wind whistles through arrow slits.",
            "The silence feels like it's listening.",
            "Faded carvings show herds charging into battle.",
            "Something moved in the shadow of the wall -- or didn't.",
        ),
    ),
    Biome(
        id="twilight", terrain="forest",
        adjectives=("Dusky", "Whispering", "Shrouded", "Dim", "Veiled", "Gloaming", "Hushed", "Lightless"),
        nouns=("Glade", "Thicket", "Hollow", "Path", "Bower", "Den", "Shade", "Mire"),
        sights=(
            "It's always dusk here, whatever the hour.",
            "Shadows pool between the trees and seem to shift when you look away.",
            "Mist hangs low and thick over the ground.",
            "Pale trunks stand in the gloom like watchers.",
            "The light here is grey and comes from nowhere in particular.",
            "Thorny undergrowth closes in on a narrow trail.",
        ),
        details=(
            "Sounds are strangely muffled.",
            "You catch movement out of the corner of your eye.",
            "The air smells of wet earth and something sour.",
            "A path you're sure you saw a moment ago is gone.",
            "Faint whispers come from no direction at all.",
            "Your own shadow seems slightly late to follow you.",
        ),
    ),
    Biome(
        id="blight", terrain="wasteland",
        adjectives=("Withered", "Ashen", "Corrupted", "Hollow", "Bleak", "Cinder", "Blighted", "Grey"),
        nouns=("Waste", "Barrens", "Scar", "Flats", "Fields", "Reach", "Ash", "Moor"),
        sights=(
            "The land here is grey and dead, as if the color has been drained from it.",
            "Twisted, leafless trees claw at a bruised sky.",
            "The ground is cracked and gives off a faint, cold smoke.",
            "Shadows lie across the ground with nothing to cast them.",
            "Whatever grew here has withered to ash.",
            "Black stones jut from the earth like broken teeth.",
        ),
        details=(
            "To the north, the sky darkens.",
            "The air presses against you like a weight.",
            "The ground seems to shift treacherously underfoot.",
            "Nothing lives here. Nothing that should.",
            "You feel watched.",
            "The silence is total.",
        ),
    ),
]

BIOMES: Dict[str, Biome] = {biome.id: biome for biome in _BIOMES}
