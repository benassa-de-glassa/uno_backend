import os
import mock

from uno_backend.main import app

from fastapi.testclient import TestClient
client = TestClient(app)

class TestAPI: 

    def test_get_players(self):
        response = client.get('/game/')
        print(response)