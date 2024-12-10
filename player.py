from enum import Enum
from abc import ABC, abstractmethod

from deck import StateError, Hand, HandState, Shoe


class PlayerAction(Enum):
    STAND = 1
    HIT = 2

    # To be added later
    # DOUBLE = 3
    # SPLIT = 4


class BasePlayer(ABC):

    def __init__(self, budget):
        if budget <= 0:
            msg = f"budget must be > 0, received {budget}"
            raise ValueError(msg)

        self.budget = budget
        self.hands = []

    def add_hand(self, hand):
        if not isinstance(hand, Hand):
            msg = f"hand must be type Hand, received {type(hand)}"
            raise TypeError(msg)
        self.hands.append(hand)

    def clear_hands(self):
        self.hands = []

    def remove_money(self, amount):
        if amount <= 0:
            msg = f"amount must be > 0, received {amount}"
            raise ValueError(msg)
        self.budget -= amount

    def add_money(self, amount):
        if amount <= 0:
            msg = f"amount must be > 0, received {amount}"
            raise ValueError(msg)
        self.budget += amount

    @property
    def staked(self):
        total = 0
        for hand in self.hands:
            total += hand.stake
        return total

    @property
    def is_broke(self, min=0):
        if self.budget < min and not self.hands:
            return True
        return False

    @abstractmethod
    def make_wager(self):
        pass

    @abstractmethod
    def take_action(self, hand, dealer_card):
        pass


class SimplePlayer(BasePlayer):

    def __init__(self, budget, wager=1, num_hands=1):
        super().__init__(budget)

        if wager <= 0:
            msg = f"wager must be > 0, received {wager}"
            raise ValueError(msg)

        if num_hands < 1 or not isinstance(num_hands, int):
            msg = f"num_hands must be an int > 0, received {num_hands}"
            raise ValueError(msg)

        self.wager = wager
        self.num_hands = num_hands

    def make_wager(self):
        wagers = []
        for i in range(self.num_hands):
            if self.budget > self.wager:
                wagers.append(self.wager)
                self.remove_money(self.wager)
        return wagers

    def take_action(self, hand, dealer_card):
        if hand.score < 17:
            return PlayerAction.HIT
        else:
            return PlayerAction.STAND


class UserPlayer(BasePlayer):

    def make_single_wager(self):
        while True:
            msg = f"How much would you like to wager? (Budget: £{self.budget})"
            wager = input(msg)
            if not wager.isdigit() or int(wager) <= 0:
                print("Wager must be a positive number.")
                continue
            elif int(wager) > self.budget:
                print("You do not have enough funds to make this wager.")
                continue
            return int(wager)

    def make_wager(self):
        wagers = []
        while not wagers:
            response = input("Would you like to play this round? [y/n]")
            if response not in ("y", "n"):
                print("Only y or n are acceptable inputs.")
            elif response == "y":
                wager = self.make_single_wager()
                wagers.append(wager)

        if wagers:
            while True:
                response = input("Would you like to play another hand? [y/n]")
                if response not in ("y", "n"):
                    print("Only y or n are acceptable inputs.")
                elif response == "y":
                    wager = self.make_single_wager(self)
                    wagers.append(wager)
                elif response == "n":
                    break
        return wagers

    def take_action(self, hand, dealer_card):
        print(f"Dealer's Hand: {dealer_card}")
        print(f"Player's Hand: {hand}")
        while True:
            msg = "What action would you like to take?"
            for action in PlayerAction:
                msg += f"\n{action.name} [{action.value}]"
            choice = input(msg)
            if (not choice.isdigit()
                    or int(choice) not in [a.value for a in PlayerAction]):
                print("You must choose one of the options in [].")
                continue
            action = PlayerAction(int(choice))
            return action


class Dealer():

    def __init__(self, num_decks):
        self.hand = None
        self.num_decks = num_decks
        self.shoe = Shoe(self.num_decks)

    def take_wager(self, player):
        wagers = player.make_wager()
        for wager in wagers:
            player.add_hand(Hand(wager))

    def deal(self, players):
        for i in range(2):
            for player in players:
                for hand in player.hands:
                    hand.hit(self.shoe.draw_card())
            self.hand.hit(self.shoe.draw_card())

    def play_hand(self, player, hand):
        while hand.state is HandState.PLAYING:
            action = player.take_action(hand, self.hand.cards[0])
            if action is PlayerAction.HIT:
                hand.hit(self.shoe.draw_card())
            elif action is PlayerAction.STAND:
                hand.stand()

    def play_dealer_hand(self):
        while self.hand.state is HandState.PLAYING:
            if self.hand.soft_score < 17:
                self.hand.hit(self.shoe.draw_card())
            else:
                self.hand.stand()

    def resolve_hand(self, hand):
        if hand.state is HandState.PLAYING:
            msg = "hand cannot be resolved while still playing"
            raise StateError(msg)

        if self.hand.state is HandState.PLAYING:
            msg = "hand cannot be resolved while dealer is still playing"
            raise StateError(msg)

        if (hand.state is HandState.BLACKJACK
                and self.hand.state is HandState.BLACKJACK):
            multiplier = 1
        elif hand.state is HandState.BLACKJACK:
            multiplier = 2.5
        elif self.hand.state is HandState.BLACKJACK:
            multiplier = 0
        elif hand.state is HandState.BUST:
            multiplier = 0
        elif self.hand.state is HandState.BUST:
            multiplier = 2
        elif hand.score == self.hand.score:
            multiplier = 1
        elif hand.score > self.hand.score:
            multiplier = 2
        elif hand.score < self.hand.score:
            multiplier = 0

        return multiplier * hand.stake

    def play_round(self, players):
        self.hand = Hand(1)
        for player in players:
            self.take_wager(player)
        self.deal(players)
        for player in players:
            for hand in player.hands:
                self.play_hand(player, hand)
        self.play_dealer_hand()
        for player in players:
            for hand in player.hands:
                winnings = self.resolve_hand(hand)
                if winnings:
                    player.add_money(winnings)
            player.clear_hands()
