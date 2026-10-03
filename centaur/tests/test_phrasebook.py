"""
The phrasebook: many ways of saying the same thing, all understood offline.

Each row is (what a player might type, the engine verb, the words that name
the target). The engine itself then works out which object those words mean.
"""

import pytest

from centaur.game import Game
from centaur.phrasebook import interpret
from centaur.tests.test_slice import walk_to

PHRASINGS = [
    # --- moving --------------------------------------------------------------
    ("n", "go", ["north"]),
    ("north", "go", ["north"]),
    ("go north", "go", ["north"]),
    ("walk north", "go", ["north"]),
    ("run north", "go", ["north"]),
    ("skip north", "go", ["north"]),
    ("gallop north", "go", ["north"]),
    ("trot to the north", "go", ["north"]),
    ("head northward", "go", ["north"]),
    ("I canter northwards", "go", ["north"]),
    ("make my way north", "go", ["north"]),
    ("carefully wander west", "go", ["west"]),
    ("I want to go east", "go", ["east"]),
    ("let's head south", "go", ["south"]),
    ("sprint south", "go", ["south"]),
    ("hurry east", "go", ["east"]),
    ("venture west", "go", ["west"]),
    ("travel to the east", "go", ["east"]),
    ("flee south", "go", ["south"]),
    ("w", "go", ["west"]),
    # --- looking ------------------------------------------------------------
    ("look", "look", []),
    ("l", "look", []),
    ("look around", "look", []),
    ("have a look around", "look", []),
    ("take a look around", "look", []),
    ("survey", "look", []),
    ("look at the roots", "examine", ["roots"]),
    ("examine roots", "examine", ["roots"]),
    ("x roots", "examine", ["roots"]),
    ("inspect the bark", "examine", ["bark"]),
    ("study the mural", "examine", ["mural"]),
    ("search the roots", "examine", ["roots"]),
    ("investigate the cairn", "examine", ["cairn"]),
    ("check out the standards", "examine", ["standards"]),
    ("take a look at the mural", "examine", ["mural"]),
    ("have a look at the cairn", "examine", ["cairn"]),
    ("peer into the pool", "examine", ["pool"]),
    ("look into the pool", "examine", ["pool"]),
    ("gaze into the pool", None, None),          # unknown verb: handled later by the LLM
    ("sniff the mushrooms", "examine", ["mushrooms"]),
    ("touch the bark", "examine", ["bark"]),
    ("dig around in the roots", "examine", ["roots"]),
    ("listen", "listen", []),
    ("listen to the crystals", "examine", ["crystals"]),
    ("read the runes", "read", ["runes"]),
    ("decipher the standards", "read", ["standards"]),
    # --- taking -------------------------------------------------------------
    ("take crystal", "take", ["crystal"]),
    ("get the spear", "take", ["spear"]),
    ("grab the spear", "take", ["spear"]),
    ("pick up the spear", "take", ["spear"]),
    ("yank the crystal", "take", ["crystal"]),
    ("rip out the crystal", "take", ["crystal"]),
    ("rip the crystal out", "take", ["crystal"]),
    ("pull out the crystal", "take", ["crystal"]),
    ("pry the crystal loose", "take", ["crystal"]),
    ("work the crystal loose", "take", ["crystal"]),
    ("pluck the ringing crystal", "take", ["ringing", "crystal"]),
    ("snatch the dagger", "take", ["dagger"]),
    ("steal the dagger", "take", ["dagger"]),
    ("collect the mushrooms", "take", ["mushrooms"]),
    ("gather some mushrooms", "take", ["mushrooms"]),
    ("harvest the mushrooms", "take", ["mushrooms"]),
    ("wrench the spear free", "take", ["spear", "free"]),
    ("dig up the roots", "take", ["roots"]),
    ("I'd like to carefully rip out the crystal", "take", ["crystal"]),
    # --- using --------------------------------------------------------------
    ("raise the focus", "use", ["focus"]),
    ("hold up the focus", "use", ["focus"]),
    ("hold the focus up to the wall", "use", ["focus", "wall"]),
    ("look through the focus", "use", ["focus"]),
    ("peer through the focus", "use", ["focus"]),
    ("brandish the spear", "use", ["spear"]),
    ("use the focus on the wall", "use", ["focus", "wall"]),
    # --- striking -----------------------------------------------------------
    ("strike the white crystal", "strike", ["white", "crystal"]),
    ("hit the amber crystal", "strike", ["amber", "crystal"]),
    ("tap the violet crystal", "strike", ["violet", "crystal"]),
    ("ring the white crystal", "strike", ["white", "crystal"]),
    ("whack the amber crystal", "strike", ["amber", "crystal"]),
    # --- the horn -----------------------------------------------------------
    ("wear the armor", "use", ["armor"]),
    ("put on the armor", "use", ["armor"]),
    ("don the armour", "use", ["armour"]),
    ("blow the horn", "blow", ["horn"]),
    ("sound the horn", "blow", ["horn"]),
    ("play the horn", "blow", ["horn"]),
    ("blow into the horn", "blow", ["horn"]),
    ("toot the horn", "blow", ["horn"]),
    # --- talking ------------------------------------------------------------
    ("talk to melia", "talk", ["melia"]),
    ("speak with the dryad", "talk", ["dryad"]),
    ("ask the satyr", "talk", ["satyr"]),
    ("chat with the lapith", "talk", ["lapith"]),
    ("greet melia", "talk", ["melia"]),
    ("say hello to melia", "talk", ["melia"]),
    ("hello", "talk", []),
    # --- fighting and mercy -------------------------------------------------
    ("fight the guardian", "fight", ["guardian"]),
    ("attack the wolves", "fight", ["wolves"]),
    ("kill the guardian", "fight", ["guardian"]),
    ("slay the guardian", "fight", ["guardian"]),
    ("charge the guardian", "fight", ["guardian"]),
    ("stab the assassin", "fight", ["assassin"]),
    ("finish him off", "fight", []),
    ("spare him", "spare", []),
    ("spare the guardian", "spare", ["guardian"]),
    ("show mercy", "spare", []),
    ("lower my spear", "spare", ["spear"]),
    ("sheathe my blade", "spare", ["blade"]),
    ("put away my spear", "spare", ["spear"]),
    ("let him go", "spare", []),
    ("stand down", "spare", []),
    ("stop", "spare", []),
    # --- everything else ----------------------------------------------------
    ("drop the map", "drop", ["map"]),
    ("put down the map", "drop", ["map"]),
    ("set down the spear", "drop", ["spear"]),
    ("i", "inventory", []),
    ("inventory", "inventory", []),
    ("check my bag", "examine", ["bag"]),
    ("wait", "wait", []),
    ("wait until dawn", "wait", ["until", "dawn"]),
    ("wait for dusk", "wait", ["dusk"]),
    ("linger until night", "wait", ["until", "night"]),
    ("rest", "rest", []),
    ("go to sleep", "rest", []),
    ("lie down", "rest", []),
    ("make camp", "rest", []),
    ("map", "map", []),
    ("help", "help", []),
    # --- harmless actions ---------------------------------------------------
    ("dance", "flavor", ["dance"]),
    ("I dance", "flavor", ["dance"]),
    ("sing", "flavor", ["sing"]),
    ("rear", "flavor", ["rear"]),
    ("graze", "flavor", ["graze"]),
    ("whinny", "flavor", ["whinny"]),
    ("swish my tail", "flavor", ["swish"]),
]


