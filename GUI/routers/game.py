from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ws_game_client import sio
from core.templates import templates
from services.renderer import render_board
from services.state_cache import get_state, get_moves, get_selected, set_selected, clear_moves


router = APIRouter()


@router.get("/board", response_class=HTMLResponse)
async def get_board(request: Request, selected: str | None = None):
    state = await get_state()
    moves, probas = await get_moves()
    return render_board(
        request,
        state,
        selected=selected,
        legal_moves=moves,
        capture_probas=probas
    )


@router.post("/click/{pos}", response_class=HTMLResponse)
async def click_square(request: Request, pos: str):
    state = await get_state()
    moves, probas = await get_moves()
    selected = await get_selected()

    if not state:
        return render_board(request, None)

    # Premier clic -> demander legal moves au moteur
    if selected is None:
        await set_selected(pos)
        await sio.emit("get_legal_moves", {
            "game_id": "test_game",
            "from": pos,
            "player": state["current_player"]
        })
        return render_board(request, state, selected=pos, legal_moves=moves, capture_probas=probas)

    # Second clic -> si movement possible
    if moves and pos in moves:
        await sio.emit("action",{
            "game_id":"test_game",
            "action":{"type":"move","from":selected,"to":pos}
        })
        await set_selected(None)
        await clear_moves()
        return render_board(request, state)

    # Second clic sur une autre pièce
    if pos in (state["board"]["pieces"].keys()):
        await set_selected(pos)
        await sio.emit("get_legal_moves", {
            "game_id":"test_game",
            "from": pos,
            "player": state["current_player"]
        })
        return render_board(request, state, selected=pos)

    # Clic sur case vide non jouable -> CLEAR HIGHLIGHT
    await set_selected(None)
    await clear_moves()
    return render_board(request, state)


@router.get("/overdrive")
async def overdrive_panel(request: Request):
    state = await get_state()
    return templates.TemplateResponse("overdrive.html", 
                                      {"request": request, "state": state})


@router.get("/hand")
async def hand_panel(request: Request):
    state = await get_state()
    return templates.TemplateResponse("hand.html", 
                                      {"request": request, "state": state})


@router.get("/captures")
async def captures_panel(request: Request):
    state = await get_state()
    return templates.TemplateResponse("captures.html", 
                                      {"request": request, "state": state})
