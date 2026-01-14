from typing import List

from game_engine.core.board import Square
from game_engine.core.events import MoveAttemptEvent, PathCheckEvent, PieceLandedEvent
from game_engine.core.game import Game
from game_engine.rules.chess_movement import is_legal_move, get_path
from game_engine.rules.combat import resolve_combat
from game_engine.actions.base_action import BaseAction


class MoveAction(BaseAction):
    def __init__(self, player_id: str, from_pos: Square, to_pos: Square):
        super().__init__(player_id)
        self.from_pos = from_pos
        self.to_pos = to_pos

    def validate(self, game: Game) -> bool:
        state = game.state
        board = state.board
        piece = board.get_piece(self.from_pos)

        if piece is None:
            return False
        if self.player_id != state.current_player:
            return False
        if piece.owner != self.player_id:
            return False
        if not board.is_inside(self.to_pos):
            return False
        return True

    def execute(self, game: Game) -> None:
        """
        Pipeline pour le déroulement de l'execution d'une action de mouvement.

        :param state: Current state of the game
        :type state: GameState
        """
        state = game.state
        board = state.board
        piece = board.get_piece(self.from_pos)

        if piece is None:
            raise RuntimeError("Invalid MoveAction execution")

        event_bus = state.event_bus

        # Move attempt
        move_event = MoveAttemptEvent(
            from_pos=self.from_pos, to_pos=self.to_pos, piece_id=piece.piece_id
        )
        event_bus.emit(move_event, state)
        if move_event.cancelled:
            return

        # Règles d’échecs classiques
        if not is_legal_move(state, self.from_pos, self.to_pos):
            return

        # Path check
        path: List[Square] = get_path(self.from_pos, self.to_pos)
        path_event = PathCheckEvent(path=path)
        event_bus.emit(path_event, state)
        if path_event.cancelled:  # Normalement jamais le cas
            return

        # Déplacement physique
        target_piece = board.get_piece(self.to_pos)

        # Combat éventuel
        if target_piece is not None:
            attacker = piece
            defender = target_piece
            success = resolve_combat(game, attacker, defender)
            if not success:
                game.end_turn()
                return

        # Le combat se passe "en l'air"
        board.move_piece(self.from_pos, self.to_pos)

        # Pièce arrivée
        landed_event = PieceLandedEvent(position=self.to_pos, piece_id=piece.piece_id)
        event_bus.emit(landed_event, state)

        # Passage au tour de l'adversaire
        game.end_turn()

        # Fin de l’action
