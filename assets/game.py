import numpy as np

from .player import Player
from .deck import Deck

import json

class Inegleit():
    def __init__(self):
        self.players = []
        self.deck = Deck()

        # playing direction
        self.forward = True

    def add_player(self, name, id=0):
        p = Player(self, name, id)

        self.players.append(p)

    def remove_player(self, id):
        pass

    def start_game(self):
        for p in self.players:
            dealt_cards = self.deck.deal_cards(7)

            p.add_cards(dealt_cards)

    def reverse_direction(self):
        self.forward = not self.forward

    def to_json(self, filename):
        game = {
            'game': 'uno',
            'direction': self.forward,
            'players': [player.to_json() for player in self.players],
            'deck': self.deck.to_json(), 
        }
        with open(filename, 'w') as outfile:
            json.dump(game, outfile)

    def from_json(self, filename):
        with open(filename, 'r') as infile:
            game = json.load(infile)

            self.forward = game['direction']
            self.players = [Player(self, player['name']) for player in game['players']]
            self.deck = Deck().from_json(game['deck'])


