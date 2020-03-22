from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
#from fastapi.staticfiles import StaticFiles
#from fastapi.responses import HTMLResponse

from routers import game
from assets.game import Inegleit

global inegleit
inegleit = Inegleit()

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