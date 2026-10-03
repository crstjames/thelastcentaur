"""
Play The Last Centaur in the terminal.

    python -m centaur.play          # continue your saved game, or start one
    python -m centaur.play --new    # start over

The game autosaves after every command.
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
import time
from pathlib import Path

from centaur.content import PROLOGUE, PROLOGUE_TITLE
from centaur.game import Game

DEFAULT_SAVE = Path.home() / ".thelastcentaur" / "save.json"
# Saves hold the whole world, including what lies where. Bump this whenever a
# content change adds or moves things in the world, so older saves start fresh
# instead of silently missing pieces.
SAVE_VERSION = 5

INTRO = """\
THE LAST CENTAUR

Cold earth. The smell of moss. You open your eyes.

(Type what you want to do. 'quit' or Ctrl-D to stop; your game is saved.)
"""


def load(path: Path):
    try:
        data = json.loads(path.read_text())
        if data.get("version") != SAVE_VERSION:
            return None
        return Game.from_dict(data["game"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def save(game: Game, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"version": SAVE_VERSION, "game": game.to_dict()}))
    tmp.replace(path)


def tell_prologue() -> None:
    """The opening crawl: one paragraph at a time, then Enter to begin."""
    print()
    for paragraph in PROLOGUE:
        print(textwrap.fill(paragraph, 72) + "\n")
        if sys.stdin.isatty():
            time.sleep(1.2)
    title = "  ".join(PROLOGUE_TITLE.upper())        # T H E   L A S T ...
    red = sys.stdout.isatty()
    if red:
        time.sleep(1.5)
    print(("\033[1;31m" if red else "") + title.center(72).rstrip() + ("\033[0m" if red else "") + "\n")
    try:
        input("(Press Enter.)")
    except (EOFError, KeyboardInterrupt):
        pass
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Play The Last Centaur.")
    parser.add_argument("--new", action="store_true", help="start a new game")
    parser.add_argument("--save", type=Path, default=DEFAULT_SAVE, help="save file location")
    args = parser.parse_args()

    game = None if args.new or not args.save.exists() else load(args.save)
    if game is None:
        game = Game.new()
        tell_prologue()
        print(INTRO)
        save(game, args.save)
    else:
        print("(Continuing your game.)\n")

    print(game.describe())
    while True:
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


if __name__ == "__main__":
    main()
