from abc import ABC
from typing import TYPE_CHECKING
from game_engine.core.events import GameEvent

if TYPE_CHECKING:
    from game_engine.core.state import GameState  


class TrapInstance(ABC):
    position: str
    owner_id: str

    def on_trigger(self, event: GameEvent, state: GameState) -> None:
        ...
