"""Tests for the web API. Skipped if the web dependencies aren't installed."""

import importlib

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Run locally: the game is kept in a save file."""
    monkeypatch.setenv("CENTAUR_SAVE", str(tmp_path / "save.json"))
    import centaur.server
    server = importlib.reload(centaur.server)
    return TestClient(server.app)


@pytest.fixture
def hosted(monkeypatch):
    """Hosted (as on Vercel): no save file, the browser keeps the game."""
    monkeypatch.delenv("CENTAUR_SAVE", raising=False)
    import centaur.server
    server = importlib.reload(centaur.server)
    yield TestClient(server.app)
    assert server.SAVE_PATH is None


def known_tiles(state):
    return sum(cell["known"] for row in state["map"] for cell in row)


def test_a_new_player_gets_the_intro(client):
    state = client.post("/api/state").json()
    assert state["fresh"] and "open your eyes" in state["intro"]
    assert state["phase"] == "day"
    assert known_tiles(state) == 1


def test_the_prologue_opens_every_visit(client):
    state = client.post("/api/state").json()
    assert state["prologue"][-1].endswith("You are...")
    client.post("/api/command", json={"text": "n"})
    assert client.post("/api/state").json()["prologue"] == state["prologue"]
    assert client.post("/api/new").json()["prologue"] == state["prologue"]


def test_commands_update_the_sidebar(client):
    client.post("/api/state")
    state = client.post("/api/command", json={"text": "examine roots"}).json()
    assert "map" in state["response"].lower()
    assert state["inventory"] == [{"name": "Old Map", "quest": False}]
    assert known_tiles(state) == 100


def test_progress_is_saved_between_requests(client):
    client.post("/api/command", json={"text": "n"})
    state = client.post("/api/state").json()
    assert not state["fresh"]
    assert state["place"] != "The Awakening Woods"


def test_new_game_starts_over(client):
    client.post("/api/command", json={"text": "n"})
    state = client.post("/api/new").json()
    assert state["fresh"] and state["place"] == "The Awakening Woods"


def test_page_and_art_are_served(client):
    assert "The Last Centaur" in client.get("/").text
    assert client.get("/assets/images/bg.png").status_code == 200


def test_moving_returns_a_structured_scene(client):
    client.post("/api/state")
    block = client.post("/api/command", json={"text": "n"}).json()["block"]
    assert block["scene"]["name"] and block["scene"]["description"]
    assert {e["direction"] for e in block["scene"]["exits"]} >= {"north", "south"}


def test_carvings_come_through_as_memories(client):
    state = client.post("/api/state").json()
    assert any("in your hand" in m for m in state["scene"]["memories"])


def test_plain_actions_have_no_scene(client):
    client.post("/api/state")
    block = client.post("/api/command", json={"text": "examine bark"}).json()["block"]
    assert block["scene"] is None and "sets of four" in block["before"]


def test_quest_items_are_marked(client):
    from centaur.content import ITEMS
    quest = {i.id for i in ITEMS.values() if i.quest}
    assert quest == {"crystal_focus", "ash_spear", "war_horn", "bronze_shield", "cloak_of_nyx", "bronze_armor"}


# ---------------- hosted: the browser keeps the save ----------------

def test_hosted_server_hands_the_save_to_the_browser(hosted):
    state = hosted.post("/api/state").json()
    assert state["fresh"] and state["save"]["game"]


def test_hosted_progress_travels_with_the_save(hosted):
    save = hosted.post("/api/state").json()["save"]
    save = hosted.post("/api/command", json={"text": "n", "save": save}).json()["save"]
    state = hosted.post("/api/state", json={"save": save}).json()
    assert not state["fresh"] and state["place"] != "The Awakening Woods"


def test_hosted_players_each_have_their_own_game(hosted):
    mine = hosted.post("/api/state").json()["save"]
    mine = hosted.post("/api/command", json={"text": "n", "save": mine}).json()["save"]
    theirs = hosted.post("/api/state").json()
    assert theirs["fresh"] and theirs["place"] == "The Awakening Woods"
    assert hosted.post("/api/state", json={"save": mine}).json()["place"] != "The Awakening Woods"


def test_hosted_server_writes_no_files(hosted, tmp_path, monkeypatch):
    monkeypatch.setattr("centaur.server.DEFAULT_SAVE", tmp_path / "nope.json")
    save = hosted.post("/api/state").json()["save"]
    hosted.post("/api/command", json={"text": "n", "save": save})
    assert not any(tmp_path.iterdir())


def test_hosted_broken_or_old_saves_start_a_new_game(hosted):
    save = hosted.post("/api/state").json()["save"]
    for bad in [{"version": save["version"] - 1, "game": save["game"]},
                {"version": save["version"], "game": {"nonsense": 1}},
                {"version": save["version"], "game": {**save["game"], "position": [99, 99]}},
                {"junk": True}]:
        state = hosted.post("/api/command", json={"text": "look", "save": bad})
        assert state.status_code == 200
        assert hosted.post("/api/state", json={"save": bad}).json()["fresh"]


def test_local_server_keeps_no_save_in_the_browser(client):
    assert client.post("/api/state").json()["save"] is None


def test_vercel_entry_point_serves_the_game(hosted):
    tomllib = pytest.importorskip("tomllib")  # Python 3.11+
    from pathlib import Path
    config = tomllib.loads((Path(__file__).parents[2] / "pyproject.toml").read_text())
    module, name = config["tool"]["vercel"]["entrypoint"].split(":")
    app = getattr(importlib.import_module(module), name)
    assert "The Last Centaur" in TestClient(app).get("/").text
