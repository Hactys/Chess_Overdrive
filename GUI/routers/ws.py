import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from GUI.db.services.session import get_db_session_ctx
from GUI.db.services.users_sessions import validate_session
from GUI.services.room_manager import room_manager
from GUI.services.state_cache import get_state


router = APIRouter()


@router.websocket("/ws/{game_id}")
async def ws_game(ws: WebSocket, game_id: str):
    session_id = ws.cookies.get("session_id")

    with get_db_session_ctx() as db:
        session = validate_session(db, uuid.UUID(session_id))
        if not session:
            await ws.close(code=4401)
            return

        user_id = session.user_id
        username = session.user.username
        disambiguator = session.user.disambiguator

    ws.state.user_id = user_id
    ws.state.username = f"{username}#{disambiguator}"

    await ws.accept()
    room_manager.join(game_id, ws)

    # push initial
    state = await get_state(game_id)
    if state:
        await ws.send_text("update_state")
        if ws.state.user_id in state["players"]:
            ws.state.is_player = True
        else:
            ws.state.is_player = False

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        room_manager.leave(game_id, ws)
