import os
import asyncio
import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from core.templates import templates, templates_path
from routers.game import router as game_router
from routers.lobby import router as lobby_router
from routers.ws import router as ws_router
from ws_game_client import init_connection, sio


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🟡 Démarrage Chess Overdrive GUI...")
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


def probacolor(prob):
    r = int(255 * (1 - prob))
    g = int(255 * prob)
    return f"rgb({r},{g},0)"

templates.env.filters["probacolor"] = probacolor


app.include_router(lobby_router)
app.include_router(game_router)
app.include_router(ws_router)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    print("🚀 Chess Overdrive GUI → http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
