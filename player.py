from enum import Enum

from deck import StateError, Hand, HandState, Shoe


class PlayerAction(Enum):
    STAND = 1
    HIT = 2
    DOUBLE = 3
    SPLIT = 4


class Player():

    def __init__(self, budget, wager=1, num_hands=1):
        if budget <= 0:
            msg = f"budget must be > 0, received {budget}"
            raise ValueError(msg)

        if wager <= 0:
            msg = f"wager must be > 0, received {wager}"
            raise ValueError(msg)

        if num_hands < 1 or not isinstance(num_hands, int):
            msg = f"num_hands must be an int > 0, received {num_hands}"
            raise ValueError(msg)

        self.budget = budget
        self.wager = wager
        self.num_hands = num_hands

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

    def make_wager(self):
        wagers = []
        for i in range(self.num_hands):
            if self.budget > self.wager:
                wagers.append(self.wager)
                self.remove_money(self.wager)
        return wagers

    def take_action(self, hand):
        if hand.score < 17:
            return PlayerAction.HIT
        else:
            return PlayerAction.STAND


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
            action = player.take_action(hand)
            if action is PlayerAction.HIT:
                hand.hit(self.shoe.draw_card())
            elif action is PlayerAction.STAND:
                hand.stand()

    def play_dealer_hand(self):
        while self.hand.state is HandState.PLAYING:
            if self.hand.score < 17:
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
