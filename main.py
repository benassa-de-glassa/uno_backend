from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from .routers import game, player

app = FastAPI()


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(
    game.router,
    prefix='/game')

app.include_router(
    player.router,
    prefix='/player')

