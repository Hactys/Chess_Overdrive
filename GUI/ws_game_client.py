import socketio
import asyncio

from GUI.services.room_manager import room_manager
from GUI.services.state_cache import set_state, set_moves


ENGINE_HTTP = "http://localhost:5000"   # Endpoint REST du moteur
ENGINE_WS   = "http://localhost:5000"   # Socket.io endpoint


sio = socketio.AsyncClient()

_joined_games = set()


async def join_game(game_id: str):
    if game_id in _joined_games:
        return
    await sio.emit("join", {"game_id": game_id, "player": "white"})
    _joined_games.add(game_id)
    print(f"📡 [GUI] Join moteur pour game {game_id}")


async def init_connection():
    print(f"🔌 [WS] Tentative connexion au moteur : {ENGINE_WS}")
    try:
        await sio.connect(ENGINE_WS, transports=["websocket"])
        print("🟢 [GUI] Connecté au moteur")
    except Exception as e:
        print("❌ WebSocket moteur inaccessible :", e)
        print("↻ nouvelle tentative dans 3s…")
        await asyncio.sleep(3)
        asyncio.create_task(init_connection())


# Connexion WebSocket
# @sio.event
# async def connect():
#     print("🟢 [WS] Connecté au moteur")
#     await sio.emit("join", {"game_id": GAME_ID, "player": PLAYER})
#     print(f"📡 Join envoyé pour game '{GAME_ID}' en tant que '{PLAYER}'")

@sio.event
async def connect_error(data):
    print("🔴 [WS] Erreur connexion :", data)


@sio.on("state")  # type: ignore
async def on_state(data):
    game_id = data["game_id"]
    await set_state(game_id, data)
    # print(f"📥 Etat reçu : {data['players']}")
    await room_manager.broadcast(game_id, "update_state")


@sio.on("legal_moves_result")  # type: ignore
async def on_moves(data):
    game_id = data["game_id"]
    moves = data.get("moves", [])
    probas = data.get("capture_probas", {})
    await set_moves(game_id, moves, probas)
    # print("📥 Moves reçus :", moves)
    await room_manager.broadcast(game_id, "update_state")
