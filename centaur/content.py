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

SLICE_GOAL = "bridle_broken"  # the end of what's playable so far

# The opening crawl, shown once before a new game begins. It ends on the title.
PROLOGUE = (
    "For as long as anyone remembered, the centaur herds ran free.",
    "Men feared them. Men envied them. Most of all, men wanted to ride them.",
    "Then one centaur took the side of men. His name was Ixion. He taught that the horse in us "
    "was a curse: that our kind should kneel, take the bridle, and be Unmade into men. Those "
    "who followed him were called the Bridled.",
    "You led the Free Herds against them. You were Centaur Prime, and you never knelt.",
    "The War of the Bridle ended in one last battle. When the dust settled, only you were left "
    "standing.",
    "But Ixion lived. He wears a golden bridle for a crown, and he no longer calls himself a "
    "centaur. He calls himself a man. A king of men.",
    "And he is not finished. He will not rest until the last of our kind is bridled, broken, "
    "or gone.",
    "No herd. No Honor Guard. No one left to stand against him.",
    "No one but you.",
    "You are the last hope of your kind. You are...",
)
PROLOGUE_TITLE = "The Last Centaur"   # the terminal's closing card (the web page has its own title)

Pos = Tuple[int, int]
Place = Union[str, Pos]       # a landmark id, "near:<landmark id>" (any tile beside it), or a tile


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
    not_items: Tuple[str, ...] = ()   # carrying none of these


ALWAYS = Condition()


def when(items=(), flags=(), not_flags=(), phases=(), not_items=()) -> Condition:
    as_tuple = lambda v: (v,) if isinstance(v, str) else tuple(v)
    return Condition(as_tuple(items), as_tuple(flags), as_tuple(not_flags), as_tuple(phases), as_tuple(not_items))


