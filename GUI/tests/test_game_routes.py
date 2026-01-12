from GUI.services.state_cache import set_state
import asyncio


def test_game_page(client):
    response = client.get("/game/testgame")
    assert response.status_code == 200
    assert "Chess Overdrive" in response.text


def test_board_without_state(client):
    response = client.get("/game/testgame/board")
    assert response.status_code == 200
    assert "En attente du moteur" in response.text


def test_board_with_state(client):
    asyncio.run(
        set_state(
            "g1",
            {
                "current_player": "white",
                "players": {},
                "board": {"pieces": {"e2": {"owner": "white", "type": "pawn"}}},
            },
        )
    )

    response = client.get("/game/g1/board")
    assert response.status_code == 200
    assert "img" in response.text  # une pièce est rendue
