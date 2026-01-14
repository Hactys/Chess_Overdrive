from typing import List
from random import shuffle

from game_engine.core.board import Piece
from game_engine.core.state import GameState, PlayerID, PlayerState
from game_engine.core.event_bus import EventBus
from game_engine.core.events import MovesGenerateEvent, TurnStartEvent, TurnEndEvent
from game_engine.actions.base_action import BaseAction
from game_engine.rules.chess_movement import MOVE_RULES, ChessMovementRule, SpectralRule


def get_moves_for_piece(state, from_pos):
    piece = state.board.get_piece(from_pos)
    if not piece:
        return []

    moves = []
    for rule in MOVE_RULES:
        moves += rule.generate(state, from_pos, piece)
    return list(set(moves))


class Game:
    """
    Orchestrateur principal du moteur.
    - Applique les actions
    - Gère les tours
    - Centralise l'EventBus
    """

    def __init__(self, state: GameState, event_bus: EventBus, player_order: List[PlayerID]):
        """
        player_order définit l'ordre de jeu (ex: ["uuid-white", "uuid-black"])
        """
        self.state = state
        self.event_bus = event_bus
        self.player_order = player_order

        if state.current_player not in player_order:
            raise ValueError("current_player must be in player_order")

        self.state.event_bus = event_bus  # Injection du bus dans l'état (choix volontaire)
        self.register_move_rules()

    def register_move_rules(self):
        bus = self.event_bus
        bus.subscribe(MovesGenerateEvent, ChessMovementRule().on_generate, priority=0)  # type: ignore
        bus.subscribe(MovesGenerateEvent, SpectralRule().on_generate, priority=-10)  # type: ignore

    def start_turn(self) -> None:
        """
        Démarre le tour du joueur courant.
        """
        event = TurnStartEvent(player_id=self.state.current_player)  # type: ignore
        self.event_bus.emit(event, self.state)

    def end_turn(self) -> None:
        """
        Termine le tour du joueur courant et passe au suivant.
        """
        event = TurnEndEvent(player_id=self.state.current_player)  # type: ignore
        self.event_bus.emit(event, self.state)

        self.state.next_turn()
        self._rotate_player()
        self.start_turn()

    def _rotate_player(self) -> None:
        """
        Passe au joueur suivant selon l'ordre défini.
        """
        idx = self.player_order.index(self.state.current_player)
        next_idx = (idx + 1) % len(self.player_order)
        self.state.current_player = self.player_order[next_idx]

    def apply_action(self, action: BaseAction) -> bool:
        """
        Applique une action du joueur courant.

        Retourne True si l'action a été exécutée,
        False si elle est invalide.
        """
        if action.player_id not in self.state.players.keys():
            print(
                f"Game.applay_action : {action.player_id} not in {self.state.players.keys()}  (game: {self.state.game_id})"
            )
            return False

        if action.player_id != self.state.current_player:
            print(
                f"Rejected action from {action.player_id}: not current player (current={self.state.current_player} game: {self.state.game_id})"
            )
            return False

        if len(self.state.players) < 2:
            print(
                f"Rejected action: game {self.state.game_id} not ready ({len(self.state.players)}/2 players)"
            )
            return False

        if not action.validate(self):
            return False

        action.execute(self)
        return True

    def get_current_player(self) -> PlayerID:
        return self.state.current_player

    def get_turn(self) -> int:
        return self.state.turn

    def get_legal_moves(self, player_id: str, from_pos: str) -> list[str]:
        """Renvoie tous les mouvements autorisés par les règles."""
        piece = self.state.board.get_piece(from_pos)
        if not piece or piece.owner != player_id:
            return []

        gen_event = MovesGenerateEvent(
            from_pos=from_pos,
            piece_id=piece.piece_id,
        )
        self.event_bus.emit(gen_event, self.state)
        moves = list(set(gen_event.moves))

        # TODO : on pourrait aussi filtrer les cases mettant son roi en échec pour les éviter
        return moves

    def add_player(self, player_id: str, username: str) -> bool:
        """
        Ajoute un joueur à la partie.
        Retourne True si succès, False sinon.
        """
        if player_id in self.state.players.keys():
            return True
        if len(self.state.players) >= 2:
            print(f"Game {self.state.game_id} already has 2 players, cannot add {player_id}.")
            return False

        self.state.players[player_id] = PlayerState(player_id, username)
        print(f"Player {player_id} joined game {self.state.game_id} ({len(self.state.players)}/2)")

        # Si c'est le 2e joueur, on peut démarrer
        if len(self.state.players) == 2:
            self._initialize_board_and_start()

        return True

    def _initialize_board_and_start(self):
        """
        Appelée automatiquement quand 2 joueurs sont présents.
        """
        player_ids = list(self.state.players.keys())

        shuffle(player_ids)

        setup_standard_board(self.state.board, player_ids)

        self.player_order = player_ids
        self.state.current_player = player_ids[0]

        self.start_turn()


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
