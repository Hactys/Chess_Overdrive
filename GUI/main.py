import os
import asyncio
import uvicorn

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from GUI.core.templates import templates_path
from GUI.routers.game import router as game_router
from GUI.routers.lobby import router as lobby_router
from GUI.routers.ws import router as ws_router
from GUI.ws_game_client import init_connection, sio
from GUI.db.init_db import init_db


load_dotenv()


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


app.include_router(lobby_router)
app.include_router(game_router)
app.include_router(ws_router)

init_db()


if __name__ == "__main__":
    print("🚀 Chess Overdrive GUI → http://localhost:8000")
    uvicorn.run("GUI.main:app", host="0.0.0.0", port=8000, reload=True)
