"""Tests for the playable slice: the Prologue and Acts I-III (the spear, the shield, the armor)."""

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
            lost_in = game.world.tiles[target].landmark
            unsolved_maze = any(m.at == lost_in and m.solved_flag not in game.flags for m in content.MAZES.values())
            if unsolved_maze and target != goal:
                continue                      # walking through would get you lost
            if target not in came_from and game.can_enter(target, pos):
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


def play_act_one(game: Game) -> None:
    assert "Ixion lives" in game.do("look")
    assert "map" in game.do("examine the roots").lower()

    walk_to(game, "melias_grove")
    assert "Not as you left" in game.do("talk to melia")

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
    assert "You led them" in result and "you can read them" in result
    assert "ash_spear" in game.inventory
    assert "Bridle-King" in game.do("read the runes")


def play_act_two(game: Game, mercy: bool = True) -> None:
    walk_to(game, "lapith_camp")
    assert "I know what you are" not in game.do("talk to caeneus")
    assert "Fell at the valley" in game.do("read the standards")
    assert "from where the sun never reaches" in game.do("talk to caeneus")

    walk_to(game, (8, 5))                     # north of the stronghold
    assert "old spear" in game.do("look")
    game.do("s")
    assert game.tile.landmark == "ruined_stronghold"
    assert "stopping of his spear" in game.do("read the bier")
    game.do("take the horn")
    assert "war_horn" in game.inventory

    walk_to(game, "warriors_rest")
    assert "glowing" in game.do("look")
    assert "You are the last of them" in game.do("examine the glowing cairn")
    assert "bronze_shield" in game.inventory

    walk_to(game, (8, 6))                     # the valley mouth
    if game.phase != "dusk":
        game.do("wait until dusk")
    assert "shapes" in game.do("look")
    assert "way into the valley is open" in game.do("blow the horn")
    game.do("n")
    assert game.tile.landmark == "enchanted_valley"
    assert "one knee" in game.do("fight the guardian")
    assert "free" in game.do("spare him" if mercy else "kill the guardian")


def play_act_three(game: Game, assassinate: bool = False) -> None:
    walk_to(game, "crossroads")
    if game.phase != "dusk":
        game.do("wait until dusk")
    assert "cold star" in game.do("talk to silenus")
    walk_to(game, (3, 5))
    assert "once toward sunset" in game.do("look")
    walk_to(game, (5, 5))
    assert "cold star one last time" in game.do("look")

    game.do("w")                              # into the glade
    for step in ["n", "n", "w"]:
        assert "push on" in game.do(step)
    assert "Cloak of Nyx" in game.do("n")
    assert "cloak_of_nyx" in game.inventory

    walk_to(game, (5, 6))
    assert "Never one without the other" in game.do("look")
    if game.phase != "night":
        game.do("wait until night")
    game.do("n")
    assert game.tile.landmark == "forgotten_grove"
    assert "A stranger looks back" in game.do("look into the pool")
    assert "Ixion, the Bridle-King" in game.do("put on the armor")
    if assassinate:
        assert "never knew you were there" in game.do("kill the ker")
    assert "Centaur Prime, who never knelt" in game.do("look into the pool")

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
    play_act_one(game)
    assert "runes" in game.flags and not game.slice_complete
    play_act_two(game)
    assert {"spirits_freed", "spared_guardian"} <= game.flags
    walk_to(game, "lapith_camp")
    assert "You let them go" in game.do("talk")
    play_act_three(game)
    assert game.slice_complete
    assert {"memory_spear", "memory_shield", "memory_armor", "bridle_broken"} <= game.flags
    assert {"ash_spear", "bronze_shield", "bronze_armor"} <= set(game.inventory)
    assert game.pride == 0


def test_killing_the_kneeling_guardian_frees_the_valley_but_costs_pride():
    game = Game.new()
    play_act_one(game)
    play_act_two(game, mercy=False)
    assert "spirits_freed" in game.flags
    assert "killed_guardian" in game.flags and game.pride == 1
    assert "bound_guardian" not in game.tile.enemies
    walk_to(game, "lapith_camp")
    assert "A beast" in game.do("talk")


# --------------------------------------------------------------------------
# Act II details
# --------------------------------------------------------------------------

def act_two_ready() -> Game:
    game = Game.new()
    game.flags.update({"runes", "memory_spear", "caeneus_trust"})
    game.inventory.append("ash_spear")
    return game


