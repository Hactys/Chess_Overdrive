from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.room_manager import room_manager
from services.state_cache import get_state


router = APIRouter()


@router.websocket("/ws/{game_id}")
async def ws_game(ws: WebSocket, game_id: str):
    await ws.accept()
    room_manager.join(game_id, ws)

    # push initial
    state = await get_state(game_id)
    if state:
        await ws.send_text("update_state")

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        room_manager.leave(game_id, ws)
