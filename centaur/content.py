"""
World content for The Last Centaur.

This is the single source of truth for everything hand-authored: landmarks and
where they sit, NPCs and what they say, items, features you can examine, the
interactions that move the story forward, echoes (notes your past self left),
signals (the world reacting as you get close), and hazards.

The engine (game.py) is generic. It knows nothing about crystals or wolves; it
just evaluates Conditions and applies Effects. Story lives here.

See GAME_DESIGN.md for the design these implement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple, Union

GRID_SIZE = 10
WORLD_SEED = 1          # fixed: every player gets the same ordinary tiles

PHASES = ("dawn", "day", "dusk", "night")
PHASE_TURNS = 6         # turns per phase; a full day is 24 turns
START_TURN = PHASE_TURNS  # the game begins at the start of "day"

SLICE_GOAL = "ward_insight"   # the end of what's playable so far

Pos = Tuple[int, int]
Place = Union[str, Pos]       # a landmark id, or a specific tile


# --------------------------------------------------------------------------
# Building blocks
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Condition:
    """True when all parts hold. Empty parts are ignored."""
    items: Tuple[str, ...] = ()       # carrying all of these
    flags: Tuple[str, ...] = ()       # all of these flags are set
    not_flags: Tuple[str, ...] = ()   # none of these flags are set
    phases: Tuple[str, ...] = ()      # time of day is one of these


ALWAYS = Condition()


def when(items=(), flags=(), not_flags=(), phases=()) -> Condition:
    as_tuple = lambda v: (v,) if isinstance(v, str) else tuple(v)
    return Condition(as_tuple(items), as_tuple(flags), as_tuple(not_flags), as_tuple(phases))


def is_met(condition: Condition, inventory: Iterable[str], flags: Iterable[str],
           phase: Optional[str] = None) -> bool:
    """Check a condition. phase=None means "some time of day" (used by the solver)."""
    inventory, flags = set(inventory), set(flags)
    return (
        inventory.issuperset(condition.items)
        and flags.issuperset(condition.flags)
        and not flags.intersection(condition.not_flags)
        and (phase is None or not condition.phases or phase in condition.phases)
    )


@dataclass(frozen=True)
class Effects:
    message: str = ""
    give: Tuple[str, ...] = ()        # items added to inventory
    flags: Tuple[str, ...] = ()       # flags set
    clues: Tuple[str, ...] = ()       # clues the player has now seen
    memory: str = ""                  # written into this tile's memory
    pride: int = 0


@dataclass(frozen=True)
class Item:
    id: str
    name: str
    description: str
    lore: str = ""
    clue: Optional[str] = None        # seen when the player examines this item


@dataclass(frozen=True)
class Enemy:
    id: str
    name: str
    description: str
    health: int
    damage: int
    defeat_requires: Condition = ALWAYS
    drops: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Line:
    """One thing an NPC can say. The first line whose condition holds is spoken."""
    when: Condition
    text: str
    effects: Effects = Effects()


@dataclass(frozen=True)
class NPC:
    id: str
    name: str
    description: str
    at: str                           # landmark id
    lines: Tuple[Line, ...]
    present_when: Condition = ALWAYS


@dataclass(frozen=True)
class Feature:
    """Something in a place you can examine and interact with."""
    id: str
    name: str
    at: Place
    words: Tuple[str, ...]            # what the player might call it
    description: str
    visible_when: Condition = ALWAYS
    clue: Optional[str] = None        # seen when examined


@dataclass(frozen=True)
class Interaction:
    """
    Doing something specific somewhere specific. The player's words must name
    the feature and/or item; the condition decides whether it works.
    """
    id: str
    verbs: Tuple[str, ...]            # canonical verbs, see game.VERBS
    at: Place
    feature: Optional[str] = None
    item: Optional[str] = None        # must be carried
    when: Condition = ALWAYS
    effects: Effects = Effects()
    otherwise: str = ""               # shown if named correctly but the condition fails
    once: bool = True
    clues: Tuple[str, ...] = ()       # fairness: at least one must be seen first (empty = self-evident)


@dataclass(frozen=True)
class Sequence:
    """Do `verb` to features in a set order (e.g. strike crystals)."""
    id: str
    at: Place
    verb: str
    steps: Tuple[str, ...]            # feature ids, in the correct order
    notes: Dict[str, str]             # feature id -> what happens when you hit it
    when: Condition
    success: Effects
    failure: str
    clues: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Echo:
    """A note your past self carved, already in a tile's memory when the game begins."""
    at: Pos
    text: str
    clue: Optional[str] = None


