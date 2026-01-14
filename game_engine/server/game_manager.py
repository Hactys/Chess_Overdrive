from typing import Dict
from hashlib import sha256

from game_engine.core.game import Game
from game_engine.core.state import GameState, PlayerState
from game_engine.core.board import Board
from game_engine.core.event_bus import EventBus
from game_engine.core.rng import RNG
from game_engine.rules import register_standard_rules


class GameManager:
    def __init__(self):
        self.games: Dict[str, Game] = {}  # game_id -> Game

    def _generate_seed(self, game_id: str) -> int:
        """Génère une seed numérique stable à partir du game_id."""
        return int(sha256(game_id.encode()).hexdigest()[:16], 16)

    def create_game(self, game_id: str, players: Dict[str, dict]):
        player_states = {}

        for pid, pdata in players.items():
            # pdata peut contenir les cartes du joueur etc. plus tard
            player_states[pid] = PlayerState(player_id=pid, username=pdata["username"])

        board = Board()
        game_seed = self._generate_seed(game_id)

        state = GameState(
            board=board,
            game_id=game_id,
            players=player_states,
            current_player=list(player_states.keys())[0],
            rng=RNG(seed=game_seed),
        )  # type: ignore

        bus = EventBus()
        register_standard_rules(bus)
        game = Game(state, bus, list(players.keys()))
        self.games[game_id] = game
        return game

    def get_game(self, game_id: str) -> Game:
        return self.games[game_id]
