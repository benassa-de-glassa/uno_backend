import datetime
import logging

from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI

import uvicorn
import socketio

from routers import game

inegleit = game.inegleit
sio = game.sio

logger = logging.getLogger("backend")
logfilename = "inegleit.log"
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(logfilename, mode="a")
fh.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
logger.addHandler(fh)
logger.info("[{}] Logging started in {}".format(datetime.datetime.now().strftime("%H:%M:%S"), logfilename))

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

# mount the socket coming from the routers/game.py file
sio_asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)

app.add_route("/socket.io/", route=sio_asgi_app)
app.add_websocket_route("/socket.io/", sio_asgi_app)

message_id = 1
messages = []
message_queue = [
    {
        "id": 1,
        "sender": "server", 
        "text": "Viel Spass mit Inegleit Online!",
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    }
]

@app.post('/lobby/send_message')
async def send_message(player_name, client_message):
    global message_id
    message_id += 1
    message_queue.append(
        {            
            "id": message_id, 
            "sender": player_name, 
            "text": client_message,
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        }
    )

@app.middleware('http')
async def trigger_sio_event(request, call_next):
    response = await call_next(request)

    await sio.emit('top-card', 
        {
            'topCard': inegleit.get_top_card(),
        }
    )

    await sio.emit('gamestate',
        {
            'penalty': inegleit.penalty["own"] 
                       + inegleit.get_active_player().attr["penalty"],
            'colorChosen': inegleit.chosen_color != "",
            'chosenColor': inegleit.chosen_color,
            'activePlayerName': inegleit.get_active_player().attr["name"],
            'forward': inegleit.forward, 
        }
        )

    await sio.emit('player-list', 
        {
            'playerList': inegleit.get_all_players(),
            'turn': inegleit.get_active_player_id(),
        }
    )

    while message_queue:
        message = message_queue.pop(0)
        messages.append(message)
        await sio.emit('message', 
        {
            'message': message
        }
    )

    return response

@sio.on('connect')
async def test_connect(sid, environ):
    logger.debug(f"Socket id {sid} connected")
    print('connect', sid)

@sio.on('disconnect request')
async def disconnect_request(sid):
    logger.debug(f"Socket id {sid} disconnected")
    await sio.disconnect(sid)

@sio.on('disconnect')
def test_disconnect(sid):
    logger.debug(f"Client socket id {sid} disconnected")
    print('Client disconnected')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000 , debug=True)