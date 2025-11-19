import random
from enum import Enum, auto
from typing import List, Optional, Tuple, Dict

class Suit(Enum):
    HEARTS = auto()
    DIAMONDS = auto()
    CLUBS = auto()
    SPADES = auto()

    def __str__(self):
        return self.name

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def __str__(self):
        return self.name

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank.name} of {self.suit.name}"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.hand: List[Card] = []
        self.won_tricks: int = 0

    def add_cards(self, cards: List[Card]):
        self.hand.extend(cards)
        self.hand.sort(key=lambda c: (c.suit.value, c.rank.value))

    def remove_card(self, card: Card):
        self.hand.remove(card)

    def has_suit(self, suit: Suit) -> bool:
        return any(c.suit == suit for c in self.hand)

class GameState(Enum):
    DETERMINE_HAKIM = auto()
    DECLARE_TRUMP = auto()
    PLAYING = auto()
    FINISHED = auto()

class HokmGame:
    def __init__(self):
        self.players = [Player(i) for i in range(4)]
        self.deck = self._create_deck()
        self.hakim_index = 0 # Default, will be determined
        self.trump_suit: Optional[Suit] = None
        self.current_player_index = 0
        self.state = GameState.DETERMINE_HAKIM
        self.current_trick: List[Tuple[int, Card]] = [] # (player_id, card)
        self.tricks_history: List[List[Tuple[int, Card]]] = []
        self.scores = {0: 0, 1: 0} # Team 0 (P0, P2) vs Team 1 (P1, P3)
        self.game_winner = None

    def _create_deck(self) -> List[Card]:
        deck = [Card(rank, suit) for suit in Suit for rank in Rank]
        random.shuffle(deck)
        return deck

    def reset(self):
        self.deck = self._create_deck()
        for p in self.players:
            p.hand = []
            p.won_tricks = 0
        self.trump_suit = None
        self.current_trick = []
        self.tricks_history = []
        self.state = GameState.DETERMINE_HAKIM
        # Hakim stays same unless specified otherwise, but for now let's redetermine or rotate?
        # Standard Hokm: Loser deals, Winner is Hakim.
        # For simplicity in ML env, we might randomize or keep fixed.
        # Let's implement a simple random deal for now.
        self._deal_initial_cards()

    def _deal_initial_cards(self):
        # Deal 5 cards to each
        for i, player in enumerate(self.players):
            player.add_cards(self.deck[i*5 : (i+1)*5])
        
        # If we need to determine Hakim based on first ace/highest card logic:
        # For this implementation, let's assume Hakim is already set or P0 for simplicity
        # unless we want to implement the full "deal until Ace" logic.
        # Let's stick to P0 is Hakim for the first game, then winner becomes Hakim.
        self.state = GameState.DECLARE_TRUMP
        self.current_player_index = self.hakim_index

    def declare_trump(self, suit: Suit):
        if self.state != GameState.DECLARE_TRUMP:
            raise ValueError("Not in trump declaration phase")
        if self.current_player_index != self.hakim_index:
            raise ValueError("Only Hakim can declare trump")
        
        self.trump_suit = suit
        self._deal_remaining_cards()
        self.state = GameState.PLAYING
        self.current_player_index = self.hakim_index # Hakim leads first trick

    def _deal_remaining_cards(self):
        # Deal remaining 8 cards
        start = 20
        for i, player in enumerate(self.players):
            player.add_cards(self.deck[start + i*8 : start + (i+1)*8])

    def get_legal_moves(self, player_id: int) -> List[Card]:
        player = self.players[player_id]
        if not self.current_trick:
            return player.hand
        
        lead_suit = self.current_trick[0][1].suit
        if player.has_suit(lead_suit):
            return [c for c in player.hand if c.suit == lead_suit]
        
        return player.hand

    def play_card(self, player_id: int, card: Card):
        if self.state != GameState.PLAYING:
            raise ValueError("Not in playing phase")
        if player_id != self.current_player_index:
            raise ValueError(f"Not player {player_id}'s turn")
        
        legal_moves = self.get_legal_moves(player_id)
        if card not in legal_moves:
             # This check assumes card object identity or equality. 
             # Since we reconstruct cards, equality check in Card class is important.
             if card not in player.hand:
                 raise ValueError("Card not in hand")
             raise ValueError(f"Illegal move: must follow suit {self.current_trick[0][1].suit}")

        self.players[player_id].remove_card(card)
        self.current_trick.append((player_id, card))
        
        if len(self.current_trick) == 4:
            self._resolve_trick()
        else:
            self.current_player_index = (self.current_player_index + 1) % 4

    def _resolve_trick(self):
        winner_idx = self._determine_trick_winner()
        self.players[winner_idx].won_tricks += 1
        
        # Team scoring
        team_idx = winner_idx % 2
        # We don't update game score yet, just track tricks. 
        # Game score is updated at end of round (13 tricks).
        
        self.tricks_history.append(self.current_trick)
        self.current_trick = []
        self.current_player_index = winner_idx
        
        if len(self.players[0].hand) == 0:
            self._end_round()

    def _determine_trick_winner(self) -> int:
        lead_suit = self.current_trick[0][1].suit
        best_play = self.current_trick[0]
        
        for player_id, card in self.current_trick[1:]:
            # If current best is trump
            if best_play[1].suit == self.trump_suit:
                if card.suit == self.trump_suit and card.rank.value > best_play[1].rank.value:
                    best_play = (player_id, card)
            # If current best is not trump
            else:
                if card.suit == self.trump_suit:
                    best_play = (player_id, card)
                elif card.suit == lead_suit and card.rank.value > best_play[1].rank.value:
                    best_play = (player_id, card)
                    
        return best_play[0]

    def _end_round(self):
        team0_tricks = self.players[0].won_tricks + self.players[2].won_tricks
        team1_tricks = self.players[1].won_tricks + self.players[3].won_tricks
        
        if team0_tricks >= 7:
            self.scores[0] += 1
            self.hakim_index = 0 # Or keep same team? Standard rules: winner becomes Hakim.
            # If team 0 was not Hakim, they become Hakim.
        else:
            self.scores[1] += 1
            self.hakim_index = 1
            
        # Check for match win (usually 7 points)
        # For ML training, we might just play single games or shorter matches.
        self.state = GameState.FINISHED