def test_the_stronghold_only_opens_from_the_north():
    game = act_two_ready()
    for side in [(7, 4), (9, 4), (8, 3)]:
        walk_to(game, side)
        direction = {(7, 4): "e", (9, 4): "w", (8, 3): "n"}[side]
        assert "no way in from this side" in game.do(direction)
        assert game.position == side
    walk_to(game, (8, 5))
    game.do("s")
    assert game.tile.landmark == "ruined_stronghold"


def test_the_stronghold_stays_shut_without_caeneus_trust():
    game = Game.new()
    walk_to(game, (8, 5))
    assert "no way in" in game.do("s")


def test_the_cairn_only_wakes_for_the_spear():
    game = act_two_ready()
    game.inventory.remove("ash_spear")
    walk_to(game, "warriors_rest")
    assert "dark and cold" in game.do("examine cairn")
    assert "bronze_shield" not in game.inventory
    game.inventory.append("ash_spear")
    assert "glowing" in game.do("look")
    game.do("take the glowing cairn")
    assert {"bronze_shield"} <= set(game.inventory) and "memory_shield" in game.flags


def test_caeneus_explains_the_shield_once_he_trusts_you():
    game = act_two_ready()
    game.flags.discard("caeneus_trust")
    game.inventory.append("bronze_shield")
    walk_to(game, "lapith_camp")
    assert "tell me you don't remember" in game.do("talk")
    game.do("read the standards")
    assert "from where the sun never reaches" in game.do("talk")
    assert "gave it back to your dead" in game.do("talk")


def test_the_horn_only_works_at_dusk_and_at_the_valley():
    game = act_two_ready()
    game.inventory.extend(["bronze_shield", "war_horn"])
    walk_to(game, (5, 5))
    game.do("wait until dusk")
    assert "nothing answers" in game.do("blow horn")        # nowhere near the valley
    walk_to(game, (8, 6))
    game.do("wait until night")
    assert "swallowed by the wind" in game.do("blow horn")
    assert "valley_open" not in game.flags
    game.do("wait until dusk")
    assert "open" in game.do("sound the horn")


def test_the_guardian_cannot_be_beaten_without_the_shield():
    game = act_two_ready()
    game.flags.add("valley_open")
    walk_to(game, "enchanted_valley")
    assert "drives you back" in game.do("fight guardian")
    assert "yielded:bound_guardian" not in game.flags


def test_sparing_before_the_fight_does_nothing():
    game = act_two_ready()
    game.flags.add("valley_open")
    walk_to(game, "enchanted_valley")
    assert game.do("spare") == "There's no one here to spare."


def test_the_spear_finally_deals_with_the_wolves():
    game = Game.new()
    game.inventory.append("ash_spear")
    assert "scatter" in game.do("fight the wolves")
    assert not game.tile.enemies
    game.do("wait until night")
    game.do("carve safe now")
    assert game.health > MAX_HEALTH - 20                    # nothing bit you


def test_waiting_for_the_current_phase_does_not_skip_a_day():
    game = Game.new()
    turn = game.turn
    assert game.do("wait until day") == "It's already day."
    assert game.turn == turn


def test_save_and_resume_mid_slice():
    game = Game.new()
    game.do("examine roots")
    walk_to(game, "melias_grove")
    game.do("talk melia")
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
    assert "memory_spear" not in game.flags
    assert game.sequence_progress.get("spear_chord", 0) == 0


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
    assert game.position == LANDMARKS["melias_grove"].pos
    assert game.health == MAX_HEALTH
    assert game.phase == "dawn"
    assert any("overcome by" in m for m in game.world.tiles[game.world.start].memory)


def test_cannot_rest_with_the_wolves():
    game = Game.new()
    assert "can't rest" in game.do("rest")


def test_the_map_is_found_not_given():
    game = Game.new()
    known = lambda: sum(cell["known"] for row in game.map_view() for cell in row)
    assert known() == 1                      # only where you've been
    assert "only where you've been" in game.do("map")
    game.do("examine roots")
    assert known() == content.GRID_SIZE ** 2
    marked = [cell for row in game.map_view() for cell in row if cell["marked"]]
    assert len(marked) == len(LANDMARKS)
    assert all(cell["name"] is None for cell in marked if not cell["here"])  # unnamed until visited


def test_caeneus_turns_away_until_you_can_read():
    game = Game.new()
    walk_to(game, "lapith_camp")
    assert "I know what you are" in game.do("talk")
    assert "can't read" in game.do("read the standards")
    game.flags.add("runes")
    assert "Fell at the valley" in game.do("read the standards")


