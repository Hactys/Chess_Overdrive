import uuid
import requests

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from core.templates import templates
from services.game_registry import register_game, list_games, join_game


ENGINE_HTTP = "http://localhost:5000"

router = APIRouter()


@router.get("/")
async def lobby(request: Request):
    games = await list_games()
    return templates.TemplateResponse(
        "lobby.html",
        {"request": request, "games": games}
    )


@router.post("/create_game")
async def create_game():
    game_id = str(uuid.uuid4())[:8]  # TODO : quand on aura des ids de joueur il faudra faire une génération en fonction des ids des deux joueurs et du temps par exemple
    player_id = "white"  # TODO : à changer quand on aura des ids de joueurs

    # Création côté moteur
    try:
        requests.post(
            f"{ENGINE_HTTP}/create",
            json={
                "game_id": game_id,
                "players": {"white": {}, "black": {}}
            }
        )
        print(f"🆕 Partie créée : {game_id}")
    except Exception as e:
        print("❌ Erreur création partie moteur :", e)

    await register_game(game_id)
    await join_game(game_id, player_id)

    return RedirectResponse(
        url=f"/game/{game_id}",
        status_code=303
    )


@router.post("/join/{game_id}")
async def join_existing_game(game_id: str):
    player_id = "white"  # TODO : à changer quand on aura des ids de joueurs
    await join_game(game_id, player_id)
    return RedirectResponse(
        url=f"/game/{game_id}",
        status_code=303,
    )