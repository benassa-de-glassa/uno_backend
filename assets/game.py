import numpy as np

from .player import Player
from .deck import Deck

import json

DEBUG = True

class Inegleit():
    """
    class members:
    
    n_players (int)     : number of players
    players (dict)      : dictionary of all players as {player_id: Player(class), ... }
    deck (class)        : deck handling the cards in the deck as well as the pile of used cards
    forward (bool)      : True if the playing direction is forward, False otherwise
    order (list)        : list of player ids in order
    active_index (int) : index of the player in order whos turn it is

    methods:

    add_player(name, index)
    remove_player()        
    start_game()
    deal_cards(id, n)   : deals n cards to player id
    """

    def __init__(self, seed=None):
        self.seed = seed
        self.game_started = False

        self.unique_id = 0 # counts up from 0 to assign unique ids
        self.n_players = 0 # number of participating players
        self.players = {}  # dictionary of {player_id: Player object}
        self.deck = Deck(seed) # Deck object

        self.order = []         # list of all player ids, has length n_players
        self.active_index = 0   # index of self.order representing the active player id

        # playing direction
        self.forward = True

        # Takes the value of a color if only one color can be played after a black card
        self.can_choose_color = False
        self.chosen_color = "" 

        # penalty cards that have to be picked up
        # own   : cards that the active player has to pick up
        # next  : cards that the next player has to pick up
        # type  : either "2" or "4" from "+2" or "+4 cards" 
        self.penalty = {
            "own": 0,
            "next": 0,
            "type": 0
        }

        self.card_picked_up = False

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
        if DEBUG:
            name = self.players[uid].attr["name"]
            print("Removed player: {} [{}]".format(name, uid))
        
        del self.players[uid]

    def deal_cards(self, uid, n):
        # lifts the n top cards of the deck
        cards = self.deck.deal_cards(n)
        # adds them to the hand of the player with id=uid
        self.players[uid].add_cards(cards)

        if DEBUG:
            print("Dealt {} cards to player {} [{}]".format(n, self.players[uid].attr["name"], uid))
        
        return [card.attr for card in cards]

    def start_game(self):
        if not self.game_started:
            self.deck.place_starting_card()
            self.game_started = True

            if DEBUG:
                print("Started game")

    def next_player(self):
        if not self.get_active_player().attr["hand"]: # player has no cards left
            self.player_finished()

        self.penalty["own"] = self.penalty["next"]
        self.penalty["next"] = 0
        i = (self.active_index + self.forward) % self.n_players
        self.active_index = i

        if DEBUG:
            print("{}'s turn. {} penalty cards".format(
                self.get_active_player().attr["name"],
                self.penalty["own"]
            ))
            
        return (True, "{}'s turn".format(self.get_active_player.attr["name"]))

    def get_active_player_id(self):
        return self.order[self.active_index]

    def get_active_player(self):
        if not self.n_players:
            return [{"id": -1, "name": "no players yet"}]
        return self.players[self.get_active_player_id()]
    
    def get_top_card(self):
        return self.deck.top_card().attr

    def get_cards(self, player_id):
        return [ card.attr for card in self.players[player_id].attr["hand"] ]
    
    def event_play_card(self, player_id, card_id):
        """ 
        check if the card can be played and play it if it can
        returns [bool, "response"]

        """
        card = self.deck.get_card(card_id)
        player = self.players[player_id]

        # asserts that the player actually has the card
        if not player.has_card(card):
            return [False, "player does not have that card"]

        top_card = self.deck.top_card()

        response = "" 

        active_id = self.get_active_player_id()

        if DEBUG:
            print("player active:", player_id == active_id)

        if player_id != active_id:
            # checks if the card can be inegleit
            if card.inegleitable(top_card):
                # if the card can be inegleit make the player the active player
                # and go to the next player
                self.active_index = self.order.index(player_id)
                response = "inegleit!"
            else: 
                # remove requests to 'inegleit' a card
                return [False, "not your turn, not possible to inegleit"]

        if player_id == active_id:
            # checks if the card can be played, argument chosen_color is only
            # relevant if a black card lies on top
            if top_card.attr["color"] == "black":
                if not card.attr["color"] == self.chosen_color:
                    return [False, "play color {}".format(self.chosen_color)]
            
            elif not card.playable(top_card):
                # remove request to play a wrong card
                return [False, "card not playable"] 
        
        # only valid cards from the active player make it until here
        
        # handle +2 card:
        # works for both inegleit and a normally played card
        # if there is still a penalty i.e. cards that the player has to pick up
        if self.penalty["own"]:
            
            if card.attr["number"] == 12 and self.penalty["type"] == 2:
                tmp = self.penalty["own"]
                self.penalty["next"] = tmp + 2
                self.penalty["own"] = 0
                response = "+{} for the next player".format(tmp+2)
            else:
                # remove requests to play when there are still cards that have to be 
                # picked up AND NO +2 is played
                return [False, "pick up {} cards first".format(self.penalty["own"])]

        # only valid cards from the active player without a penalty make it here

        if card.attr["number"] == 10: # reverse direction
            self.forward = not self.forward
            response = "reversed direction"
        elif card.attr["number"] == 11: # skip player
            self.next_player() # skips this player
            response = "next player skipped"
        elif card.attr["number"] == 12: # +2
            self.penalty["type"] = 2
            self.penalty["next"] = 2
            response = "+2 for the next player"
        
        if response == "":
            response = "successful"

        self.deck.play_card(card)
        player.remove_card(card)
        self.next_player()
        
        return [True, response]

    def event_play_black_card(self, player_id, card_id):
        card = self.deck.get_card(card_id)
        player = self.players[player_id]

        # asserts that the player actually has the card
        if not player.has_card(card):
            return [False, "player does not have that card"]

        top_card = self.deck.top_card()
        
        response = ""

        active_id = self.get_active_player_id()
        if player_id != active_id:
            # checks if the card can be inegleit
            if card.inegleitable(top_card):
                # if the card can be inegleit make the player the active player
                # and go to the next player
                self.active_index = self.order.index(player_id)
                response += "inegleit!, "
            else: 
                # remove requests to 'inegleit' a card
                return [False, "not your turn, not possible to inegleit"]

        # checks if there are still cards that have to be picked up
        if self.penalty["own"]:
            tmp = self.penalty["own"]
            if card.attr["number"] == 1 and self.penalty["type"] == 4:
                self.penalty["next"] = tmp + 4
                self.penalty["own"] = 0     
                response += ", +{} for the next player".format(tmp+2)
            else:
                # remove requests to play when there are still cards that have to be 
                # picked up AND NO +4 is played
                return [False, "pick up {} cards first".format(self.penalty["own"])]
        
        self.can_choose_color = True
        response += "choose color"
        
        if card.attr["number"] == 1: # +4
            self.penalty["type"] = 4
            assert self.penalty["next"] == 0
            self.penalty["next"] = 4
            response += ", +4 for the next player"
        
        self.deck.play_card(card)
        player.remove_card(card)

        if DEBUG:
            print("{} played {}".format(player, card))
        
        return [True, response]
    
    def event_choose_color(self, player_id, color):
        if not self.can_choose_color:
            return [False, "not allowed to choose color"]
        if not player_id == self.get_active_player_id():
            return [False, "not your turn"]
        assert color in ["red", "green", "blue", "yellow"]

        response = "{} chose color {}".format(player_id, color)

        if DEBUG:
            print(response)

        self.chosen_color = color
        self.can_choose_color = False
        self.next_player()

        return (True, response)

    def event_cant_play(self, player_id):
        self.next_player()
    
    def event_pickup_card(self, player_id):
        if player_id != self.get_active_player_id():
            return [False, "not your turn"]

        response = "picked up card"
        if self.penalty["own"]:
            self.penalty["own"] -= 1
            response += ", take {} more".format(self.penalty["own"])
        elif not self.card_picked_up:
            self.card_picked_up = True
        else:
            return (False, "you already have enough cards")

        card = self.deck.deal_cards(1) # returns a list of length 1
        self.players[player_id].add_cards(card)
        self.players[player_id].attr["said_uno"] = False

        if self.penalty["type"] == "uno" and not self.penalty["own"]:
            # if the player takes cards for not saying uno, move to the next player
            # after picking up two instead of letting him play
            self.penalty["type"] = 0
            self.next_player()

        return (True, response)
        
    def event_uno(self, player_id):
        player = self.players[player_id]
        if len(player.attr["hand"]) == 1:
            player.attr["said_uno"] = True
            return (True, "UNO")
        else: 
            return (False, "you have too many cards")

    def player_finished(self, player):
        if player.attr["said_uno"]:
            return (True, "{} won. Congratulations!".format(player.attr["name"]))
        else:
            self.penalty["own"] = 2
            self.penalty["type"] = "uno"
            return (False, "{} didn't say uno, pick up two cards!".format(player.attr["name"]))
      
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

    def reset_game(self):
        self.__init__(seed=self.seed)
