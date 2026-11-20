"""
Web front end for The Last Centaur.

    python -m centaur.server        # then open http://localhost:8765

A thin wrapper over the engine: one page, and a JSON API it talks to.

Where the game is kept depends on how the server is run:

- Run locally (`python -m centaur.server`), it reads and writes the same save
  file as the terminal game, so you can switch between the two mid-game.
- Run by a host that imports `app` (such as Vercel, via pyproject.toml), it
  keeps no files. Each browser keeps its own save and sends it with every
  request; the response carries the updated save back. So every visitor has
  their own game, with no login or database. Set CENTAUR_SAVE to use a file
  instead.

Needs fastapi and uvicorn (the engine itself has no dependencies).
"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from centaur.game import MAX_HEALTH, Game
from centaur.content import ITEMS, PHASE_TURNS, PHASES, PROLOGUE, START_TURN
from centaur.play import DEFAULT_SAVE, INTRO, from_save_data, load, save, to_save_data

HERE = Path(__file__).parent
ASSETS = HERE / "web" / "assets"
# The save file, or None to keep the save in the browser. main() defaults it to DEFAULT_SAVE.
SAVE_PATH: Optional[Path] = Path(os.environ["CENTAUR_SAVE"]) if os.environ.get("CENTAUR_SAVE") else None
PORT = int(os.environ.get("CENTAUR_PORT", "8765"))

app = FastAPI(title="The Last Centaur")
app.mount("/assets", StaticFiles(directory=ASSETS), name="assets")
_lock = threading.Lock()


class Request(BaseModel):
    save: Optional[dict] = None  # the browser's save, when the server keeps no file


class Command(Request):
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


def _load_or_new(req: Optional[Request]):
    """
    Returns (game, is_new). The save file is re-read every request, so the
    terminal and browser can share it. Without a file, the game comes from the
    save in the request; a missing, outdated or broken one starts a new game.
    """
    if SAVE_PATH is not None:
        game = load(SAVE_PATH) if SAVE_PATH.exists() else None
    else:
        game = from_save_data(req.save) if req and req.save else None
    if game is None:
        return Game.new(), True
    return game, False


def _keep(game: Game) -> dict:
    """Saves the game. Returns the save for the browser to keep, if there's no file."""
    if SAVE_PATH is not None:
        save(game, SAVE_PATH)
        return {"save": None}
    return {"save": to_save_data(game)}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(HERE / "web" / "index.html")


@app.post("/api/state")
def state(req: Optional[Request] = None) -> dict:
    with _lock:
        game, is_new = _load_or_new(req)
        description = game.describe()
        kept = _keep(game)
        fresh = is_new or game.turn == START_TURN
        return {"description": description, "scene": game.scene(), "intro": INTRO if fresh else None,
                "prologue": list(PROLOGUE), "fresh": fresh, **_view(game), **kept}


@app.post("/api/command")
def command(cmd: Command) -> dict:
    with _lock:
        game, _ = _load_or_new(cmd)
        response = game.do(cmd.text[:500])
        return {"response": response, "block": _block(game, response), **_view(game), **_keep(game)}


@app.post("/api/new")
def new_game() -> dict:
    with _lock:
        game = Game.new()
        return {"description": game.describe(), "scene": game.scene(), "intro": INTRO, "prologue": list(PROLOGUE),
                "fresh": True, **_view(game), **_keep(game)}


def main() -> None:
    import uvicorn
    global SAVE_PATH
    if SAVE_PATH is None:
        SAVE_PATH = DEFAULT_SAVE  # locally, share the terminal game's save
    print(f"The Last Centaur is running at http://localhost:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
