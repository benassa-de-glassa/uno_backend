import logging
import datetime

import socketio
from fastapi import APIRouter, WebSocket

from assets.game import Inegleit

router = APIRouter()

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=False
)

# make websocket logger less verbose

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('geventwebsocket.handler').setLevel(logging.ERROR)

logger = logging.getLogger("backend")


# main game object
inegleit = Inegleit() #(seed=1, testcase=1) # seed
#inegleit = Inegleit()

async def emit_server_message(message):
    await sio.emit('message', 
            { 
                "message": { "sender": "server", 
                             "text": message,
                             "time": datetime.datetime.now().strftime("%H:%M:%S") }
            }
        )

async def emit_player_state(player_id, message):
    await sio.emit('playerstate',
        {
            'player_id': player_id,
            'message': message
        }
    )
    
@router.post('/add_player')
async def add_player(player_name: str):
    response = inegleit.add_player(player_name)
    if response["requestValid"]:
        await emit_server_message(f"{response['player']['name']} joined.")
    return response

@router.post('/remove_player')
def remove_player(player_id: int):
    """
    Entfernt einen Spieler aus dem Spiel
    """
    return inegleit.remove_player(player_id)

@router.post('/kick_player')
async def kick_player(player_id: int, from_id: int):
    """
    Der Spieler mit der ID from_id entfernt den Spieler mit id player_id 
    aus dem Spiel.
    """
    response = inegleit.remove_player(player_id)
    if response["requestValid"]:
        await emit_server_message(f"{response['name']} has been (forcibly) "
            f"removed by {inegleit.players[from_id].attr['name']}!")
        await emit_player_state(player_id, "kicked")

    return response

@router.post('/start_game')
def start_game():
    """
    beginnt das Spiel
    """
    return inegleit.start_game()

@router.post('/deal_cards')
def deal_cards(player_id: int, n_cards: int):
    """
    Teilt karten aus dem Deck an Spieler aus
    """
    return inegleit.deal_cards(player_id, n_cards)

@router.get('/top_card')
def top_card():
    """
    Get the top card on the pile
    """
    return inegleit.get_top_card()

@router.get('/active_player')
def active_player():
    """
    gibt die ID des Spielers zurück der an der Reihe ist
    """
    return inegleit.get_active_player().attr

@router.post('/play_card')
async def play_card(player_id: int, card_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    response = inegleit.play_card(player_id, card_id)

    if not response["requestValid"] and "missedUno" in response:
        await emit_server_message(f"{response['missedUno']} failed to say Uno, you know the rules..")

    if response["requestValid"] and "inegleit" in response:
        await sio.emit('inegleit', {"playerName": response["inegleit"]})

    if response["requestValid"] and "playerWon" in response:
        if response["rank"] == 1:
            await emit_server_message("{} won. Congratulations!".format(response["playerFinished"]))
        else:
            rank = response["rank"] 
            text = ""
            if rank == 2: text = "2nd"
            elif rank == 3: text= "3rd"
            else: text = f"{rank}th"
            
            await emit_server_message(f"{response['playerFinished']} came in {text}. Well done!")
    return response
    
@router.post('/play_black_card')
async def play_black_card(player_id: int, card_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    response = inegleit.play_black_card(player_id, card_id)

    if not response["requestValid"] and "missedUno" in response:
        await emit_server_message(f"{response['missedUno']} failed to say Uno, you know the rules..")

    if response["requestValid"] and "inegleit" in response:
        await sio.emit('inegleit', {"playerName": response["inegleit"]})

    if response["requestValid"] and "playerFinished" in response:
        if response["rank"] == 1:
            await emit_server_message("{} won. Congratulations!".format(response["playerFinished"]))
        else:
            rank = response["rank"] 
            text = ""
            if rank == 2: text = "2nd"
            elif rank == 3: text= "3rd"
            else: text = f"{rank}th"
            
            await emit_server_message(f"{response['playerFinished']} came in {text}. Well done!")

    return response

@router.get('/cards')
def cards(player_id: int):
    return inegleit.get_cards(player_id)

@router.post('/choose_color')
def choose_color(player_id:int, color: str):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    return inegleit.event_choose_color(player_id, color)

@router.post('/pickup_card')
async def pickup_card(player_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    response = inegleit.event_pickup_card(player_id)

    if response["requestValid"] and "missedUno" in response:
        await emit_server_message(f"{response['missedUno']} failed to say Uno, you know the rules..")
    
    return response

@router.post('/cant_play')
def cant_play(player_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    return inegleit.event_cant_play(player_id)

@router.post('/say_uno')
async def say_uno(player_id: int):
    response = inegleit.event_uno(player_id)
    if response["requestValid"]:
        await emit_server_message(f"{response['name']} said UNO!")
    return response

@router.post('/reset_game')
async def reset_game(player_id: int):
    await emit_server_message("Game reset")
    await emit_player_state(-1, "kicked")
    return inegleit.reset_game(player_id)
