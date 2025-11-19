use serde::{Deserialize, Serialize};
use std::fmt;
use rand::seq::SliceRandom;
use rand::thread_rng;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Suit {
    Hearts,
    Diamonds,
    Clubs,
    Spades,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, PartialOrd, Ord)]
pub enum Rank {
    Two = 2,
    Three = 3,
    Four = 4,
    Five = 5,
    Six = 6,
    Seven = 7,
    Eight = 8,
    Nine = 9,
    Ten = 10,
    Jack = 11,
    Queen = 12,
    King = 13,
    Ace = 14,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Card {
    pub rank: Rank,
    pub suit: Suit,
}

impl fmt::Display for Card {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?} of {:?}", self.rank, self.suit)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Player {
    pub id: usize,
    pub hand: Vec<Card>,
    pub won_tricks: u32,
}

impl Player {
    pub fn new(id: usize) -> Self {
        Self {
            id,
            hand: Vec::new(),
            won_tricks: 0,
        }
    }

    pub fn add_cards(&mut self, cards: Vec<Card>) {
        self.hand.extend(cards);
        // Sort logic could be added here
    }

    pub fn remove_card(&mut self, card: &Card) -> bool {
        if let Some(pos) = self.hand.iter().position(|c| c == card) {
            self.hand.remove(pos);
            true
        } else {
            false
        }
    }

    pub fn has_suit(&self, suit: Suit) -> bool {
        self.hand.iter().any(|c| c.suit == suit)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum GameState {
    DetermineHakim,
    DeclareTrump,
    Playing,
    Finished,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HokmGame {
    pub players: Vec<Player>,
    pub hakim_index: usize,
    pub trump_suit: Option<Suit>,
    pub current_player_index: usize,
    pub state: GameState,
    pub current_trick: Vec<(usize, Card)>,
    pub scores: (u32, u32), // Team 0 (0,2) vs Team 1 (1,3)
}

impl HokmGame {
    pub fn new() -> Self {
        Self {
            players: (0..4).map(Player::new).collect(),
            hakim_index: 0, // Default
            trump_suit: None,
            current_player_index: 0,
            state: GameState::DetermineHakim,
            current_trick: Vec::new(),
            scores: (0, 0),
        }
    }

    pub fn create_deck() -> Vec<Card> {
        let mut deck = Vec::new();
        for suit in [Suit::Hearts, Suit::Diamonds, Suit::Clubs, Suit::Spades] {
            for rank in [
                Rank::Two, Rank::Three, Rank::Four, Rank::Five, Rank::Six, Rank::Seven,
                Rank::Eight, Rank::Nine, Rank::Ten, Rank::Jack, Rank::Queen, Rank::King, Rank::Ace,
            ] {
                deck.push(Card { rank, suit });
            }
        }
        let mut rng = thread_rng();
        deck.shuffle(&mut rng);
        deck
    }

    pub fn start_game(&mut self) {
        let deck = Self::create_deck();
        // Deal 5 cards
        for i in 0..4 {
            self.players[i].add_cards(deck[i*5..(i+1)*5].to_vec());
        }
        // Assume Hakim is 0 for now or logic to determine
        self.state = GameState::DeclareTrump;
        self.current_player_index = self.hakim_index;
        
        // Store remaining deck for later? In a real implementation we need to store it.
        // For this MVP let's just re-shuffle or store it in the struct (omitted for brevity but needed).
        // Let's assume we just deal all for now to simplify.
        let remaining = deck[20..].to_vec();
        // Hack: store remaining in player 0's extra field or just deal them now but hide them?
        // Correct way: Add `deck` field to struct.
        // For now, let's just deal all cards immediately but enforce phases.
         for i in 0..4 {
            self.players[i].add_cards(remaining[i*8..(i+1)*8].to_vec());
        }
    }

    pub fn declare_trump(&mut self, suit: Suit) -> Result<(), String> {
        if self.state != GameState::DeclareTrump {
            return Err("Not in trump declaration phase".to_string());
        }
        self.trump_suit = Some(suit);
        self.state = GameState::Playing;
        self.current_player_index = self.hakim_index;
        Ok(())
    }

    pub fn play_card(&mut self, player_id: usize, card: Card) -> Result<(), String> {
        if self.state != GameState::Playing {
            return Err("Not in playing phase".to_string());
        }
        if player_id != self.current_player_index {
            return Err(format!("Not player {}'s turn", player_id));
        }

        let player = &self.players[player_id];
        if !player.hand.contains(&card) {
            return Err("Card not in hand".to_string());
        }

        // Validate suit following
        if let Some((_, lead_card)) = self.current_trick.first() {
            if card.suit != lead_card.suit && player.has_suit(lead_card.suit) {
                return Err(format!("Must follow suit {:?}", lead_card.suit));
            }
        }

        self.players[player_id].remove_card(&card);
        self.current_trick.push((player_id, card));

        if self.current_trick.len() == 4 {
            self.resolve_trick();
        } else {
            self.current_player_index = (self.current_player_index + 1) % 4;
        }

        Ok(())
    }

    fn resolve_trick(&mut self) {
        let winner_idx = self.determine_trick_winner();
        self.players[winner_idx].won_tricks += 1;
        
        self.current_trick.clear();
        self.current_player_index = winner_idx;
        
        // Check end of round
        if self.players[0].hand.is_empty() {
            self.end_round();
        }
    }

    fn determine_trick_winner(&self) -> usize {
        let lead_suit = self.current_trick[0].1.suit;
        let mut best_play = self.current_trick[0];

        for &(player_id, card) in self.current_trick.iter().skip(1) {
            if let Some(trump) = self.trump_suit {
                if best_play.1.suit == trump {
                    if card.suit == trump && card.rank > best_play.1.rank {
                        best_play = (player_id, card);
                    }
                } else {
                    if card.suit == trump {
                        best_play = (player_id, card);
                    } else if card.suit == lead_suit && card.rank > best_play.1.rank {
                        best_play = (player_id, card);
                    }
                }
            } else {
                // No trump (shouldn't happen in Hokm but safe fallback)
                if card.suit == lead_suit && card.rank > best_play.1.rank {
                    best_play = (player_id, card);
                }
            }
        }
        best_play.0
    }

    fn end_round(&mut self) {
        let team0_tricks = self.players[0].won_tricks + self.players[2].won_tricks;
        if team0_tricks >= 7 {
            self.scores.0 += 1;
        } else {
            self.scores.1 += 1;
        }
        self.state = GameState::Finished;
    }
}
