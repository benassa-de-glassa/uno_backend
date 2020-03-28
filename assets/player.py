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

    def has_card(self, card):
        return card in self.attr["hand"]
        
    def remove_card(self, card):
        self.attr["hand"].remove(card)
    
    def toggle_uno(self):
        self.attr["said_uno"] = not self.attr["said_uno"]

    def __str__(self):
        return "{} [{}]".format(self.attr["name"], self.attr["id"])

    def to_json(self):
        return {
            "name": self.attr["name"], 
            "id": self.attr["id"],
            "numberOfCards": len(self.attr["hand"]), 
            "saidUno": self.attr["said_uno"]
            }
