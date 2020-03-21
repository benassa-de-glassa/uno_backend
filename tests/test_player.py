import os
import mock

from uno_backend.main import app

from fastapi.testclient import TestClient
client = TestClient(app)

class TestPlayer: 

    def test_start_game(self):
        response = client.get('player/add_player')
        print(response)

    
    def test_karten_verteilen(self):
        response = client.get('player/remove_player')
        print(response)
