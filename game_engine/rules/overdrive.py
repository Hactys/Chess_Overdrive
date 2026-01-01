from game_engine.core.state import GameState
from game_engine.core.events import OverdriveChangedEvent


def gain_overdrive_generic(state: GameState, player_id: str, cause: str, amount: float):
    """
    Interface générique réutilisable pour d'autres mécaniques :
    - activation effet
    - prise de risque
    - événement de chaos
    etc.
    On log la cause dans event.payload.
    """
    if amount == 0:
        return
    
    player = state.get_player(player_id)
    event = OverdriveChangedEvent(
        player_id=player_id, delta=amount, 
        new_value=player.overdrive + amount
        )
    event.payload["cause"] = cause

    event = OverdriveChangedEvent(player_id=player_id, delta=amount, new_value=player.overdrive)
    state.event_bus.emit(event, state)
    
    if not event.cancelled:
        player.overdrive += amount


def spend_overdrive(state: GameState, player_id: str, amount: float) -> bool:
    """Tente de consommer de l'overdrive. Retourne True si succès."""
    player = state.get_player(player_id)

    if player.overdrive < amount:
        return False

    player.overdrive -= amount

    event = OverdriveChangedEvent(player_id=player_id, delta=-amount, new_value=player.overdrive)
    state.event_bus.emit(event, state)
    return True


# GAMEPLAY UTILS

def gain_overdrive_from_attack(state: GameState, player_id: str, success_probability: float, success: bool):
    """
    Gain proportionnel au risque.
    - Plus le coup était risqué, plus on gagne.
    - 1/(1 - p) si réussite, 1/p si échec → récompense l'audace et équilibre le hasard.
    
    Exemple :
        p = 0.2 → si réussite -> +0.8  / si échec -> +0.2
        p = 0.7 → si réussite -> +0.3  / si échec -> +0.7
    """

    OVERDRIVE_MULTIPLIER = 5

    p = success_probability
    p = max(min(p, 0.9999), 0.0001)  # évite divisions extrêmes

    if success:
        amount = 1 / p ** 1.5 * OVERDRIVE_MULTIPLIER
    else:
        amount = 1 / (1.0 - p) ** 1.5 * OVERDRIVE_MULTIPLIER

    gain_overdrive_generic(state, player_id, "attack", amount)


def gain_overdrive_card_play(state: GameState, player_id: str, cost: float):
    """
    Gain par utilisation de carte.
    """
    gain_overdrive_generic(state, player_id, "card", cost)
