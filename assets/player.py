class Player():
    """ 
    Class members:

    name            : identifier
    uid             : identifier
    hand            : cards on the hand

    """
    def __init__(self, name, uid):
        """
        
        """
        self.attr = {
            "name": name,
            "id": uid,
            "hand": [],
            "said_uno": False
        }


    def add_cards(self, cards):
        self.attr["hand"].extend(cards)
        
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