def is_met(condition: Condition, inventory: Iterable[str], flags: Iterable[str],
           phase: Optional[str] = None) -> bool:
    """Check a condition. phase=None means "some time of day" (used by the solver)."""
    inventory, flags = set(inventory), set(flags)
    return (
        inventory.issuperset(condition.items)
        and not inventory.intersection(condition.not_items)
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
    remove_enemies: Tuple[str, ...] = ()  # taken off this tile


@dataclass(frozen=True)
class Item:
    id: str
    name: str
    description: str
    lore: str = ""
    clue: Optional[str] = None        # seen when the player examines this item
    quest: bool = False               # a story-critical find (the UI celebrates it)


@dataclass(frozen=True)
class Enemy:
    id: str
    name: str
    description: str
    health: int
    damage: int
    defeat_requires: Condition = ALWAYS
    drops: Tuple[str, ...] = ()
    on_defeat: Effects = Effects()
    yields: bool = False              # beaten, it stays and waits: an interaction decides its fate
    yielded_text: str = ""            # how it's described once it has yielded


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
    otherwise: str = ""               # shown if named correctly but the condition fails (empty: fall through)
    once: bool = True
    clues: Tuple[str, ...] = ()       # fairness: at least one must be seen first (empty = self-evident)
    words: Tuple[str, ...] = ()       # extra names for the target, e.g. an enemy's
    bare: bool = False                # also matches the verb alone ("spare")


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
class Maze:
    """
    A landmark you get lost in. While unsolved, moving from it walks a hidden
    path instead of the map: the right steps lead to its heart, a wrong one puts
    you back where you came in.
    """
    id: str
    at: str                           # landmark id
    path: Tuple[str, ...]             # directions, in order
    step_text: str                    # after each right step but the last
    failure: str                      # after a wrong step, before you're put back
    success: Effects
    solved_flag: str
    clues: Tuple[str, ...]            # fairness: ALL must be seen (each holds part of the path)


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
    enemy: Optional[str] = None       # only while this enemy is still here


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
    blocked_variants: Tuple[Tuple[Condition, str], ...] = ()   # first match replaces blocked_message
    approach_from: Tuple[str, ...] = ()   # if set, can only be entered from a neighbour on these sides
    items: Tuple[str, ...] = ()
    enemies: Tuple[str, ...] = ()


# --------------------------------------------------------------------------
# Landmarks (fixed map; y=0 is the south edge)
# --------------------------------------------------------------------------

_LANDMARKS = [
    Landmark(
        id="awakening_woods", name="The Awakening Woods", pos=(5, 0), biome="woods",
        description=(
            "Ancient woods where you woke on cold earth, with no strength and no name. Great "
            "roots knot the ground around you, and the bark of the nearest oak is scored with "
            "deep scratches at about the height of your shoulder."
        ),
        enemies=("wolf_pack",),
    ),
    Landmark(
        id="melias_grove", name="Melia's Grove", pos=(2, 1), biome="woods",
        description=(
            "A grove of ash trees, tall and grey-barked, around one far older than the rest. "
            "Its bark has the shape of a woman in it, if you look long enough, and she has been "
            "looking back at you since you arrived."
        ),
    ),
    Landmark(
        id="lapith_camp", name="The Lapith Camp", pos=(8, 1), biome="meadow",
        description=(
            "A soldier's camp, and a man's: one tent, one cold fire. Around it stands a ring of "
            "captured battle standards, centaur standards, their colours faded to grey. A "
            "broad-shouldered Lapith in bronze sits by the fire, sharpening a blade that is "
            "already sharp. There isn't a scar on him."
        ),
    ),
    Landmark(
        id="crossroads", name="The Crossroads", pos=(5, 3), biome="meadow",
        description=(
            "Three worn trails meet at a tall standing stone covered in weathered runes. In the "
            "dust around its base are small cloven hoofprints that stop mid-stride, as if "
            "whoever made them simply stepped out of the world."
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
        description=(
            "Twilight closes around you like water. The trees are pale and close together, and "
            "every way you look is the same way. You are not sure which direction you came in by."
        ),
        variants=(
            (when(flags="glade_solved"),
             "The heart of the Twilight Glade: a ring of pale trees around a patch of soft "
             "grass, where the light never quite decides what hour it is. From here the paths "
             "out are plain enough."),
        ),
    ),
    Landmark(
        id="warriors_rest", name="Warriors' Rest", pos=(6, 6), biome="ruins",
        description=(
            "A sheltered hollow, quiet as a held breath. A cairn of stacked stones stands at its "
            "centre, over what can only be graves."
        ),
        variants=(
            (when(items="ash_spear", not_flags="shield_found"),
             "A sheltered hollow, quiet as a held breath. At its centre stands a cairn of stacked "
             "stones over what can only be graves, and the runes on its top stone are glowing a "
             "cold blue."),
        ),
    ),
    Landmark(
        id="ruined_stronghold", name="The Ruined Stronghold", pos=(8, 4), biome="ruins",
        description=(
            "The crumbling heart of a centaur stronghold. You came in by a gap in the north wall "
            "that you'd never have found without knowing it was there. In a hall open to the sky "
            "stands a stone bier, and on it lies a battered war horn, as if someone set it down "
            "and meant to come back."
        ),
        variants=(
            (when(items="war_horn"),
             "The crumbling heart of a centaur stronghold, open to the sky. The bier where the "
             "horn lay is empty now, and somehow the hall feels more abandoned for it."),
        ),
        enter_when=when(flags="caeneus_trust"),
        approach_from=("north",),
        blocked_message="Collapsed walls and rubble. There's no way in from this side.",
        items=("war_horn",),
    ),
    Landmark(
        id="enchanted_valley", name="The Enchanted Valley", pos=(8, 7), biome="meadow",
        description=(
            "A long valley of old battlefields. Rusted blades stand in the grass like grave "
            "markers, and the air is thick with the dead: you can't see them, but you can feel "
            "them watching."
        ),
        variants=(
            (when(flags="spirits_freed"),
             "A long valley of old battlefields, quiet now. The wind moves through the grass "
             "like a breath let out after a very long time."),
        ),
        enter_when=when(flags="valley_open"),
        blocked_message="Spectral winds howl out of the valley mouth and drive you back.",
        enemies=("bound_guardian",),
    ),
    Landmark(
        id="forgotten_grove", name="The Forgotten Grove", pos=(5, 7), biome="twilight",
        description=(
            "A grove where the shadows move with purpose. Something stands among the trees, "
            "tall and still and looking for you, and its gaze slides over you without catching. "
            "Beneath the largest tree lies a still black pool."
        ),
        enter_when=when(items="cloak_of_nyx", phases="night"),
        blocked_message=(
            "Even wrapped in the cloak, you'd be seen in this light. Something in the shadows is "
            "waiting for you to be careless."
        ),
        blocked_variants=(
            (when(not_items="cloak_of_nyx"),
             "Shadows thick as smoke swirl across the way. Something in them is watching, and "
             "it has already seen you. You back away."),
        ),
        enemies=("death_spirit",),
    ),
    Landmark(
        id="ixions_hold", name="Ixion's Hold", pos=(5, 9), biome="blight",
        description=(
            "A black fortress of iron and old stone. Over its gate hangs a great iron wheel, "
            "and the air smells of hot metal and frightened horses."
        ),
        enter_when=when(flags=("bridle_broken", "finale_written")),   # the finale isn't written yet
        blocked_message=(
            "Your legs refuse you. Every step north, something in your head hauls you around, "
            "like a rein you can't see."
        ),
        blocked_variants=(
            (when(flags="bridle_broken"),
             "The bridle on your mind is gone; you felt it break. But the Hold's gates are "
             "still shut, and what waits beyond them hasn't been written yet."),
        ),
    ),
]

LANDMARKS: Dict[str, Landmark] = {l.id: l for l in _LANDMARKS}
START_LANDMARK = "awakening_woods"
FALL_LANDMARK = "melias_grove"        # where you wake if you fall
FALL_MESSAGE = (
    "You wake to birdsong and grey dawn light. Someone has carried you to the ash grove. "
    "Melia says nothing, but there's a blanket of moss over your back."
)

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
        description=(
            "A war map on a fold of oiled hide, marked with faded ink. The marks look like your "
            "own hand."
        ),
    ),
    Item(
        id="crystal_focus", quest=True, name="Crystal Focus",
        description="A crystalline lens, cut and polished. It channels the energies of the land.",
        lore=(
            "Cut by the Oreads, the nymphs of the mountains, who could see what the stone was "
            "hiding. Within its facets you can see the ebb and flow of the land's power. Held up "
            "to sunlight in places of power, it is said to reveal what has been hidden."
        ),
        clue="focus_lore",
    ),
    Item(
        id="ash_spear", quest=True, name="Ash Spear",
        description=(
            "A long spear of pale ash with a bronze head, worn smooth where your hands go. It "
            "fits them as if it had never left."
        ),
        lore=(
            "Its shaft was cut from Melia's own tree, as the great spears always were. Below the "
            "head, in the runes of the Free Herds: \"Held by the Prime. Lowered for no one.\""
        ),
    ),
    Item(
        id="war_horn", quest=True, name="Horn of the Fallen",
        description=(
            "A battered war horn bound in bronze. Your Honor Guard sounded it to call the fallen "
            "back to the line, at the hour when the dead are closest."
        ),
        clue="horn_lore",
    ),
    Item(
        id="bronze_shield", quest=True, name="Bronze Shield",
        description=(
            "A great round shield faced with bronze, dented by a hundred blows. On its face, a "
            "centaur rears beneath a single star."
        ),
        lore=(
            "The emblem of the Free Herds: the centaur that never kneels, under the cold star "
            "that never moves."
        ),
    ),
    Item(
        id="cloak_of_nyx", quest=True, name="Cloak of Nyx",
        description="A cloak that seems to drink the light around it.",
        lore=(
            "Woven, the satyrs say, from the edge of Nyx's own robe: Night herself, whom even "
            "Zeus feared. In daylight it only blurs you; in true dark, the wearer all but "
            "disappears."
        ),
        clue="cloak_dark",
    ),
    Item(
        id="bronze_armor", quest=True, name="Bronze Armor",
        description=(
            "A centaur's war harness and cuirass of bronze, made for a chest broader than any "
            "man's. It's yours. It fits like a memory."
        ),
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
        defeat_requires=when(items="ash_spear"),
        on_defeat=Effects(message="The pack breaks and scatters into the trees. They won't be back."),
    ),
    Enemy(
        id="bound_guardian", name="Bound Guardian",
        description=(
            "A towering shape of shadow in the armour of a centaur Honor Guard. Across its face, "
            "where a mouth should be, lies the shadow of a golden bridle. It moves like a "
            "soldier who has been on watch for a very long time."
        ),
        health=150, damage=40,
        defeat_requires=when(items=("ash_spear", "bronze_shield")),
        yields=True,
        yielded_text="The Bound Guardian kneels before you, waiting.",
        on_defeat=Effects(
            message=(
                "Its blows ring off your shield, and the Ash Spear bites where nothing else "
                "could. The Bound Guardian staggers and falls to one knee. The shadow thins, and "
                "for a moment you see a centaur's face behind the golden bridle: tired, and very "
                "young. It bows its head and waits for the blow."
            ),
            flags=("yielded:bound_guardian",),
        ),
    ),
    Enemy(
        id="death_spirit", name="Ker",
        description=(
            "A Ker, one of the death-spirits of the old stories, bound by Ixion to guard this "
            "grove. It sees everything that the dark doesn't hide."
        ),
        health=80, damage=50,
        defeat_requires=when(items=("cloak_of_nyx", "ash_spear"), phases="night"),
        on_defeat=Effects(
            message=(
                "You come at it out of the dark it can't see into. The Ash Spear goes in without "
                "a sound, and the Ker is simply gone, like a candle pinched out. It never knew "
                "you were there. You tell yourself that makes it cleaner."
            ),
            memory="Here, unseen, you killed the Ker.",
            pride=1,
        ),
    ),
]
ENEMIES: Dict[str, Enemy] = {e.id: e for e in _ENEMIES}


