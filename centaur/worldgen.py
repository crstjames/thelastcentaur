"""
World generation for The Last Centaur.

Builds a GRID_SIZE x GRID_SIZE world from a seed:
  1. Scatter the hand-authored landmarks within their placement constraints.
  2. Give every other tile the biome of its nearest landmark (with a little
     jitter, so borders look organic), then a unique name and description.
  3. Prove the world is winnable: replay each of the three paths and reject
     the layout if any of them can't reach and defeat the final boss.

The same seed always produces the same world. Each tile carries its own
mutable state (items, enemies, visited, memory) that the engine changes as
the game is played; World.to_dict()/from_dict() round-trips all of it.

Run `python -m centaur.worldgen --seed 7` to print a map.
"""

from __future__ import annotations

import argparse
import random
from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from centaur import content
from centaur.content import (
    BIOMES, ENEMIES, GRID_SIZE, ITEMS, LANDMARKS, NPCS, PATHS, is_met,
)

Pos = Tuple[int, int]

DIRECTIONS: Dict[str, Pos] = {
    "north": (0, 1),
    "south": (0, -1),
    "east": (1, 0),
    "west": (-1, 0),
}

AMBIENT_ENEMY_CHANCE = 0.15
MAX_ATTEMPTS = 500


@dataclass
class Tile:
    x: int
    y: int
    biome: str
    name: str
    description: str
    landmark: Optional[str] = None
    items: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    visited: bool = False
    memory: List[str] = field(default_factory=list)  # what has happened here, oldest first

    @property
    def pos(self) -> Pos:
        return (self.x, self.y)


