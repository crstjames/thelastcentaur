"""
Web front end for The Last Centaur.

    python -m centaur.server        # then open http://localhost:8765

A thin wrapper over the engine: one page, and a JSON API it talks to. It
reads and writes the same save file as the terminal game, so you can switch
between the two mid-game. Single player and local only; there's no login.

Needs fastapi and uvicorn (the engine itself has no dependencies).
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from centaur.game import MAX_HEALTH, Game
from centaur.content import ITEMS, PHASE_TURNS, PHASES, PROLOGUE, START_TURN
from centaur.play import DEFAULT_SAVE, INTRO, load, save

HERE = Path(__file__).parent
ASSETS = HERE / "web" / "assets"
SAVE_PATH = Path(os.environ.get("CENTAUR_SAVE", DEFAULT_SAVE))
PORT = int(os.environ.get("CENTAUR_PORT", "8765"))

app = FastAPI(title="The Last Centaur")
app.mount("/assets", StaticFiles(directory=ASSETS), name="assets")
_lock = threading.Lock()


class Command(BaseModel):
    text: str


def _view(game: Game) -> dict:
    return {
        "place": game.tile.name,
        "phase": game.phase,
        "phase_progress": (game.turn % PHASE_TURNS) / PHASE_TURNS,
        "phase_index": PHASES.index(game.phase),
        "health": game.health,
        "max_health": MAX_HEALTH,
        "inventory": [{"name": ITEMS[i].name, "quest": ITEMS[i].quest} for i in game.inventory],
        "map": game.map_view(),
        "turn": game.turn,
        "slice_complete": game.slice_complete,
    }


def _block(game: Game, response: str) -> dict:
    """
    Split a response into text before the place description, the description
    itself (as structured parts), and text after it, so the page can lay out
    the place prominently. Responses without a description are plain text.
    """
    if game.last_scene and game.last_scene[0] in response:
        text, scene = game.last_scene
        before, after = response.split(text, 1)
        return {"before": before.strip(), "scene": scene, "after": after.strip()}
    return {"before": response.strip(), "scene": None, "after": ""}


def _load_or_new():
    """Returns (game, is_new). The save file is re-read every request, so the terminal and browser can share it."""
    game = load(SAVE_PATH) if SAVE_PATH.exists() else None
    if game is None:
        game = Game.new()
        save(game, SAVE_PATH)
        return game, True
    return game, False


@app.get("/")
def index() -> FileResponse:
    return FileResponse(HERE / "web" / "index.html")


@app.get("/api/state")
def state() -> dict:
    with _lock:
        game, is_new = _load_or_new()
        description = game.describe()
        save(game, SAVE_PATH)
        fresh = is_new or game.turn == START_TURN
        return {"description": description, "scene": game.scene(), "intro": INTRO if fresh else None,
                "prologue": list(PROLOGUE), "fresh": fresh, **_view(game)}


@app.post("/api/command")
def command(cmd: Command) -> dict:
    with _lock:
        game, _ = _load_or_new()
        response = game.do(cmd.text[:500])
        save(game, SAVE_PATH)
        return {"response": response, "block": _block(game, response), **_view(game)}


@app.post("/api/new")
def new_game() -> dict:
    with _lock:
        game = Game.new()
        save(game, SAVE_PATH)
        return {"description": game.describe(), "scene": game.scene(), "intro": INTRO, "prologue": list(PROLOGUE), "fresh": True, **_view(game)}


def main() -> None:
    import uvicorn
    print(f"The Last Centaur is running at http://localhost:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
