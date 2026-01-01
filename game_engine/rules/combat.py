import math

from game_engine.core.game import Game
from game_engine.core.board import Piece
from game_engine.core.events import CombatCalculateEvent, CombatResolvedEvent
from game_engine.rules.overdrive import gain_overdrive_from_attack


def calculate_combat_proba(game: Game, attacker: Piece, defender: Piece) -> float:
    """
    Calcule la probabilité de victoire de l'attaquant contre le défenseur,
    en déclenchant tous les hooks du moteur.
    """
    state = game.state
    event_bus = game.event_bus

    # Valeurs par défaut
    x = attacker.force
    y = defender.force
    k = 1.514
    a = 1.25

    calc_event = CombatCalculateEvent(
                    attacker_id=attacker.piece_id,
                    defender_id=defender.piece_id,
                    x=x, y=y, k=k, a=a
                )
    event_bus.emit(calc_event, state)
    if calc_event.cancelled:
        return -1  # TODO : need to completly handle this case, temporary fix
    
    x, y, k, a = calc_event.x, calc_event.y, calc_event.k, calc_event.a

    exponent = -k * (math.sqrt(x) - math.sqrt(y) + a)
    probability =  1.0 / (1.0 + math.exp(exponent))

    return probability


def resolve_combat(game: Game, attacker: Piece, defender: Piece) -> bool:
    """
    Résout un combat via RNG.
    Retourne True si l'attaquant gagne.
    """
    probability = calculate_combat_proba(game, attacker, defender)

    roll = game.state.rng.random()
    success = roll <= probability

    resolve_event = CombatResolvedEvent(
        attacker_id=attacker.piece_id,
        defender_id=defender.piece_id,
        success=success,
        probability=probability
    )
    game.state.event_bus.emit(resolve_event, game.state)

    if not resolve_event.cancelled:
        gain_overdrive_from_attack(game.state, attacker.owner, probability, success)

        attacker_square = game.state.board.get_square(attacker.piece_id)
        defender_square = game.state.board.get_square(defender.piece_id)
        if success :  # Défenseur détruit
            game.state.board.remove_piece(defender_square)
            return True
        # Attaquant détruit
        game.state.board.remove_piece(attacker_square)
        return False
    return False
