from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from routers import game, player

global game_object
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

# from assets.game import Inegleit
# @app.on_event('startup')
# def start_game():
#     game_object = Inegleit()
#     print(game_object)

app.mount('/', StaticFiles(directory='static', html=True), name='static')
