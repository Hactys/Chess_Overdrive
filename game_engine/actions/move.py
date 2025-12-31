from typing import List

from game_engine.core.board import Square
from game_engine.core.events import (MoveAttemptEvent, PathCheckEvent, PieceLandedEvent, 
                                     CombatCalculateEvent, CombatResolvedEvent)
from game_engine.core.game import Game
from game_engine.rules.chess_movement import is_legal_move, get_path
from game_engine.rules.combat import compute_probability
from game_engine.actions.base_action import BaseAction


class MoveAction(BaseAction):
    def __init__(self, from_pos: Square, to_pos: Square):
        self.from_pos = from_pos
        self.to_pos = to_pos

    def validate(self, game: Game) -> bool:
        state = game.state
        board = state.board
        piece = board.get_piece(self.from_pos)

        if piece is None:
            return False
        if piece.owner != state.current_player:
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
            from_pos=self.from_pos,
            to_pos=self.to_pos,
            piece_id=piece.piece_id
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
        if path_event.cancelled:
            return

        # Déplacement physique
        target_piece = board.get_piece(self.to_pos)
        board.move_piece(self.from_pos, self.to_pos)

        # Pièce arrivée
        landed_event = PieceLandedEvent(
            position=self.to_pos,
            piece_id=piece.piece_id
        )
        event_bus.emit(landed_event, state)

        # Combat éventuel
        if target_piece is not None:
            attacker = piece
            defender = target_piece
            
            x = attacker.force  # Valeurs par défaut
            y = defender.force
            k = 0.485  # Valeur de lissage de la probabilité de capture
            a = 1.75   # Valeur d'aventage pour l'attaquant 

            calc_event = CombatCalculateEvent(
                attacker_id=attacker.piece_id,
                defender_id=defender.piece_id,
                x=x, y=y, k=k, a=a
            )  # type: ignore
            event_bus.emit(calc_event, state)
            if calc_event.cancelled:
                return

            probability = compute_probability(
                calc_event.x, calc_event.y,
                calc_event.k, calc_event.a
            )
            calc_event.probability = probability

            roll = state.rng.random()
            success = roll <= probability

            resolve_event = CombatResolvedEvent(
                attacker_id=attacker.piece_id,
                defender_id=defender.piece_id,
                success=success,
                probability=probability
            )  # type: ignore
            event_bus.emit(resolve_event, state)

            if success:  # Défenseur détruit
                board.remove_piece(self.to_pos)
                board.set_piece(self.to_pos, attacker)
            else:  # Attaquant détruit
                board.remove_piece(self.from_pos)

        # Passage au tour de l'adversaire
        game.end_turn()


        # Fin de l’action
