from typing import Dict
from hashlib import sha256

from game_engine.core.game import Game
from game_engine.core.state import GameState, PlayerState
from game_engine.core.board import Board, Piece
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
        setup_standard_board(board, list(players.keys()))
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


def setup_standard_board(board, players):
    """
    Initialise les pièces d'échecs standard sur l'échiquier.
    Force basique : pion=1, cavalier/fou/tour=3, dame=9, roi=5 par exemple.
    Les valeurs sont modifiables pour équilibrer le système.
    Agi par effet de bord.
    """
    # pièces blanches
    pieces_white = {
        "a1": ("rook", 3),
        "b1": ("knight", 3),
        "c1": ("bishop", 3),
        "d1": ("queen", 9),
        "e1": ("king", 5),
        "f1": ("bishop", 3),
        "g1": ("knight", 3),
        "h1": ("rook", 3),
    }
    for col in "abcdefgh":
        pieces_white[f"{col}2"] = ("pawn", 1)

    for pos, (ptype, force) in pieces_white.items():
        board.set_piece(
            pos,
            Piece(
                piece_id=f"w_{pos}", color="white", owner=players[0], piece_type=ptype, force=force
            ),
        )

    # pièces noires
    pieces_black = {
        "a8": ("rook", 3),
        "b8": ("knight", 3),
        "c8": ("bishop", 3),
        "d8": ("queen", 9),
        "e8": ("king", 5),
        "f8": ("bishop", 3),
        "g8": ("knight", 3),
        "h8": ("rook", 3),
    }
    for col in "abcdefgh":
        pieces_black[f"{col}7"] = ("pawn", 1)

    for pos, (ptype, force) in pieces_black.items():
        board.set_piece(
            pos,
            Piece(
                piece_id=f"b_{pos}", color="black", owner=players[1], piece_type=ptype, force=force
            ),
        )
