#Nuestra api con endpoints
#Crear primero entorno virtual y descargar dependecias con "fastapi[standar]""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from fastapi.responses import RedirectResponse
from models import Base, engine  # Importa Base desde models.py
from routers import game, websocket, card, in_game, debugging, messages, timer
import uvicorn


# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Context manager to start and stop the application."""
    try:
        Base.metadata.create_all(engine)
        yield
    finally:
        pass

# FastAPI instance
app = FastAPI(
    title="The Switcher",
    description="The Switcher - Card Game",
    version="Demo 1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.game)
app.include_router(card.card)
app.include_router(in_game.in_game)
app.include_router(websocket.ws)
app.include_router(debugging.debug)
app.include_router(messages.messages)
app.include_router(timer.timer)

# Root router
@app.get("/", tags=["root"])
def redirect_to_docs():
    return RedirectResponse(url="/docs/")

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8000)