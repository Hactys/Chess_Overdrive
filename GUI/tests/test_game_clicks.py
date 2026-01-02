import asyncio
from GUI.services.state_cache import set_state


def test_click_square_no_state(client):
    response = client.post("/game/g1/click/e2")
    assert response.status_code == 200


def test_first_click_selects_piece(client, monkeypatch):
    async def fake_emit(*args, **kwargs):
        pass

    monkeypatch.setattr("GUI.routers.game.sio.emit", fake_emit)

    asyncio.run(
        set_state(
            "g2",
            {
                "current_player": "white",
                "players": {},
                "board": {"pieces": {"e2": {"owner": "white", "type": "pawn"}}},
            }
        )
    )

    response = client.post("/game/g2/click/e2")
    assert response.status_code == 200
