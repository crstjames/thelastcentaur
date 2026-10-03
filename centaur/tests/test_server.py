"""Tests for the web API. Skipped if the web dependencies aren't installed."""

import importlib

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("CENTAUR_SAVE", str(tmp_path / "save.json"))
    import centaur.server
    server = importlib.reload(centaur.server)
    return TestClient(server.app)


def known_tiles(state):
    return sum(cell["known"] for row in state["map"] for cell in row)


def test_a_new_player_gets_the_intro(client):
    state = client.get("/api/state").json()
    assert state["fresh"] and "open your eyes" in state["intro"]
    assert state["phase"] == "day"
    assert known_tiles(state) == 1


def test_the_prologue_opens_every_visit(client):
    state = client.get("/api/state").json()
    assert state["prologue"][-1].endswith("You are...")
    client.post("/api/command", json={"text": "n"})
    assert client.get("/api/state").json()["prologue"] == state["prologue"]
    assert client.post("/api/new").json()["prologue"] == state["prologue"]


def test_commands_update_the_sidebar(client):
    client.get("/api/state")
    state = client.post("/api/command", json={"text": "examine roots"}).json()
    assert "map" in state["response"].lower()
    assert state["inventory"] == [{"name": "Old Map", "quest": False}]
    assert known_tiles(state) == 100


def test_progress_is_saved_between_requests(client):
    client.post("/api/command", json={"text": "n"})
    state = client.get("/api/state").json()
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
    client.get("/api/state")
    block = client.post("/api/command", json={"text": "n"}).json()["block"]
    assert block["scene"]["name"] and block["scene"]["description"]
    assert {e["direction"] for e in block["scene"]["exits"]} >= {"north", "south"}


def test_carvings_come_through_as_memories(client):
    state = client.get("/api/state").json()
    assert any("in your hand" in m for m in state["scene"]["memories"])


def test_plain_actions_have_no_scene(client):
    client.get("/api/state")
    block = client.post("/api/command", json={"text": "examine bark"}).json()["block"]
    assert block["scene"] is None and "sets of four" in block["before"]


def test_quest_items_are_marked(client):
    from centaur.content import ITEMS
    quest = {i.id for i in ITEMS.values() if i.quest}
    assert quest == {"crystal_focus", "ash_spear", "war_horn", "bronze_shield", "cloak_of_nyx", "bronze_armor"}