@dataclass
class World:
    seed: int
    size: int
    tiles: Dict[Pos, Tile]
    landmarks: Dict[str, Pos]  # landmark id -> position

    @property
    def start(self) -> Pos:
        return self.landmarks[content.START_LANDMARK]

    def tile(self, pos: Pos) -> Optional[Tile]:
        return self.tiles.get(pos)

    def neighbors(self, pos: Pos) -> Dict[str, Pos]:
        x, y = pos
        result = {}
        for direction, (dx, dy) in DIRECTIONS.items():
            target = (x + dx, y + dy)
            if target in self.tiles:
                result[direction] = target
        return result

    def can_enter(self, pos: Pos, inventory) -> bool:
        tile = self.tiles[pos]
        if tile.landmark is None:
            return True
        return is_met(LANDMARKS[tile.landmark].enter_requires, inventory)

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "size": self.size,
            "landmarks": {k: list(v) for k, v in self.landmarks.items()},
            "tiles": [asdict(tile) for tile in self.tiles.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "World":
        tiles = {}
        for raw in data["tiles"]:
            tile = Tile(**raw)
            tiles[tile.pos] = tile
        return cls(
            seed=data["seed"],
            size=data["size"],
            tiles=tiles,
            landmarks={k: tuple(v) for k, v in data["landmarks"].items()},
        )


class GenerationError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------

def generate(seed: int) -> World:
    """Generate a winnable world for `seed`."""
    rng = random.Random(seed)
    for _ in range(MAX_ATTEMPTS):
        positions = _place_landmarks(rng)
        if positions is None:
            continue
        world = _build_world(seed, positions, rng)
        if all(solve(world, path).won for path in PATHS):
            return world
    raise GenerationError(f"could not generate a winnable world for seed {seed}")


def _place_landmarks(rng: random.Random) -> Optional[Dict[str, Pos]]:
    positions: Dict[str, Pos] = {}
    for landmark in LANDMARKS.values():  # dicts keep authoring order
        rule = landmark.placement
        candidates = []
        for x in range(rule.cols[0], rule.cols[1] + 1):
            for y in range(rule.rows[0], rule.rows[1] + 1):
                if any(max(abs(x - px), abs(y - py)) < 2 for px, py in positions.values()):
                    continue  # keep landmarks from touching, even diagonally
                if rule.near is not None:
                    nx, ny = positions[rule.near]
                    distance = abs(x - nx) + abs(y - ny)
                    if not rule.distance[0] <= distance <= rule.distance[1]:
                        continue
                candidates.append((x, y))
        if not candidates:
            return None
        positions[landmark.id] = rng.choice(candidates)
    return positions


def _build_world(seed: int, positions: Dict[str, Pos], rng: random.Random) -> World:
    tiles: Dict[Pos, Tile] = {}
    used_names: Set[str] = set()
    used_descriptions: Set[Tuple[str, str]] = set()

    for landmark_id, (x, y) in positions.items():
        landmark = LANDMARKS[landmark_id]
        tiles[(x, y)] = Tile(
            x=x, y=y,
            biome=landmark.biome,
            name=landmark.name,
            description=landmark.description,
            landmark=landmark_id,
            items=list(landmark.items),
            enemies=list(landmark.enemies),
            npcs=list(landmark.npcs),
        )
        used_names.add(landmark.name)

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if (x, y) in tiles:
                continue
            biome = BIOMES[_nearest_biome((x, y), positions, rng)]
            enemies = []
            if biome.ambient_enemies and rng.random() < AMBIENT_ENEMY_CHANCE:
                enemies.append(rng.choice(biome.ambient_enemies))
            tiles[(x, y)] = Tile(
                x=x, y=y,
                biome=biome.id,
                name=_unique_name(biome, used_names, rng),
                description=_unique_description(biome, used_descriptions, rng),
                enemies=enemies,
            )

    return World(seed=seed, size=GRID_SIZE, tiles=tiles, landmarks=dict(positions))


def _nearest_biome(pos: Pos, positions: Dict[str, Pos], rng: random.Random) -> str:
    x, y = pos
    best_biome, best_score = None, None
    for landmark_id, (lx, ly) in positions.items():
        landmark = LANDMARKS[landmark_id]
        score = abs(x - lx) + abs(y - ly) - landmark.influence + rng.random() * 1.5
        if best_score is None or score < best_score:
            best_biome, best_score = landmark.biome, score
    return best_biome


def _unique_name(biome, used: Set[str], rng: random.Random) -> str:
    options = [f"{a} {n}" for a in biome.adjectives for n in biome.nouns if f"{a} {n}" not in used]
    if options:
        name = rng.choice(options)
    else:  # biome vocabulary exhausted; fall back to numbering
        base = f"{rng.choice(biome.adjectives)} {rng.choice(biome.nouns)}"
        n = 2
        while f"{base} {n}" in used:
            n += 1
        name = f"{base} {n}"
    used.add(name)
    return name


def _unique_description(biome, used: Set[Tuple[str, str]], rng: random.Random) -> str:
    options = [(s, d) for s in biome.sights for d in biome.details if (s, d) not in used]
    pair = rng.choice(options) if options else (rng.choice(biome.sights), rng.choice(biome.details))
    used.add(pair)
    return " ".join(pair)


# --------------------------------------------------------------------------
# Solver -- proves a path can be completed on a given world
# --------------------------------------------------------------------------

@dataclass
class SolveResult:
    path: Optional[str]
    won: bool
    inventory: Set[str]
    defeated: Set[str]
    reached_landmarks: Set[str]


def solve(world: World, path: Optional[str] = None) -> SolveResult:
    """
    Explore `world` greedily until nothing new can be gained.

    With `path` set, the player only picks up items belonging to that path
    (plus path-less items), so a path counts as winnable only if it doesn't
    secretly depend on another path's gear. With `path=None`, anything goes.
    """
    def allowed(item_id: str) -> bool:
        item_path = ITEMS[item_id].path
        return path is None or item_path is None or item_path == path

    inventory: Set[str] = set()
    defeated: Set[Pos] = set()
    defeated_ids: Set[str] = set()
    reached: Set[str] = set()

    changed = True
    while changed:
        changed = False
        for pos in _reachable(world, inventory):
            tile = world.tiles[pos]
            if tile.landmark:
                reached.add(tile.landmark)
            gains = []
            for npc_id in tile.npcs:
                gains.extend(NPCS[npc_id].gives)
            for item_id in tile.items:
                if is_met(ITEMS[item_id].take_requires, inventory):
                    gains.append(item_id)
            if pos not in defeated:
                beatable = [e for e in tile.enemies if is_met(ENEMIES[e].defeat_requires, inventory)]
                if beatable and len(beatable) == len(tile.enemies):
                    defeated.add(pos)
                    for enemy_id in beatable:
                        defeated_ids.add(enemy_id)
                        gains.extend(ENEMIES[enemy_id].drops)
                    changed = True
            for item_id in gains:
                if allowed(item_id) and item_id not in inventory:
                    inventory.add(item_id)
                    changed = True

    won = content.FINAL_BOSS in defeated_ids
    return SolveResult(path=path, won=won, inventory=inventory, defeated=defeated_ids, reached_landmarks=reached)


def _reachable(world: World, inventory: Set[str]) -> Set[Pos]:
    seen = {world.start}
    queue = deque([world.start])
    while queue:
        pos = queue.popleft()
        for target in world.neighbors(pos).values():
            if target not in seen and world.can_enter(target, inventory):
                seen.add(target)
                queue.append(target)
    return seen


# --------------------------------------------------------------------------
# Debug rendering
# --------------------------------------------------------------------------

BIOME_GLYPHS = {
    "woods": "♣", "meadow": "·", "highlands": "▲", "crystal": "◆",
    "ruins": "#", "twilight": "~", "blight": "×",
}


def render(world: World) -> str:
    """ASCII map with a legend. North is up."""
    letters = {}
    for i, landmark_id in enumerate(world.landmarks):
        letters[world.landmarks[landmark_id]] = chr(ord("A") + i)

    lines = []
    for y in reversed(range(world.size)):
        row = []
        for x in range(world.size):
            tile = world.tiles[(x, y)]
            row.append(letters.get((x, y), BIOME_GLYPHS.get(tile.biome, "?")))
        lines.append(f"{y} " + " ".join(row))
    lines.append("  " + " ".join(str(x) for x in range(world.size)))
    lines.append("")
    for landmark_id, pos in world.landmarks.items():
        lines.append(f"  {letters[pos]}  {LANDMARKS[landmark_id].name}  {pos}")
    lines.append("")
    lines.append("  " + "  ".join(f"{glyph} {biome}" for biome, glyph in BIOME_GLYPHS.items()))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and print a Last Centaur world.")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    problems = content.validate_content()
    if problems:
        raise SystemExit("Content problems:\n  " + "\n  ".join(problems))

    seed = args.seed if args.seed is not None else random.randrange(1_000_000)
    world = generate(seed)
    print(f"Seed {seed}\n")
    print(render(world))
    print()
    for path in PATHS:
        result = solve(world, path)
        print(f"  {path:<8} winnable: {result.won}")


if __name__ == "__main__":
    main()
