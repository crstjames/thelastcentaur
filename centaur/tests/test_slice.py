"""Tests for the playable slice: the Prologue and Act I (Insight)."""

import dataclasses
import json
from collections import deque

import pytest

from centaur import content
from centaur.content import FOCUS_TILE, LANDMARKS, PHASE_TURNS, SLICE_GOAL
from centaur.game import MAX_HEALTH, Game
from centaur.solver import solve
from centaur.worldgen import build_world


def walk_to(game: Game, goal) -> None:
    """Walk to `goal` by typing direction commands, like a player would."""
    if isinstance(goal, str):
        goal = LANDMARKS[goal].pos
    came_from = {game.position: None}
    queue = deque([game.position])
    while queue:
        pos = queue.popleft()
        if pos == goal:
            break
        for direction, target in game.world.neighbors(pos).items():
            if target not in came_from and game.can_enter(target):
                came_from[target] = (pos, direction)
                queue.append(target)
    assert goal in came_from, f"no route to {goal}"
    steps = []
    pos = goal
    while came_from[pos] is not None:
        pos, direction = came_from[pos]
        steps.append(direction)
    for direction in reversed(steps):
        game.do(direction[0])
    assert game.position == goal


def play_slice(game: Game) -> None:
    assert "Don't trust the crown" in game.do("look")
    assert "map" in game.do("examine the roots").lower()

    walk_to(game, "druids_grove")
    assert "Again" in game.do("talk to the hermit")

    walk_to(game, "mystic_mountains")
    assert "early riser" in game.do("look")
    game.do("wait until dawn")
    assert "singing" in game.do("listen")

    walk_to(game, FOCUS_TILE)
    assert "Crystal Focus" in game.do("take the ringing crystal")
    assert "crystal_focus" in game.inventory

    walk_to(game, "crystal_caves")
    assert game.phase in ("dawn", "day")
    assert "folds away" in game.do("hold up the focus")
    assert "white at the front" in game.do("examine the mural")
    game.do("strike the white crystal")
    game.do("strike the amber crystal")
    result = game.do("strike the violet crystal")
    assert "you can read them" in result
    assert "I learned. It wasn't enough." in game.do("read the runes")


# --------------------------------------------------------------------------
# Content, world and fairness
# --------------------------------------------------------------------------

def test_content_is_consistent():
    assert content.validate_content() == []


def test_world_is_fixed():
    assert build_world().to_dict() == build_world().to_dict()


def test_landmarks_sit_where_the_design_says():
    world = build_world()
    for landmark in LANDMARKS.values():
        assert world.tiles[landmark.pos].landmark == landmark.id


def test_every_tile_has_a_unique_name():
    names = [tile.name for tile in build_world().tiles.values()]
    assert len(names) == len(set(names)) == content.GRID_SIZE ** 2


def test_echoes_are_already_carved_into_the_world():
    world = build_world()
    for echo in content.ECHOES:
        assert echo.text in world.tiles[echo.at].memory


def test_slice_is_fair():
    assert solve().has(SLICE_GOAL)


def test_solver_catches_a_puzzle_without_a_findable_clue(monkeypatch):
    unclued = dataclasses.replace(content.INTERACTIONS["open_caves"], clues=("nowhere_to_be_found",))
    monkeypatch.setitem(content.INTERACTIONS, "open_caves", unclued)
    assert not solve().has(SLICE_GOAL)
    assert solve(require_clues=False).has(SLICE_GOAL)


# --------------------------------------------------------------------------
# Playing the slice
# --------------------------------------------------------------------------

def test_the_slice_can_be_played_to_the_end():
    game = Game.new()
    play_slice(game)
    assert game.slice_complete
    assert "insight" in game.flags


def test_save_and_resume_mid_slice():
    game = Game.new()
    game.do("examine roots")
    walk_to(game, "druids_grove")
    game.do("talk hermit")
    game.do("carve I was here")

    resumed = Game.from_dict(json.loads(json.dumps(game.to_dict())))
    assert resumed.to_dict() == game.to_dict()
    assert 'Carved here, in your hand: "I was here"' in resumed.do("look")