# --------------------------------------------------------------------------
# NPCs
# --------------------------------------------------------------------------

_NPCS = [
    NPC(
        id="melia", name="Melia", at="melias_grove",
        description=(
            "The dryad of the eldest ash: grey-skinned, green-eyed, as patient as wood. She "
            "looks at you as if you were a branch she'd lost."
        ),
        lines=(
            Line(
                when(flags="memory_spear"),
                "Melia touches the spear's shaft, and for a moment her eyes close. \"Home,\" she "
                "says. \"For both of you.\" Then, harder: \"He took more than this. Some of it is "
                "in the hands of men now. Go and take it back.\"",
            ),
            Line(
                when(not_flags="met_melia"),
                "The bark shifts, and a woman steps out of the ash: grey-skinned, green-eyed. "
                "\"You've come back,\" Melia says. \"Not as you left.\" She studies you. \"You "
                "don't know me. You don't know yourself. My tree gave you your spear, centaur, "
                "and his servants took it from you.\" A long pause. \"What you lost still sings "
                "in the high places. Listen for it at first light.\"",
                Effects(flags=("met_melia",), clues=("melia_song",)),
            ),
            Line(
                when(items="crystal_focus"),
                "Melia's eyes go to the Focus. \"The Oreads cut that. It remembers the sun. So "
                "should you.\"",
                Effects(clues=("focus_sun",)),
            ),
            Line(
                ALWAYS,
                "\"The high places sing at first light,\" Melia says. \"Have you listened?\"",
                Effects(clues=("melia_song",)),
            ),
        ),
    ),
    NPC(
        id="caeneus", name="Caeneus", at="lapith_camp",
        description=(
            "A Lapith soldier, broad and weathered and grey at the temples, and not a single "
            "scar on him anywhere. He is very obviously not pleased to see you."
        ),
        lines=(
            Line(
                when(flags="killed_guardian"),
                "Caeneus looks at your spear, then at you, for a long moment. \"So you are what he "
                "says you are. A beast.\" He turns back to the cold fire. \"There's an old satyr "
                "who drinks at the crossroads when the day ends. He hates the Bridle-King more "
                "than I do. Go and find him. Maybe he'll see something in you that I can't.\"",
                Effects(clues=("silenus_dusk",)),
            ),
            Line(
                when(flags="spared_guardian"),
                "\"You let them go.\" Caeneus is quiet for a long while. \"You spared me too, on "
                "that field. I told myself it was contempt.\" He sets down the whetstone. "
                "\"There's an old satyr who drinks at the crossroads when the day ends. He hates "
                "the Bridle-King more than I do. Find him at dusk.\"",
                Effects(clues=("silenus_dusk",)),
            ),
            Line(
                when(items="bronze_shield", flags="caeneus_trust"),
                "Caeneus sees the shield on your arm and nods slowly. \"I carried that off the "
                "field. A Lapith can't hang a centaur's shield in his tent. So I gave it back to "
                "your dead.\"",
            ),
            Line(
                when(flags="caeneus_trust"),
                "\"From where the sun never reaches,\" Caeneus repeats, without looking up. \"Go.\"",
            ),
            Line(
                when(flags=("runes", "clue:standards_names")),
                "Caeneus watches you read the standards to the end, to the place where a name was "
                "cut away. \"So you remember,\" he says quietly. \"I took those from the field. I "
                "couldn't leave them in the mud.\" He looks north. \"Your old stronghold still "
                "stands, what's left of it. Enter it as your herd did, the night it fell: from "
                "where the sun never reaches.\"",
                Effects(flags=("caeneus_trust",), clues=("stronghold_north",)),
            ),
            Line(
                when(flags="runes"),
                "Caeneus's blade stops. \"You can read them now, can't you? Your runes.\" He nods "
                "at the standards. \"Then read those, and tell me you don't remember.\"",
            ),
            Line(
                ALWAYS,
                "Caeneus turns his back on you. \"I know what you are.\"",
            ),
        ),
    ),
    NPC(
        id="silenus", name="Silenus", at="crossroads",
        description=(
            "A fat old satyr with a white beard, goat legs and a wineskin, and eyes far sharper "
            "than the rest of him. He was here all along."
        ),
        present_when=when(flags="spirits_freed", phases="dusk"),
        lines=(
            Line(
                when(flags="bridle_broken"),
                "Silenus looks you up and down, armor and all, and for once doesn't drink. "
                "\"There he is. The Prime.\" He nods north. \"The Bridle-King is in his Hold. "
                "Go and do what Primes do.\"",
            ),
            Line(
                when(not_flags="met_silenus"),
                "An old satyr steps out of the dusk exactly where the hoofprints end, a wineskin "
                "in one hand. \"Ha! The Prime, on his own four feet. They said Ixion broke you.\" "
                "He drinks. \"Your bronze, your armor, he gave to a Ker to guard, in the grove "
                "where the shadows move. You'll never reach it seen. In the glade north of here "
                "hangs a cloak woven from Night herself. The glade will try to turn you around. "
                "Walk it like this: twice toward the cold star that never moves.\" He frowns into "
                "the wineskin. \"The rest... you knew the rest as a colt. You always carved "
                "everything. Look where the twilight lingers.\"",
                Effects(flags=("met_silenus",), clues=("silenus_way",)),
            ),
            Line(
                when(items="cloak_of_nyx"),
                "\"Nyx's own weaving,\" Silenus says of the cloak, impressed despite himself. "
                "\"The Ker sees everything but the dark. Go at night, and go wrapped.\"",
                Effects(clues=("grove_night",)),
            ),
            Line(
                ALWAYS,
                "\"Twice toward the cold star,\" Silenus repeats, and hiccups. \"The rest is in "
                "your own hand, in the twilight either side of the glade.\"",
                Effects(clues=("silenus_way",)),
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
            "Deep scratches, gouged in sets of four. Someone your size made these, not long "
            "ago. Someone with hooves and hands, who was very angry."
        ),
    ),
    # --- Melia's Grove ----------------------------------------------------------
    Feature(
        id="eldest_ash", name="the eldest ash", at="melias_grove",
        words=("ash", "tree", "bark", "eldest", "trunk"),
        description=(
            "The oldest ash you've ever seen. Low on its trunk is an old scar, smooth with "
            "years, where a long straight bough was once cut away."
        ),
    ),
    # --- Crossroads -----------------------------------------------------------
    Feature(
        id="standing_stone", name="the standing stone", at="crossroads",
        words=("stone", "runes", "standing", "rune"),
        description="A tall stone, crowded with runes worn almost smooth. To you they're just scratches.",
        visible_when=when(not_flags="runes"),
    ),
    Feature(
        id="standing_stone_read", name="the standing stone", at="crossroads",
        words=("stone", "runes", "standing", "rune"),
        description=(
            "The runes have rearranged themselves into sense: \"Here the herds parted, the free "
            "and the bridled. Here, one day, the free will run again.\""
        ),
        visible_when=when(flags="runes"),
    ),
    Feature(
        id="vanishing_hoofprints", name="the hoofprints", at="crossroads",
        words=("hoofprints", "prints", "tracks", "footprints", "dust", "cloven"),
        description=(
            "Small cloven prints, a goat's or something like one, walking on two legs. They "
            "walk up to the stone, take one more step, and end."
        ),
    ),
    # --- Lapith Camp ------------------------------------------------------------
    Feature(
        id="battle_standards", name="the battle standards", at="lapith_camp",
        words=("standards", "standard", "banners", "banner", "flags", "runes", "trophies"),
        description=(
            "Centaur standards, taken in war, faded grey, stitched with rows of runes you can't "
            "read. Someone has kept them clean."
        ),
        visible_when=when(not_flags="runes"),
    ),
    Feature(
        id="battle_standards_read", name="the battle standards", at="lapith_camp",
        words=("standards", "standard", "banners", "banner", "flags", "runes", "names", "trophies"),
        description=(
            "The runes are names: the Honor Guard of the Free Herds, rank by rank. Most are "
            "marked with the sign for the dead. One, near the bottom, carries a longer mark: "
            "\"Fell at the valley, guarding the way.\" At the very top, where the Prime's name "
            "would go, the cloth has been cut away."
        ),
        visible_when=when(flags="runes"),
        clue="standards_names",
    ),
    # --- Ruined Stronghold ------------------------------------------------------
    Feature(
        id="stone_bier", name="the stone bier", at="ruined_stronghold",
        words=("bier", "slab", "stone", "runes", "altar"),
        description=(
            "A long stone bier, where the Free Herds laid their dead before the pyre. Runes run "
            "around its edge: \"A Prime's strength is in the stopping of his spear.\""
        ),
        visible_when=when(flags="runes"),
        clue="strength_to_stop",
    ),
    # --- Warriors' Rest -------------------------------------------------------
    Feature(
        id="cairn", name="the cairn", at="warriors_rest",
        words=("cairn", "stones", "stone", "pile", "runes", "graves"),
        description="A cairn of stacked stones over the graves. Old runes on the top stone are dark and cold.",
        visible_when=when(not_items="ash_spear", not_flags="shield_found"),
    ),
    Feature(
        id="cairn_glowing", name="the glowing cairn", at="warriors_rest",
        words=("cairn", "stones", "stone", "pile", "runes", "glowing", "glow", "graves"),
        description=(
            "The runes on the cairn's top stone are glowing, a cold blue that pulses in time with "
            "something. It takes you a moment to realise it's the spear in your hand. Between "
            "the stones, something red and bronze catches the light."
        ),
        visible_when=when(items="ash_spear", not_flags="shield_found"),
    ),
    Feature(
        id="cairn_opened", name="the cairn", at="warriors_rest",
        words=("cairn", "stones", "stone", "pile", "runes", "graves"),
        description=(
            "The cairn, a few stones shifted where you took your shield. The runes are dark "
            "again. They're names, you realise: your Honor Guard, buried by a Lapith's hands."
        ),
        visible_when=when(flags="shield_found"),
    ),
    # --- Enchanted Valley, seen from beside it ---------------------------------
    Feature(
        id="valley_winds", name="the spectral winds", at="near:enchanted_valley",
        words=("winds", "wind", "valley", "mouth", "spirits", "spectral"),
        description=(
            "Out of the valley mouth comes a wind with no weather in it. It howls without "
            "moving the grass."
        ),
        visible_when=when(not_flags="valley_open", phases=("dawn", "day", "night")),
    ),
    Feature(
        id="valley_winds_dusk", name="the spectral winds", at="near:enchanted_valley",
        words=("winds", "wind", "valley", "mouth", "spirits", "spectral", "figures", "shapes"),
        description=(
            "Out of the valley mouth comes a wind with no weather in it. In the failing light it "
            "has shapes: centaurs in old armour, ranks of them, turning to look your way and "
            "coming apart again. The dead are close at dusk."
        ),
        visible_when=when(not_flags="valley_open", phases="dusk"),
        clue="dusk_winds",
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
            "A vast mural of a war between centaurs. The Free Herds charge across the rock "
            "beneath three banners: white at the front, amber behind it, and violet at the rear. "
            "At the head of the charge, under the white banner, rides a centaur with a long ash "
            "spear raised. You know those markings. They are yours.\n\nAcross from them stand "
            "centaurs in bits and bridles, men on their backs, and behind them a crowned "
            "centaur whose crown is a golden bridle."
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
        visible_when=when(flags="caves_open", not_flags="runes"),
    ),
    Feature(
        id="cave_runes", name="the runes", at="crystal_caves",
        words=("scratches", "scratch", "stone", "runes", "writing", "marks", "words"),
        description=(
            "\"The spear of the Prime. Sealed in stone by order of the Bridle-King, until the "
            "herds are no more.\" Below it, cut fresh and deep, in a hand you know is your own: "
            "\"Not yet.\""
        ),
        visible_when=when(flags="runes"),
    ),
    # --- Forgotten Grove ---------------------------------------------------
    Feature(
        id="hanging_armor", name="the armor", at="forgotten_grove",
        words=("armor", "armour", "bronze", "cuirass", "harness", "tree", "branch"),
        description=(
            "Hung from the largest tree like a trophy: a centaur's war harness and cuirass of "
            "bronze, dented and dark with old blood. Your hands know the buckles before your "
            "eyes do."
        ),
        visible_when=when(not_flags="armor_found"),
    ),
    Feature(
        id="still_pool", name="the still pool", at="forgotten_grove",
        words=("pool", "water", "reflection", "still", "black"),
        description="A still black pool beneath the largest tree. Not a ripple moves on it.",
        visible_when=when(not_flags="memory_armor"),
    ),
    Feature(
        id="still_pool_after", name="the still pool", at="forgotten_grove",
        words=("pool", "water", "reflection", "still", "black"),
        description="The pool shows you your own face now: the Prime's. It's enough.",
        visible_when=when(flags="memory_armor"),
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
                "Tangled in the roots, half buried, is a fold of oiled hide. A war map. The ink "
                "is faded, but the hand that drew it is unmistakably your own."
            ),
            give=("old_map",),
            memory="You pulled an old war map, in your own hand, from these roots.",
        ),
    ),
    Interaction(
        id="mountain_crystals_rooted", verbs=("take", "strike"), at="mystic_mountains",
        feature="mountain_crystals", once=False,
        effects=Effects(message=(
            "These crystals are rooted deep in the cliff, and they don't ring when you touch "
            "them. Whatever is singing up here, it isn't these."
        )),
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
        clues=("melia_song", "crystal_song", "crystal_dawn"),
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
    Interaction(
        id="find_shield", verbs=("examine", "take"), at="warriors_rest", feature="cairn_glowing",
        effects=Effects(
            message=(
                "You lift away the glowing stones. Beneath them, wrapped in a Lapith soldier's "
                "red cloak, is a great round shield faced with bronze: a centaur rearing beneath "
                "a single star. As your arm slides into its straps, the runes go dark.\n\nAnd you "
                "remember.\n\nThe last battle. The Free Herds and the Bridled, crashing together "
                "in the valley, and the Lapiths riding in behind. You remember the noise, and "
                "then the quiet. You remember walking the field at dusk, turning over every "
                "body, looking for one more centaur still breathing, and finding none. Not one, "
                "on either side. You walked off that field alone.\n\nYou are the last of them."
            ),
            give=("bronze_shield",),
            flags=("shield_found", "memory_shield"),
            memory="Here, among the graves of your Honor Guard, you took back your shield.",
        ),
        clues=("old_steel",),
    ),
    Interaction(
        id="open_valley", verbs=("blow", "use"), at="near:enchanted_valley",
        item="war_horn", words=("winds", "wind", "valley", "mouth", "spirits"),
        when=when(phases="dusk"),
        effects=Effects(
            message=(
                "You set the horn to your lips and blow. The note rolls down into the valley and "
                "the shapes in the wind stop. Then, rank by rank, they turn toward the sound, and "
                "the howling falls away into silence. The way into the valley is open."
            ),
            flags=("valley_open",),
            memory="At dusk you sounded the Horn of the Fallen here, and the dead let you pass.",
        ),
        otherwise=(
            "The horn's note rolls into the valley and is swallowed by the wind. Nothing answers. "
            "Perhaps the dead aren't listening at this hour."
        ),
        clues=("horn_lore", "dusk_winds", "dusk_echo"),
    ),
    Interaction(
        id="spare_guardian", verbs=("spare",), at="enchanted_valley",
        words=("guardian", "bound", "spirit", "spear", "weapon"), bare=True,
        when=when(flags="yielded:bound_guardian", not_flags="spirits_freed"),
        effects=Effects(
            message=(
                "You lower the Ash Spear. The Guardian looks up, not understanding. Then the "
                "golden bridle across its face cracks and falls away, and the shadow streams out "
                "of it like smoke. What is left is a young centaur in the colours of your Honor "
                "Guard. \"Prime,\" he says, wondering. \"You came back for us.\" He bows to you. "
                "All down the valley, the dead bow with him, and then they are gone, free."
            ),
            flags=("spirits_freed", "spared_guardian"),
            remove_enemies=("bound_guardian",),
            memory="Here you spared the Bound Guardian, and the dead of the valley went free.",
        ),
    ),
    Interaction(
        id="kill_guardian", verbs=("fight",), at="enchanted_valley",
        words=("guardian", "bound", "spirit"), bare=True,
        when=when(flags="yielded:bound_guardian", not_flags="spirits_freed"),
        effects=Effects(
            message=(
                "You drive the spear home. The Guardian comes apart like smoke in a high wind, "
                "without a sound, and the golden bridle falls into the grass and crumbles. The "
                "valley's dead are free; you feel them go. You tell yourself that's what this "
                "was. But something behind your ribs doesn't believe you."
            ),
            flags=("spirits_freed", "killed_guardian"),
            remove_enemies=("bound_guardian",),
            memory="Here you killed the Bound Guardian as it knelt, and the dead of the valley went free.",
            pride=1,
        ),
    ),
    Interaction(
        id="take_armor", verbs=("take", "use"), at="forgotten_grove", feature="hanging_armor",
        effects=Effects(
            message=(
                "You lift the bronze down from the tree and buckle it on, strap by strap, the way "
                "you have a thousand times. The weight settles across your back.\n\nAnd you "
                "remember everything.\n\nThe rumour, carried by frightened men: a centaur in the "
                "north, crowned with a golden bridle. Horses going missing. Foals. The ride north, "
                "alone, carving your marks as you went. The iron wheel over the gate. And him, "
                "waiting for you: Ixion, the Bridle-King, smiling, his hand raised, and the "
                "Lapith sorcery coming off it like heat.\n\nHe didn't kill you. He put a bridle "
                "on your mind and turned you loose, to wander without a name.\n\nYou know where "
                "he is now."
            ),
            give=("bronze_armor",),
            flags=("armor_found",),
            memory="Here you took your armor back from Ixion's tree, and remembered him.",
        ),
    ),
    Interaction(
        id="look_into_pool", verbs=("examine",), at="forgotten_grove", feature="still_pool",
        when=when(items="bronze_armor", phases="night"),
        effects=Effects(
            message=(
                "You lean over the pool. In the black water, for the first time since you woke, "
                "you see yourself as you are: the ash spear, the bronze shield with its rearing "
                "centaur, the armor of the Free Herds. Centaur Prime, who never knelt.\n\n"
                "Somewhere behind your eyes, something snaps like a rein cut through. The last of "
                "the bridle on your mind is broken."
            ),
            flags=("memory_armor",),
            memory="Here, in the still pool, you saw yourself as you are: Centaur Prime.",
        ),
        otherwise=(
            "A stranger looks back at you from the black water: a centaur with no armor and no "
            "name, and a hard, lost look in his eyes."
        ),
    ),
]
INTERACTIONS: Dict[str, Interaction] = {i.id: i for i in _INTERACTIONS}

