import functools
import numpy as np
from gymnasium import spaces
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers

from ml.hokm.game import HokmGame, GameState, Card, Suit, Rank

class HokmEnv(AECEnv):
    metadata = {"render_modes": ["human"], "name": "hokm_v2"}

    def __init__(self, render_mode=None):
        self.possible_agents = ["player_" + str(r) for r in range(4)]
        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )
        self.render_mode = render_mode
        self._game = HokmGame()
        
        # Action space: 52 cards
        self._action_spaces = {agent: spaces.Discrete(52) for agent in self.possible_agents}
        
        # Observation space
        # 1. Current hand (52 binary)
        # 2. Current trick (4 * 52 binary - who played what)
        # 3. Trump suit (4 binary one-hot)
        # 4. Hakim (4 binary one-hot)
        # 5. My Index (4 binary one-hot) - helpful for shared policy
        # Total: 52 + 208 + 4 + 4 + 4 = 272
        # Simplified for now.
        self._observation_spaces = {
            agent: spaces.Dict({
                "observation": spaces.Box(low=0, high=1, shape=(272,), dtype=np.int8),
                "action_mask": spaces.Box(low=0, high=1, shape=(52,), dtype=np.int8),
            })
            for agent in self.possible_agents
        }

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return self._observation_spaces[agent]

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return self._action_spaces[agent]

    def render(self):
        if self.render_mode == "human":
            print(f"State: {self._game.state}")
            print(f"Trick: {self._game.current_trick}")
            print(f"Scores: {self._game.scores}")

    def observe(self, agent):
        agent_id = self.agent_name_mapping[agent]
        player = self._game.players[agent_id]
        
        # 1. Hand (52)
        hand_vec = np.zeros(52, dtype=np.int8)
        for card in player.hand:
            idx = self._card_to_idx(card)
            hand_vec[idx] = 1
            
        # 2. Current Trick (208)
        trick_vec = np.zeros(208, dtype=np.int8)
        for pid, card in self._game.current_trick:
            # Relative position to current agent might be better, but absolute is easier for now
            idx = pid * 52 + self._card_to_idx(card)
            trick_vec[idx] = 1
            
        # 3. Trump Suit (4)
        trump_vec = np.zeros(4, dtype=np.int8)
        if self._game.trump_suit:
            trump_vec[self._game.trump_suit.value - 1] = 1
            
        # 4. Hakim (4)
        hakim_vec = np.zeros(4, dtype=np.int8)
        hakim_vec[self._game.hakim_index] = 1
        
        # 5. My Index (4)
        id_vec = np.zeros(4, dtype=np.int8)
        id_vec[agent_id] = 1
        
        obs = np.concatenate([hand_vec, trick_vec, trump_vec, hakim_vec, id_vec])
        
        # Action Mask
        mask = np.zeros(52, dtype=np.int8)
        if self._game.state == GameState.PLAYING:
            if agent_id == self._game.current_player_index:
                legal_cards = self._game.get_legal_moves(agent_id)
                for card in legal_cards:
                    mask[self._card_to_idx(card)] = 1
        elif self._game.state == GameState.DECLARE_TRUMP:
            if agent_id == self._game.hakim_index:
                # Can declare any suit. But action space is 52 cards.
                # We need to map actions to "Declare Suit" or "Play Card".
                # For simplicity, let's say playing any card of a suit declares that suit.
                mask.fill(1) # Any card can be "played" to declare its suit
        
        return {"observation": obs, "action_mask": mask}

    def close(self):
        pass

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        
        self._game.reset()
        
        # Determine who starts
        # In our game logic, state starts at DETERMINE_HAKIM then DECLARE_TRUMP
        # But _deal_initial_cards moves it to DECLARE_TRUMP and sets current_player to Hakim
        
        self._agent_selector = agent_selector(self.agents)
        
        # Fast forward to the correct agent
        self.agent_selection = self.possible_agents[self._game.current_player_index]

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return

        agent = self.agent_selection
        agent_id = self.agent_name_mapping[agent]
        
        # Map action index back to card/suit
        # Action is 0-51
        card = self._idx_to_card(action)
        
        if self._game.state == GameState.DECLARE_TRUMP:
            self._game.declare_trump(card.suit)
            # Game state moves to PLAYING, current player is still Hakim (leader)
        elif self._game.state == GameState.PLAYING:
            self._game.play_card(agent_id, card)
        
        # Update rewards
        # We can give dense rewards here if we want
        # For now, let's just give 1 for winning game
        
        if self._game.state == GameState.FINISHED:
            for i, agent_name in enumerate(self.agents):
                team = i % 2
                # If team won
                if (team == 0 and self._game.scores[0] > self._game.scores[1]) or \
                   (team == 1 and self._game.scores[1] > self._game.scores[0]):
                    self.rewards[agent_name] = 1
                else:
                    self.rewards[agent_name] = -1
            
            self.terminations = {a: True for a in self.agents}
        
        self._cumulative_rewards[agent] = 0
        self.agent_selection = self.possible_agents[self._game.current_player_index]
        self._accumulate_rewards()

    def _card_to_idx(self, card: Card) -> int:
        # Suit: Hearts=0, Diamonds=1, Clubs=2, Spades=3
        # Rank: 2=0 ... Ace=12
        suit_offset = (card.suit.value - 1) * 13
        rank_offset = card.rank.value - 2
        return suit_offset + rank_offset

    def _idx_to_card(self, idx: int) -> Card:
        suit_val = (idx // 13) + 1
        rank_val = (idx % 13) + 2
        return Card(Rank(rank_val), Suit(suit_val))
