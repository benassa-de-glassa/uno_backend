from fastapi import APIRouter, WebSocket
import os

from assets.game import Inegleit

router = APIRouter()

inegleit = Inegleit()

game_file = 'uno.json'

@router.get('/initialize_game')
def initialize_game():    
    pass
    
@router.post('/add_player')
def add_player(player_name: str):
    uid = inegleit.add_player(player_name)
    return { "name": player_name, "id": uid}

@router.get('/start_game')
def start_game():
    """
    beginnt das Spiel
    """
    inegleit.start_game()

@router.post('/deal_cards')
def deal_cards(player_id: int, n_cards: int):
    """
    Teilt karten aus dem Deck an Spieler aus
    """
    cards = inegleit.deal_cards(player_id, n_cards)
    return [card for card in cards]

# @router.post('/top_card')
# def top_card():
#     """
#     Get the top card on the pile
#     """
#     tc = inegleit.top_card()
#     return tc

@router.get('/turn')
def whose_turn():
    """
    gibt die ID des Spielers zurück der an der Reihe ist
    """
    return inegleit.get_active_player_id()

@router.post('/play_card')
def play_card(player_id: int, card_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    pass

@router.post('/remove_player')
def remove_player(player_id: int):
    """
    Entfernt einen Spieler aus dem Spiel
    """
    pass

@router.get('/cards')
def cards(player_id: int):
    return inegleit.get_cards(player_id)
    
@router.websocket('/top_card')
async def top_card(websocket: WebSocket):

    await websocket.accept()
    while True:
        tc = inegleit.top_card()
        await websocket.send_text(f"Message text was {tc}")