_SEQUENCES = [
    Sequence(
        id="spear_chord", at="crystal_caves", verb="strike",
        steps=("white_crystal", "amber_crystal", "violet_crystal"),
        notes={
            "white_crystal": "The white crystal sings a high, clear note.",
            "amber_crystal": "The amber crystal answers with a warm, middle note.",
            "violet_crystal": "The violet crystal gives a low note you feel in your chest.",
        },
        when=when(flags="caves_open", not_flags="memory_spear"),
        success=Effects(
            message=(
                "The three notes hang in the air and braid together into a chord. The mural "
                "blazes with light, and the cave floor splits along an old seam. Laid in the rock "
                "beneath it is a long spear of pale ash with a bronze head. Your hand closes on "
                "it before you think.\n\nAnd you remember.\n\nThousands of hooves behind you. A "
                "battle cry in your own voice. The Free Herds, running under the white banner, "
                "and you at their head. You led them.\n\nYour eyes ache, then clear. The "
                "scratches beside the mural are no longer scratches. They are the runes of the "
                "Free Herds, and you can read them."
            ),
            give=("ash_spear",),
            flags=("memory_spear", "runes"),
            memory="Here you struck the chord, and took back your spear.",
        ),
        failure=(
            "Discord shrieks through the cave and the crystals go dark for a moment. Whatever "
            "you started, you'll have to start again."
        ),
        clues=("mural_order",),
    ),
]
SEQUENCES: Dict[str, Sequence] = {s.id: s for s in _SEQUENCES}

