import logging

import json
import numpy as np

from .player import Player
from .deck import Deck


DEBUG = True

logger = logging.getLogger("backend")

class Inegleit():
    """
    Uno game instance handling the game logic, the players, and the
    cards.  All game actions from the players are requests sent via
    routers to the same game instance which verifies them, e.g.
    play_card().
    The return value is always a dict containing always the key
    {"requestValid": (bool)} to indicate if, for example after a request
    to play a card, the card has actually been played.  If the request
    is not valid, there isa {"message": (str)} keyword explaining the
    reason for the denied request.
    """

    def __init__(self, seed=None, testcase=None):
        # for testing purposes, only relevant for self.deck
        self.seed = seed            # for randomized card shuffling
        self.testcase = testcase    # creates a certain deck config.

        if self.testcase:
            logger.warning("Initialized test case")
        if self.seed:
            logger.warning("Initialized game with seed")

        self.game_started = False

        self.unique_id = 1  # counts up from 1 to assign unique ids
        self.n_players = 0  # number of participating players
        self.players = {}  # dictionary of {player_id: Player object}

        # Deck object handling the cards
        self.deck = Deck(seed, testcase)

        # order: list of all player ids, has length n_players
        # order[active_index] is the id of the active player
        self.order = []
        self.active_index = 0

        self.forward = True     # playing direction

        # indicators relevant for black cards being played
        self.can_choose_color = False
        self.chosen_color = ""

        # Penalty cards that have to be picked up (e.g. after +2)
        # "own"   : cards that the active player has to pick up
        # "next"  : cards that the next player has to pick up
        self.penalty = {
            "own": 0,
            "next": 0
        }

        # A player can only end his turn if he either played a card or
        # picked up a card
        self.card_picked_up = False

        # players that reached zero cards
        self.winners = []

    def add_player(self, name):
        """
        Answers requests to add a player.
        Checks if the name is valid (not already taken or emtpy) and
        assigns a unique id. Creates the player object.

        Returns the player attributes if the request is valid.
        """
        king = False
        # top secret way to become king
        if name.startswith("king "):
            name = name[5:]
            king = True
        
        elif self.n_players == 0:
            king = True

        # check for empty string
        if not name:
            logger.debug("{} is not a valid name".format(name))
            return {"requestValid": False, "message": "choose non-empty string"}

        # check for duplicate names
        if name in [p.attr["name"] for p in self.players.values()]:
            logger.debug("Suggested name is already taken")
            return {"requestValid": False, "message": "name already taken"}

        player_id = self.unique_id
        self.unique_id += 1

        p = Player(name, player_id, king=king)
        self.players[player_id] = p
        self.n_players += 1
        self.order.append(player_id)

        logger.info("Added player: {} [{}]".format(name, player_id))

        return {"requestValid": True, "player": p.attr}

    def remove_player(self, player_id):
        """
        Removes a player and adds his cards to the pile. Handles special
        situations such as the player being active or currently choosing
        a color. Special situations are not thoroughly tested.
        """
        logger.debug("Try to remove player ID {}".format(player_id))

        if not player_id in self.players.keys():
            logger.debug("player not found")
            return {"requestValid": False, "message": "player not found"}

        player = self.players[player_id]

        if self.game_started:
            # Handle special situations
            if self.get_active_player_id() == player_id:
                # if the player is active, move to the next player without "baggage"
                self.penalty["next"] = 0
                if self.can_choose_color:
                    self.chosen_color = "red"
                    self.can_choose_color = False
                self.next_player()

            # add his cards to the pile
            self.deck.add_to_pile(player.attr["hand"])

        del self.players[player_id]
        self.order.remove(player_id)
        self.n_players -= 1

        # the active index could be out of bounds
        if self.n_players:
            self.active_index %= self.n_players


        message = "Removed player: {}".format(player)
        logger.info(message)

        return {"requestValid": True, "message": message, "name": player.attr["name"]}

    def deal_cards(self, player_id, n):
        """
        Deals cards of the deck and returns them to the frontend
        to display them.
        TODO: should not be necessary to return the cards as update_cards
        is called anyway.
        """
        if not player_id in self.players.keys():
            message = "Player with id {} not found!".format(player_id)
            logger.critical(message)
            return {"requestValid": False, "message": message}

        # lifts the n top cards of the deck
        cards = self.deck.deal_cards(n)

        # adds them to the hand of the player with id=player_id
        self.players[player_id].add_cards(cards)

        logger.info("Dealt {} cards to player {} [{}]".format(
            n, self.players[player_id].attr["name"], player_id))

        # "cards": [card.attr for card in cards]}
        return {"requestValid": True}

    def start_game(self):
        """
        Currently all players can call start_game. Only place the top_card
        the first time.
        TODO: let the game start automatically for all players as soon as
        one person clicks start game.
        """
        if not self.game_started:
            self.deck.place_starting_card()
            self.game_started = True

            logger.info("Started game. {}'s turn".format(
                        self.get_active_player().attr["name"]))

        return {"requestValid": True}

    def next_player(self):
        """
        Exclusively called internally. Prepares the next turn by
        resetting indicators and handling the penalties for the
        next player.
        """
        if not self.n_players:
            return

        # resets the indicators
        self.card_picked_up = False

        # activates the penalty for the next player e.g. after playing a +2 card
        self.penalty["own"] = self.penalty["next"]
        self.penalty["next"] = 0

        if self.get_active_player().attr["finished"]:
            self.order.pop(self.active_index)
            self.n_players -= 1
            if self.n_players:
                self.active_index = (self.active_index - (not self.forward)) % self.n_players
            else:
                logger.info("Game finished")
            
        else:
            # 2*bool-1 is 1 if true and -1 if false #maths
            new_index = (self.active_index + (2*self.forward-1)) % self.n_players
            self.active_index = new_index

        message = "{}'s turn. {} penalty cards".format(
            self.get_active_player().attr["name"],
            self.penalty["own"]
        )
        logger.info(message)

    def get_active_player_id(self):
        if not self.n_players:  # no players have joined
            return None
        return self.order[self.active_index]

    def get_active_player(self):
        # if there are no players return an "empty" player
        if not self.n_players:
            return Player(None, -1)
        return self.players[self.get_active_player_id()]

    def get_all_players(self):
        return [self.players[key].to_json() for key in self.players]

    def get_top_card(self):
        return self.deck.top_card().attr

    def get_cards(self, player_id):
        return [card.attr for card in self.players[player_id].attr["hand"]]

    def player_is_active(self, player_id):
        # helper method for readability
        return self.get_active_player_id() == player_id

    def validate_move(self, player, card, top_card):
        """
        Only internally called by both play_card() and play_black_card().
        The method performs multiple checks to decide the validity of the
        requests to play a card, as explained in the code.

        If the request is found to be invalid, it returns
            {"requestValid": False, "message": reason(str)}

        If the request is valid it returns
            {"requestValid": True}
        with optional additional flags such as
            {"inegleit": (bool)}
            {"playerFinished": (bool)}
            {"raisePenalty": (bool)}
        which can be read by play_(black_)card and the respective
        router.  They are also logged for debugging purposes.
        """
        if not self.player_is_active(player.attr["id"]):
            # checks if the card can be inegleit
            if card.inegleitable(top_card):
                # if the card can be inegleit make the player the active
                # player and move on to the next player
                self.active_index = self.order.index(player.attr["id"])

                if self.penalty["own"]:
                    # this is the case if a player has an active penalty
                    # while a second player inegleits a second (+2 or +4)
                    # card thus raising the penalty.
                    if not card.able_to_raise_penalty(top_card):
                        # this shouldn't happen!
                        logger.critical(
                            "{} inegleited {} on {} while own penalty was {}"
                            .format(
                                player, card, top_card, self.penalty["own"]
                            )
                        )
                    return {"requestValid": True,
                            "inegleit": True,
                            "raisePenalty": True}

                if (self.penalty["next"]
                  and card.attr["color"] == "black"
                  and card.attr["number"] == 1):
                    # this is the case if a player is currently choosing
                    # a card after playing a +4 while a second player
                    # inegleits another +4
                    if not card.able_to_raise_penalty(top_card):
                        # this shouldn't happen!
                        logger.critical(
                            "{} inegleited {} on {} while next penalty was {}"
                            .format(
                                player, card, top_card, self.penalty["next"]
                            )
                        )
                        logger.debug("black +4 inegleit before choosing color")
                        return {"requestValid": True,
                                "inegleit": True,
                                "raisePenalty": True}

                return {"requestValid": True, "inegleit": True}
            else:
                # remove requests to 'inegleit' a card
                return {"requestValid": False,
                        "message": "not your turn, not possible to inegleit"}

        # ==> player is active

        # checks if the player has a penalty (= cards to pick up)
        if self.penalty["own"]:
            if card.able_to_raise_penalty(top_card):
                return {"requestValid": True, "raisePenalty": True}
            else:
                # not allowed to play before picking up all penalty cards
                return {"requestValid": False,
                        "message": "pick up {} cards first".format(
                                   self.penalty["own"])}

        if player.attr["penalty"]:
            # this sort of penalty is only obtained for not saying uno
            return {"requestValid": False,
                    "message": "pick up {} cards as punishment".format(
                               player.attr["penalty"])}

        # checks if the card can be played, argument chosen_color is only
        # relevant if a black card lies on top
        if (top_card.attr["color"] == "black"
          and not card.attr["color"] == "black"):
                if card.attr["color"] == self.chosen_color:
                    # reset color choice to empty
                    self.chosen_color = ""
                    return {"requestValid": True}
                else:
                    return {"requestValid": False,
                            "message": "play color {}".format(self.chosen_color)}

        elif not card.playable(top_card):
              # remove request to play a wrong card
            return {"requestValid": False, "message": "card not playable"}

        if len(player.attr["hand"]) == 1:
            # the player has one card
            if player.attr["said_uno"]:
                return {"requestValid": True, "playerFinished": player.attr}
            else:
                # punish player for not saying uno
                player.attr["penalty"] = 2
                message = "{} didn't say uno, has to pick up two cards!".format(
                    player)
                logger.info(message)
                return {"requestValid": False, "message": message, "missedUno": player.attr["name"]}

        return {"requestValid": True}

    def play_card(self, player_id, card_id):
        """
        Method that handles request by players to play a certain card.

        Returns
            {"requestValid": (bool), "message": (str)}
        with optional additional flags such as
            {"inegleit": (bool)}
            {"playerFinished": (bool)}
            {"raisePenalty": (bool)}
        """
        card = self.deck.get_card(card_id)
        player = self.players[player_id]
        top_card = self.deck.top_card()

        logger.debug("Request from {} to play {} on {}".format(
            player, card, top_card))

        if not player.has_card(card):
            # this shouldn't happen!
            response = "player does not have that card"
            logger.critical("Move denied:" + response)
            return {"requestValid": False, "message": response}

        # check if the move is valid and the card can be played
        response = self.validate_move(player, card, top_card)

        logger.debug(response)

        if not response["requestValid"]:
            return response

        # ==> move is valid, the card will be played

        message = ""

        # if the move is valid although there is a penalty this means
        # the player can raise the penalty for the next player
        if card.attr["number"] == 12:  # a +2 card
            if self.penalty["own"]:
                if not response["raisePenalty"]:
                    logger.critical("The move was deemed valid although \
                                there is a penalty that is not raised!")

                # makes the "own" penalty the basis for raising the penalty
                # for the next player.  Black (+4) cards are handled by
                # play_black_card thus the only possibility is adding +2
                self.penalty["next"] = self.penalty["own"]
                self.penalty["own"] = 0
                message += "penalty raised, "

            # now self.penalty["own"] = 0 in either case
            self.penalty["next"] += 2
            message += "+{} for the next player".format(self.penalty["next"])

        elif card.attr["number"] == 10:
            # reverse direction
            self.forward = not self.forward
            message += "reversed direction"
        elif card.attr["number"] == 11:
            # skip player because next_player is called again below
            self.next_player()
            message += "next player skipped"

        self.deck.play_card(card)
        player.remove_card(card)
        logger.info("{} played {}. ".format(player, card))
        logger.debug(message)

        # already checked in validate_move() if the player said UNO
        if not player.attr["hand"]:
            return self.player_finished(player)

        self.next_player()

        response["message"] = message
        if "inegleit" in response:
            # change dict value to the player name for display
            response["inegleit"] = player.attr["name"]
        return response

    def play_black_card(self, player_id, card_id):
        """
        Method that handles request by players to play a black card.

        Returns
            {"requestValid": (bool), "message": (str)}
        with optional additional flags such as
            {"inegleit": (bool)}
            {"playerFinished": (bool)}
            {"raisePenalty": (bool)}
        """
        card = self.deck.get_card(card_id)
        player = self.players[player_id]
        top_card = self.deck.top_card()

        logger.debug("Request from {} to play {} on {}".format(
            player, card, top_card))

        if not player.has_card(card):
            # this shouldn't happen!
            response = "player does not have that card"
            logger.warning("Move denied:" + response)
            return {"requestValid": False, "message": response}

        response = self.validate_move(player, card, top_card)

        logger.debug(response)

        if not response["requestValid"]:
            return response

        # ==> move is valid, the card will be played

        # Identify the player that can choose the color by id.  This
        # prevents players from being able to choose a color in
        # inegleit situations i.e. if a second player inegleits a black
        # card before the first player chose a color
        self.can_choose_color = self.get_active_player_id()
        message = "{} can choose color".format(player)

        # if the move is valid although there is a penalty this means
        # the player can raise the penalty for the next player
        if card.attr["number"] == 1:  # a +4 card since it's black
            if self.penalty["own"]:
                if not response["raisePenalty"]:
                    logger.critical("The move was deemed valid although \
                                    there is a penalty that is not raised!")

                # makes the "own" penalty the basis for raising the penalty
                # for the next player.  Colored (+2) cards are handled by
                # play_black_card thus the only possibility is adding +4
                self.penalty["next"] = self.penalty["own"]
                self.penalty["own"] = 0
                message += ", penalty raised"

            # now self.penalty["own"] = 0 in either case
            self.penalty["next"] += 4
            self.penalty["own"] = 0
            message += ", +{} for the next player".format(self.penalty["next"])

        self.deck.play_card(card)
        player.remove_card(card)
        logger.debug("{} played {}. ".format(player, card) + message)
        logger.info("{} played {}".format(player, card))
        logger.debug(message)

        # already checked in validate_move() if the player said UNO
        if not player.attr["hand"]:
            return self.player_finished(player)

        # next_player() will only be called after the player picks a
        # color

        response["message"] = message
        return response

    def event_choose_color(self, player_id, color):
        logger.debug("Request from {} to choose color {}".format(
            self.players[player_id], color))

        if not player_id == self.get_active_player_id():
            response = {"requestValid": False, "message": "not your turn"}
            logger.debug(response)
            return response

        if self.can_choose_color != player_id:
            response = {"requestValid": False,
                        "message": "not allowed to choose color (anymore)"}
            logger.debug(response)
            return response

        logger.info("{} chose color {}".format(self.players[player_id], color))

        self.chosen_color = color
        self.can_choose_color = False
        self.next_player()

        return {"requestValid": True, "color": color}

    def event_cant_play(self, player_id):
        self.next_player()
        return {"requestValid": True}

    def event_pickup_card(self, player_id):
        """ 
        returns (bool1, bool2, str)

        bool1   : card picked up
        bool2   : true if the card was picked up because of a penalty
        str     : response
        """
        if player_id != self.get_active_player_id():
            return {"requestValid": False, "message": "not your turn"}

        player = self.players[player_id]

        response = {} # empty dict that is now filled

        message = "picked up card"
        # frontend needs to know if the card was picked up due to penalty or not
        reason_is_penalty = False

        # due to +2 or +4 cards
        if self.penalty["own"]:
            reason_is_penalty = True
            self.penalty["own"] -= 1
            message += ", take {} more".format(self.penalty["own"])

        # due to not saying UNO
        elif player.attr["penalty"]:
            reason_is_penalty = True
            player.attr["penalty"] -= 1
            message += ", take {} more".format(
                player.attr["penalty"])

        # punish player for not saying UNO even though he can't finish
        elif len(player.attr["hand"]) == 1 and not player.attr["said_uno"]:
            reason_is_penalty = True
            # one card was already picked up thus 1 remaining
            player.attr["penalty"] = 1
            message += f", take {player.attr['penalty']} more"
            response["missedUno"] = player.attr["name"] 

        elif not self.card_picked_up:
            self.card_picked_up = True
        else:
            return {"requestValid": False, "message": "you already have enough cards"}

        card = self.deck.deal_cards(1)  # returns a list of length 1
        player.add_cards(card)
        player.attr["said_uno"] = False

        logger.debug(f"{player} picks up {card[0]}")

        response["requestValid"] = True
        response["reasonIsPenalty"] = reason_is_penalty
        response["message"] = message

        return response

    def event_uno(self, player_id):
        player = self.players[player_id]
        if len(player.attr["hand"]) == 1:
            player.attr["said_uno"] = True
            logger.info("{} said UNO".format(self.players[player_id]))
            return {"requestValid": True, 
                    "message": "UNO", 
                    "name": player.attr["name"]}
        else:
            return {"requestValid": False, "message": "you have the wrong number of cards ({})".format(len(player.attr["hand"]))}

    def player_finished(self, player):
        if not self.winners:
            message = "{} won. Congratulations!".format(player)
        else:
            message = f"{player} came in {len(self.winners)}. place. Well done!"

        logger.info(message)

        player.attr["finished"] = True
        self.winners.append(player.attr["id"])

        # still let the winner choose the color if he finishes with a black card
        if not self.can_choose_color:
            self.next_player()

        return {"requestValid": True,
                "playerFinished": player.attr["name"],
                "rank": len(self.winners),
                "message": message}

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
