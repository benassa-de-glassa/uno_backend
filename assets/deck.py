import json
import random

class Deck():
    """
    Class members:

    N               : number of cards in the deck
    allcards        : list containing 108 Card(class) in order
    current_cards   : list of length <108 storing the index of the current cards in the deck in allcards
                      e.g. [0,1] corresponds to the two cards "red 0" and "green 0" according to the order of creation
    pile            : already played cards
                
    Class methods:

    shuffle_cards() : returns a random permutation of current_cards
    get_card(i)     : helper function that returns the Card(class) corresponding to the index i
    deal_cards(n)   : deals the n top cards e.g. at the beginning of the game or after +2/+4 cards 
                      returns n instances of Card(class)
    play_card(i)    : attemts to play the Card with index i, returns True if it is possible and adds it to the pile, and False otherwise
                      ## TODO: handle that the card is removed from the players hand

    """
    def __init__(self, seed=None):
        if seed:
            random.seed(seed)
        self.N = 0 # anzahl karten
        self.allcards = [] # verdeckter stapel
        self.pile = [] # offener stapel

        """
        For colored cards:
        0-9     : normal numbers
        10      : reverse direction
        11      : skip player
        12      : +2 
        =============================
        
        For black cards:
        0       : choose color
        1       : +4 and choose color

        =============================
        In the end there is a list of 108 Cards.
        """

        # creates all colored cards
        for color in ["red", "green", "blue", "yellow"]:
            # add a single zero per color
            self.allcards.append(Card(color, 0, self.N))
            self.N += 1
            # add two of each kind
            for i in range(12):
                self.allcards.append(Card(color, i, self.N))
                self.allcards.append(Card(color, i+1, self.N+1))
                self.N += 2
        # creates the black cards
        for i in range(4): 
            self.allcards.append(Card("black", 0, self.N)) # choose color
            self.N += 1
        for i in range(4):
            self.allcards.append(Card("black", 1, self.N)) # +4 card
            self.N += 1

        # make a copy of the deck
        self.current_cards = self.allcards.copy()
        # shuffles the cards
        self.shuffle_cards()

    def place_starting_card(self):
        # places the starting card:
        self.pile.append(self.current_cards.pop())

        # avoids having a black starting card
        if self.top_card().attr["color"] == "black":
            self.place_starting_card()

    def get_card(self, i):
        return self.allcards[i]
    
    def shuffle_cards(self):
        random.shuffle(self.current_cards)

    def top_card(self):
        if len(self.pile) > 0:
            return self.pile[-1]
        else:
            return []
    def deal_cards(self, n):
        if n < self.N:
            cards = [self.current_cards.pop() for i in range(n)]
            return cards
        else:
            # TODO: reshuffle
            raise ValueError
            
    def to_json(self):
        return {
            'stack' : [Card.to_json(card) for card in self.allcards],
            'pile': [Card.to_json(card) for card in self.pile]
        }

    # def from_json(self, deck):
    #     self.allcards = []
    #     self.pile = []
    #     for card in deck['stack']:
    #         self.allcards.append( Card(card['color'], card['number'], card['uid']))
    #     for card in deck['pile']:
    #         self.pile.append( Card(card['color'], card['number'], card['uid']))
   
    def play_card(self, card):
        self.pile.append(card)

class Card():
    def __init__(self, color, number, id):
        self.attr = {
            "id": id,
            "color": color,
            "number": number
        }

    def playable(self, top_card):
        """
        tests if this card (self) can be placed upon top card on the staple
        """

        if self.attr["color"] == "black":
            return True
        elif self.attr["color"] == top_card.attr["color"] or self.attr["number"] == top_card.attr["number"]:
            return True
        return False
        
    # def to_json(self):
    #     return self.attr

    # def from_json(self, card):
    #     self.attr["color"] = card["color"]
    #     self.attr["number"] = card["number"]
    
    def inegleitable(self, top_card):
        """ 
        tests if the card can be inegleit
        """
        if self.attr["color"] == top_card.attr["color"] and self.attr["number"] == top_card.attr["number"]:
            return True
        else: return False

    def __str__(self):
        if self.attr["color"] == "black":
            if self.attr["number"] == 0:
                text = "?"
            else:
                text = "+4"
        elif self.attr["number"] == 10:
            text = "<=>"
        elif self.attr["number"] == 11:
            text = "(/)"
        elif self.attr["number"] == 12:
            text = "+2"
        else:
            text = str(self.attr["number"])

        

        return self.attr["color"] + " " + text
