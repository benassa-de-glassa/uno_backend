from fastapi import APIRouter

router = APIRouter()

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
