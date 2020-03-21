import numpy as np

from player import Player
from deck import Deck


class Inegleit():
    """
    class members:
    
    n_players (int)     : number of players
    players (list)      : list of all Player(class)
    deck (class)        : deck handling the cards in the deck as well as the pile of used cards
    forward (bool)      : True if the playing direction is forward, False otherwise
    active_player (int) : index of the player whos turn it is

    methods:

    add_player(name, index) :
    remove_player()         :
    start_game()            : initializes the game and assigns each player an index
    
    """

    def __init__(self):
        self.n_players = 0
        self.players = []
        self.deck = Deck()

        # playing direction
        self.forward = True
        self.active_player = 0

    def add_player(self, name, index=0):
        self.n_players += 1
        p = Player(self, name, id)

        self.players.append(p)

    def remove_player(self, id):
        pass

    def start_game(self):
        self.player_indexes = list(range(self.n_players))
        for p in self.players:
            dealt_cards = self.deck.deal_cards(7)

            p.add_cards(dealt_cards)

        # chooses a random player to begin
        self.active_player = np.random.randint(self.n_players)

    def next_player(self, n=1):
        # n=2 means one player is skipped
        i = (self.active_player + self.forward*n) % self.n_players
        self.active_player = i

    def event_play_card(self, player_index, card):
        """ 
        event triggered by the player
        """
        top_card = self.deck.get_top_card()

        if player_index != self.active_player:
            # checks if the card can be inegleit
            if card.inegleitable(top_card):
                # if the card can be inegleit make the player the active player
                # and go to the next player
                self.deck.play_card(card)
                self.active_player = player_index
                self.next_player()
            else: pass # TODO: some kind of error message
        
        if player_index == self.active_player:
            if card.playable(top_card):
                self.deck.play_card(card)
                
                # handle black cards
                if card.color == "black":
                    if card.number == 0: # choose color
                        pass
                    if card.number == 1: # +4 and choose color
                        pass
            
                # handle colored cards
                elif card.number == 10: # reverse direction
                    self.forward = not self.forward
                elif card.number == 11: # skip player
                    self.next_player() # skips this player
                elif card.number == 12: # +2
                    pass

                self.next_player()

            else: pass # TODO: error message

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

        

