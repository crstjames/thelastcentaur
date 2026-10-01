"""
Play The Last Centaur in the terminal.

    python -m centaur.play               # continue your saved game, or start one
    python -m centaur.play --new         # start over with a random world
    python -m centaur.play --new --seed 7

The game autosaves after every command.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from centaur.game import Game

DEFAULT_SAVE = Path.home() / ".thelastcentaur" / "save.json"

INTRO = """\
THE LAST CENTAUR

You wake on cold earth, stripped of your power by the barrier. Somewhere to
the north, the last other centaur sits on a stolen throne. Three survivors of
the old wars wait nearby. Each knows a different way to reach the throne.

Type 'help' for commands. Ctrl-D or 'quit' to stop -- your game is saved.
"""


def load(path: Path) -> Game:
    return Game.from_dict(json.loads(path.read_text()))


def save(game: Game, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(game.to_dict()))
    tmp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Play The Last Centaur.")
    parser.add_argument("--new", action="store_true", help="start a new game")
    parser.add_argument("--seed", type=int, help="world seed for a new game")
    parser.add_argument("--save", type=Path, default=DEFAULT_SAVE, help="save file location")
    args = parser.parse_args()

    if args.save.exists() and not args.new:
        game = load(args.save)
        print(f"(Continuing your game -- world {game.world.seed}, turn {game.turn}.)\n")
    else:
        seed = args.seed if args.seed is not None else random.randrange(1_000_000)
        game = Game.new(seed)
        print(INTRO)
        save(game, args.save)

    print(game.describe())
    while not game.over:
        try:
            line = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip().lower() in ("quit", "exit", "q"):
            break
        print()
        print(game.do(line))
        save(game, args.save)

    if game.over:
        print("\nThanks for playing. Run with --new to begin again.")


if __name__ == "__main__":
    main()