@dataclass(frozen=True)
class Signal:
    """The world reacting as you approach something, louder as you get closer."""
    id: str
    target: Pos
    biomes: Tuple[str, ...]
    when: Condition
    by_distance: Tuple[str, ...]      # index = manhattan distance to target
    clue: Optional[str] = None


@dataclass(frozen=True)
class Hazard:
    """Something that hurts you for spending a turn somewhere."""
    at: str
    when: Condition
    damage: int
    message: str


@dataclass(frozen=True)
class Landmark:
    id: str
    name: str
    pos: Pos
    biome: str
    description: str
    variants: Tuple[Tuple[Condition, str], ...] = ()   # first match replaces description
    enter_when: Condition = ALWAYS
    blocked_message: str = ""
    items: Tuple[str, ...] = ()
    enemies: Tuple[str, ...] = ()


# --------------------------------------------------------------------------
# Landmarks (fixed map; y=0 is the south edge)
# --------------------------------------------------------------------------

_LANDMARKS = [
    Landmark(
        id="awakening_woods", name="The Awakening Woods", pos=(5, 0), biome="woods",
        description=(
            "Ancient woods where you woke on cold earth, stripped of your power. Great roots "
            "knot the ground around you, and the bark of the nearest oak is scored with deep "
            "scratches at about the height of your shoulder."
        ),
        enemies=("wolf_pack",),
    ),
    Landmark(
        id="druids_grove", name="The Hermit's Grove", pos=(2, 1), biome="woods",
        description=(
            "A quiet grove ringed by birches. An old druid sits on a flat stone at its centre, "
            "as though they have been waiting for you for a very long time."
        ),
    ),
    Landmark(
        id="warriors_camp", name="The Fallen Warrior's Camp", pos=(8, 1), biome="meadow",
        description=(
            "A small camp ringed by old battle standards, their colours faded to grey. A "
            "scarred centaur sits by a cold fire, sharpening a blade that is already sharp."
        ),
    ),
    Landmark(
        id="trials_path", name="The Crossroads", pos=(5, 3), biome="meadow",
        description=(
            "Three worn trails meet at a tall standing stone covered in weathered runes. In the "
            "dust around its base are hoofprints that stop mid-stride, as if whoever made them "
            "simply stepped out of the world."
        ),
    ),
    Landmark(
        id="mystic_mountains", name="The Mystic Mountains", pos=(1, 4), biome="highlands",
        description=(
            "Jagged peaks pierce the clouds, etched with old runes. Crystal formations stud the "
            "cliffs, and the wind moves between them with a sound almost like breath."
        ),
    ),
    Landmark(
        id="crystal_caves", name="The Crystal Caves", pos=(2, 7), biome="crystal",
        description=(
            "A cave mouth in the cliff, rimmed with crystal. Just inside, a shimmering wall of "
            "light fills the passage, rippling like heat over stone."
        ),
        variants=(
            (when(flags="caves_open"),
             "Beyond the cave mouth a vaulted chamber opens up, lit by its own crystal. A great "
             "mural covers the far wall, and before it rise three tall crystals: amber, violet "
             "and white. Beside the mural, the stone is covered in fine scratches."),
        ),
    ),
    Landmark(
        id="twilight_glade", name="The Twilight Glade", pos=(4, 5), biome="twilight",
        description="A clearing where twilight seems to linger whatever the hour.",
        enter_when=when(flags="act3_open"),
        blocked_message="You walk toward the glade, and somehow find yourself back where you started.",
    ),
    Landmark(
        id="warriors_rest", name="Warriors' Rest", pos=(6, 6), biome="ruins",
        description=(
            "A sheltered hollow where ancient warriors once made camp. A cairn of stacked "
            "stones stands at its centre."
        ),
    ),
    Landmark(
        id="ancient_ruins", name="The Ancient Ruins", pos=(8, 4), biome="ruins",
        description="Crumbling ruins of a mighty centaur stronghold, echoing with memories of battle.",
        enter_when=when(flags="act2_open"),
        blocked_message="Collapsed walls and rubble. There's no way in from here.",
    ),
    Landmark(
        id="enchanted_valley", name="The Enchanted Valley", pos=(8, 7), biome="meadow",
        description="A valley of old battlefields, where the spirits of fallen warriors still linger.",
        enter_when=when(flags="act2_open"),
        blocked_message="Spectral winds howl out of the valley mouth and drive you back.",
    ),
    Landmark(
        id="forgotten_grove", name="The Forgotten Grove", pos=(5, 7), biome="twilight",
        description="A grove where shadows move with purpose.",
        enter_when=when(flags="act3_open"),
        blocked_message="Shadows thick as smoke swirl across the way. Something in them is watching.",
    ),
    Landmark(
        id="shadow_domain", name="The Shadow Domain", pos=(5, 9), biome="blight",
        description="A realm of perpetual twilight, where reality wavers like a mirage.",
        enter_when=when(flags="barrier_down"),
        blocked_message=(
            "The air hardens into an invisible wall. Pressing against it is like pressing "
            "against your own reflection."
        ),
    ),
]

