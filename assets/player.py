class Player():
    """ 
    Class members:

    game            : parent game
    name            : identifier
    id              : identifier
    hand            : cards on the hand

    """
    def __init__(self, game, name, index=0):
        """
        
        """
        self.game = game
        self.name = name
        self.index = index

        self.hand = []

        self.said_uno = False

    def add_cards(self, cards):
        self.hand.extend(cards)


