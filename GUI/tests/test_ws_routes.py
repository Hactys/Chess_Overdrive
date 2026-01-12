import asyncio
from GUI.services.state_cache import set_state


def test_ws_connect(client):
    """
    Vérifie qu'une connexion websocket est acceptée
    """
    with client.websocket_connect("/ws/testgame") as ws:
        ws.send_text("ping")


def test_ws_sends_initial_update_when_state_exists(client):
    """
    Si un state existe, le serveur doit push 'update_state'
    à la connexion
    """
    asyncio.run(
        set_state(
            "g_ws",
            {
                "current_player": "white",
                "players": {},
                "board": {"pieces": {}},
            },
        )
    )

    with client.websocket_connect("/ws/g_ws") as ws:
        msg = ws.receive_text()
        assert msg == "update_state"
