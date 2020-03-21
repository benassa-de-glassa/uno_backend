import numpy as np

from player import Player
from deck import Deck


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
