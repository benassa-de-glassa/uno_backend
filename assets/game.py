import logging

import numpy as np

from .player import Player
from .deck import Deck

import json

DEBUG = True

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler('inegleit.log', mode='a'))
logger.debug("Logging started")

class Inegleit():
    """
    class members:
    
    n_players (int)     : number of players
    players (dict)      : dictionary of all players as {player_id: Player(class), ... }
    deck (class)        : deck handling the cards in the deck as well as the pile of used cards
    forward (bool)      : True if the playing direction is forward, False otherwise
    order (list)        : list of player ids in order
    active_index (int)  : index of the player in order whos turn it is

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
        Checks if the name is already taken or an emtpy string and adds 
        it to the player dict after assigning a unique ID. 
        """
        if not name:
            logger.debug("{} is not a valid name".format(name))
            return {"requestValid": False, "message": "choose non-empty string"}

        if name in [p.attr["name"] for p in self.players.values()]:
            logger.debug("Suggested name is already taken")
            return {"requestValid": False, "message": "name already taken"}

        player_id = self.unique_id
        self.unique_id += 1

        p = Player(name, player_id)
        self.players[player_id] = p
        self.n_players += 1
        self.order.append(player_id)

        logger.info("Added player: {} [{}]".format(name, player_id))
        
        return {"requestValid": True, "player": p.attr}
    
    def remove_player(self, player_id):
        logger.debug("Try to remove player ID {}".format(player_id))

        if not player_id in self.players.keys():
            logger.debug("player not found")
            return {"requestValid": False, "message": "player not found"}
        player = self.players[player_id]
        message = "Removed player: {}".format(player) 
        
        del self.players[player_id]
        self.order.remove(player_id)
        self.n_players -= 1

        # if the last player in self.order is active move to the next
        if self.active_index == self.n_players:
            self.penalty["next"] = 0
            self.next_player()

        logger.info(message)

        return {"requestValid": True, "message": message}

    def deal_cards(self, player_id, n):
        if not player_id in self.players.keys():
            logger.critical("Player with id {} not found!".format(player_id))
            return []
        # lifts the n top cards of the deck
        cards = self.deck.deal_cards(n)
        # adds them to the hand of the player with id=player_id
        self.players[player_id].add_cards(cards)

        logger.info("Dealt {} cards to player {} [{}]".format(n, self.players[player_id].attr["name"], player_id))
        
        return [card.attr for card in cards]

    def start_game(self):
        if not self.game_started:
            self.deck.place_starting_card()
            self.game_started = True

        message = "Started game. {}'s turn".format(self.get_active_player().attr["name"])

        logger.info(response)

        return {"requestValid": True, "message": message}

    def next_player(self):
        # resets the indicators
        self.card_picked_up = False

        # activates the penalty for the next player e.g. after playing a +2 card
        self.penalty["own"] = self.penalty["next"]
        self.penalty["next"] = 0

        # 2*bool-1 is 1 if true and -1 if false #maths
        i = (self.active_index + (2*self.forward-1)) % self.n_players
        self.active_index = i

        message = "{}'s turn. {} penalty cards".format(
                self.get_active_player().attr["name"],
                self.penalty["own"]
            )

        logger.info(message)

        return {"requestValid": True, "message": message}

    def get_active_player_id(self):
        if self.order != []:
            return self.order[self.active_index]
        else:
            return None

    def get_active_player(self):
        # if there are no players return an "empty" player
        if not self.n_players:
            return Player(None, -1)
        return self.players[self.get_active_player_id()]
    
    def get_all_players(self):
        return [ self.players[key].to_json() for key in self.players ]
    
    def get_top_card(self):
        # should not be needed with websockets working
        return self.deck.top_card().attr

    def get_cards(self, player_id):
        return [ card.attr for card in self.players[player_id].attr["hand"] ]

    def player_is_active(self, player_id):
        # helper method for readability
        return self.get_active_player_id() == player_id

    def test_validate_move(self, player, card, top_card):
        if not self.player_is_active(player.attr["id"]):
            # checks if the card can be inegleit
            if card.inegleitable(top_card):
                # if the card can be inegleit make the player the active player
                # and go to the next player
                self.active_index = self.order.index(player.attr["id"])

                if self.penalty["own"]:
                    assert card.able_to_raise_penalty(top_card)
                    return {"requestValid": True, "inegleit": True, "raisePenalty": True}
                return {"requestValid": True, "inegleit": True}
            else: 
                # remove requests to 'inegleit' a card
                return {"requestValid": False, "message": "not your turn, not possible to inegleit"}
        
        # ==> player is active

        # checks if the player has a penalty (= cards to pick up)
        if self.penalty["own"]:
            if card.able_to_raise_penalty(top_card):
                return {"requestValid": True, "raisePenalty": True}
            else:
                return {"requestValid": False, "message": "pick up {} cards first".format(self.penalty["own"])}
        
        if player.attr["penalty"]:
            return {"requestValid": False, "message": "pick up {} cards as punishment".format(player.attr["penalty"])}

        # checks if the card can be played, argument chosen_color is only
        # relevant if a black card lies on top
        if top_card.attr["color"] == "black":
            if card.attr["color"] == self.chosen_color:
                # reset color choice to empty
                self.chosen_color = ""
                return {"requestValid": True}
            else:
                return {"requestValid": False, "message": "play color {}".format(self.chosen_color)}

        elif not card.playable(top_card):
            # remove request to play a wrong card
            return {"requestValid": False, "message": "card not playable"}

        return {"requestValid": True}

    def test_play_card(self, player_id, card_id):
        card = self.deck.get_card(card_id)
        player = self.players[player_id]
        top_card = self.deck.top_card()

        logger.debug("Request from [{}] to play {} on {}".format(player_id, card, top_card))
       
        response = self.test_validate_move(player, card, top_card)
        
        logger.debug(response)

        if not response["requestValid"]:
            return response

        # ==> move is valid

        # if the move is valid although there is a penalty this means
        # the player can raise the penalty for the next player
        if self.penalty["own"]:
            self.penalty["next"] = self.penalty["own"]
            self.penalty["own"] = 0
            
        message = "card played"
        if card.attr["number"] == 10: # reverse direction
            self.forward = not self.forward
            message += ", reversed direction"
        elif card.attr["number"] == 11: # skip player
            self.next_player() # skips this player
            message += ", next player skipped"
        elif card.attr["number"] == 12: # +2
            self.penalty["next"] += 2
            message += ", +{} for the next player".format(self.penalty["next"])

        self.deck.play_card(card)
        player.remove_card(card)

        logger.debug("{} played {}".format(player, card))

        if not player.attr["hand"]: # empty list <=> player has no cards left
            return self.player_finished()
            
        self.next_player()

        response["message"] = message

        return response


    def event_play_card(self, player_id, card_id):
        """ 
        Handles the request from [player_id] to play [card_id].

        Returns ( card_played(bool), response(str) )
        """
        
        card = self.deck.get_card(card_id)
        player = self.players[player_id]
        top_card = self.deck.top_card()

        logger.debug("Request from [{}] to play {} on {}".format(player_id, card, top_card))

        is_inegleit = False

        # asserts that the player actually has the card
        if not player.has_card(card):
            response = "player does not have that card"
            logger.warning("Move denied:" + response)
            return {"requestValid": False, "message": response}

        response = "" 

        # if the card is played ontop of a black card reset the chosen color to ""
        reset_color = False 

        if not self.player_is_active(player_id):
            # checks if the card can be inegleit
            if card.inegleitable(top_card):
                # if the card can be inegleit make the player the active player
                # and go to the next player
                self.active_index = self.order.index(player_id)
                is_inegleit = True
                response = "inegleit!"
            else: 
                # remove requests to 'inegleit' a card
                return {"requestValid": False, "message": "not your turn, not possible to inegleit"}
         
        else: # player is active
            # checks if the card can be played, argument chosen_color is only
            # relevant if a black card lies on top
            if top_card.attr["color"] == "black":
                if not card.attr["color"] == self.chosen_color:
                    return {"requestValid": False, "message": "play color {}".format(self.chosen_color)}
                reset_color = True

            elif not card.playable(top_card):
                # remove request to play a wrong card
                return {"requestValid": False, "message": "card not playable"}
        
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
                return {"requestValid": False, "message": "pick up {} cards first".format(self.penalty["own"])}

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

        if DEBUG:
            print("{} played {}".format(player, card))

        if not player.attr["hand"]: # player has no cards left
            return self.player_finished()
        if reset_color:
            self.chosen_color = ""

        self.next_player()

        responseJSON = {
            "requestValid": True, 
            "inegleit": is_inegleit, 
            "message": response
        }
        
        return responseJSON

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
                response += "inegleit!"
            else: 
                # remove requests to 'inegleit' a card
                return [False, "not your turn, not possible to inegleit"]

        # checks if there are still cards that have to be picked up
        if self.penalty["own"]:
            tmp = self.penalty["own"]
            if card.attr["number"] == 1 and self.penalty["type"] == 4:
                self.penalty["next"] = tmp + 4
                self.penalty["own"] = 0     
                response += " +{} for the next player".format(tmp+2)
            else:
                # remove requests to play when there are still cards that have to be 
                # picked up AND NO +4 is played
                return [False, "pick up {} cards first".format(self.penalty["own"])]
        
        elif card.attr["number"] == 1: # +4
            self.penalty["type"] = 4
            self.penalty["next"] = 4
            response += " +4 for the next player"

        self.can_choose_color = True
        response += "choose color"
        
        self.deck.play_card(card)
        player.remove_card(card)

        if not player.attr["hand"]: # player has no cards left
            return self.player_finished()

        if DEBUG:
            print("{} played {}".format(player, card))
        
        return [True, response]
    
    def event_choose_color(self, player_id, color):
        if not self.can_choose_color:
            return [False, "not allowed to choose color"]
        if not player_id == self.get_active_player_id():
            return [False, "not your turn"]

        response = "{} chose color {}".format(self.players[player_id], color)

        if DEBUG:
            print(response)

        self.chosen_color = color
        self.can_choose_color = False
        self.next_player()

        return (True, response)

    def event_cant_play(self, player_id):
        return self.next_player()
    
    def event_pickup_card(self, player_id):
        """ 
        returns (bool1, bool2, str)

        bool1   : card picked up
        bool2   : true if the card was picked up because of a penalty
        str     : response
        """
        if player_id != self.get_active_player_id():
            return [False, False, "not your turn"]

        response = "picked up card"
        reason_is_penalty = False # frontend needs to know if the card was picked up due to penalty or not

        if self.penalty["own"]:
            reason_is_penalty = True
            self.penalty["own"] -= 1
            response += ", take {} more".format(self.penalty["own"])
        elif not self.card_picked_up:
            self.card_picked_up = True
        else:
            return (False, False, "you already have enough cards")

        card = self.deck.deal_cards(1) # returns a list of length 1
        self.players[player_id].add_cards(card)
        self.players[player_id].attr["said_uno"] = False

        if self.penalty["type"] == "uno" and not self.penalty["own"]:
            # if the player takes cards for not saying uno, move to the next player
            # after picking up two instead of letting him play
            self.penalty["type"] = 0
            self.next_player()

        if DEBUG:
            print("{} picks up {}".format(self.players[player_id], card[0]))

        return (True, reason_is_penalty, response)
        
    def event_uno(self, player_id):
        player = self.players[player_id]
        if len(player.attr["hand"]) == 1:
            player.attr["said_uno"] = True
            return (True, "UNO")
        else: 
            return (False, "you have the wrong number of cards ({})".format(len(player.attr["hand"])))

    def player_finished(self):
        player = self.get_active_player()
        if player.attr["said_uno"]:
            if not player.attr["penalty"]:
                return (True, "{} won. Congratulations!".format(player.attr["name"]))
            else:
                return (False, "Player has an active penalty of {} cards.".format(player.attr["penalty"]))
        else:
            self.penalty["own"] = 2
            self.penalty["type"] = "uno"
            return (False, "{} didn't say uno, pick up two cards!".format(player.attr["name"]))    
    
    def reset_game(self):
        self.__init__(seed=self.seed)

    # def to_json(self, filename):
    #     game = {
    #         'game': 'uno',
    #         'direction': self.forward,
    #         'players': [player.to_json() for player in self.players],
    #         'deck': self.deck.to_json(), 
    #     }
    #     with open(filename, 'w') as outfile:
    #         json.dump(game, outfile)

    # def from_json(self, filename):
    #     with open(filename, 'r') as infile:
    #         game = json.load(infile)

    #         self.forward = game['direction']
    #         self.players = [Player(self, player['name']) for player in game['players']]
    #         self.deck = Deck().from_json(game['deck'])
