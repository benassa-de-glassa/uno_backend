import os
import mock

from uno_backend.main import app

from fastapi.testclient import TestClient
client = TestClient(app)

class TestGame: 

    def test_start_game(self):
        response = client.get('game/start_game')
        print(response)

    
    def test_karten_verteilen(self):
        response = client.get('game/karten_verteilen')
        print(response)

        
    def test_turn(self):
        response = client.get('game/turn')
        print(response)

    
    def test_valid_card(self):
        response = client.get('game/valid')
        print(response)