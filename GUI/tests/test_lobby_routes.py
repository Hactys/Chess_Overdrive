import pytest
from GUI.ws_game_client import sio


def test_create_game_redirect(client, monkeypatch):
    # Mock appel HTTP moteur
    monkeypatch.setattr("GUI.routers.lobby.requests.post", lambda *args, **kwargs: None)

    # 🔥 Mock Socket.IO emit (IMPORTANT)
    async def fake_emit(*args, **kwargs):
        return None

    monkeypatch.setattr(sio, "emit", fake_emit)

    response = client.post("/create_game", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"].startswith("/game/")
