from enum import Enum


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