@pytest.mark.parametrize("text, verb, args", PHRASINGS)
def test_phrasing(text, verb, args):
    parsed = interpret(text)
    if verb is None:
        assert parsed.verb == "unknown"
    else:
        assert (parsed.verb, parsed.args) == (verb, args)


def test_there_are_well_over_a_hundred_phrasings():
    assert len(PHRASINGS) > 100


def test_carving_keeps_your_own_words():
    assert interpret('I carve "Chris was here"').message == '"Chris was here"'
    assert interpret("Engrave Turn Back").message == "Turn Back"


def test_harmless_actions_take_no_time_and_change_nothing():
    game = Game.new()
    turn, before = game.turn, game.to_dict()
    assert game.do("dance") == "You dance a few steps. Nothing happens."
    assert game.do("rear up") == "You rear up on your hind legs. Nothing happens."
    assert game.turn == turn and game.to_dict() == before


def test_striking_an_enemy_is_fighting_it():
    game = Game.new()
    assert "drives you back" in game.do("hit the wolves")


def test_act_one_with_different_words():
    """Play Act I again, saying everything differently."""
    game = Game.new()
    assert "map" in game.do("I'd like to dig around in the roots").lower()
    walk_to(game, "melias_grove")
    assert "Not as you left" in game.do("say hello to the dryad")
    walk_to(game, "mystic_mountains")
    game.do("linger until dawn")
    assert "singing" in game.do("listen")
    walk_to(game, (1, 6))
    assert "Crystal Focus" in game.do("carefully rip out the singing crystal")
    walk_to(game, "crystal_caves")
    assert "folds away" in game.do("hold the focus up to the shimmering wall")
    game.do("take a look at the mural")
    game.do("tap the white crystal")
    game.do("hit the amber crystal")
    assert "you can read them" in game.do("ring the violet crystal")
    assert "ash_spear" in game.inventory