LANDMARKS: Dict[str, Landmark] = {l.id: l for l in _LANDMARKS}
START_LANDMARK = "awakening_woods"
FALL_LANDMARK = "druids_grove"        # where you wake if you fall

# Tiles whose biome is set by hand rather than by nearest landmark.
BIOME_OVERRIDES: Dict[Pos, str] = {
    (1, 6): "highlands",              # the singing crystal
    (1, 5): "highlands",
    (0, 6): "highlands",
}

FOCUS_TILE: Pos = (1, 6)


# --------------------------------------------------------------------------
# Items and enemies
# --------------------------------------------------------------------------

_ITEMS = [
    Item(
        id="old_map", name="Old Map",
        description="A fold of oiled hide marked with faded ink. The marks look like your own hand.",
    ),
    Item(
        id="crystal_focus", name="Crystal Focus",
        description="A crystalline lens, cut and polished. It channels the energies of the land.",
        lore=(
            "Made by the druid circles that once mediated between the warring herds. Within its "
            "facets you can see the ebb and flow of the land's power. Held up to sunlight in "
            "places of power, it is said to reveal what has been hidden."
        ),
        clue="focus_lore",
    ),
]
ITEMS: Dict[str, Item] = {i.id: i for i in _ITEMS}

_ENEMIES = [
    Enemy(
        id="wolf_pack", name="Twilight Wolf Pack",
        description=(
            "Wolves touched by shadow, circling just beyond reach. By day they keep their "
            "distance. You don't like to think about the night."
        ),
        health=60, damage=15,
        defeat_requires=when(items="ancient_sword"),  # not obtainable yet: you can't win this
    ),
]
ENEMIES: Dict[str, Enemy] = {e.id: e for e in _ENEMIES}


# --------------------------------------------------------------------------
# NPCs
# --------------------------------------------------------------------------

