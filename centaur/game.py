"""
The game loop for The Last Centaur.

    game = Game.new()
    print(game.do("look"))
    print(game.do("examine the roots"))

Game.do() takes one line of player input and returns the text response. All
state lives on the Game object and round-trips through to_dict()/from_dict().

The engine is generic: it evaluates content.Conditions and applies
content.Effects. Nothing here knows about crystals or wolves.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set

from centaur import content
from centaur.content import (
    DERIVED, ECHOES, ENEMIES, FEATURES, HAZARDS, INTERACTIONS, ITEMS, LANDMARKS, MAZES, NPCS,
    PHASES, PHASE_TURNS, SEQUENCES, SIGNALS, Effects, Place, Pos, is_met,
)
from centaur.worldgen import BIOME_GLYPHS, DIRECTIONS, Tile, World, build_world

MAX_HEALTH = 100
MEMORY_SHOWN = 4

DIRECTION_ALIASES = {"n": "north", "s": "south", "e": "east", "w": "west"}
DIRECTION_ALIASES.update({d: d for d in DIRECTIONS})

STOPWORDS = {"the", "a", "an", "to", "with", "at", "on", "up", "of", "my", "it", "in", "from", "around", "for",
             "him", "her", "them", "into", "toward", "towards"}

VERBS = {
    "look": ("look", "l"),
    "examine": ("examine", "x", "inspect", "search", "study", "check", "feel", "dig", "listen"),
    "read": ("read",),
    "take": ("take", "get", "grab", "pick", "pull", "loosen", "free"),
    "use": ("use", "raise", "hold", "lift", "show", "point", "shine", "wave"),
    "strike": ("strike", "hit", "tap", "ring", "knock", "kick"),
    "go": ("go", "move", "walk", "run", "head", "travel"),
    "drop": ("drop", "leave"),
    "talk": ("talk", "speak", "ask", "greet"),
    "fight": ("fight", "attack", "kill", "slay", "finish"),
    "spare": ("spare", "mercy", "forgive", "release", "sheathe", "lower"),
    "blow": ("blow", "sound", "play", "toot"),
    "inventory": ("inventory", "inv", "i"),
    "status": ("status", "stats", "health"),
    "map": ("map", "m"),
    "carve": ("carve", "write", "mark", "scratch"),
    "rest": ("rest", "sleep"),
    "wait": ("wait", "z"),
    "help": ("help", "h", "?"),
}
VERB_LOOKUP = {alias: verb for verb, aliases in VERBS.items() for alias in aliases}

# Actions that let time pass. Looking and examining are free.
TIMED_VERBS = {"take", "use", "strike", "go", "drop", "talk", "fight", "carve", "spare", "blow"}

PHASE_LINES = {
    "dawn": "Pale light is creeping up from the east.",
    "day": "",
    "dusk": "The light is going long and amber.",
    "night": "It is dark.",
}
PHASE_CHANGES = {
    "dawn": "The sky greys, then pales. Dawn.",
    "day": "The sun clears the horizon.",
    "dusk": "The shadows stretch long. Dusk is coming.",
    "night": "Night falls.",
}

HELP_TEXT = """\
You can look, move (n / s / e / w), examine things, take them, use them,
talk to whoever is there, wait, rest, and carve words for whoever comes next.
Beyond that, try what seems sensible. The world is listening."""


@dataclass
class Game:
    world: World
    position: Pos
    inventory: List[str] = field(default_factory=list)
    flags: Set[str] = field(default_factory=set)
    health: int = MAX_HEALTH
    turn: int = content.START_TURN
    pride: int = 0
    sequence_progress: Dict[str, int] = field(default_factory=dict)   # sequences and mazes
    maze_origin: Optional[Pos] = None     # where you walked into the maze you're lost in
    last_scene: Optional[tuple] = field(default=None, repr=False, compare=False)  # not saved

    # ------------------------------------------------------------------
    # Construction and persistence
    # ------------------------------------------------------------------

    @classmethod
    def new(cls) -> "Game":
        world = build_world()
        game = cls(world=world, position=world.start)
        game._arrive()
        return game

    def to_dict(self) -> dict:
        return {
            "world": self.world.to_dict(),
            "position": list(self.position),
            "inventory": list(self.inventory),
            "flags": sorted(self.flags),
            "health": self.health,
            "turn": self.turn,
            "pride": self.pride,
            "sequence_progress": dict(self.sequence_progress),
            "maze_origin": list(self.maze_origin) if self.maze_origin else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Game":
        return cls(
            world=World.from_dict(data["world"]),
            position=tuple(data["position"]),
            inventory=list(data["inventory"]),
            flags=set(data["flags"]),
            health=data["health"],
            turn=data["turn"],
            pride=data["pride"],
            sequence_progress=dict(data["sequence_progress"]),
            maze_origin=tuple(data["maze_origin"]) if data.get("maze_origin") else None,
        )

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    @property
    def phase(self) -> str:
        return PHASES[(self.turn // PHASE_TURNS) % len(PHASES)]

    @property
    def tile(self) -> Tile:
        return self.world.tiles[self.position]

    @property
    def slice_complete(self) -> bool:
        return content.SLICE_GOAL in self.flags

    def is_here(self, place: Place) -> bool:
        return is_at(self.world, place, self.position)

    def met(self, condition) -> bool:
        return is_met(condition, self.inventory, self.flags, self.phase)

    def can_enter(self, pos: Pos, origin: Optional[Pos] = None) -> bool:
        """Whether you could step into `pos` from `origin` (default: where you are)."""
        return can_enter(self.world, pos, origin or self.position, self.inventory, self.flags, self.phase)

    def features_here(self) -> List[str]:
        return [f.id for f in FEATURES.values() if self.is_here(f.at) and self.met(f.visible_when)]

    def npcs_here(self) -> List[str]:
        return [n.id for n in NPCS.values() if self.is_here(n.at) and self.met(n.present_when)]

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def do(self, text: str) -> str:
        words = re.findall(r"[a-z0-9']+", text.lower())
        if not words:
            return "Say something, or type 'help'."
        first, rest = words[0], words[1:]

        if first in DIRECTION_ALIASES:
            return self._timed("go", lambda: self._go(DIRECTION_ALIASES[first]))

        verb = VERB_LOOKUP.get(first)
        if verb == "look" and rest:
            # "look at X" examines; "look through X" uses it
            verb = "use" if rest[0] == "through" else "examine"
        if verb == "examine" and first == "listen" and not rest:
            return self._listen()
        if verb is None:
            return f"You're not sure how to '{first}'."

        if verb == "carve":
            message = text.strip().split(None, 1)[1] if len(text.split()) > 1 else ""
            return self._timed(verb, lambda: self._carve(message))

        args = [w for w in rest if w not in STOPWORDS]
        handler = getattr(self, "_go_words" if verb == "go" else f"_{verb}")
        if verb in TIMED_VERBS:
            return self._timed(verb, lambda: handler(args))
        return handler(args)

    def _timed(self, verb: str, action) -> str:
        """Run an action that takes a turn, then let the world respond."""
        before = (self.position, self.turn)
        self._maze_step_taken = False
        response = action()
        if verb == "go" and self.position == before[0] and not self._maze_step_taken:
            return response  # you didn't actually go anywhere
        self.turn += 1
        return response + self._after_turn(before[1])

    def _after_turn(self, previous_turn: int) -> str:
        notes = []
        previous_phase = PHASES[(previous_turn // PHASE_TURNS) % len(PHASES)]
        if self.phase != previous_phase:
            notes.append(PHASE_CHANGES[self.phase])
        for hazard in HAZARDS:
            if hazard.enemy and hazard.enemy not in self.tile.enemies:
                continue
            if self.is_here(hazard.at) and self.met(hazard.when):
                self.health -= hazard.damage
                notes.append(hazard.message)
                if self.health <= 0:
                    notes.append(self._fall(f"the {LANDMARKS[hazard.at].name}"))
                    break
        return "".join("\n\n" + note for note in notes)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def _look(self, args: Sequence[str] = ()) -> str:
        return self.describe()

    def _go(self, direction: str) -> str:
        maze = self._active_maze()
        if maze:
            return self._maze_step(maze, direction)
        target = self.world.neighbors(self.position).get(direction)
        if target is None:
            return "The land ends there. You can't go that way."
        if not self.can_enter(target, self.position):
            return self._blocked_message(LANDMARKS[self.world.tiles[target].landmark])
        origin = self.position
        self.position = target
        maze = self._active_maze()
        if maze:                              # you've just walked into it
            self.maze_origin = origin
            self.sequence_progress.pop(maze.id, None)
        self._arrive()
        return self.describe()

    def _blocked_message(self, landmark) -> str:
        for condition, message in landmark.blocked_variants:
            if self.met(condition):
                return message
        return landmark.blocked_message

    def _active_maze(self):
        """The maze you're lost in right now, if any."""
        return next(
            (m for m in MAZES.values() if self.is_here(m.at) and m.solved_flag not in self.flags),
            None,
        )

    def _maze_step(self, maze, direction: str) -> str:
        self._maze_step_taken = True
        progress = self.sequence_progress.get(maze.id, 0)
        if direction == maze.path[progress]:
            progress += 1
            if progress < len(maze.path):
                self.sequence_progress[maze.id] = progress
                return maze.step_text
            self.sequence_progress.pop(maze.id, None)
            self.flags.add(maze.solved_flag)
            return self._apply(maze.success) + "\n\n" + self.describe()
        self.sequence_progress.pop(maze.id, None)
        landmark_pos = LANDMARKS[maze.at].pos
        self.position = self.maze_origin or (landmark_pos[0], landmark_pos[1] - 1)
        self.maze_origin = None
        self._arrive()
        return maze.failure + "\n\n" + self.describe()

    def _go_words(self, args: Sequence[str]) -> str:
        if not args or args[0] not in DIRECTION_ALIASES:
            return "Go where? North, south, east or west."
        return self._go(DIRECTION_ALIASES[args[0]])

    def _examine(self, args: Sequence[str]) -> str:
        if not args:
            return self.describe()
        handled = self._try_story("examine", args)
        if handled is not None:
            return handled
        feature_id = self._pick(args, self.features_here(), lambda f: FEATURES[f].words)
        if isinstance(feature_id, str) and feature_id.startswith("?"):
            return feature_id[1:]
        if feature_id:
            feature = FEATURES[feature_id]
            self._see(feature.clue)
            return feature.description
        item_id = self._match_item(args, self.inventory + self.tile.items)
        if item_id:
            item = ITEMS[item_id]
            self._see(item.clue)
            return f"{item.name}: {item.description}" + (f"\n\n{item.lore}" if item.lore else "")
        npc_id = self._match_named(args, self.npcs_here(), NPCS)
        if npc_id:
            return f"{NPCS[npc_id].name}: {NPCS[npc_id].description}"
        enemy_id = self._match_named(args, self.tile.enemies, ENEMIES)
        if enemy_id:
            return f"{ENEMIES[enemy_id].name}: {ENEMIES[enemy_id].description}"
        return "You don't see that here."

    def _read(self, args: Sequence[str]) -> str:
        if not args:
            return "Read what?"
        handled = self._try_story("read", args)
        return handled if handled is not None else self._examine(args)

    def _take(self, args: Sequence[str]) -> str:
        if not args:
            return "Take what?"
        handled = self._try_story("take", args)
        if handled is not None:
            return handled
        item_id = self._match_item(args, self.tile.items)
        if item_id:
            self.tile.items.remove(item_id)
            self.inventory.append(item_id)
            name = ITEMS[item_id].name
            self._remember(f"You took the {name} from here.")
            return f"You take the {name}."
        if self._pick(args, self.features_here(), lambda f: FEATURES[f].words):
            return "It won't come away."
        return "You don't see that here."

    def _use(self, args: Sequence[str]) -> str:
        if not args:
            return "Use what?"
        handled = self._try_story("use", args)
        if handled is not None:
            return handled
        item_id = next((i for i in self.inventory if any(_word_forms(a) & _item_words(i) for a in args)), None)
        if item_id:
            return f"You raise the {ITEMS[item_id].name}. Nothing happens."
        if self._pick(args, self.features_here(), lambda f: FEATURES[f].words):
            return "Nothing happens."
        return "You don't have that."

    def _strike(self, args: Sequence[str]) -> str:
        if not args:
            return "Strike what?"
        handled = self._try_story("strike", args)
        if handled is not None:
            return handled
        feature_id = self._pick(args, self.features_here(), lambda f: FEATURES[f].words)
        if isinstance(feature_id, str) and feature_id.startswith("?"):
            return feature_id[1:]
        if feature_id:
            return f"You strike {FEATURES[feature_id].name}. Nothing happens."
        return "You don't see that here."

    def _drop(self, args: Sequence[str]) -> str:
        item_id = self._match_item(args, self.inventory)
        if item_id is None:
            return "You aren't carrying that."
        self.inventory.remove(item_id)
        self.tile.items.append(item_id)
        name = ITEMS[item_id].name
        self._remember(f"You left the {name} here.")
        return f"You set down the {name}."

    def _talk(self, args: Sequence[str]) -> str:
        present = self.npcs_here()
        if not present:
            return "There's no one here to talk to."
        npc_id = self._match_named(args, present, NPCS) if args else None
        if npc_id is None:
            if len(present) > 1 and args:
                return "Which of them?"
            npc_id = present[0]  # with one person here, any way of addressing them works
        for line in NPCS[npc_id].lines:
            if self.met(line.when):
                self._apply(line.effects)
                return line.text
        return "They say nothing."

    def _fight(self, args: Sequence[str]) -> str:
        handled = self._try_story("fight", args)   # e.g. finishing an enemy that has yielded
        if handled is not None:
            return handled
        enemies = self.tile.enemies
        if not enemies:
            return "There's nothing here to fight."
        enemy_id = self._match_named(args, enemies, ENEMIES) if args else enemies[0]
        if enemy_id is None:
            return "That isn't here."
        enemy = ENEMIES[enemy_id]
        if not self.met(enemy.defeat_requires):
            self.health -= enemy.damage
            if self.health <= 0:
                return self._fall(f"the {enemy.name}")
            return (
                f"You throw yourself at the {enemy.name}, but you have nothing that can hurt "
                f"it. It drives you back. (-{enemy.damage} health)"
            )
        if enemy.yields and f"yielded:{enemy_id}" in self.flags:
            return f"The {enemy.name} is already beaten. It waits to learn what you'll do."
        cost = enemy.damage // 2
        self.health -= cost
        if self.health <= 0:
            return self._fall(f"the {enemy.name}")
        if not enemy.yields:
            enemies.remove(enemy_id)
            self._remember(f"You defeated the {enemy.name} here.")
        self.inventory.extend(i for i in enemy.drops if i not in self.inventory)
        message = self._apply(enemy.on_defeat) or f"You defeat the {enemy.name}."
        return f"{message} (-{cost} health)"

    def _spare(self, args: Sequence[str]) -> str:
        handled = self._try_story("spare", args)
        return handled if handled is not None else "There's no one here to spare."

    def _blow(self, args: Sequence[str]) -> str:
        handled = self._try_story("blow", args)
        if handled is not None:
            return handled
        item_id = next((i for i in self.inventory if any(_word_forms(a) & _item_words(i) for a in args)), None)
        if item_id:
            return f"You blow the {ITEMS[item_id].name}. The note fades, and nothing answers."
        return "You have nothing to blow."

    def _carve(self, message: str) -> str:
        message = message.strip()
        if not message:
            return "Carve what?"
        self._remember(f'Carved here, in your hand: "{message}"')
        return "You carve your words where the next traveler will find them."

    def _wait(self, args: Sequence[str] = ()) -> str:
        target = next((a for a in args if a in PHASES), None)
        if target == self.phase:
            return f"It's already {target}."
        before = self.turn
        self.turn = (self.turn // PHASE_TURNS + 1) * PHASE_TURNS
        if target:
            while self.phase != target:
                self.turn += PHASE_TURNS
        return "Time passes." + self._after_turn(before)

    def _rest(self, args: Sequence[str] = ()) -> str:
        if self.tile.enemies or any(self.is_here(h.at) for h in HAZARDS):
            return "You can't rest here. Not with what's circling."
        self.health = MAX_HEALTH
        return "You rest, and your strength returns. " + self._wait(args)

    def _listen(self) -> str:
        heard = self._signal_lines()
        return " ".join(heard) if heard else "You hear only the wind."

    def _inventory(self, args: Sequence[str] = ()) -> str:
        if not self.inventory:
            return "You carry nothing."
        return "You carry:\n" + "\n".join(f"  {ITEMS[i].name}" for i in self.inventory)

    def _status(self, args: Sequence[str] = ()) -> str:
        return f"Health {self.health}/{MAX_HEALTH}. It is {self.phase}. You are at {self.tile.name}."

    def map_view(self) -> List[List[dict]]:
        """
        What the player knows of the map, north row first. You remember places
        you've been; the Old Map shows the land and marks places, unnamed.
        """
        has_map = "old_map" in self.inventory
        rows = []
        for y in reversed(range(self.world.size)):
            row = []
            for x in range(self.world.size):
                tile = self.world.tiles[(x, y)]
                known = tile.visited or has_map
                row.append({
                    "x": x,
                    "y": y,
                    "known": known,
                    "biome": tile.biome if known else None,
                    "marked": bool(tile.landmark) and known,
                    "name": tile.name if tile.visited else None,
                    "here": (x, y) == self.position,
                })
            rows.append(row)
        return rows

    def _map(self, args: Sequence[str] = ()) -> str:
        lines = []
        for row in self.map_view():
            glyphs = []
            for cell in row:
                if cell["here"]:
                    glyphs.append("@")
                elif cell["marked"]:
                    glyphs.append("*")
                elif cell["known"]:
                    glyphs.append(BIOME_GLYPHS.get(cell["biome"], "?"))
                else:
                    glyphs.append(" ")
            lines.append(" ".join(glyphs))
        legend = "@ you   * a marked place"
        if "old_map" not in self.inventory:
            legend += "   (only where you've been)"
        return "\n".join(lines) + "\n" + legend

    def _help(self, args: Sequence[str] = ()) -> str:
        return HELP_TEXT

    # ------------------------------------------------------------------
    # Story interactions
    # ------------------------------------------------------------------

    def _try_story(self, verb: str, args: Sequence[str]) -> Optional[str]:
        """Sequences and interactions take priority over the generic verbs."""
        for sequence in SEQUENCES.values():
            if sequence.verb == verb and self.is_here(sequence.at) and self.met(sequence.when):
                feature_id = self._pick(args, sequence.steps, lambda f: FEATURES[f].words)
                if isinstance(feature_id, str) and feature_id.startswith("?"):
                    return feature_id[1:]
                if feature_id:
                    return self._sequence_step(sequence, feature_id)

        for interaction in INTERACTIONS.values():
            if verb not in interaction.verbs or not self.is_here(interaction.at):
                continue
            if interaction.once and f"done:{interaction.id}" in self.flags:
                continue
            if interaction.item and interaction.item not in self.inventory:
                continue
            vocabulary: Set[str] = set(interaction.words)
            if interaction.feature:
                feature = FEATURES[interaction.feature]
                if not self.met(feature.visible_when):
                    continue
                vocabulary.update(feature.words)
            if interaction.item:
                vocabulary.update(_item_words(interaction.item))
            if not (_all_named(args, vocabulary) or (interaction.bare and not args)):
                continue
            if not self.met(interaction.when):
                if interaction.otherwise:
                    return interaction.otherwise
                continue
            if interaction.once:
                self.flags.add(f"done:{interaction.id}")
            return self._apply(interaction.effects)
        return None

    def _sequence_step(self, sequence, feature_id: str) -> str:
        progress = self.sequence_progress.get(sequence.id, 0)
        note = sequence.notes.get(feature_id, "")
        if sequence.steps[progress] != feature_id:
            self.sequence_progress[sequence.id] = 0
            return f"{note}\n\n{sequence.failure}".strip()
        progress += 1
        if progress < len(sequence.steps):
            self.sequence_progress[sequence.id] = progress
            return note
        self.sequence_progress.pop(sequence.id, None)
        return f"{note}\n\n{self._apply(sequence.success)}"

    def _apply(self, effects: Effects) -> str:
        reached_goal_before = content.SLICE_GOAL in self.flags
        apply_effects(effects, self.inventory, self.flags)
        self.pride += effects.pride
        for enemy_id in effects.remove_enemies:
            if enemy_id in self.tile.enemies:
                self.tile.enemies.remove(enemy_id)
        if effects.memory:
            self._remember(effects.memory)
        message = effects.message
        if content.SLICE_GOAL in self.flags and not reached_goal_before:
            message += (
                "\n\n~ You have reached the end of what has been written so far. "
                "Explore as long as you like. ~"
            )
        return message

    # ------------------------------------------------------------------
    # Description
    # ------------------------------------------------------------------

    def describe(self) -> str:
        """The current place as text. Also remembered as `last_scene` so a UI can lay it out."""
        scene = self.scene()
        lines = [scene["name"], scene["description"]]
        if scene["atmosphere"]:
            lines.append(" ".join(scene["atmosphere"]))
        if scene["memories"]:
            lines.append("")
            lines.extend(scene["memories"])
        lines.append("")
        lines.extend(line for _, line in scene["presence"])
        lines.append("Exits -- " + "; ".join(f"{e['direction']}: {e['name']}" for e in scene["exits"]))
        text = "\n".join(lines)
        self.last_scene = (text, scene)
        return text

    def scene(self) -> dict:
        """The current place, in parts: name, description, atmosphere, memories, presence, exits."""
        tile = self.tile
        description = tile.description
        if tile.landmark:
            for condition, variant in LANDMARKS[tile.landmark].variants:
                if self.met(condition):
                    description = variant
                    break

        atmosphere = [PHASE_LINES[self.phase]] + self._signal_lines()
        for feature_id in self.features_here():
            feature = FEATURES[feature_id]
            if not isinstance(feature.at, str) or feature.at.startswith("near:"):
                # features on ordinary tiles, or seen from beside a place, announce themselves
                atmosphere.append(feature.description)

        memories = [m for m in tile.memory if not m.startswith("You first came here")][-MEMORY_SHOWN:]
        if memories:
            for echo in ECHOES:
                if echo.at == self.position and echo.clue:
                    self._see(echo.clue)

        presence = [("person", f"{NPCS[n].name} is here.") for n in self.npcs_here()]
        if tile.enemies:
            for enemy_id in tile.enemies:
                enemy = ENEMIES[enemy_id]
                if enemy.yields and f"yielded:{enemy_id}" in self.flags:
                    presence.append(("person", enemy.yielded_text))
                else:
                    presence.append(("danger", f"Nearby: {enemy.name}."))
        if tile.items:
            presence.append(("item", "You see: " + ", ".join(ITEMS[i].name for i in tile.items) + "."))

        in_maze = self._active_maze() is not None
        return {
            "name": tile.name,
            "description": description,
            "atmosphere": [a for a in atmosphere if a],
            "memories": memories,
            "presence": presence,
            "exits": [
                {"direction": d, "name": "Twilight" if in_maze else self.world.tiles[p].name}
                for d, p in self.world.neighbors(self.position).items()
            ],
        }

    def _signal_lines(self) -> List[str]:
        heard = []
        for signal in SIGNALS:
            distance = abs(self.position[0] - signal.target[0]) + abs(self.position[1] - signal.target[1])
            if (
                distance < len(signal.by_distance)
                and self.tile.biome in signal.biomes
                and self.met(signal.when)
                and signal.by_distance[distance]
            ):
                heard.append(signal.by_distance[distance])
                self._see(signal.clue)
        return heard

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _arrive(self) -> None:
        if not self.tile.visited:
            self.tile.visited = True
            self._remember(f"You first came here on turn {self.turn}.")

    def _remember(self, text: str) -> None:
        self.tile.memory.append(text)

    def _see(self, clue: Optional[str]) -> None:
        if clue:
            self.flags.add(f"clue:{clue}")

    def _fall(self, cause: str) -> str:
        self._remember(f"You fell here, overcome by {cause}.")
        self.health = MAX_HEALTH
        self.position = LANDMARKS[content.FALL_LANDMARK].pos
        self.turn = (self.turn // (PHASE_TURNS * len(PHASES)) + 1) * PHASE_TURNS * len(PHASES)  # next dawn
        self._arrive()
        return (
            "Darkness takes you...\n\n"
            "You wake to birdsong and grey dawn light. Someone has carried you to the "
            "Hermit's grove. The Hermit says nothing, but there's a blanket over your back.\n\n"
            + self.describe()
        )

    def _pick(self, args: Sequence[str], candidates: Iterable[str], words_of) -> Optional[str]:
        """
        The single candidate the player named. Returns None if nothing matches,
        or a string starting with '?' asking them to be more specific.
        """
        if not args:
            return None
        matches = [c for c in candidates if _all_named(args, set(words_of(c)))]
        if len(matches) > 1:
            names = sorted({FEATURES[m].name if m in FEATURES else m for m in matches})
            if len(names) > 1:
                return "?Which do you mean: " + ", ".join(names[:-1]) + " or " + names[-1] + "?"
        return matches[0] if matches else None

    def _match_item(self, args: Sequence[str], candidates: Iterable[str]) -> Optional[str]:
        for item_id in candidates:
            if _all_named(args, _item_words(item_id)):
                return item_id
        return None

    def _match_named(self, args: Sequence[str], candidates: Iterable[str], catalog: Dict) -> Optional[str]:
        for candidate in candidates:
            vocabulary = set(re.findall(r"[a-z0-9]+", f"{candidate} {catalog[candidate].name}".lower()))
            if _all_named(args, vocabulary):
                return candidate
        return None


def is_at(world: World, place: Place, pos: Pos) -> bool:
    """Whether `pos` is `place`: a landmark id, "near:<landmark id>", or a tile."""
    if isinstance(place, str):
        if place.startswith("near:"):
            target = LANDMARKS[place[len("near:"):]].pos
            return abs(pos[0] - target[0]) + abs(pos[1] - target[1]) == 1
        return world.tiles[pos].landmark == place
    return tuple(place) == tuple(pos)


def can_enter(world: World, pos: Pos, origin: Pos, inventory, flags, phase=None) -> bool:
    """Whether a player at `origin` can step into the neighbouring tile `pos`."""
    landmark_id = world.tiles[pos].landmark
    if landmark_id is None:
        return True
    landmark = LANDMARKS[landmark_id]
    if not is_met(landmark.enter_when, inventory, flags, phase):
        return False
    if landmark.approach_from:
        side = next((d for d, (dx, dy) in DIRECTIONS.items() if (pos[0] + dx, pos[1] + dy) == tuple(origin)), None)
        return side in landmark.approach_from
    return True


def apply_effects(effects: Effects, inventory: List[str], flags: Set[str]) -> None:
    """The part of applying effects the solver shares with the game."""
    inventory.extend(i for i in effects.give if i not in inventory)
    flags.update(effects.flags)
    flags.update(f"clue:{c}" for c in effects.clues)
    for condition, flag in DERIVED:
        if is_met(condition, inventory, flags):
            flags.add(flag)


def _item_words(item_id: str) -> Set[str]:
    return set(re.findall(r"[a-z0-9]+", f"{item_id} {ITEMS[item_id].name}".lower()))


def _all_named(args: Sequence[str], vocabulary: Set[str]) -> bool:
    return bool(args) and all(_word_forms(w) & vocabulary for w in args)


def _word_forms(word: str) -> Set[str]:
    """The word plus naive singulars, so 'wolves' finds 'wolf' and 'crystals' finds 'crystal'."""
    word = word.replace("'s", "")
    forms = {word}
    if word.endswith("ves"):
        forms.add(word[:-3] + "f")
    if word.endswith("es"):
        forms.add(word[:-2])
    if word.endswith("s"):
        forms.add(word[:-1])
    return forms
