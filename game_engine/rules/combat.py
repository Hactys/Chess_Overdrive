import math
from game_engine.core.state import GameState


def compute_probability(x: float, y: float, k: float, a: float) -> float:
    """
    Calcule la probabilité de victoire de l'attaquant.
    """
    exponent = -k * (x - y + a)
    return 1.0 / (1.0 + math.exp(exponent))


def resolve_combat(state: GameState, attacker_id: str, 
                   defender_id: str, probability: float) -> bool:
    """
    Résout un combat via RNG.
    Retourne True si l'attaquant gagne.
    """
    roll = state.rng.random()
    return roll <= probability
