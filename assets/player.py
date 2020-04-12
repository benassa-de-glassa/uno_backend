class Player():
    """ 
    Class members:

    name            : identifier
    uid             : identifier
    hand            : cards on the hand

    """
    def __init__(self, name, uid, king=False):
        """
        
        """
        self.attr = {
            "name": name,
            "id": uid,
            "hand": [],
            "said_uno": False,      # bool
            "penalty": 0,           # int, punishment for not saying uno
            "has_received_initial_cards": False,
            "king": king,
            "finished": False, 
            "rank": 0,
        }
        
    def add_cards(self, cards):
        self.attr["hand"].extend(cards)

    def has_card(self, card):
        return card in self.attr["hand"]
        
    def remove_card(self, card):
        self.attr["hand"].remove(card)

    def __str__(self):
        return "{} [{}]".format(self.attr["name"], self.attr["id"])

    def to_json(self):
        return {
            "name": self.attr["name"], 
            "id": self.attr["id"],
            "king": self.attr["king"],
            "numberOfCards": len(self.attr["hand"]), 
            "saidUno": self.attr["said_uno"],
            "gotInitialCards": self.attr["has_received_initial_cards"],
            "finished": self.attr["finished"],
            "rank": self.attr["rank"]
        }
