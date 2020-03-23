import numpy as np

from .player import Player
from .deck import Deck

import json

DEBUG = True

class Inegleit():
    """
    class members:
    
    n_players (int)     : number of players
    players (list)      : list of all Player(class)
    deck (class)        : deck handling the cards in the deck as well as the pile of used cards
    forward (bool)      : True if the playing direction is forward, False otherwise
    order (list)        : list of userids in order
    active_player (int) : index of the player in order whos turn it is

    methods:

    add_player(name, index) :
    remove_player()         :
    start_game()            : initializes the game and assigns each player an index
    
    """

    def __init__(self):
        self.unique_id = 0 # counts up from 0 to assign unique ids
        self.n_players = 0
        self.players = {}
        self.deck = Deck()

        # playing direction
        self.forward = True
        self.order = []

        self.active_player = 0

    def add_player(self, name):
        """ 
        creates player "name", returns the unique id
        """
        uid = self.unique_id
        self.unique_id += 1

        p = Player(name, uid)
        self.players[uid] = p
        self.n_players += 1
        self.order.append(uid)

        if DEBUG:
            print("Added player: {} [{}]".format(name, uid))
        
        return uid
    
    def remove_player(self, uid):
        pass

    def deal_cards(self, uid, n):
        # lifts the n top cards of the deck
        cards = self.deck.deal_cards(n)
        # adds them to the hand of the player with id=uid
        self.players[uid].add_cards(cards)

        if DEBUG:
            print("Deal {} cards to player {} [{}]".format(n, self.players[uid].attr["name"], uid))
        
        return [card.attr for card in cards]

    def start_game(self):
        if DEBUG:
            print("Started game")
        self.deck.place_starting_card()

    def next_player(self, n=1):
        # n=2 means one player is skipped
        i = (self.active_player + self.forward*n) % self.n_players
        self.active_player = i

    def get_active_player_id(self):
        return self.order[self.active_player]
    
    def top_card(self):
        return self.deck.get_top_card().attr

    def get_cards(self, pid):
        return [ card.attr for card in self.players[pid].attr["hand"] ]

    def event_play_card(self, player_id, card_id):
        """ 
        event triggered by the player
        
        """
        card = self.deck.get_card(card_id)
        top_card = self.deck.get_top_card()

        player = self.players[player_id]

        if DEBUG:
            print("player active:", player_id == self.active_player)

        if player_id != self.active_player:
            # checks if the card can be inegleit
            if card.inegleitable(top_card):
                # if the card can be inegleit make the player the active player
                # and go to the next player
                self.deck.play_card(card)
                self.active_player = player_id
                self.next_player()
                return [True, "inegleit"]
            else: 
                return [False, "not possible to inegleit"]
        
        if player_id == self.active_player:
            if not card.playable(top_card):
                return [False, "card not playable"]
            
            else:
                self.deck.play_card(card)
                
                msg = ""

                # handle black cards
                if card.attr["color"] == "black":
                    if card.attr["number"] == 0: # choose color
                        msg = "choose color"
                    if card.attr["number"] == 1: # +4 and choose color
                        msg = "choose color, +4 for the next player"
            
                # handle colored cards
                elif card.attr["number"] == 10: # reverse direction
                    self.forward = not self.forward
                    msg = "reverse direction"
                elif card.attr["number"] == 11: # skip player
                    self.next_player() # skips this player
                    msg = "next player skipped"
                elif card.attr["number"] == 12: # +2
                    msg = "+2 for the next player"

                player.remove_card(card)
                self.next_player()
                return [True, msg]

            

    def event_pickup_card(self, player, n=1):
        cards = self.deck.deal_cards(n) # list of length n
        player.add_cards(cards)
        player.said_uno == False

    def event_cant_play(self):
        self.next_player()

    def event_uno(self, player):
        if len(player.hand) == 1:
            player.said_uno == True
        else: pass # TODO: tell the player he's an idiot

    def event_player_finished(self, player):
        if player.said_uno:
            pass # congratulate him
        else:
            pass # force him to pick up two cards and laugh at him
      

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
