import asyncio
from datetime import datetime, timezone
from GUI.ws_game_client import sio

_games = {}
_lock = asyncio.Lock()

# structure :
# game_id -> {
#   "created_at": datetime,
#   "players": set(),
# }


async def register_game(game_id: str):
    async with _lock:
        _games[game_id] = {
            "created_at": datetime.now(timezone.utc),
            "players": set(),
        }


async def list_games():
    async with _lock:
        return {
            gid: {
                "created_at": info["created_at"],
                "player_count": len(info["players"]),
            }
            for gid, info in _games.items()
        }


async def join_game(game_id: str, player_id: str):
    async with _lock:
        if game_id in _games:
            await sio.emit("join", {"game_id": game_id, "player": player_id})
            _games[game_id]["players"].add(player_id)


async def leave_game(game_id: str, player_id: str):
    async with _lock:
        if game_id in _games:
            _games[game_id]["players"].discard(player_id)
