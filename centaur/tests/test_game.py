import json
from collections import deque

import pytest

from centaur.content import ENEMIES, ITEMS, LANDMARKS, NPCS
from centaur.game import MAX_HEALTH, Game
from centaur.worldgen import DIRECTIONS

# Each path as the steps a player takes: (verb, landmark, thing).
WALKTHROUGHS = {
    "warrior": [
        ("talk", "warriors_camp", "fallen_warrior"),
        ("take", "ancient_ruins", "ancient_sword"),
        ("take", "warriors_armory", "war_horn"),
        ("fight", "enchanted_valley", "shadow_guardian"),
        ("fight", "shadow_domain", "shadow_centaur"),
    ],
    "mystic": [
        ("talk", "druids_grove", "hermit_druid"),
        ("take", "mystic_mountains", "crystal_focus"),
        ("take", "crystal_caves", "druid_staff"),
        ("fight", "crystal_outpost", "corrupted_druid"),
        ("fight", "shadow_domain", "shadow_centaur"),
    ],
    "stealth": [
        ("talk", "trials_path", "shadow_scout"),
        ("take", "twilight_glade", "stealth_cloak"),
        ("take", "forgotten_grove", "phantom_dagger"),
        ("fight", "shadow_domain", "shadow_centaur"),
    ],
}

CATALOGS = {"talk": NPCS, "take": ITEMS, "fight": ENEMIES}


def walk_to(game: Game, goal) -> None:
    """Walk to `goal` by typing direction commands, like a player would."""
    came_from = {game.position: None}
    queue = deque([game.position])
    while queue:
        pos = queue.popleft()
        if pos == goal:
            break
        for direction, target in game.world.neighbors(pos).items():
            if target not in came_from and game.world.can_enter(target, game.inventory):
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


def play(game: Game, path: str) -> None:
    for verb, landmark, thing in WALKTHROUGHS[path]:
        walk_to(game, game.world.landmarks[landmark])
        name = CATALOGS[verb][thing].name
        response = game.do(f"{verb} {name}")
        if verb in ("talk", "take"):
            item = NPCS[thing].gives[0] if verb == "talk" else thing
            assert item in game.inventory, f"{path}: '{verb} {name}' failed: {response}"
        else:
            assert thing not in game.tile.enemies, f"{path}: '{verb} {name}' failed: {response}"


@pytest.mark.parametrize("seed", range(40))
@pytest.mark.parametrize("path", sorted(WALKTHROUGHS))
def test_each_path_can_be_played_to_victory(seed, path):
    game = Game.new(seed)
    play(game, path)
    assert game.over
    assert game.won_path == path


def test_save_and_resume_mid_game():
    game = Game.new(8)
    walk_to(game, game.world.landmarks["warriors_camp"])
    game.do("talk warrior")
    game.do("carve the herd remembers")

    resumed = Game.from_dict(json.loads(json.dumps(game.to_dict())))
    assert resumed.to_dict() == game.to_dict()
    play(resumed, "warrior")
    assert resumed.won_path == "warrior"


def test_tiles_remember_what_happened():
    game = Game.new(2)
    game.do("carve Chris was here")
    game.do("take supplies")
    walk_to(game, game.world.landmarks["druids_grove"])
    walk_to(game, game.world.start)

    look = game.do("look")
    assert 'Carved here, in your hand: "Chris was here"' in look
    assert "You took the Basic Supplies from here." in look


def test_barred_landmarks_explain_themselves():
    game = Game.new(5)
    ruins = game.world.landmarks["ancient_ruins"]
    # stand next to the ruins
    for direction, (dx, dy) in DIRECTIONS.items():
        beside = (ruins[0] - dx, ruins[1] - dy)
        if beside in game.world.tiles and game.world.tiles[beside].landmark is None:
            game.position = beside
            break
    assert "(barred)" in game.describe()
    assert LANDMARKS["ancient_ruins"].blocked_message in game.do(direction)
    assert game.position == beside


def test_cannot_find_the_focus_without_the_scroll():
    game = Game.new(6)
    walk_to(game, game.world.landmarks["mystic_mountains"])
    assert game.do("take crystal focus") == ITEMS["crystal_focus"].hidden_message
    assert "crystal_focus" not in game.inventory


def test_wrong_gear_gets_you_driven_back():
    game = Game.new(6)
    game.inventory.append("war_horn")  # can enter the valley, but has no sword
    walk_to(game, game.world.landmarks["enchanted_valley"])
    response = game.do("fight guardian")
    assert "drives you back" in response
    assert "shadow_guardian" in game.tile.enemies


def test_falling_in_battle_returns_you_to_the_start():
    game = Game.new(6)
    game.inventory.append("war_horn")
    walk_to(game, game.world.landmarks["enchanted_valley"])
    valley = game.position
    for _ in range(5):
        response = game.do("fight guardian")
    assert game.position == game.world.start
    assert game.health == MAX_HEALTH
    assert "You fell here, fighting the Shadow Guardian." in game.world.tiles[valley].memory


@pytest.mark.parametrize(
    "command, expected",
    [
        ("talk to the hermit", "Hermit Druid"),
        ("speak with druid", "Hermit Druid"),
        ("TALK HERMIT", "Hermit Druid"),
        ("dance", "don't know how"),
        ("", "Say something"),
        ("go", "Go where"),
    ],
)
def test_parser(command, expected):
    game = Game.new(1)
    walk_to(game, game.world.landmarks["druids_grove"])
    assert expected in game.do(command)


def test_plural_enemy_names():
    game = Game.new(1)
    assert "wolf_pack" in game.tile.enemies
    assert "defeat the Twilight Wolf Pack" in game.do("fight wolves")


def test_talking_twice_gives_one_gift():
    game = Game.new(1)
    walk_to(game, game.world.landmarks["druids_grove"])
    game.do("talk hermit")
    second = game.do("talk hermit")
    assert game.inventory.count("ancient_scroll") == 1
    assert NPCS["hermit_druid"].dialogue["after"] in second