_NPCS = [
    NPC(
        id="hermit_druid", name="The Hermit Druid", at="druids_grove",
        description="Ancient and still, with eyes that seem to be remembering you.",
        lines=(
            Line(
                when(flags="ward_insight"),
                "The Hermit looks at you for a long time. \"So. You've seen the mural, and whose "
                "face it bears. Now you know what you were. What you will be is still yours to "
                "choose.\"",
            ),
            Line(
                when(not_flags="met_hermit"),
                "The Hermit looks up, and something like grief crosses their face. \"You've come "
                "back. Again.\" A long pause. \"Will you learn from our past, or repeat it? ... "
                "What you lost still sings in the high places. Listen for it at first light.\"",
                Effects(flags=("met_hermit",), clues=("hermit_song",)),
            ),
            Line(
                when(items="crystal_focus"),
                "The Hermit's eyes go to the Focus. \"It remembers the sun. So should you.\"",
                Effects(clues=("focus_sun",)),
            ),
            Line(
                ALWAYS,
                "\"The high places sing at first light,\" the Hermit says. \"Have you listened?\"",
                Effects(clues=("hermit_song",)),
            ),
        ),
    ),
    NPC(
        id="fallen_warrior", name="The Fallen Warrior", at="warriors_camp",
        description="Scarred, grey at the muzzle, and very obviously not pleased to see you.",
        lines=(
            Line(
                when(flags="insight"),
                "The Fallen Warrior's blade stops. \"You can read them now, can't you? The "
                "runes.\" They nod at the standards. \"Then read those, and tell me you don't "
                "remember.\"",
            ),
            Line(
                ALWAYS,
                "The Fallen Warrior turns their back on you. \"I know what you are.\"",
            ),
        ),
    ),
]
NPCS: Dict[str, NPC] = {n.id: n for n in _NPCS}


# --------------------------------------------------------------------------
# Features
# --------------------------------------------------------------------------

