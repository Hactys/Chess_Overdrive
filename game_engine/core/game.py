from typing import List

from game_engine.core.state import GameState, PlayerID
from game_engine.core.event_bus import EventBus
from game_engine.core.events import TurnStartEvent, TurnEndEvent
from game_engine.actions.base_action import BaseAction
from game_engine.rules.chess_movement import MOVE_RULES


def get_moves_for_piece(state, from_pos):
    piece = state.board.get_piece(from_pos)
    if not piece: 
        return []
    
    moves=[]
    for rule in MOVE_RULES:
        moves += rule.generate(state, from_pos, piece)
    for rule in MOVE_RULES:
        moves = rule.modify(state, from_pos, piece, moves)
    return list(set(moves))


class Game:
    """
    Orchestrateur principal du moteur.
    - Applique les actions
    - Gère les tours
    - Centralise l'EventBus
    """
    def __init__(self, state: GameState, event_bus: EventBus, 
                 player_order: List[PlayerID]):
        """
        player_order définit l'ordre de jeu (ex: ["white", "black"]) à remplacer par les IDs
        """
        self.state = state
        self.event_bus = event_bus
        self.player_order = player_order

        if state.current_player not in player_order:
            raise ValueError("current_player must be in player_order")

        self.state.event_bus = event_bus  # Injection du bus dans l'état (choix volontaire)

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

        self._rotate_player()
        self.state.next_turn()

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
        if not action.validate(self.state):
            return False

        action.execute(self.state)
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

        moves = []
        moves = get_moves_for_piece(self.state, from_pos)

        # TODO : on pourrait aussi filtrer les cases mettant son roi en échec pour les éviter
        return moves
