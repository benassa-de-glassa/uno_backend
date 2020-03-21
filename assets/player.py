class Player():
    """ 
    Class members:

    game            : parent game
    name            : identifier
    id              : identifier
    hand            : cards on the hand

    """
    def __init__(self, game, name, id=0):
        """
        
        """
        self.game = game
        self.name = name
        self.id = id

        self.hand = []

    def add_cards(self, cards):
        self.hand.extend(cards)

    def lay_card(self, i):
        """
        i : index of the card in self.cards. 
        needs to tests if the card can be played and pops it if it can
        """


    
    def shout_uno(self):
        pass

