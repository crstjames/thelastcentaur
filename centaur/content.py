"""
World content for The Last Centaur.

This is the single source of truth for everything hand-authored in the world:
landmarks, NPCs, items, enemies, biomes and the three paths. It says *what*
exists and *what unlocks what*. It never says *where* -- landmark placement is
randomized per game by worldgen.py within the constraints declared here.

Requirements are written as alternatives of item sets ("OR of ANDs"):
    all_of("a", "b")          -> need a AND b
    any_of(["a"], ["b", "c"]) -> need a, OR (b AND c)
An empty requirement means "always allowed".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Sequence, Tuple

GRID_SIZE = 10

Requirement = Tuple[Tuple[str, ...], ...]

WARRIOR = "warrior"
MYSTIC = "mystic"
STEALTH = "stealth"
PATHS = (WARRIOR, MYSTIC, STEALTH)


def all_of(*items: str) -> Requirement:
    return (tuple(items),) if items else ()


def any_of(*options: Sequence[str]) -> Requirement:
    return tuple(tuple(option) for option in options)


def is_met(requirement: Requirement, inventory: Iterable[str]) -> bool:
    if not requirement:
        return True
    have = set(inventory)
    return any(have.issuperset(option) for option in requirement)


def required_items(requirement: Requirement) -> set:
    return {item for option in requirement for item in option}


# --------------------------------------------------------------------------
# Data types
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Item:
    id: str
    name: str
    description: str
    lore: str = ""
    path: Optional[str] = None          # which path this item belongs to, if any
    take_requires: Requirement = ()     # e.g. you can't find the Focus without the Scroll
    hidden_message: str = ""            # shown when you try to take it without the requirement


@dataclass(frozen=True)
class Enemy:
    id: str
    name: str
    description: str
    health: int
    damage: int
    behavior: str = ""
    drops: Tuple[str, ...] = ()
    defeat_requires: Requirement = ()   # without these you cannot win the fight
    night_only: bool = False
    boss: bool = False


@dataclass(frozen=True)
class NPC:
    id: str
    name: str
    description: str
    backstory: str
    dialogue: Dict[str, str]            # keys: greeting, gift, after, pre_final
    gives: Tuple[str, ...] = ()         # handed over the first time you talk
    path: Optional[str] = None


@dataclass(frozen=True)
class Biome:
    id: str
    terrain: str
    adjectives: Tuple[str, ...]
    nouns: Tuple[str, ...]
    sights: Tuple[str, ...]             # first sentence of a generated tile description
    details: Tuple[str, ...]            # second sentence
    ambient_enemies: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Placement:
    """Where worldgen is allowed to put a landmark. y=0 is the south edge."""
    rows: Tuple[int, int]
    cols: Tuple[int, int] = (0, GRID_SIZE - 1)
    near: Optional[str] = None          # another landmark id, placed earlier in LANDMARKS
    distance: Tuple[int, int] = (1, GRID_SIZE * 2)  # manhattan distance from `near`


@dataclass(frozen=True)
class Landmark:
    id: str
    name: str
    biome: str
    description: str
    placement: Placement
    history: str = ""
    path: Optional[str] = None
    influence: float = 0.0              # how far this landmark's biome spreads beyond its neighbours
    enter_requires: Requirement = ()
    blocked_message: str = ""
    npcs: Tuple[str, ...] = ()
    items: Tuple[str, ...] = ()
    enemies: Tuple[str, ...] = ()


# --------------------------------------------------------------------------
# Items
# --------------------------------------------------------------------------

_ITEMS = [
    # --- Warrior path -----------------------------------------------------
    Item(
        id="warrior_map",
        name="Warrior's Map",
        description="A battle map scratched onto hide, marking the way to a ruined stronghold.",
        path=WARRIOR,
    ),
    Item(
        id="ancient_sword",
        name="The Ancient Sword",
        description="A blade that remembers the first centaur wars.",
        lore=(
            "Forged in the time when centaurs first turned against each other, this blade "
            "was wielded by the legendary warrior-sage Chiron. Its edge never dulls, and the "
            "runes along its length pulse with memories of ancient battles. Those who listen "
            "closely claim to hear whispers of long-forgotten battle tactics in its presence. "
            "The pommel bears the mark of the First Herd, and the crossguard is carved with "
            "the great migration that led to the centaur wars."
        ),
        path=WARRIOR,
    ),
    Item(
        id="war_horn",
        name="Horn of the Fallen",
        description="Its call can rally ancient spirits to your aid.",
        path=WARRIOR,
    ),
    Item(
        id="guardian_essence",
        name="Guardian's Essence",
        description="The bound power of the Shadow Guardian. The Shadow Domain's wards recognise it.",
        path=WARRIOR,
    ),
    # --- Mystic path ------------------------------------------------------
    Item(
        id="ancient_scroll",
        name="Ancient Scroll",
        description="A scroll of druidic verse. Read closely, it describes a crystal hidden in the peaks.",
        path=MYSTIC,
    ),
    Item(
        id="crystal_focus",
        name="Crystal Focus",
        description="Channels the magical energies of the land.",
        lore=(
            "A crystalline lens created by the druid circles that once mediated between "
            "warring centaur herds. Within its facets you can see the ebb and flow of the "
            "land's energies; it hums different tones as it passes over places of power. "
            "Its core is said to hold a fragment of the first dawn that witnessed the birth "
            "of the centaur race."
        ),
        path=MYSTIC,
        take_requires=all_of("ancient_scroll"),
        hidden_message="The rock face hums faintly, but you have no idea where to look.",
    ),
    Item(
        id="druid_staff",
        name="Staff of Nature's Wrath",
        description="Holds power over the natural world.",
        path=MYSTIC,
    ),
    Item(
        id="nature_key",
        name="Heartwood Key",
        description="Grown, not carved, from the corrupted druid's heart-tree. It unlocks the oldest wards.",
        path=MYSTIC,
    ),
    # --- Stealth path -----------------------------------------------------
    Item(
        id="shadow_key",
        name="Shadow Key",
        description="A key of solidified shadow that opens ways most eyes never see.",
        path=STEALTH,
    ),
    Item(
        id="stealth_cloak",
        name="Cloak of Shadows",
        description="Renders the wearer nearly invisible.",
        lore=(
            "Woven from the essence of twilight by the Shadow Weavers, a secretive circle of "
            "centaur mystics who believed true power lay in remaining unseen. The cloak "
            "drinks in light, and its patterns shift so that it never looks the same way "
            "twice. It is strongest at dawn and dusk, when light and shadow are thinnest."
        ),
        path=STEALTH,
    ),
    Item(
        id="phantom_dagger",
        name="Phantom's Edge",
        description="A blade that can cut through magical barriers.",
        path=STEALTH,
        take_requires=all_of("stealth_cloak"),
        hidden_message="The Phantom Assassin's gaze never leaves the blade. You'd never get close unseen.",
    ),
    # --- Optional / lore --------------------------------------------------
    Item(
        id="basic_supplies",
        name="Basic Supplies",
        description="A bundle of dried fruit, a waterskin and some twine.",
    ),
    Item(
        id="old_map",
        name="Old Map",
        description="A faded map of the land. The ink seems to redraw itself as you travel.",
    ),
    Item(
        id="ancient_inscription",
        name="Rubbing of an Ancient Inscription",
        description="Charcoal on bark, copied from a crossroads stone.",
        lore=(
            "The First Sundering: the moment pride first divided the centaur herds, leading "
            "to separate territories and the first conflicts over land and power."
        ),
    ),
    Item(
        id="ancient_battle_plan",
        name="Ancient Battle Plan",
        description="Troop movements of a war nobody won.",
        lore=(
            "The War of Seven Herds: the conflict that reduced the centaurs to a fraction of "
            "their former glory, leaving only the strongest or most cunning alive."
        ),
    ),
    Item(
        id="mystic_research_notes",
        name="Mystic Research Notes",
        description="Crystal-etched notes from the mystics who once studied here.",
        lore=(
            "The Great Migration: changing lands forced the herds to move, and the disputes "
            "over new territory became the first great battles between centaur lords."
        ),
    ),
    Item(
        id="crystal_shard",
        name="Crystal Shard",
        description="A sliver of mountain crystal that sings when the wind touches it.",
    ),
    Item(
        id="crown_of_dominion",
        name="Crown of Dominion",
        description="The rival's crown. What you do with it is the last choice of the game.",
    ),
    # --- Enemy drops ------------------------------------------------------
    Item(id="wolf_fang", name="Wolf Fang", description="A fang still faintly cold with shadow."),
    Item(id="void_fang", name="Void Fang", description="It casts no shadow of its own."),
    Item(id="golem_core", name="Golem Core", description="A crystal heart, still warm."),
    Item(id="spectral_essence", name="Spectral Essence", description="A wisp of an old soldier's resolve."),
    Item(id="warrior_memory", name="Warrior's Memory", description="A shard of a fallen centaur's last battle."),
    Item(id="twilight_shard", name="Twilight Shard", description="A sliver of the moment between day and night."),
    Item(id="crystallized_mana", name="Crystallized Mana", description="Raw magic, frozen solid."),
    Item(id="shadow_steel", name="Shadow Steel", description="Metal forged in the rival's service."),
    Item(id="void_essence", name="Void Essence", description="A handful of nothing that is somehow heavy."),
    Item(id="shadow_essence_fragment", name="Shadow Essence Fragment", description="A torn scrap of a night hunter."),
]

ITEMS: Dict[str, Item] = {item.id: item for item in _ITEMS}


# --------------------------------------------------------------------------
# Enemies
# --------------------------------------------------------------------------

_ENEMIES = [
    # --- Ambient enemies (spawn in biomes) --------------------------------
    Enemy(
        id="wolf_pack", name="Twilight Wolf Pack",
        description="A pack of wolves touched by shadow magic, hunting in perfect coordination.",
        behavior="Surrounds prey and attacks from multiple directions. Stronger at night.",
        health=60, damage=15, drops=("wolf_fang",),
    ),
    Enemy(
        id="shadow_stalker", name="Shadow Stalker",
        description="A creature of pure darkness that hunts at night.",
        health=80, damage=25, drops=("shadow_essence_fragment",), night_only=True,
    ),
    Enemy(
        id="shadow_hound", name="Shadow Hound",
        description="A creature of pure shadow, barely visible until it strikes.",
        behavior="Invisible in shadows, revealed by light sources.",
        health=45, damage=25, drops=("void_fang",),
    ),
    Enemy(
        id="twilight_wisp", name="Twilight Wisp",
        description="A mischievous spirit that leads travelers astray.",
        behavior="Creates illusions and false paths. Cannot be harmed by physical attacks.",
        health=30, damage=15, drops=("twilight_shard",),
    ),
    Enemy(
        id="crystal_golem", name="Crystal Golem",
        description="A massive construct of living crystal, pulsing with stored magical energy.",
        behavior="Reflects magical attacks. Must be shattered to defeat.",
        health=120, damage=30, drops=("golem_core",),
    ),
    Enemy(
        id="mana_wraith", name="Mana Wraith",
        description="A spirit that feeds on magical energy, drawn to sources of power.",
        behavior="Drains magical items and abilities. Stronger near sources of magic.",
        health=70, damage=25, drops=("crystallized_mana",),
    ),
    Enemy(
        id="spectral_sentinel", name="Spectral Sentinel",
        description="The vigilant spirit of an ancient guard, still patrolling its post.",
        behavior="Calls reinforcements when threatened. Can phase through walls.",
        health=80, damage=35, drops=("spectral_essence",),
    ),
    Enemy(
        id="corrupted_centaur_spirit", name="Corrupted Centaur Spirit",
        description="The twisted remnant of a fallen centaur warrior, consumed by darkness.",
        behavior="Uses corrupted versions of centaur battle techniques.",
        health=90, damage=40, drops=("warrior_memory",),
    ),
    Enemy(
        id="shadow_knight", name="Shadow Knight",
        description="An elite warrior in service to the Shadow Centaur, wielding both blade and shadow.",
        behavior="Combines martial prowess with shadow magic. Can command lesser shadows.",
        health=150, damage=45, drops=("shadow_steel",),
    ),
    Enemy(
        id="void_walker", name="Void Walker",
        description="A being of pure void, barely held together by the Shadow Centaur's will.",
        behavior="Can create areas of absolute darkness. Immune to physical damage.",
        health=100, damage=40, drops=("void_essence",),
    ),
    # --- Path bosses ------------------------------------------------------
    Enemy(
        id="shadow_guardian", name="Shadow Guardian",
        description="A manifestation of the Shadow Centaur's power, bound to guard the old battlefield.",
        health=150, damage=40, drops=("guardian_essence",),
        defeat_requires=all_of("ancient_sword"), boss=True,
    ),
    Enemy(
        id="corrupted_druid", name="Corrupted Druid",
        description="Once a protector of these lands and the Hermit's student, now twisted by dark magic.",
        health=100, damage=30, drops=("nature_key",),
        defeat_requires=all_of("druid_staff"), boss=True,
    ),
    Enemy(
        id="phantom_assassin", name="Phantom Assassin",
        description="A deadly spirit that guards the secret paths.",
        behavior="Strikes from nowhere. Those who cannot hide from it do not see it coming.",
        health=80, damage=50, drops=("void_essence",),
        defeat_requires=all_of("stealth_cloak", "phantom_dagger"), boss=True,
    ),
    Enemy(
        id="shadow_centaur", name="The Shadow Centaur",
        description="Your rival, the second centaur, wielding powers both ancient and terrible.",
        health=300, damage=60, drops=("crown_of_dominion",),
        defeat_requires=any_of(
            ["ancient_sword", "war_horn"],        # warrior: face them in open combat
            ["crystal_focus", "druid_staff"],     # mystic: turn the land's power against them
            ["stealth_cloak", "phantom_dagger"],  # stealth: strike before they know you're there
        ),
        boss=True,
    ),
]

ENEMIES: Dict[str, Enemy] = {enemy.id: enemy for enemy in _ENEMIES}


# --------------------------------------------------------------------------
# NPCs
# --------------------------------------------------------------------------

_NPCS = [
    NPC(
        id="hermit_druid",
        name="The Hermit Druid",
        description="An ancient druid who remembers the age of centaur wars.",
        backstory=(
            "Once a respected elder among the centaur mystics, they foresaw the coming wars "
            "but their warnings went unheeded. They keep their vigil still, guarding old "
            "knowledge and waiting for someone who might learn from the past rather than "
            "repeat it."
        ),
        dialogue={
            "greeting": "Ah, another proud centaur. Will you learn from our past, or repeat it?",
            "gift": "Take this scroll. Read it slowly; the mountains keep what it speaks of.",
            "after": "The shadow grows stronger with each passing day...",
            "pre_final": "Three paths lie before you. Choose wisely.",
        },
        gives=("ancient_scroll",),
        path=MYSTIC,
    ),
    NPC(
        id="fallen_warrior",
        name="The Fallen Warrior",
        description="A battle-scarred veteran of the centaur wars, now seeking redemption.",
        backstory=(
            "They once led the Honor Guard that protected the greatest of the centaur lords. "
            "When pride and ambition tore their world apart, they chose exile rather than "
            "join the slaughter of their kin. Their worst wounds are the ones you can't see."
        ),
        dialogue={
            "greeting": "Strength alone won't save you. Trust me, I learned that the hard way.",
            "gift": "This map shows where the old stronghold fell. The weapons there still sing.",
            "after": "The old weapons still sing with power, if you know where to look.",
            "pre_final": "Face them with honor, but don't let pride blind you.",
        },
        gives=("warrior_map",),
        path=WARRIOR,
    ),
    NPC(
        id="shadow_scout",
        name="The Shadow Scout",
        description="A mysterious figure who knows the secret paths.",
        backstory=(
            "Neither fully of light nor darkness, they learned to walk the hidden paths "
            "during the great wars and saved many lives that way, though few know it. They "
            "believe wisdom lies in understanding both light and shadow, not choosing one."
        ),
        dialogue={
            "greeting": "Not all victories require bloodshed, clever one.",
            "gift": "Take this key. Where twilight lingers, it will show you a cloak worth wearing.",
            "after": "The shadows whisper of hidden passages...",
            "pre_final": "Sometimes the best path is the one least traveled.",
        },
        gives=("shadow_key",),
        path=STEALTH,
    ),
]

NPCS: Dict[str, NPC] = {npc.id: npc for npc in _NPCS}


# --------------------------------------------------------------------------
# Biomes -- every non-landmark tile is generated from one of these
# --------------------------------------------------------------------------

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
        ambient_enemies=("wolf_pack", "shadow_stalker"),
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
        ambient_enemies=("wolf_pack", "corrupted_centaur_spirit"),
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
            "Somewhere above, crystals ring in the wind.",
            "An eagle circles overhead.",
            "The cold here bites hard.",
            "Reality seems to bend slightly at the edge of your vision.",
            "You can see a long way from here.",
        ),
        ambient_enemies=("mana_wraith", "crystal_golem"),
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
        ambient_enemies=("crystal_golem", "mana_wraith"),
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
        ambient_enemies=("spectral_sentinel", "corrupted_centaur_spirit"),
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
        ambient_enemies=("shadow_hound", "twilight_wisp"),
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
        ambient_enemies=("shadow_knight", "void_walker"),
    ),
]

BIOMES: Dict[str, Biome] = {biome.id: biome for biome in _BIOMES}


# --------------------------------------------------------------------------
# Landmarks -- the hand-authored story locations.
# Order matters: a landmark's `near` target must appear earlier in this list.
# --------------------------------------------------------------------------

_LANDMARKS = [
    Landmark(
        id="awakening_woods",
        name="The Awakening Woods",
        biome="woods",
        description=(
            "Ancient woods where you first awoke, stripped of your power by the barrier. The "
            "trees seem to whisper with memories of old conflicts, and the sky shifts between "
            "golden light and ominous shadow."
        ),
        history=(
            "Long ago these woods were neutral ground where the herds gathered for peace talks. "
            "Some say the trees still hold echoes of oaths both kept and broken."
        ),
        placement=Placement(rows=(0, 0), cols=(3, 6)),
        items=("basic_supplies", "old_map"),
        enemies=("wolf_pack",),
    ),
    Landmark(
        id="druids_grove",
        name="The Hermit's Grove",
        biome="woods",
        description="A peaceful grove where the Hermit Druid contemplates the mysteries of the past.",
        placement=Placement(rows=(0, 2), near="awakening_woods", distance=(2, 3)),
        path=MYSTIC,
        npcs=("hermit_druid",),
    ),
    Landmark(
        id="warriors_camp",
        name="The Fallen Warrior's Camp",
        biome="meadow",
        description="A small camp surrounded by old battle standards, where the Fallen Warrior keeps watch.",
        placement=Placement(rows=(0, 2), near="awakening_woods", distance=(2, 3)),
        path=WARRIOR,
        npcs=("fallen_warrior",),
    ),
    Landmark(
        id="trials_path",
        name="The Crossroads of Trials",
        biome="meadow",
        description=(
            "A crossroads marked by ancient stones, where three worn trails diverge -- each "
            "leading to a different destiny. A figure lingers in the shadow of the largest stone."
        ),
        placement=Placement(rows=(1, 3), near="awakening_woods", distance=(2, 4)),
        path=STEALTH,
        npcs=("shadow_scout",),
        items=("ancient_inscription",),
    ),
    # --- Warrior path -----------------------------------------------------
    Landmark(
        id="ancient_ruins",
        name="The Ancient Ruins",
        biome="ruins",
        description="Crumbling ruins of a mighty centaur stronghold, echoing with memories of battle.",
        placement=Placement(rows=(3, 5)),
        path=WARRIOR,
        enter_requires=all_of("warrior_map"),
        blocked_message="Collapsed walls and overgrowth hide any way in. You'd need to know the old routes.",
        items=("ancient_sword",),
        enemies=("spectral_sentinel",),
    ),
    Landmark(
        id="warriors_armory",
        name="The Warriors' Armory",
        biome="ruins",
        description="An ancient armory where the mightiest weapons of the centaur wars were kept.",
        placement=Placement(rows=(3, 7), near="ancient_ruins", distance=(2, 3)),
        path=WARRIOR,
        enter_requires=all_of("ancient_sword"),
        blocked_message="A sealed stone door bears a sword-shaped hollow. Nothing else will open it.",
        items=("war_horn",),
    ),
    Landmark(
        id="enchanted_valley",
        name="The Enchanted Valley",
        biome="meadow",
        description="A valley of ancient battlefields, where the spirits of fallen warriors still linger.",
        placement=Placement(rows=(5, 7)),
        path=WARRIOR,
        enter_requires=all_of("war_horn"),
        blocked_message="Spectral winds howl across the valley mouth and drive you back.",
        enemies=("shadow_guardian",),
    ),
    Landmark(
        id="warriors_rest",
        name="Warriors' Rest",
        biome="ruins",
        description="A sheltered hollow where ancient warriors once made camp.",
        placement=Placement(rows=(2, 6)),
        items=("ancient_battle_plan",),
        enemies=("corrupted_centaur_spirit",),
    ),
    # --- Mystic path ------------------------------------------------------
    Landmark(
        id="mystic_mountains",
        name="The Mystic Mountains",
        biome="highlands",
        description=(
            "Jagged peaks pierce the clouds, etched with runes that pulse with ancient power. "
            "Crystal formations dot the cliffs, each singing a different note on the wind."
        ),
        history=(
            "These peaks were once sanctuaries for centaur mystics. The crystals that grow here "
            "were used to record their discoveries, though many were lost in the great wars."
        ),
        placement=Placement(rows=(3, 5)),
        path=MYSTIC,
        items=("crystal_focus", "crystal_shard"),
        enemies=("mana_wraith",),
    ),
    Landmark(
        id="crystal_caves",
        name="The Crystal Caves",
        biome="crystal",
        description="A vast network of crystal-lined caves, humming with ancient magical frequencies.",
        placement=Placement(rows=(4, 7)),
        path=MYSTIC,
        enter_requires=all_of("crystal_focus"),
        blocked_message="A shimmering wall of ancient magic seals the cave mouth.",
        items=("druid_staff",),
        enemies=("crystal_golem",),
    ),
    Landmark(
        id="crystal_outpost",
        name="The Crystal Outpost",
        biome="crystal",
        description="A former research post of the centaur mystics, now overrun by crystal and something worse.",
        placement=Placement(rows=(5, 7)),
        path=MYSTIC,
        enter_requires=all_of("crystal_focus"),
        blocked_message="Crystal has grown across every door. You can't see a way through.",
        items=("mystic_research_notes",),
        enemies=("corrupted_druid",),
    ),
    # --- Stealth path -----------------------------------------------------
    Landmark(
        id="twilight_glade",
        name="The Twilight Glade",
        biome="twilight",
        description="A small clearing where twilight seems to linger eternally.",
        placement=Placement(rows=(2, 5)),
        path=STEALTH,
        enter_requires=all_of("shadow_key"),
        blocked_message="You walk toward the glade, and somehow end up back where you started.",
        items=("stealth_cloak",),
        enemies=("shadow_hound",),
    ),
    Landmark(
        id="forgotten_grove",
        name="The Forgotten Grove",
        biome="twilight",
        description="A mysterious grove where shadows move with purpose and secrets hide in plain sight.",
        placement=Placement(rows=(5, 7)),
        path=STEALTH,
        enter_requires=all_of("stealth_cloak"),
        blocked_message="Impenetrable shadows swirl across the path. Unseen eyes would spot you instantly.",
        items=("phantom_dagger",),
        enemies=("phantom_assassin",),
    ),
    # --- Finale -----------------------------------------------------------
    Landmark(
        id="shadow_domain",
        name="The Shadow Domain",
        biome="blight",
        description=(
            "A realm of perpetual twilight where reality wavers like a mirage. This was once "
            "the First Herd's greatest city; now it is your rival's seat of power."
        ),
        history=(
            "It fell into darkness in the last days of the centaur wars. The second centaur "
            "has corrupted its ancient wards into weapons against anyone who approaches."
        ),
        placement=Placement(rows=(9, 9), cols=(3, 6)),
        influence=2.0,  # the corruption spreads
        enter_requires=any_of(["guardian_essence"], ["nature_key"], ["phantom_dagger"]),
        blocked_message="The corrupted wards flare and hurl you back. You need something they recognise -- or something that can cut them.",
        enemies=("shadow_centaur",),
    ),
]

LANDMARKS: Dict[str, Landmark] = {landmark.id: landmark for landmark in _LANDMARKS}

START_LANDMARK = "awakening_woods"
FINAL_BOSS = "shadow_centaur"


# --------------------------------------------------------------------------
# Content validation -- catches typos and broken references
# --------------------------------------------------------------------------

def validate_content() -> list:
    """Return a list of problems with the content above. Empty means OK."""
    problems = []

    def check_items(where: str, item_ids: Iterable[str]) -> None:
        for item_id in item_ids:
            if item_id not in ITEMS:
                problems.append(f"{where}: unknown item '{item_id}'")

    for item in ITEMS.values():
        check_items(f"item {item.id} take_requires", required_items(item.take_requires))
        if item.path is not None and item.path not in PATHS:
            problems.append(f"item {item.id}: unknown path '{item.path}'")

    for enemy in ENEMIES.values():
        check_items(f"enemy {enemy.id} drops", enemy.drops)
        check_items(f"enemy {enemy.id} defeat_requires", required_items(enemy.defeat_requires))

    for npc in NPCS.values():
        check_items(f"npc {npc.id} gives", npc.gives)

    for biome in BIOMES.values():
        for enemy_id in biome.ambient_enemies:
            if enemy_id not in ENEMIES:
                problems.append(f"biome {biome.id}: unknown enemy '{enemy_id}'")

    seen = set()
    placed_somewhere = set()
    for landmark in _LANDMARKS:
        where = f"landmark {landmark.id}"
        if landmark.biome not in BIOMES:
            problems.append(f"{where}: unknown biome '{landmark.biome}'")
        near = landmark.placement.near
        if near is not None and near not in seen:
            problems.append(f"{where}: 'near' target '{near}' must be listed earlier")
        check_items(f"{where} items", landmark.items)
        check_items(f"{where} enter_requires", required_items(landmark.enter_requires))
        for enemy_id in landmark.enemies:
            if enemy_id not in ENEMIES:
                problems.append(f"{where}: unknown enemy '{enemy_id}'")
        for npc_id in landmark.npcs:
            if npc_id not in NPCS:
                problems.append(f"{where}: unknown npc '{npc_id}'")
        placed_somewhere.update(landmark.items)
        for npc_id in landmark.npcs:
            placed_somewhere.update(NPCS[npc_id].gives if npc_id in NPCS else ())
        for enemy_id in landmark.enemies:
            placed_somewhere.update(ENEMIES[enemy_id].drops if enemy_id in ENEMIES else ())
        seen.add(landmark.id)

    for biome in BIOMES.values():
        for enemy_id in biome.ambient_enemies:
            if enemy_id in ENEMIES:
                placed_somewhere.update(ENEMIES[enemy_id].drops)

    for item in ITEMS.values():
        if item.path is not None and item.id not in placed_somewhere:
            problems.append(f"item {item.id}: path item is never placed, given or dropped")

    if START_LANDMARK not in LANDMARKS:
        problems.append(f"start landmark '{START_LANDMARK}' does not exist")
    if FINAL_BOSS not in ENEMIES:
        problems.append(f"final boss '{FINAL_BOSS}' does not exist")

    return problems
