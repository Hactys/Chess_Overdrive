import pytest
from GUI.services.game_registry import register_game, list_games, join_game
from GUI.ws_game_client import sio


@pytest.mark.asyncio
async def test_register_and_list_game(monkeypatch):
    async def fake_emit(event, data):
        pass

    monkeypatch.setattr(sio, "emit", fake_emit)

    await register_game("g1")
    games = await list_games()

    assert "g1" in games
    assert games["g1"]["player_count"] == 0


@pytest.mark.asyncio
async def test_join_game(monkeypatch):
    called = {}

    async def fake_emit(event, data):
        called["event"] = event
        called["data"] = data

    monkeypatch.setattr(sio, "emit", fake_emit)

    await register_game("g2")
    await join_game("g2", "white")

    assert called["event"] == "join"
    assert called["data"]["player"] == "white"
