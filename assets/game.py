import logging

import numpy as np

from .player import Player
from .deck import Deck

import json

DEBUG = True

logger = logging.getLogger("backend")

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

    def __init__(self, seed=None, testcase=None):
        self.seed = seed
        self.testcase = testcase

        if self.testcase:
            logger.warning("Initialized test case")
        if self.seed:
            logger.warning("Initialized game with seed")

        self.game_started = False

        self.unique_id = 1 # counts up from 1 to assign unique ids
        self.n_players = 0 # number of participating players
        self.players = {}  # dictionary of {player_id: Player object}
        self.deck = Deck(seed, testcase) # Deck object

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
            "next": 0
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
        
        if self.game_started:
            if self.get_active_player_id == player_id:
                # if the player is active, move to the next player without "baggage"
                self.penalty["next"] = 0
                if self.can_choose_color:
                    self.chosen_color = "red"
                    self.can_choose_color 
                self.next_player()
                
            # if the next player is the last player, the active index is too
            # large for the new self.order => decrease it by one
            if self.get_active_player_id == self.n_players:
                self.active_index -= 1
            
            # add his cards to the pile
            self.deck.add_to_pile(player.attr["hand"])

        del self.players[player_id]
        self.order.remove(player_id)
        self.n_players -= 1

        message = "Removed player: {}".format(player) 
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
        if n == 7:
            self.players[player_id].attr['has_received_initial_cards'] = True
        return [card.attr for card in cards]

    def start_game(self):
        if not self.game_started:
            self.deck.place_starting_card()
            self.game_started = True

            logger.info( "Started game. {}'s turn".format(self.get_active_player().attr["name"]) )
        
        return {"requestValid": True}

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

    def validate_move(self, player, card, top_card):
        if not self.player_is_active(player.attr["id"]):
            # checks if the card can be inegleit
            if card.inegleitable(top_card):
                # if the card can be inegleit make the player the active player
                # and go to the next player
                self.active_index = self.order.index(player.attr["id"])

                if self.penalty["own"]:
                    assert card.able_to_raise_penalty(top_card)
                    return {"requestValid": True, "inegleit": True, "raisePenalty": True}
                
                if self.penalty["next"] and card.attr["color"] == "black" and card.attr["number"] == 1:
                    # the card is a +4 that has been inegleit before a player chose a color
                    logger.debug("black +4 inegleit before choosing color")
                    #self.penalty["own"] = self.penalty["next"] 
                    #self.penalty["next"] = 0
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
        if top_card.attr["color"] == "black" and not card.attr["color"] == "black":
            if card.attr["color"] == self.chosen_color:
                # reset color choice to empty
                self.chosen_color = ""
                return {"requestValid": True}
            else:
                return {"requestValid": False, "message": "play color {}".format(self.chosen_color)}

        elif not card.playable(top_card):
            # remove request to play a wrong card
            return {"requestValid": False, "message": "card not playable"}

        if len(player.attr["hand"]) == 1:
            if player.attr["said_uno"]:
                return {"requestValid": True, "playerFinished": player.attr}
            else:
                player.attr["penalty"] = 2
                message = "{} didn't say uno, has to pick up two cards!".format(player)
                logger.info(message)
                return {"requestValid": False, "message": message}

        return {"requestValid": True}

    def play_card(self, player_id, card_id):
        card = self.deck.get_card(card_id)
        player = self.players[player_id]
        top_card = self.deck.top_card()

        logger.debug("Request from {} to play {} on {}".format(player, card, top_card))

        if not player.has_card(card):
            response = "player does not have that card"
            logger.warning("Move denied:" + response)
            return {"requestValid": False, "message": response}
       
        response = self.validate_move(player, card, top_card)
        
        logger.debug(response)

        if not response["requestValid"]:
            return response

        # ==> move is valid

        message = "card played"

        # if the move is valid although there is a penalty this means
        # the player can raise the penalty for the next player
        if self.penalty["own"]:
            self.penalty["next"] = self.penalty["own"]
            self.penalty["own"] = 0
            message += ", penalty raised"
        
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
        logger.debug("{} played {} >> ".format(player, card) + message)

        if not player.attr["hand"]:
            return self.player_finished(player)

        self.next_player()

        response["message"] = message
        return response

    def play_black_card(self, player_id, card_id):
        card = self.deck.get_card(card_id)
        player = self.players[player_id]
        top_card = self.deck.top_card()

        logger.debug("Request from {} to play {} on {}".format(player, card, top_card))

        if not player.has_card(card):
            response = "player does not have that card"
            logger.warning("Move denied:" + response)
            return {"requestValid": False, "message": response}
       
        response = self.validate_move(player, card, top_card)
        
        logger.debug(response)

        if not response["requestValid"]:
            return response

        # ==> move is valid
        self.can_choose_color = self.get_active_player_id()
        message = "{} can choose color".format(player)

        # if the move is valid although there is a penalty this means
        # the player can raise the penalty for the next player
        if self.penalty["own"]:
            self.penalty["next"] = self.penalty["own"]
            self.penalty["own"] = 0

        if card.attr["number"] == 1:
            self.penalty["next"] += 4
            self.penalty["own"] = 0     
            message += ", +{} for the next player".format(self.penalty["next"])
            
        self.deck.play_card(card)
        player.remove_card(card)

        if not player.attr["hand"]:
            return self.player_finished(player)

        logger.info("{} played {}".format(player, card))
        logger.debug(message)

        response["message"] = message
        return response
  
    def event_choose_color(self, player_id, color):
        logger.debug("Request from {} to choose color {}".format(self.players[player_id], color))
         
        if not player_id == self.get_active_player_id():
            response = {"requestValid": False, "message": "not your turn"}
            logger.debug(response)
            return response

        if self.can_choose_color != player_id:
            response = {"requestValid": False, "message": "not allowed to choose color (anymore)"}
            logger.debug(response)
            return response

        logger.info("{} chose color {}".format(self.players[player_id], color))

        self.chosen_color = color
        self.can_choose_color = False
        self.next_player()

        return {"requestValid": True, "color": color}

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
            return {"requestValid": False, "message": "not your turn"}

        message = "picked up card"
        reason_is_penalty = False # frontend needs to know if the card was picked up due to penalty or not

        if self.penalty["own"]:
            reason_is_penalty = True
            self.penalty["own"] -= 1
            message += ", take {} more".format(self.penalty["own"])
        elif self.players[player_id].attr["penalty"]:
            reason_is_penalty = True
            self.players[player_id].attr["penalty"] -= 1
            message += ", take {} more".format(self.players[player_id].attr["penalty"])

        elif not self.card_picked_up:
            self.card_picked_up = True
        else:
            self.next_player()
            return {"requestValid": False, "message": "you already have enough cards"}

        card = self.deck.deal_cards(1) # returns a list of length 1
        self.players[player_id].add_cards(card)
        self.players[player_id].attr["said_uno"] = False

        logger.debug("{} picks up {}".format(self.players[player_id], card[0]))

        return {"requestValid": True, "reasonIsPenalty": reason_is_penalty, "message": message}
        
    def event_uno(self, player_id):
        player = self.players[player_id]
        if len(player.attr["hand"]) == 1:
            player.attr["said_uno"] = True
            logger.info("{} said UNO".format(self.players[player_id]))
            return {"requestValid": True, "message": "UNO"}
        else: 
            return {"requestValid": False, "message": "you have the wrong number of cards ({})".format(len(player.attr["hand"]))}

    def player_finished(self, player):
        message = "{} won. Congratulations!".format(player)
        logger.info(message)
        return {"requestValid": True, "playerWon": player.attr["name"], "message": message}
            
    def reset_game(self, player_id):
        try:
            logger.info("Game reset by {}".format(self.players[player_id]))
        except KeyError:
            # if somebody else already reset the game there is no key anymore
            logger.warning("Game reset by former id {}".format(player_id))

        self.__init__(seed=self.seed, testcase=self.testcase)
        
        return {"requestValid": True}        

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



    # def event_play_card(self, player_id, card_id):
    #     """ 
    #     Handles the request from [player_id] to play [card_id].

    #     Returns ( card_played(bool), response(str) )
    #     """
        
    #     card = self.deck.get_card(card_id)
    #     player = self.players[player_id]
    #     top_card = self.deck.top_card()

    #     logger.debug("Request from [{}] to play {} on {}".format(player_id, card, top_card))

    #     is_inegleit = False

    #     # asserts that the player actually has the card
    #     if not player.has_card(card):
    #         response = "player does not have that card"
    #         logger.warning("Move denied:" + response)
    #         return {"requestValid": False, "message": response}

    #     response = "" 

    #     # if the card is played ontop of a black card reset the chosen color to ""
    #     reset_color = False 

    #     if not self.player_is_active(player_id):
    #         # checks if the card can be inegleit
    #         if card.inegleitable(top_card):
    #             # if the card can be inegleit make the player the active player
    #             # and go to the next player
    #             self.active_index = self.order.index(player_id)
    #             is_inegleit = True
    #             response = "inegleit!"
    #         else: 
    #             # remove requests to 'inegleit' a card
    #             return {"requestValid": False, "message": "not your turn, not possible to inegleit"}
         
    #     else: # player is active
    #         # checks if the card can be played, argument chosen_color is only
    #         # relevant if a black card lies on top
    #         if top_card.attr["color"] == "black":
    #             if not card.attr["color"] == self.chosen_color:
    #                 return {"requestValid": False, "message": "play color {}".format(self.chosen_color)}
    #             reset_color = True

    #         elif not card.playable(top_card):
    #             # remove request to play a wrong card
    #             return {"requestValid": False, "message": "card not playable"}
        
    #     # only valid cards from the active player make it until here
        
    #     # handle +2 card:
    #     # works for both inegleit and a normally played card
    #     # if there is still a penalty i.e. cards that the player has to pick up
    #     if self.penalty["own"]:
    #         if card.attr["number"] == 12 and self.penalty["type"] == 2:
    #             tmp = self.penalty["own"]
    #             self.penalty["next"] = tmp + 2
    #             self.penalty["own"] = 0
    #             response = "+{} for the next player".format(tmp+2)
    #         else:
    #             # remove requests to play when there are still cards that have to be 
    #             # picked up AND NO +2 is played
    #             return {"requestValid": False, "message": "pick up {} cards first".format(self.penalty["own"])}

    #     # only valid cards from the active player without a penalty make it here

    #     if card.attr["number"] == 10: # reverse direction
    #         self.forward = not self.forward
    #         response = "reversed direction"
    #     elif card.attr["number"] == 11: # skip player
    #         self.next_player() # skips this player
    #         response = "next player skipped"
    #     elif card.attr["number"] == 12: # +2
    #         self.penalty["type"] = 2
    #         self.penalty["next"] = 2
    #         response = "+2 for the next player"
        
    #     if response == "":
    #         response = "successful"

    #     self.deck.play_card(card)
    #     player.remove_card(card)

    #     if DEBUG:
    #         print("{} played {}".format(player, card))

    #     if not player.attr["hand"]: # player has no cards left
    #         return self.player_finished()
    #     if reset_color:
    #         self.chosen_color = ""

    #     self.next_player()

    #     responseJSON = {
    #         "requestValid": True, 
    #         "inegleit": is_inegleit, 
    #         "message": response
    #     }
        
    #     return responseJSON


    # def event_play_black_card(self, player_id, card_id):
    #     card = self.deck.get_card(card_id)
    #     player = self.players[player_id]

    #     # asserts that the player actually has the card
    #     if not player.has_card(card):
    #         return [False, "player does not have that card"]

    #     top_card = self.deck.top_card()
        
    #     message = ""

    #     active_id = self.get_active_player_id()
    #     if player_id != active_id:
    #         # checks if the card can be inegleit
    #         if card.inegleitable(top_card):
    #             # if the card can be inegleit make the player the active player
    #             # and go to the next player
    #             logger.debug("black card inegleit")
    #             logger.debug("current penalty: " + str(self.penalty) )
    #             self.active_index = self.order.index(player_id)
    #             message += "inegleit!"
    #         else: 
    #             # remove requests to 'inegleit' a card
    #             return [False, "not your turn, not possible to inegleit"]

    #     # checks if there are still cards that have to be picked up
    #     if self.penalty["own"]:
    #         tmp = self.penalty["own"]
    #         if card.attr["number"] == 1 and self.penalty["type"] == 4:
    #             self.penalty["next"] = tmp + 4
    #             self.penalty["own"] = 0     
    #             message += " +{} for the next player".format(tmp+2)
    #         else:
    #             # remove requests to play when there are still cards that have to be 
    #             # picked up AND NO +4 is played
    #             return [False, "pick up {} cards first".format(self.penalty["own"])]
        
    #     elif card.attr["number"] == 1: # +4
    #         self.penalty["type"] = 4
    #         self.penalty["next"] = 4
    #         message += " +4 for the next player"

    #     self.can_choose_color = self.get_active_player_id()
    #     message += "[{}] can choose color".format(self.can_choose_color)
        
    #     self.deck.play_card(card)
    #     player.remove_card(card)

    #     if not player.attr["hand"]: # player has no cards left
    #         return self.player_finished()

    #     logger.debug("{} played {}".format(player, card))
        
    #     return {"requestValid": True, "message": message}
  