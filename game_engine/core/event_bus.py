from typing import Callable, Dict, List, Type, Tuple, TYPE_CHECKING
from collections import defaultdict

from .events import GameEvent
if TYPE_CHECKING:
    from game_engine.core.state import GameState  


EventHandler = Callable[[GameEvent, "GameState"], None]


class EventBus:
    """
    Bus d'événements central du moteur.

    - Supporte les priorités
    - Permet modification / annulation des événements
    - Ordre déterministe
    """
    def __init__(self):
        # event_type -> list[(priority, handler)]
        self._handlers: Dict[
            Type[GameEvent],
            List[Tuple[int, EventHandler]]
        ] = defaultdict(list)

    def subscribe(self, event_type: Type[GameEvent], 
                        handler: EventHandler, priority: int = 0) -> None:
        """
        Inscrit un handler sur un type d'événement.
        Plus la priorité est élevée, plus le handler est appelé tôt.
        """
        self._handlers[event_type].append((priority, handler))
        self._handlers[event_type].sort(key=lambda x: -x[0])  # Tri décroissant par priorité

    def emit(self, event: GameEvent, state: "GameState") -> None:
        """
        Émet un événement :
        - appelle tous les handlers correspondants
        - s'arrête si l'événement est annulé
        """
        state.log_event(event)

        for event_type, handlers in self._handlers.items():
            if isinstance(event, event_type):  # Dispatch par type
                for _, handler in handlers:
                    if event.cancelled:  # Besoin d'être à l'intérieur si un handler annulé l'event
                        return
                    handler(event, state)
