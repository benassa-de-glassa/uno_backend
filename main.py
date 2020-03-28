from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI

import uvicorn
#from fastapi.staticfiles import StaticFiles
#from fastapi.responses import HTMLResponse

import socketio

from routers import game
# from assets.game import Inegleit

# global inegleit
# inegleit = Inegleit()

from routers.game import inegleit

origins = [
    "*",
]


app = FastAPI(
    # title=config.PROJECT_NAME,
    # description=config.PROJECT_NAME,
    # version=config.PROJECT_VERSION,
    debug=True
)




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

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*' #','.join(config.ALLOW_ORIGIN)
)

sio_asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)


app.add_route("/socket.io/", route=sio_asgi_app)#, methods=['GET', 'POST'])
app.add_websocket_route("/socket.io/", sio_asgi_app)

background_task_started = False


async def background_task():
    while True:
        await sio.sleep(1)

        await sio.emit('player-list', 
            {
                'playerList': inegleit.get_all_players(),
                'turn': inegleit.get_active_player_id()
            }
        )


@sio.on('connect')
async def test_connect(sid, environ):
    print('connect', sid)

    global background_task_started
    if not background_task_started:
        sio.start_background_task(background_task)
        background_task_started = True

@sio.on('disconnect request')
async def disconnect_request(sid):
    await sio.disconnect(sid)

@sio.on('disconnect')
def test_disconnect(sid):
    print('Client disconnected')
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000 , debug=True)