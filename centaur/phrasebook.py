"""
The phrasebook: how The Last Centaur understands what the player typed.

interpret("I'd like to carefully rip out the crystal") -> Parsed("take", ["crystal"])

Everything here works offline and instantly. It maps phrasings onto the
engine's verbs at the *verb* level ("yank" means take), so it covers every
object in the game at once; the engine works out which object was meant.
Words the LLM interpreter learns later can be added to these tables.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

DIRECTION_ALIASES = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "north": "north", "south": "south", "east": "east", "west": "west",
    "northward": "north", "southward": "south", "eastward": "east", "westward": "west",
    "northwards": "north", "southwards": "south", "eastwards": "east", "westwards": "west",
}
DIRECTION_WORDS = {w for w in DIRECTION_ALIASES if len(w) > 1}   # single letters only count on their own

# The engine's verbs, and every word that means each one.
VERBS = {
    "look": ("look", "l", "survey"),
    "examine": (
        "examine", "x", "inspect", "search", "study", "check", "feel", "dig", "listen", "observe",
        "investigate", "scan", "peer", "smell", "sniff", "touch", "probe", "poke", "rummage",
        "explore", "view", "watch", "eye", "regard", "admire", "contemplate",
    ),
    "read": ("read", "decipher", "translate"),
    "take": (
        "take", "get", "grab", "pick", "pull", "loosen", "free", "yank", "rip", "pluck", "snatch",
        "collect", "gather", "fetch", "seize", "grasp", "wrench", "pry", "prise", "tear", "harvest",
        "scoop", "acquire", "obtain", "steal", "swipe", "nab", "claim", "retrieve", "unearth",
        "work",                                                  # "work the crystal loose"
    ),
    "use": ("use", "raise", "hold", "lift", "show", "point", "shine", "brandish", "aim",
            "present", "wield", "wear", "don"),
    "strike": ("strike", "hit", "tap", "ring", "knock", "kick", "smack", "bang", "thump", "whack",
               "chime", "ding", "bash"),
    "go": (
        "go", "move", "walk", "run", "head", "travel", "skip", "gallop", "trot", "canter", "wander",
        "stroll", "hike", "ride", "dash", "sprint", "hurry", "hop", "jog", "step", "proceed",
        "continue", "venture", "advance", "march", "amble", "roam", "trek", "journey", "turn",
        "race", "bolt", "flee", "retreat",
    ),
    "drop": ("drop", "leave", "discard", "abandon", "ditch"),
    "talk": ("talk", "speak", "ask", "greet", "chat", "converse", "address", "hail", "question",
             "consult", "hello", "hi", "hey"),
    "fight": ("fight", "attack", "kill", "slay", "finish", "battle", "engage", "charge", "stab",
              "slash", "assault", "murder", "execute", "destroy", "smite"),
    "spare": ("spare", "mercy", "forgive", "release", "sheathe", "lower", "stop", "relent", "pardon",
              "absolve", "withdraw"),
    "blow": ("blow", "sound", "play", "toot", "trumpet"),
    "inventory": ("inventory", "inv", "i", "items", "bag", "pack", "belongings"),
    "status": ("status", "stats", "health"),
    "map": ("map", "m"),
    "carve": ("carve", "write", "mark", "scratch", "engrave", "etch", "inscribe"),
    "rest": ("rest", "sleep", "nap", "doze"),
    "wait": ("wait", "z", "pause", "linger", "loiter", "idle"),
    "help": ("help", "h", "?", "commands"),
}
VERB_LOOKUP = {alias: verb for verb, aliases in VERBS.items() for alias in aliases}

# Multi-word verbs, checked before single words. Longest match wins.
PHRASES = {
    ("pick", "up"): "take",
    ("dig", "up"): "take",
    ("pull", "out"): "take",
    ("rip", "out"): "take",
    ("tear", "out"): "take",
    ("pry", "out"): "take",
    ("pry", "loose"): "take",
    ("prise", "out"): "take",
    ("look", "around"): "look",
    ("look", "about"): "look",
    ("have", "a", "look", "around"): "look",
    ("have", "a", "look", "at"): "examine",
    ("take", "a", "look", "at"): "examine",
    ("take", "a", "look", "around"): "look",
    ("check", "out"): "examine",
    ("peer", "into"): "examine",
    ("peer", "through"): "use",
    ("hold", "up"): "use",
    ("put", "on"): "use",
    ("strap", "on"): "use",
    ("put", "down"): "drop",
    ("set", "down"): "drop",
    ("let", "go", "of"): "drop",
    ("let", "him", "go"): "spare",
    ("let", "it", "go"): "spare",
    ("let", "them", "go"): "spare",
    ("let", "her", "go"): "spare",
    ("put", "away"): "spare",
    ("stand", "down"): "spare",
    ("show", "mercy"): "spare",
    ("have", "mercy"): "spare",
    ("say", "hello"): "talk",
    ("go", "to", "sleep"): "rest",
    ("lie", "down"): "rest",
    ("lay", "down"): "rest",
    ("make", "camp"): "rest",
    ("blow", "into"): "blow",
}

# Words that carry no meaning at the start of a command ("I want to ...").
FILLER_PREFIXES = sorted([
    ("i", "want", "to"), ("i", "would", "like", "to"), ("i'd", "like", "to"), ("i", "will"), ("i'll",),
    ("i", "try", "to"), ("i", "try"), ("try", "to"), ("attempt", "to"), ("let", "me"), ("let's",),
    ("i", "am", "going", "to"), ("i'm", "going", "to"), ("going", "to"), ("can", "i"), ("could", "i"),
    ("may", "i"), ("please",), ("go", "ahead", "and"), ("now",), ("then",), ("and",), ("i",),
    ("centaur",), ("you",),
], key=len, reverse=True)

ADVERBS = {
    "quickly", "slowly", "carefully", "gently", "quietly", "softly", "firmly", "hard", "just",
    "really", "also", "again", "briefly", "boldly", "cautiously", "loudly", "silently",
    "swiftly", "calmly", "bravely", "please", "very", "now",
}

STOPWORDS = {
    "the", "a", "an", "to", "with", "at", "on", "up", "of", "my", "it", "in", "from", "around",
    "for", "him", "her", "them", "into", "toward", "towards", "out", "off", "loose", "away", "some",
    "that", "this", "those", "these", "its", "his", "their", "your", "me", "over", "by", "onto",
    "inside", "there", "here", "down", "across", "through", "upon", "all", "any",
}

# Harmless things a centaur can do. They take no time and change nothing.
FLAVOR = {
    "dance": "You dance a few steps",
    "sing": "You sing a few bars",
    "laugh": "You laugh",
    "cry": "You let yourself cry for a moment",
    "weep": "You let yourself weep for a moment",
    "jump": "You jump",
    "leap": "You leap",
    "rear": "You rear up on your hind legs",
    "buck": "You buck and kick at the air",
    "prance": "You prance in place",
    "stamp": "You stamp a hoof",
    "stomp": "You stamp a hoof",
    "shout": "You shout",
    "yell": "You yell",
    "scream": "You scream",
    "howl": "You howl",
    "roar": "You roar",
    "whistle": "You whistle",
    "hum": "You hum",
    "pray": "You pray",
    "meditate": "You sit with your thoughts",
    "kneel": "You kneel",
    "bow": "You bow",
    "nod": "You nod",
    "sit": "You fold your legs and sit",
    "stretch": "You stretch",
    "yawn": "You yawn",
    "sigh": "You sigh",
    "smile": "You smile",
    "frown": "You frown",
    "clap": "You clap",
    "think": "You think",
    "ponder": "You ponder",
    "relax": "You relax",
    "breathe": "You breathe deeply",
    "shake": "You shake yourself off",
    "whinny": "You let out a whinny",
    "neigh": "You let out a whinny",
    "snort": "You snort",
    "graze": "You crop at the grass",
    "spin": "You turn in a circle",
    "twirl": "You turn in a circle",
    "cheer": "You cheer",
    "curse": "You curse",
    "swear": "You swear under your breath",
    "hug": "You wrap your arms around yourself",
    "wave": "You wave",
    "salute": "You salute",
    "flex": "You flex",
    "swish": "You swish your tail",
}


@dataclass
class Parsed:
    verb: str                      # an engine verb, or "go", "flavor", "listen", "unknown", "empty"
    args: List[str] = field(default_factory=list)
    message: str = ""              # carve: the player's own words; flavor: the line to show

    def as_tuple(self) -> Tuple[str, Tuple[str, ...]]:
        return self.verb, tuple(self.args)


def interpret(text: str) -> Parsed:
    raw_words = re.findall(r"[a-z0-9'?]+", text.lower())
    words = _strip_fillers(raw_words)
    words = [w for w in words if w not in ADVERBS]
    if not words:
        return Parsed("empty")

    # A bare direction, or a direction anywhere in a sentence about moving
    if len(words) == 1 and words[0] in DIRECTION_ALIASES:
        return Parsed("go", [DIRECTION_ALIASES[words[0]]])

    verb, rest = _match_verb(words)
    first = words[0]

    if verb == "look" and rest:
        # "look at X" examines; "look through X" uses it; "look into X" examines
        verb = "use" if rest[0] == "through" else "examine"
    if verb == "examine" and first == "listen" and not rest:
        return Parsed("listen")

    direction = next((DIRECTION_ALIASES[w] for w in (rest if verb else words) if w in DIRECTION_WORDS), None)
    if direction and verb in (None, "go"):
        return Parsed("go", [direction])

    if verb is None:
        if first in FLAVOR:
            return Parsed("flavor", [first], f"{FLAVOR[first]}. Nothing happens.")
        return Parsed("unknown", [first])

    if verb == "carve":
        return Parsed("carve", [], _words_after(text, first))

    args = [w for w in rest if w not in STOPWORDS]
    if verb == "go":
        return Parsed("go", [])           # moving, but no direction given
    return Parsed(verb, args)


def _strip_fillers(words: List[str]) -> List[str]:
    i = 0
    stripped = True
    while stripped and i < len(words):
        stripped = False
        for prefix in FILLER_PREFIXES:
            if tuple(words[i:i + len(prefix)]) == prefix and i + len(prefix) < len(words):
                i += len(prefix)
                stripped = True
                break
    return words[i:]


def _match_verb(words: List[str]) -> Tuple[Optional[str], List[str]]:
    for length in range(min(4, len(words)), 1, -1):
        verb = PHRASES.get(tuple(words[:length]))
        if verb:
            return verb, words[length:]
    return VERB_LOOKUP.get(words[0]), words[1:]


def _words_after(text: str, word: str) -> str:
    """The player's own text after `word`, with original capitalisation."""
    match = re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE)
    return text[match.end():].strip() if match else ""
