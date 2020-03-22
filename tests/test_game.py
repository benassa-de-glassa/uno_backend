import sys

from fastapi.testclient import TestClient

sys.path.append("../")
from main import app

client = TestClient(app)

class TestGame(): 

    def test_initialize_game(self):
        response = client.get('game/initialize_game')
        print("initialized:", response.json())

    def test_add_player(self, name):
        response = client.post('game/add_player?player_name={}'.format(name))
        print("added player", response.json())

    def test_deal_cards(self):
        response = client.post('game/deal_cards?player_id=0&n_cards=7')
        print("dealt cards", response.json())
    
    def test_start_game(self):
        response = client.get('game/start_game')
        print("started game", response.json())

    def test_top_card(self):
        response = client.post('game/top_card')
        print("top card:", response.json())

    def test_turn(self):
        response = client.get('game/turn')
        print("whose turn:", response.json())
    
    def test_valid_card(self):
        response = client.get('game/valid?card_id=5')
        print(response.json())

    def test_get_cards(self, player_id):
        response = client.get('game/cards?player_id={}'.format(player_id))
        print(response.json())

tester = TestGame()

tester.test_initialize_game()
tester.test_add_player("lara")
tester.test_add_player("bene")
tester.test_deal_cards()
tester.test_start_game()
tester.test_top_card()
tester.test_turn()
tester.test_get_cards(0)

