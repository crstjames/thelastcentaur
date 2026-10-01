"""
The game loop for The Last Centaur.

    game = Game.new(seed=7)
    print(game.do("look"))
    print(game.do("talk to the hermit"))

Game.do() takes one line of player input and returns the text response. All
state lives on the Game object and round-trips through to_dict()/from_dict(),
so saving is just writing JSON.

There is no class selection: your path is whatever your gear says it is. The
Shadow Centaur can be beaten with any one of the three paths' item sets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

from centaur import content
from centaur.content import ENEMIES, ITEMS, LANDMARKS, NPCS, PATHS, is_met
from centaur.worldgen import BIOME_GLYPHS, DIRECTIONS, Pos, Tile, World, generate

MAX_HEALTH = 100
MEMORY_SHOWN = 3

DIRECTION_ALIASES = {"n": "north", "s": "south", "e": "east", "w": "west"}
DIRECTION_ALIASES.update({d: d for d in DIRECTIONS})

STOPWORDS = {"the", "a", "an", "to", "with", "at", "on", "up", "of", "my"}

VERBS = {
    "look": ("look", "l"),
    "go": ("go", "move", "walk", "run", "head", "travel"),
    "take": ("take", "get", "grab", "pick"),
    "drop": ("drop", "leave"),
    "talk": ("talk", "speak", "ask", "greet"),
    "fight": ("fight", "attack", "kill", "strike"),
    "examine": ("examine", "x", "read", "inspect", "study"),
    "inventory": ("inventory", "inv", "i"),
    "status": ("status", "stats", "health"),
    "map": ("map", "m"),
    "carve": ("carve", "write", "mark", "scratch"),
    "rest": ("rest", "sleep", "wait"),
    "help": ("help", "h", "?"),
}
VERB_LOOKUP = {alias: verb for verb, aliases in VERBS.items() for alias in aliases}

HELP_TEXT = """\
Commands:
  look                    describe where you are
  n / s / e / w           move (or: go north)
  take <item>             pick something up
  drop <item>             leave something here
  examine <item>          look closely at something (also: read)
  talk <someone>          speak with someone here
  fight <enemy>           fight an enemy here
  carve <words>           leave a message on this spot
  rest                    recover your strength (only where it's safe)
  inventory / status / map / help"""


@dataclass
class Game:
    world: World
    position: Pos
    inventory: List[str] = field(default_factory=list)
    health: int = MAX_HEALTH
    turn: int = 0
    met: Set[str] = field(default_factory=set)        # NPCs who've already given their gift
    defeated: Set[str] = field(default_factory=set)   # unique (boss) enemies defeated
    won_path: Optional[str] = None

    # ------------------------------------------------------------------
    # Construction and persistence
    # ------------------------------------------------------------------

    @classmethod
    def new(cls, seed: int) -> "Game":
        world = generate(seed)
        game = cls(world=world, position=world.start)
        game._arrive()
        return game

    def to_dict(self) -> dict:
        return {
            "world": self.world.to_dict(),
            "position": list(self.position),
            "inventory": list(self.inventory),
            "health": self.health,
            "turn": self.turn,
            "met": sorted(self.met),
            "defeated": sorted(self.defeated),
            "won_path": self.won_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Game":
        return cls(
            world=World.from_dict(data["world"]),
            position=tuple(data["position"]),
            inventory=list(data["inventory"]),
            health=data["health"],
            turn=data["turn"],
            met=set(data["met"]),
            defeated=set(data["defeated"]),
            won_path=data["won_path"],
        )

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    @property
    def over(self) -> bool:
        return self.won_path is not None

    @property
    def tile(self) -> Tile:
        return self.world.tiles[self.position]

    def do(self, text: str) -> str:
        words = re.findall(r"[a-z0-9'?]+", text.lower())
        if not words:
            return "Say something, or type 'help'."
        if self.over:
            return "Your story is told. Start a new game to play again."

        first, rest = words[0], words[1:]
        if first in DIRECTION_ALIASES:
            return self._go(DIRECTION_ALIASES[first])
        verb = VERB_LOOKUP.get(first)
        if verb is None:
            return f"You don't know how to '{first}'. Type 'help' for commands."

        if verb == "carve":
            # keep the player's own words, minus the verb
            message = text.strip().split(None, 1)[1] if len(text.split()) > 1 else ""
            return self._carve(message)

        args = [w for w in rest if w not in STOPWORDS]
        handler = getattr(self, f"_{verb}")
        return handler(args) if verb != "go" else self._go_words(args)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def _look(self, args: Sequence[str] = ()) -> str:
        if args:
            return self._examine(args)
        return self.describe()

    def _go_words(self, args: Sequence[str]) -> str:
        if not args or args[0] not in DIRECTION_ALIASES:
            return "Go where? North, south, east or west."
        return self._go(DIRECTION_ALIASES[args[0]])

    def _go(self, direction: str) -> str:
        target = self.world.neighbors(self.position).get(direction)
        if target is None:
            return "The land ends there. You can't go that way."
        if not self.world.can_enter(target, self.inventory):
            landmark = LANDMARKS[self.world.tiles[target].landmark]
            return f"{landmark.name}: {landmark.blocked_message}"
        self.position = target
        self.turn += 1
        self._arrive()
        return self.describe()

    def _take(self, args: Sequence[str]) -> str:
        if not args:
            return "Take what?"
        item_id = _match(args, self.tile.items, ITEMS)
        if item_id is None:
            return "You don't see that here."
        item = ITEMS[item_id]
        if not is_met(item.take_requires, self.inventory):
            return item.hidden_message or "You can't reach it."
        self.tile.items.remove(item_id)
        self.inventory.append(item_id)
        self.turn += 1
        self._remember(f"You took the {item.name} from here.")
        return f"You take the {item.name}. {item.description}"

    def _drop(self, args: Sequence[str]) -> str:
        item_id = _match(args, self.inventory, ITEMS)
        if item_id is None:
            return "You aren't carrying that."
        self.inventory.remove(item_id)
        self.tile.items.append(item_id)
        self.turn += 1
        name = ITEMS[item_id].name
        self._remember(f"You left the {name} here.")
        return f"You set down the {name}."

    def _examine(self, args: Sequence[str]) -> str:
        if not args:
            return self.describe()
        item_id = _match(args, self.inventory + self.tile.items, ITEMS)
        if item_id is not None:
            item = ITEMS[item_id]
            text = f"{item.name}: {item.description}"
            return f"{text}\n\n{item.lore}" if item.lore else text
        npc_id = _match(args, self.tile.npcs, NPCS)
        if npc_id is not None:
            npc = NPCS[npc_id]
            return f"{npc.name}: {npc.description}"
        enemy_id = _match(args, self._enemies_here(), ENEMIES)
        if enemy_id is not None:
            enemy = ENEMIES[enemy_id]
            return " ".join(filter(None, [f"{enemy.name}: {enemy.description}", enemy.behavior]))
        if self.tile.landmark and set(args) & {"area", "here", "around", "place"}:
            landmark = LANDMARKS[self.tile.landmark]
            return landmark.history or landmark.description
        return "You don't see that here."

    def _talk(self, args: Sequence[str]) -> str:
        if not self.tile.npcs:
            return "There's no one here to talk to."
        npc_id = _match(args, self.tile.npcs, NPCS) if args else self.tile.npcs[0]
        if npc_id is None:
            return "They aren't here."
        npc = NPCS[npc_id]
        self.turn += 1
        if npc_id not in self.met:
            self.met.add(npc_id)
            self.inventory.extend(i for i in npc.gives if i not in self.inventory)
            self._remember(f"You spoke with {npc.name} here for the first time.")
            gifts = ", ".join(ITEMS[i].name for i in npc.gives)
            lines = [f'{npc.name}: "{npc.dialogue["greeting"]}"', f'"{npc.dialogue["gift"]}"']
            if gifts:
                lines.append(f"You receive: {gifts}.")
            return "\n".join(lines)
        if self._holds_domain_key():
            return f'{npc.name}: "{npc.dialogue["pre_final"]}"'
        return f'{npc.name}: "{npc.dialogue["after"]}"'

    def _fight(self, args: Sequence[str]) -> str:
        enemies = self._enemies_here()
        if not enemies:
            return "There's nothing here to fight."
        enemy_id = _match(args, enemies, ENEMIES) if args else enemies[0]
        if enemy_id is None:
            return "That enemy isn't here."
        enemy = ENEMIES[enemy_id]
        self.turn += 1

        if not is_met(enemy.defeat_requires, self.inventory):
            self.health -= enemy.damage
            if self.health <= 0:
                return self._fall(enemy)
            return (
                f"You charge the {enemy.name}, but nothing you have can truly harm it. "
                f"It drives you back. (-{enemy.damage} health, {self.health} left)"
            )

        cost = enemy.damage // 2
        self.health -= cost
        if self.health <= 0:
            return self._fall(enemy)
        self.tile.enemies.remove(enemy_id)
        if enemy.boss:
            self.defeated.add(enemy_id)
        drops = [i for i in enemy.drops if i not in self.inventory]
        self.inventory.extend(drops)
        self._remember(f"You defeated the {enemy.name} here.")
        lines = [f"You defeat the {enemy.name}. (-{cost} health, {self.health} left)"]
        if drops:
            lines.append("You claim: " + ", ".join(ITEMS[i].name for i in drops) + ".")
        if enemy_id == content.FINAL_BOSS:
            lines.append(self._victory())
        return "\n".join(lines)

    def _carve(self, message: str) -> str:
        message = message.strip()
        if not message:
            return "Carve what?"
        self.turn += 1
        self._remember(f'Carved here, in your hand: "{message}"')
        return "You carve your words where the next traveler will find them."

    def _rest(self, args: Sequence[str] = ()) -> str:
        if self._enemies_here():
            return "You can't rest with enemies nearby."
        self.turn += 1
        self.health = MAX_HEALTH
        return "You rest until your strength returns."

    def _inventory(self, args: Sequence[str] = ()) -> str:
        if not self.inventory:
            return "You carry nothing."
        return "You carry:\n" + "\n".join(f"  {ITEMS[i].name}" for i in self.inventory)

    def _status(self, args: Sequence[str] = ()) -> str:
        lines = [f"Health {self.health}/{MAX_HEALTH}   Turn {self.turn}   At {self.tile.name}"]
        for path in PATHS:
            held = [ITEMS[i].name for i in self.inventory if ITEMS[i].path == path]
            if held:
                lines.append(f"  {path.title()}: {', '.join(held)}")
        return "\n".join(lines)

    def _map(self, args: Sequence[str] = ()) -> str:
        knows_land = "old_map" in self.inventory
        rows = []
        for y in reversed(range(self.world.size)):
            row = []
            for x in range(self.world.size):
                tile = self.world.tiles[(x, y)]
                if (x, y) == self.position:
                    row.append("@")
                elif tile.landmark and (tile.visited or knows_land):
                    row.append("*")
                elif tile.visited or knows_land:
                    row.append(BIOME_GLYPHS.get(tile.biome, "?"))
                else:
                    row.append(" ")
            rows.append(" ".join(row))
        legend = "@ you   * landmark"
        if not knows_land:
            legend += "   (only places you've been -- a map would show more)"
        return "\n".join(rows) + "\n" + legend

    def _help(self, args: Sequence[str] = ()) -> str:
        return HELP_TEXT

    # ------------------------------------------------------------------
    # Description
    # ------------------------------------------------------------------

    def describe(self) -> str:
        tile = self.tile
        lines = [tile.name, tile.description]

        memories = [m for m in tile.memory if not m.startswith("You first came here")]
        if memories:
            lines.append("")
            lines.append("You remember: " + " ".join(memories[-MEMORY_SHOWN:]))

        lines.append("")
        if tile.npcs:
            lines.append("Here: " + ", ".join(NPCS[n].name for n in tile.npcs) + ".")
        enemies = self._enemies_here()
        if enemies:
            lines.append("Danger: " + ", ".join(ENEMIES[e].name for e in enemies) + ".")
        if tile.items:
            lines.append("You see: " + ", ".join(ITEMS[i].name for i in tile.items) + ".")

        exits = []
        for direction, pos in self.world.neighbors(self.position).items():
            neighbor = self.world.tiles[pos]
            label = neighbor.name
            if not self.world.can_enter(pos, self.inventory):
                label += " (barred)"
            exits.append(f"{direction}: {label}")
        lines.append("Exits -- " + "; ".join(exits))
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _arrive(self) -> None:
        if not self.tile.visited:
            self.tile.visited = True
            self._remember(f"You first came here on turn {self.turn}.")

    def _remember(self, text: str) -> None:
        self.tile.memory.append(text)

    def _enemies_here(self) -> List[str]:
        # No day/night cycle yet, so night-only enemies stay hidden.
        return [e for e in self.tile.enemies if not ENEMIES[e].night_only]

    def _holds_domain_key(self) -> bool:
        return is_met(LANDMARKS["shadow_domain"].enter_requires, self.inventory)

    def _fall(self, enemy) -> str:
        self._remember(f"You fell here, fighting the {enemy.name}.")
        self.health = MAX_HEALTH
        self.position = self.world.start
        return (
            f"The {enemy.name} overwhelms you. Darkness...\n\n"
            "You wake among the roots of the Awakening Woods, aching but whole.\n\n"
            + self.describe()
        )

    def _victory(self) -> str:
        options = ENEMIES[content.FINAL_BOSS].defeat_requires
        for option in options:
            if set(option) <= set(self.inventory):
                paths = {ITEMS[i].path for i in option}
                self.won_path = paths.pop() if len(paths) == 1 else "unknown"
                break
        else:
            self.won_path = "unknown"
        return (
            f"\nThe Shadow Centaur falls. The barrier that bound you shatters, and your "
            f"power floods back.\nYou won by the {self.won_path} path in {self.turn} turns."
        )


def _match(words: Sequence[str], candidates: Sequence[str], catalog: Dict) -> Optional[str]:
    """Find the candidate whose id or name contains every word the player typed."""
    wanted = [w.replace("'s", "") for w in words]
    for candidate in candidates:
        entry = catalog[candidate]
        vocabulary = set(re.findall(r"[a-z0-9]+", f"{candidate} {entry.name}".lower().replace("'s", "")))
        if all(_word_forms(w) & vocabulary for w in wanted):
            return candidate
    return None


def _word_forms(word: str) -> Set[str]:
    """The word plus naive singulars, so 'wolves' finds 'wolf' and 'hounds' finds 'hound'."""
    forms = {word}
    if word.endswith("ves"):
        forms.add(word[:-3] + "f")
    if word.endswith("es"):
        forms.add(word[:-2])
    if word.endswith("s"):
        forms.add(word[:-1])
    return forms
