from fastapi import APIRouter

# from assets import Game, Player


router = APIRouter()

@router.get('/start_game')
def start_game():
    """
    beginnt das Spiel
    """
    pass

@router.post('/deal_cards')
def deal_cards():
    """
    Teilt karten aus dem Deck an Spieler aus
    """

    for player in players:
        pass

@router.get('/turn')
def whose_turn():
    """
    gibt die ID des Spielers zurück der an der Reihe ist
    """
    pass

@router.get('/valid_card')
def valid_card(card_id: int):
    """
    gibt zurück ob eine zu spielende Karte erlaubt ist
    """
    pass