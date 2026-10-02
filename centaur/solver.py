"""
Fairness solver for The Last Centaur.

Plays the game abstractly, as an idealised player who explores everything
reachable but only attempts a clue-gated interaction after seeing one of its
clues. If this player can reach a goal flag, every puzzle on the way there can
be worked out from things actually encountered in the world.

Time is treated as free: a player can always wait for any time of day, so
each phase is tried in turn.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import List, Set

from centaur.content import (
    ECHOES, ENEMIES, FEATURES, INTERACTIONS, ITEMS, LANDMARKS, NPCS, PHASES, SEQUENCES,
    SIGNALS, Place, Pos, is_met,
)
from centaur.game import apply_effects, can_enter, is_at
from centaur.worldgen import World, build_world


@dataclass
class SolveResult:
    flags: Set[str]
    inventory: List[str]
    reached: Set[Pos]

    def has(self, flag: str) -> bool:
        return flag in self.flags


def solve(require_clues: bool = True, world: World = None) -> SolveResult:
    world = world or build_world()
    inventory: List[str] = []
    flags: Set[str] = set()

    def at(place: Place, pos: Pos) -> bool:
        return is_at(world, place, pos)

    def clued(clues) -> bool:
        return not require_clues or not clues or any(f"clue:{c}" in flags for c in clues)

    reached: Set[Pos] = set()
    changed = True
    while changed:
        before = (len(inventory), len(flags))
        reached = _reachable(world, inventory, flags)

        for echo in ECHOES:
            if echo.at in reached and echo.clue:
                flags.add(f"clue:{echo.clue}")
        for item_id in inventory:
            if ITEMS[item_id].clue:
                flags.add(f"clue:{ITEMS[item_id].clue}")

        for phase in PHASES:
            met = lambda condition: is_met(condition, inventory, flags, phase)
            for pos in reached:
                tile = world.tiles[pos]
                inventory.extend(i for i in tile.items if i not in inventory)
                for signal in SIGNALS:
                    distance = abs(pos[0] - signal.target[0]) + abs(pos[1] - signal.target[1])
                    if (distance < len(signal.by_distance) and tile.biome in signal.biomes
                            and met(signal.when) and signal.clue):
                        flags.add(f"clue:{signal.clue}")
                for feature in FEATURES.values():
                    if at(feature.at, pos) and met(feature.visible_when) and feature.clue:
                        flags.add(f"clue:{feature.clue}")
                for npc in NPCS.values():
                    if at(npc.at, pos) and met(npc.present_when):
                        line = next((l for l in npc.lines if met(l.when)), None)
                        if line:
                            apply_effects(line.effects, inventory, flags)
                for interaction in INTERACTIONS.values():
                    if not at(interaction.at, pos) or f"done:{interaction.id}" in flags:
                        continue
                    if interaction.item and interaction.item not in inventory:
                        continue
                    if interaction.feature and not met(FEATURES[interaction.feature].visible_when):
                        continue
                    if met(interaction.when) and clued(interaction.clues):
                        if interaction.once:
                            flags.add(f"done:{interaction.id}")
                        apply_effects(interaction.effects, inventory, flags)
                for sequence in SEQUENCES.values():
                    if at(sequence.at, pos) and met(sequence.when) and clued(sequence.clues):
                        apply_effects(sequence.success, inventory, flags)
                for enemy_id in tile.enemies:
                    enemy = ENEMIES[enemy_id]
                    if met(enemy.defeat_requires):
                        inventory.extend(i for i in enemy.drops if i not in inventory)
                        apply_effects(enemy.on_defeat, inventory, flags)

        changed = (len(inventory), len(flags)) != before

    return SolveResult(flags=flags, inventory=inventory, reached=reached)


def _reachable(world: World, inventory, flags) -> Set[Pos]:
    seen = {world.start}
    queue = deque([world.start])
    while queue:
        pos = queue.popleft()
        for target in world.neighbors(pos).values():
            if target not in seen and can_enter(world, target, pos, inventory, flags):
                seen.add(target)
                queue.append(target)
    return seen


if __name__ == "__main__":
    from centaur.content import SLICE_GOAL, validate_content
    problems = validate_content()
    print("content:", "ok" if not problems else problems)
    result = solve()
    print(f"slice goal '{SLICE_GOAL}' reachable fairly:", result.has(SLICE_GOAL))
