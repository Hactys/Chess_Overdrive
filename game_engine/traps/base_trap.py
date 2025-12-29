from abc import ABC
from game_engine.core.events import GameEvent
from game_engine.core.state import GameState


class TrapInstance(ABC):
    position: str
    owner_id: str

    def on_trigger(self, event: GameEvent, state: GameState) -> None:
        ...