def test_the_crystal_only_sings_at_dawn():
    game = Game.new()
    walk_to(game, FOCUS_TILE)
    assert game.phase != "dawn"
    assert game.do("listen") == "You hear only the wind."
    assert game.do("take ringing crystal") == "You don't see that here."
    game.do("wait until dawn")
    assert "louder than all the rest" in game.do("look")


def test_signal_gets_louder_as_you_get_closer():
    game = Game.new()
    walk_to(game, (1, 3))
    game.do("wait until dawn")
    lines = []
    for target in [(1, 3), (1, 4), (1, 5)]:
        walk_to(game, target)
        lines.append(game.do("listen"))
    assert lines == [
        "Faintly, on the wind, you hear crystals singing.",
        "You can hear crystals singing nearby.",
        "Very close by, a single crystal is ringing, high and clear.",
    ]


def test_the_focus_needs_sunlight():
    game = Game.new()
    game.inventory.append("crystal_focus")
    walk_to(game, "crystal_caves")
    game.do("wait until night")
    assert "dark and cold" in game.do("raise the focus")
    assert "caves_open" not in game.flags
    game.do("wait until dawn")
    assert "folds away" in game.do("raise the focus")


def test_wrong_order_resets_the_chord():
    game = Game.new()
    game.flags.add("caves_open")
    walk_to(game, "crystal_caves")
    game.do("strike white crystal")
    assert "Discord" in game.do("strike violet crystal")
    game.do("strike amber crystal")
    assert "ward_insight" not in game.flags
    assert game.sequence_progress.get("insight_ward", 0) == 0


def test_ambiguous_crystal_asks_which():
    game = Game.new()
    game.flags.add("caves_open")
    walk_to(game, "crystal_caves")
    assert game.do("strike crystal").startswith("Which do you mean")


def test_wolves_bite_at_night_and_you_wake_in_the_grove():
    game = Game.new()
    game.do("wait until night")
    bites = 0
    while game.position == game.world.start:
        response = game.do("examine roots") if bites == 0 else game.do("carve help")
        bites += 1
        assert bites < 20
    assert game.position == LANDMARKS["druids_grove"].pos
    assert game.health == MAX_HEALTH
    assert game.phase == "dawn"
    assert any("overcome by" in m for m in game.world.tiles[game.world.start].memory)


def test_cannot_rest_with_the_wolves():
    game = Game.new()
    assert "can't rest" in game.do("rest")


def test_the_map_is_found_not_given():
    game = Game.new()
    assert "no map" in game.do("map")
    game.do("examine roots")
    assert "@" in game.do("map")


def test_the_fallen_warrior_turns_away_until_you_can_read():
    game = Game.new()
    walk_to(game, "warriors_camp")
    assert "I know what you are" in game.do("talk")
    assert "can't read" in game.do("read the standards")
    game.flags.add("insight")
    assert "Fell at the valley" in game.do("read the standards")


@pytest.mark.parametrize(
    "command, expected",
    [
        ("look at the bark", "sets of four"),
        ("x roots", "map"),
        ("talk to the old druid", "Again"),   # any way of addressing the one person here
        ("dance", "not sure how"),
        ("", "Say something"),
        ("go", "Go where"),
        ("raise the old map", "Nothing happens"),
    ],
)
def test_parser(command, expected):
    game = Game.new()
    if "druid" in command:
        walk_to(game, "druids_grove")
    if "raise" in command:
        game.inventory.append("old_map")
    assert expected in game.do(command)


def test_examining_is_free_but_moving_takes_time():
    game = Game.new()
    turn = game.turn
    game.do("look")
    game.do("examine bark")
    assert game.turn == turn
    game.do("n")
    assert game.turn == turn + 1
    game.do("wait")
    assert game.turn % PHASE_TURNS == 0
