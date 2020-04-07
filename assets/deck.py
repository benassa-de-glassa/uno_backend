import json
import random

class Deck():
    """
    Class members:

    N(int)          : number of cards in the deck
    allcards(list)  : list containing 108 Card(class) in order
    current_cards   : list of length <108 storing the index of the current cards
    (list)            in the deck in allcards
                      e.g. [0,1] corresponds to the two cards "red 0" and "green 0"
                      according to the order of creation
    pile(list)      : list of already played cards
                
    Class methods:

    __init__(seed)  : creates all Card instances and shuffles them
    shuffle_cards() : applies a random permutation to the current_cards
    get_card(i)     : helper function that returns the Card(class) corresponding
                      to the index i
    deal_cards(n)   : deals the n top cards e.g. at the beginning of the game, 
                      after +2/+4 cards, or after a player is unable to play
                      returns n instances of Card(class)
    play_card(i)    : attemts to play the Card with index i, returns True if it
                      is possible and adds it to the pile, and False otherwise
    """
    def __init__(self, seed=None, testcase=None):
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

        # apply random permutation (possibility to select a seed)
        self.shuffle_cards()

        # selected card distribution
        if testcase:
            self.setup_testcase(testcase)

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
            # placeholder card
            return Card('white', 'no card yet', '-1')

    def deal_cards(self, n):
        # checks if there are enough cards in the deck otherwise the pile is
        # added to the currentcards and reshuffled, keeping the top card
        if n < len(self.current_cards):
            cards = [self.current_cards.pop() for i in range(n)]
            return cards
        else:
            topcard = self.pile.pop()
            self.current_cards.extend(self.pile)
            self.pile = [topcard]
            self.shuffle_cards()
            self.deal_cards(n)
            
    def to_json(self):
        return {
            'stack' : [card.to_json() for card in self.allcards],
            'pile': [card.to_json() for card in self.pile]
        }

    def play_card(self, card):
        self.pile.append(card)

    def setup_testcase(self, testcase):
        if testcase == 1:
            card_ids = [104, 105, 11, 12, 13, 14, 15, 16, 17, 106, 107, 77]
            cards = [self.get_card(i) for i in card_ids]
            print("TEST / Added " + str([str(card) for card in cards]) + " to deck.")
            self.current_cards.extend(cards)

    # def from_json(self, deck):
    #     self.allcards = []
    #     self.pile = []
    #     for card in deck['stack']:
    #         self.allcards.append( Card(card['color'], card['number'], card['uid']))
    #     for card in deck['pile']:
    #         self.pile.append( Card(card['color'], card['number'], card['uid']))
   

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
        return False

    def able_to_raise_penalty(self, top_card):
        if self.attr["color"] == "black" and top_card.attr["color"] == "black" and self.attr["number"] == 1 and top_card.attr["number"] == 1:
            return True
        if self.attr["number"] == 12 and top_card.attr["number"] == 12:
            return True
        return False

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
