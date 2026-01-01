import socketio
import asyncio
import requests

from ws_manager import ws_manager
from services.state_cache import set_state, set_moves


ENGINE_HTTP = "http://localhost:5000"   # Endpoint REST du moteur
ENGINE_WS   = "http://localhost:5000"   # Socket.io endpoint

GAME_ID = "test_game"
PLAYER = "white"

sio = socketio.AsyncClient()


async def init_connection():
    print(f"🔌 [WS] Tentative connexion au moteur : {ENGINE_WS}")

    # Tentative de création de partie
    try:
        r = requests.post(f"{ENGINE_HTTP}/create", json={
            "game_id": GAME_ID,
            "players": {"white": {}, "black": {}}
        })

        if r.status_code == 200:
            print(f"🆕 Partie '{GAME_ID}' créée")
        else:
            print(f"ℹ Partie '{GAME_ID}' existante ou non créable (HTTP {r.status_code})")
    except Exception as e:
        print(f"❌ Impossible de contacter moteur HTTP pour création : {e}")

    # Connexion WebSocket
    @sio.event
    async def connect():
        print("🟢 [WS] Connecté au moteur")
        await sio.emit("join", {"game_id": GAME_ID, "player": PLAYER})
        print(f"📡 Join envoyé pour game '{GAME_ID}' en tant que '{PLAYER}'")

    @sio.event
    async def connect_error(data):
        print("🔴 [WS] Erreur connexion :", data)

    @sio.on("state")  # type: ignore
    async def on_state(data):
        await set_state(data)
        # print(f"📥 Etat reçu : {data['players']}")
        await ws_manager.broadcast("update_state")

    @sio.on("legal_moves_result")  # type: ignore
    async def on_moves(data):
        moves = data.get("moves", [])
        probas = data.get("capture_probas", {})
        await set_moves(moves, probas)
        # print("📥 Moves reçus :", moves)
        await ws_manager.broadcast("update_state")

    # Connexion avec fallback retry
    try:
        await sio.connect(ENGINE_WS, transports=["websocket"])
        print("🟢 [WS] Connecté en écoute…")
        await sio.wait()
    except Exception as e:
        print("❌ WebSocket moteur inaccessible :", e)
        print("↻ nouvelle tentative dans 3s…")
        await asyncio.sleep(3)
        asyncio.create_task(init_connection())
