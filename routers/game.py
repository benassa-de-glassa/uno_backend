from fastapi import APIRouter
import os

from assets.game import Inegleit

router = APIRouter()

# main game object
inegleit = Inegleit()
    
@router.post('/add_player')
def add_player(player_name: str):
    uid = inegleit.add_player(player_name)
    return { "name": player_name, "id": uid}

@router.post('/remove_player')
def remove_player(player_id: int):
    """
    Entfernt einen Spieler aus dem Spiel
    """
    pass

@router.post('/start_game')
def start_game():
    """
    beginnt das Spiel
    """
    inegleit.start_game()
    return 200

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
    return inegleit.get_active_player()

@router.post('/play_card')
def play_card(player_id: int, card_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    return inegleit.event_play_card(player_id, card_id)
    

@router.post('/play_black_card')
def play_black_card(player_id: int, card_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    return inegleit.event_play_black_card(player_id, card_id)

@router.get('/cards')
def cards(player_id: int):
    return inegleit.get_cards(player_id)

@router.post('/choose_color')
def choose_color(color: str):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    und spielt diese im backend
    """
    inegleit.choose_color(color)
    return 200
    
