from fastapi import APIRouter
import os

from assets.game import Inegleit

from routers.player import karten

router = APIRouter()

game_file = 'uno.json'

@router.get('/start_game')
def start_game():
    """
    beginnt das Spiel
    """
    game = Inegleit()
    game.add_player('spieler 1')
    game.add_player('spieler 2')
    game.add_player('spieler 3')
    game.to_json(game_file)
    return 200


@router.post('/karten_verteilen')
def karten_verteilen(player_id: int, n_cards: int):
    """
    Teilt karten aus dem Deck an Spieler aus
    """
    game = Inegleit()
    game.from_json(game_file)


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
