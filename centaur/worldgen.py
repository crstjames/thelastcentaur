"""
Builds The Last Centaur's world.

Landmarks sit at the fixed positions in content.py. Every other tile takes
the biome of its nearest landmark (unless content.BIOME_OVERRIDES says
otherwise) and gets a unique generated name and description. Generation uses
a fixed seed, so every player gets the same world.

Each tile carries mutable state the game changes as you play: items,
enemies, visited, and memory. Echoes (your past self's carvings) are already
in tile memory when the world is built. World.to_dict()/from_dict() round-trip
all of it.

Run `python -m centaur.worldgen` to print the map.
"""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from centaur.biomes import BIOMES, Biome
from centaur.content import (
    BIOME_OVERRIDES, ECHOES, GRID_SIZE, LANDMARKS, START_LANDMARK, WORLD_SEED, Pos,
)

DIRECTIONS: Dict[str, Pos] = {
    "north": (0, 1),
    "south": (0, -1),
    "east": (1, 0),
    "west": (-1, 0),
}


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
    visited: bool = False
    memory: List[str] = field(default_factory=list)  # what has happened here, oldest first

    @property
    def pos(self) -> Pos:
        return (self.x, self.y)


@dataclass
class World:
    size: int
    tiles: Dict[Pos, Tile]

    @property
    def start(self) -> Pos:
        return LANDMARKS[START_LANDMARK].pos

    def neighbors(self, pos: Pos) -> Dict[str, Pos]:
        x, y = pos
        result = {}
        for direction, (dx, dy) in DIRECTIONS.items():
            target = (x + dx, y + dy)
            if target in self.tiles:
                result[direction] = target
        return result

    def to_dict(self) -> dict:
        return {"size": self.size, "tiles": [asdict(tile) for tile in self.tiles.values()]}

    @classmethod
    def from_dict(cls, data: dict) -> "World":
        tiles = {}
        for raw in data["tiles"]:
            tile = Tile(**raw)
            tiles[tile.pos] = tile
        return cls(size=data["size"], tiles=tiles)


def build_world() -> World:
    rng = random.Random(WORLD_SEED)
    tiles: Dict[Pos, Tile] = {}
    used_names: Set[str] = set()
    used_descriptions: Set[Tuple[str, str]] = set()

    for landmark in LANDMARKS.values():
        x, y = landmark.pos
        tiles[(x, y)] = Tile(
            x=x, y=y,
            biome=landmark.biome,
            name=landmark.name,
            description=landmark.description,
            landmark=landmark.id,
            items=list(landmark.items),
            enemies=list(landmark.enemies),
        )
        used_names.add(landmark.name)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if (x, y) in tiles:
                continue
            biome = BIOMES[BIOME_OVERRIDES.get((x, y)) or _nearest_biome((x, y), rng)]
            tiles[(x, y)] = Tile(
                x=x, y=y,
                biome=biome.id,
                name=_unique_name(biome, used_names, rng),
                description=_unique_description(biome, used_descriptions, rng),
            )

    for echo in ECHOES:
        tiles[echo.at].memory.append(echo.text)

    return World(size=GRID_SIZE, tiles=tiles)


def _nearest_biome(pos: Pos, rng: random.Random) -> str:
    x, y = pos
    best_biome, best_score = None, None
    for landmark in LANDMARKS.values():
        lx, ly = landmark.pos
        score = abs(x - lx) + abs(y - ly) + rng.random() * 1.5
        if best_score is None or score < best_score:
            best_biome, best_score = landmark.biome, score
    return best_biome


def _unique_name(biome: Biome, used: Set[str], rng: random.Random) -> str:
    options = [f"{a} {n}" for a in biome.adjectives for n in biome.nouns if f"{a} {n}" not in used]
    name = rng.choice(options)
    used.add(name)
    return name


def _unique_description(biome: Biome, used: Set[Tuple[str, str]], rng: random.Random) -> str:
    options = [(s, d) for s in biome.sights for d in biome.details if (s, d) not in used]
    pair = rng.choice(options) if options else (rng.choice(biome.sights), rng.choice(biome.details))
    used.add(pair)
    return " ".join(pair)


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
    for i, landmark in enumerate(LANDMARKS.values()):
        letters[landmark.pos] = chr(ord("A") + i)

    lines = []
    for y in reversed(range(world.size)):
        row = [letters.get((x, y), BIOME_GLYPHS.get(world.tiles[(x, y)].biome, "?")) for x in range(world.size)]
        lines.append(f"{y} " + " ".join(row))
    lines.append("  " + " ".join(str(x) for x in range(world.size)))
    lines.append("")
    for landmark in LANDMARKS.values():
        lines.append(f"  {letters[landmark.pos]}  {landmark.name}  {landmark.pos}")
    lines.append("")
    lines.append("  " + "  ".join(f"{glyph} {biome}" for biome, glyph in BIOME_GLYPHS.items()))
    return "\n".join(lines)


if __name__ == "__main__":
    print(render(build_world()))