_FEATURES = [
    # --- Awakening Woods ----------------------------------------------------
    Feature(
        id="roots", name="the roots", at="awakening_woods",
        words=("roots", "root", "ground", "earth"),
        description="The roots heave up out of the soil. Something pale is caught between them.",
    ),
    Feature(
        id="scratched_bark", name="the scratched bark", at="awakening_woods",
        words=("bark", "scratches", "oak", "tree", "marks"),
        description=(
            "Deep scratches, gouged in sets of four. Someone your size made these, a long "
            "time ago. Someone with hooves and hands, who was very angry or very afraid."
        ),
    ),
    # --- Crossroads -----------------------------------------------------------
    Feature(
        id="standing_stone", name="the standing stone", at="trials_path",
        words=("stone", "runes", "standing", "rune"),
        description="A tall stone, crowded with runes worn almost smooth. To you they're just scratches.",
        visible_when=when(not_flags="insight"),
    ),
    Feature(
        id="standing_stone_read", name="the standing stone", at="trials_path",
        words=("stone", "runes", "standing", "rune"),
        description=(
            "The runes have rearranged themselves into sense: \"Here the herds parted. Here, "
            "one day, they might meet again.\""
        ),
        visible_when=when(flags="insight"),
    ),
    Feature(
        id="vanishing_hoofprints", name="the hoofprints", at="trials_path",
        words=("hoofprints", "prints", "tracks", "footprints", "dust"),
        description="Light, careful prints. They walk up to the stone, take one more step, and end.",
    ),
    # --- Fallen Warrior's Camp ------------------------------------------------
    Feature(
        id="battle_standards", name="the battle standards", at="warriors_camp",
        words=("standards", "standard", "banners", "banner", "flags", "runes"),
        description="Old standards, faded grey, stitched with rows of runes you can't read.",
        visible_when=when(not_flags="insight"),
    ),
    Feature(
        id="battle_standards_read", name="the battle standards", at="warriors_camp",
        words=("standards", "standard", "banners", "banner", "flags", "runes", "names"),
        description=(
            "The runes are names: the Honor Guard, rank by rank. Most are marked with the sign "
            "for the dead. One, near the bottom, carries a longer mark: \"Fell at the valley, "
            "guarding the way.\" At the very top, where a lord's name would go, the cloth has "
            "been cut away."
        ),
        visible_when=when(flags="insight"),
    ),
    # --- Warriors' Rest -------------------------------------------------------
    Feature(
        id="cairn", name="the cairn", at="warriors_rest",
        words=("cairn", "stones", "stone", "pile"),
        description="A cairn of stacked stones. Old runes on the top stone are dark and cold.",
    ),
    # --- Mystic Mountains -----------------------------------------------------
    Feature(
        id="mountain_crystals", name="the crystals", at="mystic_mountains",
        words=("crystals", "crystal", "cliffs", "formations"),
        description=(
            "Crystal juts from the cliffs in clusters. When the wind moves through them they "
            "almost seem to hum."
        ),
    ),
    # --- The singing crystal (an ordinary tile) -------------------------------
    Feature(
        id="singing_crystal", name="the ringing crystal", at=FOCUS_TILE,
        words=("crystal", "ringing", "singing", "louder", "note", "song", "crack"),
        description=(
            "One crystal rings louder than all the rest, a clear, high note. Looking closer, "
            "it doesn't seem to be growing from the rock at all. It's wedged into a crack."
        ),
        visible_when=when(phases="dawn", not_flags="focus_found"),
    ),
    # --- Crystal Caves --------------------------------------------------------
    Feature(
        id="shimmering_wall", name="the shimmering wall", at="crystal_caves",
        words=("wall", "shimmer", "shimmering", "light", "barrier", "passage"),
        description=(
            "A wall of light, rippling like heat. Shapes seem to move inside it, a pattern "
            "just too blurred to make out."
        ),
        visible_when=when(not_flags="caves_open"),
    ),
    Feature(
        id="mural", name="the mural", at="crystal_caves",
        words=("mural", "painting", "wall", "banners", "banner", "herds", "war", "picture"),
        description=(
            "A vast mural of the War of Seven Herds. The herds charge across the rock beneath "
            "three banners: white at the front, amber behind it, and violet at the rear. "
            "Beneath the violet banner rides a crowned centaur. You know those markings. "
            "They are yours."
        ),
        visible_when=when(flags="caves_open"),
        clue="mural_order",
    ),
    Feature(
        id="amber_crystal", name="the amber crystal", at="crystal_caves",
        words=("amber", "crystal", "orange", "gold", "honey"),
        description="A tall crystal glowing like honey. It looks as though it would ring if struck.",
        visible_when=when(flags="caves_open"),
    ),
    Feature(
        id="violet_crystal", name="the violet crystal", at="crystal_caves",
        words=("violet", "crystal", "purple"),
        description="A tall crystal, deep violet. It looks as though it would ring if struck.",
        visible_when=when(flags="caves_open"),
    ),
    Feature(
        id="white_crystal", name="the white crystal", at="crystal_caves",
        words=("white", "crystal", "clear", "pale"),
        description="A tall crystal, white as frost. It looks as though it would ring if struck.",
        visible_when=when(flags="caves_open"),
    ),
    Feature(
        id="cave_scratches", name="the scratches", at="crystal_caves",
        words=("scratches", "scratch", "stone", "runes", "writing", "marks"),
        description="Fine, careful scratches cover the stone beside the mural. They mean nothing to you.",
        visible_when=when(flags="caves_open", not_flags="insight"),
    ),
    Feature(
        id="cave_runes", name="the runes", at="crystal_caves",
        words=("scratches", "scratch", "stone", "runes", "writing", "marks", "words"),
        description=(
            "\"The first ward is Insight. The Hermit holds it, and the Hermit's question is the "
            "lock: will you learn?\" Below it, in a hand you know is your own, freshly cut: "
            "\"I learned. It wasn't enough.\""
        ),
        visible_when=when(flags="insight"),
    ),
]
FEATURES: Dict[str, Feature] = {f.id: f for f in _FEATURES}


# --------------------------------------------------------------------------
# Interactions and sequences
# --------------------------------------------------------------------------

