from fastapi import APIRouter

router = APIRouter()

@router.post('/add_player')
def add_player(player_name: str):
    """
    Fügt dem Spiel einen Spieler hinzu
    """

@router.post('/remove_player')
def remove_player(player_name: str):
    """
    Entfernt einen Spieler aus dem Spiel
    """