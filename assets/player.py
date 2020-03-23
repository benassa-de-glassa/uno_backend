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
        
    def remove_card(self, card):
        self.attr["hand"].remove(card)
    
    def toggle_uno(self):
        self.attr["said_uno"] = not self.attr["said_uno"]

