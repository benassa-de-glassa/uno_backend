from fastapi import APIRouter
import os

from routers.player import karten
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
    print(player_name, uid)
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
    pass

@router.get('/turn')
def whose_turn():
    """
    gibt die ID des Spielers zurück der an der Reihe ist
    """
    pass

@router.post('/play_card')
def play_card(player_id: int, card_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    
    return karten(card_id)

@router.post('/add_player')
def add_player(player_name: str):
    """
    Fügt dem Spiel einen Spieler hinzu
    """
    pass

@router.post('/remove_player')
def remove_player(player_name: str):
    """
    Entfernt einen Spieler aus dem Spiel
    """
    pass

@router.get('/cards')
def karten(player_id:int):
    cards = [
        {'id': 1, 'color': 'green', 'number': 12},
        {'id': 2, 'color': 'red', 'number': 5},
        {'id': 3, 'color': 'blue', 'number': 10}
    ]
    try:
        cards.pop(player_id)
    except:
        print(player_id)
    return cards
