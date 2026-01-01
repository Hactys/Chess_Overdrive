import math
from typing import TYPE_CHECKING

from game_engine.core.events import (
    TriggerOverloadEvent,
    OverloadExplosionEvent,
    EndOverloadEvent,
    TurnStartEvent
)

if TYPE_CHECKING:
    from game_engine.core.state import GameState


def overload_probability(overdrive: float) -> float:
    # Probabilité d'entrée en Overload
    # x = overdrive / 100
    # P(overload) = arctan(a*(x-1)) * (2/pi)
    if overdrive < 100:
        return 0
    a = 1.962610507
    x = overdrive / 100.0
    return min(1.0, math.atan(a * (x - 1)) * (2 / math.pi))  # normalement le min n'est pas nécessaire


def handle_overload_start(event: TurnStartEvent, state: GameState):
    """Vérifie au début du tour si un joueur doit entrer en overload."""
    player = state.get_player(event.player_id)

    # calcul de probabilité
    p = overload_probability(player.overdrive) 

    trigger_event = TriggerOverloadEvent(player_id=player.player_id, probability=p)
    state.event_bus.emit(trigger_event, state)

    if trigger_event.cancelled or trigger_event.triggered:
        return

    # Jet de RNG pour savoir si overload commence
    roll = state.rng.random()
    if roll <= p:
        trigger_event.triggered = True
        # Explosion immédiate au tour de surcharge
        overload_explosion(state, player.player_id)


def overload_explosion(state: GameState, player_id: str):
    """Déclenche une explosion random sur une pièce du joueur + propagation."""

    player = state.get_player(player_id)

    # Sélection d'une pièce aléatoire
    pieces = [(pos, piece) for pos, piece in state.board._grid.items()
              if piece and piece.owner == player_id]

    if not pieces:
        return  # aucun effet si plus de pièce

    pos, piece = state.rng.choice(pieces)

    destroyed = []
    destroyed.append(piece.piece_id)

    # Propagation aux cases adjacentes
    for adj in state.board.get_adjacent_squares(pos):
        p = state.board.get_piece(adj)
        if p:
            destroyed.append(p.piece_id)

    # suppression physique
    for pid in destroyed:
        square = state.board.get_square(pid)
        state.board.remove_piece(square)

    # event de destruction complète
    ev = OverloadExplosionEvent(player_id=player_id, piece_id=piece.piece_id, destroyed=destroyed)
    state.event_bus.emit(ev, state)


def end_overload(state: GameState, player_id: str, reason: str = "stabilized"):
    """Fin d'overload manuelle ou automatique."""
    ev = EndOverloadEvent(player_id=player_id, reason=reason)
    state.event_bus.emit(ev, state)
