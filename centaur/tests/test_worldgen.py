import json

import pytest

from centaur import content
from centaur.content import ENEMIES, LANDMARKS, NPCS, PATHS
from centaur.worldgen import World, generate, solve

SEEDS = range(200)


def test_content_is_consistent():
    assert content.validate_content() == []


def test_same_seed_same_world():
    assert generate(123).to_dict() == generate(123).to_dict()


def test_different_seeds_differ():
    assert generate(1).landmarks != generate(2).landmarks


@pytest.mark.parametrize("seed", SEEDS)
def test_every_path_is_winnable(seed):
    world = generate(seed)
    for path in PATHS:
        assert solve(world, path).won, f"seed {seed}: {path} path cannot be completed"


@pytest.mark.parametrize("seed", SEEDS)
def test_landmarks_respect_placement(seed):
    world = generate(seed)
    assert set(world.landmarks) == set(LANDMARKS)
    for landmark_id, (x, y) in world.landmarks.items():
        rule = LANDMARKS[landmark_id].placement
        assert rule.rows[0] <= y <= rule.rows[1], landmark_id
        assert rule.cols[0] <= x <= rule.cols[1], landmark_id
        if rule.near:
            nx, ny = world.landmarks[rule.near]
            assert rule.distance[0] <= abs(x - nx) + abs(y - ny) <= rule.distance[1], landmark_id


def test_world_covers_grid_with_unique_tile_names():
    world = generate(5)
    assert len(world.tiles) == content.GRID_SIZE ** 2
    names = [tile.name for tile in world.tiles.values()]
    assert len(names) == len(set(names))


def test_start_and_finale_positions():
    world = generate(9)
    assert world.start[1] == 0
    assert world.landmarks["shadow_domain"][1] == content.GRID_SIZE - 1


def test_round_trips_through_json_with_tile_memory():
    world = generate(11)
    tile = world.tiles[world.start]
    tile.memory.append("You carved your name into an oak.")
    tile.visited = True

    restored = World.from_dict(json.loads(json.dumps(world.to_dict())))

    assert restored.to_dict() == world.to_dict()
    assert restored.tiles[restored.start].memory == ["You carved your name into an oak."]


def test_solver_detects_a_broken_path():
    world = generate(3)
    camp = world.tiles[world.landmarks["warriors_camp"]]
    camp.npcs.remove("fallen_warrior")  # nobody hands out the warrior_map now

    assert not solve(world, "warrior").won
    assert solve(world, "mystic").won


def test_paths_do_not_borrow_each_others_gear():
    world = generate(4)
    result = solve(world, "stealth")
    assert "ancient_sword" not in result.inventory
    assert "druid_staff" not in result.inventory


def test_every_path_has_a_mentor_and_a_boss():
    for path in PATHS:
        assert any(npc.path == path for npc in NPCS.values()), path
        assert any(
            LANDMARKS[l].path == path and any(ENEMIES[e].boss for e in LANDMARKS[l].enemies)
            for l in LANDMARKS
        ), path
