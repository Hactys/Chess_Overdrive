import os
import asyncio
import uvicorn

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from GUI.core.templates import templates_path
from GUI.routers.auth import router as auth_router
from GUI.routers.game import router as game_router
from GUI.routers.lobby import router as lobby_router
from GUI.routers.ws import router as ws_router
from GUI.ws_game_client import init_connection, sio
from GUI.db.init_db import init_db


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🟡 Démarrage Chess Overdrive GUI...")
    init_db()
    # Lancement non-bloquant du client moteur
    asyncio.create_task(init_connection())
    print("🔌 Connexion au moteur en tâche de fond...")

    yield

    print("🛑 Fermeture Socket.IO...")
    try:
        await sio.disconnect()
    except:
        pass


app = FastAPI(lifespan=lifespan)

static_path = os.path.join(os.path.dirname(templates_path), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    """
    Redirection propre vers /login en cas de 401,
    compatible HTMX et requêtes HTML normales.
    """
    if exc.status_code != 401:
        raise exc

    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:  # Cas HTMX : on force une redirection client-side
        response = HTMLResponse("")
        response.headers["HX-Redirect"] = "/login"
        return response

    # Cas navigation classique
    return RedirectResponse(url="/login", status_code=303)


app.include_router(lobby_router)
app.include_router(game_router)
app.include_router(auth_router)
app.include_router(ws_router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(r"GUI\static\favicon.ico")


if __name__ == "__main__":
    print("🚀 Chess Overdrive GUI → http://localhost:8000")
    uvicorn.run("GUI.main:app", host="0.0.0.0", port=8000, reload=True)