_MAZES = [
    Maze(
        id="twilight_glade", at="twilight_glade",
        path=("north", "north", "west", "north"),
        step_text="You push on. The pale trees close in behind you, and everything ahead looks the same.",
        failure=(
            "The trees turn you gently around. A few steps later you walk out of the twilight "
            "exactly where you walked in."
        ),
        success=Effects(
            message=(
                "One last step, and the trees open onto a ring of soft grass at the heart of the "
                "glade. Hanging from a low branch, as if left for you, is a cloak that drinks in "
                "the light. You take down the Cloak of Nyx."
            ),
            give=("cloak_of_nyx",),
            memory="You found your way to the heart of the glade, and the Cloak of Nyx.",
        ),
        solved_flag="glade_solved",
        clues=("silenus_way", "glade_sunset", "glade_last"),
    ),
]
MAZES: Dict[str, Maze] = {m.id: m for m in _MAZES}

# Flags that follow from other flags, whatever order they were earned in.
DERIVED = [
    (when(flags=("memory_spear", "memory_shield", "memory_armor")), "bridle_broken"),
]


# --------------------------------------------------------------------------
# Echoes, signals, hazards
# --------------------------------------------------------------------------

def carved(text: str) -> str:
    return f'Carved here, in your hand: "{text}"'