@pytest.mark.parametrize(
    "command, expected",
    [
        ("look at the bark", "sets of four"),
        ("x roots", "map"),
        ("talk to the old dryad", "Not as you left"),   # any way of addressing the one person here
        ("dance", "Nothing happens"),
        ("teleport to the throne", "not sure how"),
        ("", "Say something"),
        ("go", "Go where"),
        ("raise the old map", "Nothing happens"),
    ],
)
def test_parser(command, expected):
    game = Game.new()
    if "dryad" in command:
        walk_to(game, "melias_grove")
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



# --------------------------------------------------------------------------
# Act III details
# --------------------------------------------------------------------------

def act_three_ready() -> Game:
    game = act_two_ready()
    game.inventory.append("bronze_shield")
    game.flags.update({"memory_shield", "spirits_freed"})
    return game


def test_silenus_only_appears_at_dusk_once_the_valley_is_free():
    game = act_two_ready()
    walk_to(game, "crossroads")
    game.do("wait until dusk")
    assert "Silenus" not in game.do("look")           # not before the valley
    game.flags.add("spirits_freed")
    assert "Silenus is here" in game.do("look")
    game.do("wait until night")
    assert "Silenus" not in game.do("look")


def test_a_wrong_step_in_the_glade_puts_you_back_where_you_came_in():
    game = act_three_ready()
    walk_to(game, (4, 4))                             # south of the glade
    game.do("n")
    assert "Twilight" in game.do("look")              # every exit looks the same
    game.do("n")
    assert "walk out of the twilight" in game.do("s")
    assert game.position == (4, 4)
    assert "cloak_of_nyx" not in game.inventory


def test_the_glade_path_works_from_any_entrance_and_takes_time():
    game = act_three_ready()
    walk_to(game, (3, 5))
    game.do("e")
    turn = game.turn
    for step in "nnwn":
        game.do(step)
    assert "cloak_of_nyx" in game.inventory
    assert game.turn == turn + 4
    assert "From here the paths out are plain" in game.do("look")
    game.do("n")
    assert game.position == (4, 6)                    # once solved, it's an ordinary place


def test_the_grove_turns_you_away_without_the_cloak_or_the_dark():
    game = act_three_ready()
    walk_to(game, (5, 6))
    game.do("wait until night")
    assert "already seen you" in game.do("n")
    game.inventory.append("cloak_of_nyx")
    game.do("wait until day")
    assert "seen in this light" in game.do("n")
    game.do("wait until night")
    game.do("n")
    assert game.tile.landmark == "forgotten_grove"


def test_dawn_in_the_grove_is_deadly():
    game = act_three_ready()
    game.inventory.append("cloak_of_nyx")
    walk_to(game, (5, 6))
    game.do("wait until night")
    game.do("n")
    response = game.do("wait")                        # into the dawn
    assert "Ker" in response and game.health == MAX_HEALTH - 50


def test_the_pool_only_shows_the_prime_once_you_wear_the_armor():
    game = act_three_ready()
    game.inventory.append("cloak_of_nyx")
    walk_to(game, (5, 6))
    game.do("wait until night")
    game.do("n")
    assert "A stranger looks back" in game.do("look into the pool")
    assert "memory_armor" not in game.flags
    assert "You know where he is" in game.do("take the armor")
    response = game.do("look into the pool")
    assert "Centaur Prime" in response
    assert "end of what has been written" in response
    assert {"memory_armor", "bridle_broken"} <= game.flags


def test_killing_the_ker_costs_pride():
    game = Game.new()
    play_act_one(game)
    play_act_two(game)
    play_act_three(game, assassinate=True)
    assert game.pride == 1
    assert game.slice_complete


def test_the_bridle_breaks_whatever_order_the_memories_return_in():
    game = Game.new()
    game.flags.update({"memory_armor", "memory_shield"})
    game._apply(content.Effects(flags=("memory_spear",)))
    assert "bridle_broken" in game.flags


def test_ixions_hold_turns_you_back_until_the_bridle_breaks():
    game = Game.new()
    walk_to(game, (5, 8))
    assert "a rein you can't see" in game.do("n")


def test_ixions_hold_stays_shut_until_the_finale_is_written():
    game = Game.new()
    game.flags.add("bridle_broken")
    walk_to(game, (5, 8))
    assert "hasn't been written yet" in game.do("n")
