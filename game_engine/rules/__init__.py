from game_engine.core.event_bus import EventBus
from .blocking_rules import handle_blocking
from game_engine.core.events import PathCheckEvent


def register_standard_rules(bus: EventBus):
    """
    Active toutes les règles de base du jeu.
    (appelé au lancement d'une partie)
    """
    # Blocage de chemin → priorité haute (avant effets exotiques)
    bus.subscribe(PathCheckEvent, handle_blocking, priority=10)  # type: ignore