# Marks you cut on your ride north to Ixion, before he took your memory.
ECHOES = [
    Echo(at=(5, 0), text=carved("Ixion lives. I ride north to end it.")),
    Echo(at=(5, 3), text=carved("If I don't come back, look for what I carried: the ash, the bronze, the shield.")),
    Echo(at=(1, 4), text=carved("The stones only sing for the early riser."), clue="crystal_dawn"),
    Echo(at=(2, 6), text=carved("Sunlight, not torchlight. The Focus remembers the sun."), clue="sunlight_echo"),
    Echo(at=(8, 5), text=carved("The old spear wakes the old stones."), clue="old_steel"),
    Echo(at=(6, 6), text=carved("The dead walk at dusk. Even the ones who keep the gates."), clue="dusk_echo"),
    Echo(at=(3, 5), text=carved("The glade, the way I learned it as a colt: after the cold star twice, once toward sunset."), clue="glade_sunset"),
    Echo(at=(5, 5), text=carved("And after sunset, the cold star one last time. Then you're through."), clue="glade_last"),
    Echo(at=(5, 6), text=carved("Night and the cloak. Never one without the other."), clue="grove_night"),
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
        enemy="wolf_pack",
    ),
    Hazard(
        at="forgotten_grove", when=when(phases=("dawn", "day", "dusk")), damage=50,
        message=(
            "The light finds you, and so does the Ker. Something cold passes through your side. "
            "(-50 health)"
        ),
        enemy="death_spirit",
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
    for enemy in ENEMIES.values():
        flags_set.update(enemy.on_defeat.flags)
    for maze in MAZES.values():
        flags_set.update(maze.success.flags + (maze.solved_flag,))
    flags_set.update(flag for _, flag in DERIVED)

    def check_place(where: str, place: Place) -> None:
        if isinstance(place, str):
            if place.startswith("near:"):
                place = place[len("near:"):]
            if place not in LANDMARKS:
                problems.append(f"{where}: unknown landmark '{place}'")
        elif not (0 <= place[0] < GRID_SIZE and 0 <= place[1] < GRID_SIZE):
            problems.append(f"{where}: position {place} is off the map")

    def check_items(where: str, item_ids) -> None:
        for item_id in item_ids:
            if item_id not in ITEMS:
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
    for hazard in HAZARDS:
        check_place("hazard", hazard.at)
        if hazard.enemy and hazard.enemy not in ENEMIES:
            problems.append(f"hazard at {hazard.at}: unknown enemy '{hazard.enemy}'")

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

    for maze in MAZES.values():
        where = f"maze {maze.id}"
        check_place(where, maze.at)
        check_items(where, maze.success.give)
        if not maze.clues:
            problems.append(f"{where}: has no clues pointing to the path")
        for clue in maze.clues:
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
