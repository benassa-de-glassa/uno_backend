import sys

from fastapi.testclient import TestClient

sys.path.append("../")
from main import app, inegleit
from assets.deck import Card

client = TestClient(app)

def test_play():
    client.get('game/initialize_game')
    
    # add two players
    client.post('game/add_player?player_name=player1')
    client.post('game/add_player?player_name=player2')
    
    # make both of them have one black ? card
    card1 = inegleit.deck.get_card(100)
    card2 = inegleit.deck.get_card(101)
    card3 = inegleit.deck.get_card(3) # red 2
    card4 = inegleit.deck.get_card(4) # red 2
    inegleit.players[1].add_cards([card1])
    inegleit.players[2].add_cards([card2, card3, card4])

    inegleit.players[1].attr['said_uno'] = True

    response = client.post('game/play_black_card?player_id=1&card_id=100')
    print(response._content)
    print(inegleit.get_active_player_id())
    response = client.post('game/play_black_card?player_id=2&card_id=101')
    print(inegleit.n_players)
    print(response._content)


test_play()