_INTERACTIONS = [
    Interaction(
        id="find_old_map", verbs=("examine",), at="awakening_woods", feature="roots",
        effects=Effects(
            message=(
                "Tangled in the roots, half buried, is a fold of oiled hide. A map. The ink is "
                "faded, but the hand that drew it is unmistakably your own."
            ),
            give=("old_map",),
            memory="You pulled an old map, in your own hand, from these roots.",
        ),
    ),
    Interaction(
        id="find_focus", verbs=("examine", "take", "strike", "use"), at=FOCUS_TILE,
        feature="singing_crystal",
        when=when(phases="dawn"),
        effects=Effects(
            message=(
                "You work the ringing crystal loose from its crack. It isn't a crystal at all, "
                "but a lens, cut and polished by hands. The moment it comes free, every crystal "
                "on the mountain falls silent. You hold the Crystal Focus."
            ),
            give=("crystal_focus",),
            flags=("focus_found",),
            memory="At first light, the crystals sang here, and you found the Crystal Focus.",
        ),
        clues=("hermit_song", "crystal_song", "crystal_dawn"),
    ),
    Interaction(
        id="open_caves", verbs=("use",), at="crystal_caves",
        feature="shimmering_wall", item="crystal_focus",
        when=when(phases=("dawn", "day")),
        effects=Effects(
            message=(
                "You raise the Crystal Focus. Sunlight pours through it and splits into a "
                "hundred threads, and the shapes in the wall snap into focus: a pattern, a lock, "
                "and the light is its key. The wall folds away like a curtain drawn aside."
            ),
            flags=("caves_open",),
            memory="Here, sunlight through the Focus parted the shimmering wall.",
        ),
        otherwise="You raise the Crystal Focus, but it's dark and cold in your hand. It needs a light you don't have right now.",
        clues=("focus_lore", "focus_sun", "sunlight_echo"),
    ),
]
INTERACTIONS: Dict[str, Interaction] = {i.id: i for i in _INTERACTIONS}

_SEQUENCES = [
    Sequence(
        id="insight_ward", at="crystal_caves", verb="strike",
        steps=("white_crystal", "amber_crystal", "violet_crystal"),
        notes={
            "white_crystal": "The white crystal sings a high, clear note.",
            "amber_crystal": "The amber crystal answers with a warm, middle note.",
            "violet_crystal": "The violet crystal gives a low note you feel in your chest.",
        },
        when=when(flags="caves_open", not_flags="ward_insight"),
        success=Effects(
            message=(
                "The three notes hang in the air and braid together into a chord. The mural "
                "blazes with light, and something that was taken from you comes back. Your eyes "
                "ache, then clear. The scratches beside the mural are no longer scratches. They "
                "are words, and you can read them."
            ),
            flags=("ward_insight", "insight"),
            memory="Here you struck the chord, and the Insight ward broke.",
        ),
        failure=(
            "Discord shrieks through the cave and the crystals go dark for a moment. Whatever "
            "you started, you'll have to start again."
        ),
        clues=("mural_order",),
    ),
]
SEQUENCES: Dict[str, Sequence] = {s.id: s for s in _SEQUENCES}


# --------------------------------------------------------------------------
# Echoes, signals, hazards
# --------------------------------------------------------------------------

def carved(text: str) -> str:
    return f'Carved here, in your hand: "{text}"'


ECHOES = [
    Echo(at=(5, 0), text=carved("If you're reading this, it happened again. Don't trust the crown.")),
    Echo(at=(5, 3), text=carved("Three of them. Three wards. Three tests. I failed the last one.")),
    Echo(at=(1, 4), text=carved("The stones only sing for the early riser."), clue="crystal_dawn"),
    Echo(at=(2, 6), text=carved("Sunlight, not torchlight. The Focus remembers the sun."), clue="sunlight_echo"),
]

SIGNALS = [
    Signal(
        id="crystal_song", target=FOCUS_TILE, biomes=("highlands", "crystal"),
        when=when(phases="dawn", not_flags="focus_found"),
        by_distance=(
            "",  # on the tile itself, the feature description takes over
            "Very close by, a single crystal is ringing, high and clear.",
            "You can hear crystals singing nearby.",
            "Faintly, on the wind, you hear crystals singing.",
        ),
        clue="crystal_song",
    ),
]

