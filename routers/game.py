from fastapi import APIRouter

router = APIRouter()

@router.post('/karten_verteilen')
def karten_verteilen():
    """
    Teilt karten aus dem Deck an Spieler aus
    """

    for player in players:
        pass

@router.get('/turn')
def whose_turn():
    """
    returns the id of the player whose turn it is
    """
    pass

@router.get('/valid_card')
def valid_card(card_id: int):
    """
    returns whether the next card is valid to be played
    """
    pass