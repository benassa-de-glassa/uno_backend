from fastapi import APIRouter, WebSocket

import socketio

from assets.game import Inegleit

router = APIRouter()

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=False
)

# make websocket logger less verbose
import logging
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('geventwebsocket.handler').setLevel(logging.ERROR)

logger = logging.getLogger("backend")


# main game object
inegleit = Inegleit() 

async def emit_server_message(message):
    await sio.emit('message', 
            { 
                "message": { "sender": "server", "text": message }
            }
        )

    
@router.post('/add_player')
def add_player(player_name: str):
    return inegleit.add_player(player_name)

@router.post('/remove_player')
def remove_player(player_id: int):
    """
    Entfernt einen Spieler aus dem Spiel
    """
    return inegleit.remove_player(player_id)

@router.get('/player_exists')
def add_player(player_id: int, player_name: str):
    for player in inegleit.get_all_players():
        if player_id == player['id'] and player_name == player['name']:
            return player
    return False

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

    if response["requestValid"] and "inegleit" in response:
        await sio.emit('inegleit', {"playerName": response["inegleit"]})

    if response["requestValid"] and "playerWon" in response:
        await emit_server_message("{} won. Congratulations!".format(response["playerWon"]))
        
    return response
    
@router.post('/play_black_card')
async def play_black_card(player_id: int, card_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    response = inegleit.play_black_card(player_id, card_id)

    if response["requestValid"] and "inegleit" in response:
        await sio.emit('inegleit', {"playerName": "Test"})

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
def pickup_card(player_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    return inegleit.event_pickup_card(player_id)

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
        await emit_server_message("{} said UNO!".format(player_id))
    return response

@router.post('/reset_game')
async def reset_game(player_id: int):
    await emit_server_message("Game reset")
    return inegleit.reset_game(player_id)
