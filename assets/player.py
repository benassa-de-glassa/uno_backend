class Player():
    """ 
    Class members:

    game            : parent game
    name            : identifier
    uid             : identifier
    hand            : cards on the hand

    """
    def __init__(self, game, name, uid=0):
        """
        
        """
        self.game = game
        self.name = name
        self.id = uid
        
        self.hand = []

        self.said_uno = False

    def add_cards(self, cards):
        self.hand.extend(cards)
        
    def lay_card(self, i):
        """
        i : index of the card in self.cards. 
        needs to tests if the card can be played and pops it if it can
        """

    
    def shout_uno(self):
        pass
      
    def to_json(self):
        return {
            'name': self.name
            }

    def from_json(self, player):
        self.name = player['name']

