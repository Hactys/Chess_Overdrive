import uuid
import requests

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from core.templates import templates
from ws_game_client import join_game

ENGINE_HTTP = "http://localhost:5000"

router = APIRouter()


@router.get("/")
async def lobby(request: Request):
    return templates.TemplateResponse(
        "lobby.html",
        {"request": request}
    )


@router.post("/create_game")
async def create_game():
    game_id = str(uuid.uuid4())[:8]  # TODO : quand on aura des ids de joueur il faudra faire une génération en fonction des ids des deux joueurs et du temps par exemple

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

    await join_game(game_id)

    return RedirectResponse(
        url=f"/game/{game_id}",
        status_code=303
    )
