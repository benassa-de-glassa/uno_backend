import sys

from fastapi.testclient import TestClient

sys.path.append("../")
from main import app

client = TestClient(app)

class TestGame: 

    def test_initialize_game(self):
        response = client.get('game/initialize_game')
        print(response)

    def test_add_player(self, name):
        response = client.post('game/add_player?player_name={}'.format(name))
        print(response)

    def test_deal_cards(self):
        response = client.get('game/deal_cards')
        print(response)
        
    def test_turn(self):
        response = client.get('game/turn')
        print(response)
    
    def test_valid_card(self):
        response = client.get('game/valid')
        print(response)

tester = TestGame()

tester.test_initialize_game()
tester.test_add_player("lara")
tester.test_add_player("bene")