HAZARDS = [
    Hazard(
        at="awakening_woods", when=when(phases="night"), damage=20,
        message="In the dark, the wolves close in and snap at your flanks. (-20 health)",
    ),
]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def _clues_produced() -> set:
    produced = set()
    produced.update(i.clue for i in ITEMS.values() if i.clue)
    produced.update(f.clue for f in FEATURES.values() if f.clue)
    produced.update(e.clue for e in ECHOES if e.clue)
    produced.update(s.clue for s in SIGNALS if s.clue)
    for npc in NPCS.values():
        for line in npc.lines:
            produced.update(line.effects.clues)
    for interaction in INTERACTIONS.values():
        produced.update(interaction.effects.clues)
    return produced


def validate_content() -> list:
    """Return a list of problems with the content above. Empty means OK."""
    problems = []
    flags_set = set()
    for npc in NPCS.values():
        for line in npc.lines:
            flags_set.update(line.effects.flags)
    for interaction in INTERACTIONS.values():
        flags_set.update(interaction.effects.flags)
    for sequence in SEQUENCES.values():
        flags_set.update(sequence.success.flags)

    def check_place(where: str, place: Place) -> None:
        if isinstance(place, str):
            if place not in LANDMARKS:
                problems.append(f"{where}: unknown landmark '{place}'")
        elif not (0 <= place[0] < GRID_SIZE and 0 <= place[1] < GRID_SIZE):
            problems.append(f"{where}: position {place} is off the map")

    def check_items(where: str, item_ids) -> None:
        for item_id in item_ids:
            if item_id not in ITEMS and item_id != "ancient_sword":  # Act II, not written yet
                problems.append(f"{where}: unknown item '{item_id}'")

    positions = {}
    for landmark in LANDMARKS.values():
        check_place(f"landmark {landmark.id}", landmark.pos)
        if landmark.pos in positions:
            problems.append(f"landmark {landmark.id}: shares {landmark.pos} with {positions[landmark.pos]}")
        positions[landmark.pos] = landmark.id
        check_items(f"landmark {landmark.id} items", landmark.items)
        for enemy_id in landmark.enemies:
            if enemy_id not in ENEMIES:
                problems.append(f"landmark {landmark.id}: unknown enemy '{enemy_id}'")

    for npc in NPCS.values():
        check_place(f"npc {npc.id}", npc.at)
    for feature in FEATURES.values():
        check_place(f"feature {feature.id}", feature.at)
    for enemy in ENEMIES.values():
        check_items(f"enemy {enemy.id}", enemy.defeat_requires.items + enemy.drops)

    produced = _clues_produced()
    for interaction in INTERACTIONS.values():
        where = f"interaction {interaction.id}"
        check_place(where, interaction.at)
        check_items(where, ((interaction.item,) if interaction.item else ()) + interaction.effects.give)
        if interaction.feature and interaction.feature not in FEATURES:
            problems.append(f"{where}: unknown feature '{interaction.feature}'")
        if interaction.item and not interaction.clues:
            problems.append(f"{where}: uses an item but has no clues pointing to it")
        for clue in interaction.clues:
            if clue not in produced:
                problems.append(f"{where}: clue '{clue}' is never shown to the player")
    for sequence in SEQUENCES.values():
        where = f"sequence {sequence.id}"
        check_place(where, sequence.at)
        for step in sequence.steps:
            if step not in FEATURES:
                problems.append(f"{where}: unknown feature '{step}'")
        if not sequence.clues:
            problems.append(f"{where}: has no clues pointing to the order")
        for clue in sequence.clues:
            if clue not in produced:
                problems.append(f"{where}: clue '{clue}' is never shown to the player")

    for pos in BIOME_OVERRIDES:
        if pos in positions:
            problems.append(f"biome override {pos} is a landmark tile")
    if FOCUS_TILE in positions:
        problems.append("FOCUS_TILE must be an ordinary tile")
    if SLICE_GOAL not in flags_set:
        problems.append(f"SLICE_GOAL '{SLICE_GOAL}' is never set")
    return problems
