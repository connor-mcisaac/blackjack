from enum import Enum
import random


class StateError(Exception):
    pass


class _rank(Enum):
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"

    def __str__(self):
        return self.value


class _suit(Enum):
    HEARTS = "H"
    DIAMONDS = "D"
    CLUBS = "C"
    SPADES = "S"

    def __str__(self):
        icons = {
            "H": "\u2665",
            "D": "\u2666",
            "C": "\u2660",
            "S": "\u2663"
        }
        return icons[self.value]


class HandState(Enum):
    PLAYING = 1
    STANDING = 2
    BUST = 3


class Card():

    def __init__(self, rank, suit):
        self.rank = _rank(rank)
        self.suit = _suit(suit)

    @property
    def value(self):
        if self.rank.value == "A":
            return 1
        elif self.rank.value in ("J", "Q", "K"):
            return 10
        return int(self.rank.value)

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Hand():

    def __init__(self):
        self.cards = []
        self.state = HandState.PLAYING

    @property
    def score(self):
        score = 0
        for card in self.cards:
            score += card.value
        return score

    @property
    def is_soft(self):
        score = self.score
        for card in self.cards:
            if card.rank == _rank.ACE and score <= 11:
                return True
        return False

    @property
    def is_bust(self):
        if self.score > 21:
            return True
        return False

    @property
    def soft_score(self):
        score = self.score
        if self.is_soft:
            score += 10
        return score

    def hit(self, card):
        if not isinstance(card, Card):
            msg = f"card must be of type Card, received {type(card)} instead"
            raise TypeError(msg)

        if self.state is not HandState.PLAYING:
            msg = f"Cannot hit when hand is {self.state.name}"
            raise StateError(msg)

        self.cards.append(card)
        if self.is_bust:
            self.state = HandState.BUST

    def stand(self):
        self.state = HandState.STANDING

    def __repr__(self):
        return " | ".join([str(card) for card in self.cards])


class Deck():

    def __init__(self, shuffle=True):
        self.cards = []
        for suit in _suit:
            for rank in _rank:
                card = Card(rank.value, suit.value)
                self.cards.append(card)
        if shuffle:
            self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def __len__(self):
        return len(self.cards)

    def draw_card(self):
        return self.cards.pop()


class Shoe(Deck):

    def __init__(self, num_decks):
        self.cards = []
        for i in range(num_decks):
            self.add_deck()
        self.shuffle()

    def add_deck(self):
        for suit in _suit:
            for rank in _rank:
                card = Card(rank.value, suit.value)
                self.cards.append(card)
