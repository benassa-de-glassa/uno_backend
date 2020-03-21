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
    def __init__(self):
        self.N = 0 
        self.allcards = []
        self.pile = []

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
        for col in ["red", "green", "blue", "yellow"]:
            self.allcards.append(Card(col, 0))
            self.N += 1
            for i in range(12):
                self.allcards.append(Card(col, i+1))
                self.allcards.append(Card(col, i+1))
                self.N += 2

        # creates the black cards
        for i in range(4):
            self.allcards.append(Card("black", 0)) # choose color
            self.allcards.append(Card("black", 1)) # +4 card
            self.N += 2

        self.current_cards = self.allcards.copy()
        # shuffles the cards
        self.shuffle_cards()

        # places the starting card:
        self.pile.append(self.current_cards.pop())

    def shuffle_cards(self):
        random.shuffle(self.current_cards)

    def get_top_card(self):
        return self.pile[-1]

    def deal_cards(self, n):
        if n < self.N:
            cards = [self.current_cards.pop() for i in range(n)]
            return cards
        else:
            raise ValueError

    def play_card(self, card):
        self.pile.append(card)

class Card():
    def __init__(self, color, number):
        self.color = color
        self.number = number

    def playable(self, top_card):
        """
        tests if this card (self) can be placed upon top card on the staple
        """

        if self.color == "black":
            return True
        elif self.color == top_card.color or self.number == top_card.number:
            return True
        else: return False
    
    def inegleitable(self, top_card):
        """ 
        tests if the card can be inegleit
        """
        if self.color == top_card.color and self.number == top_card.number:
            return True
        else: return False

    def __str__(self):
        return self.color + str(self.number)