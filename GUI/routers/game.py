from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from GUI.auth.dependencies import get_current_user
from GUI.ws_game_client import sio
from GUI.db.models.user import Users
from GUI.core.templates import templates
from GUI.services.renderer import render_board
from GUI.services.game_registry import list_games
from GUI.services.state_cache import (
    clear_proba,
    get_state,
    get_moves,
    get_selected,
    set_selected,
    clear_moves,
)


router = APIRouter()


@router.get("/game/{game_id}")
async def game_page(request: Request, game_id: str, user: Users = Depends(get_current_user)):
    games = await list_games()
    if game_id not in games.keys():  # Si la game_id est invalide, on renvoie sur le lobby
        return RedirectResponse(url=f"/", status_code=303)
    return templates.TemplateResponse(
        "game.html", {"request": request, "game_id": game_id, "user": user}
    )


@router.get("/game/{game_id}/board", response_class=HTMLResponse)
async def get_board(request: Request, game_id: str, user: Users = Depends(get_current_user)):
    state = await get_state(game_id)
    moves, probas = await get_moves(game_id)
    selected = await get_selected(game_id, user.id)

    return render_board(
        request, game_id, state, selected=selected, legal_moves=moves, capture_probas=probas
    )


@router.post("/game/{game_id}/click/{pos}", response_class=HTMLResponse)
async def click_square(
    request: Request, game_id: str, pos: str, user: Users = Depends(get_current_user)
):
    player_id = str(user.id)
    state = await get_state(game_id)
    moves, probas = await get_moves(game_id)
    selected = await get_selected(game_id, player_id)

    if not state:
        return render_board(request, game_id, None)

    current_player = state["current_player"]

    # Premier clic -> sélection + demande coups légaux
    if selected is None:
        await set_selected(game_id, player_id, pos)
        await sio.emit(
            "get_legal_moves",
            {"game_id": game_id, "from": pos, "player": current_player},
        )
        return render_board(
            request, game_id, state, selected=pos, legal_moves=moves, capture_probas=probas
        )

    # Second clic + coup valide
    if moves and pos in moves:
        await sio.emit(
            "action", {"game_id": game_id, "action": {"type": "move", "from": selected, "to": pos}}
        )
        await set_selected(game_id, player_id, None)
        await clear_moves(game_id)
        await clear_proba(game_id)
        return render_board(request, game_id, state)

    # Second clic sur une autre pièce -> changer sélection
    if pos in state["board"]["pieces"]:
        await set_selected(game_id, player_id, pos)
        await sio.emit(
            "get_legal_moves", {"game_id": game_id, "from": pos, "player": current_player}
        )
        return render_board(request, game_id, state, selected=pos)

    # Clic sur case vide non jouable -> clear sélection
    await set_selected(game_id, player_id, None)
    await clear_moves(game_id)
    return render_board(request, game_id, state)


@router.get("/game/{game_id}/overdrive")
async def overdrive_panel(request: Request, game_id: str):
    state = await get_state(game_id)
    return templates.TemplateResponse("overdrive.html", {"request": request, "state": state})


@router.get("/game/{game_id}/hand")
async def hand_panel(request: Request, game_id: str):
    state = await get_state(game_id)
    return templates.TemplateResponse("hand.html", {"request": request, "state": state})


@router.get("/game/{game_id}/captures")
async def captures_panel(request: Request, game_id: str):
    state = await get_state(game_id)
    return templates.TemplateResponse("captures.html", {"request": request, "state": state})
