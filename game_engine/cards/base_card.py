from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_engine.core.state import GameState  


class CardInstance:
    card_id: str
    owner_id: str


class BaseCard(ABC):
    card_id: str
    cost_overdrive: float

    @abstractmethod
    def can_play(self, state: GameState, targets: dict) -> bool:
        ...

    @abstractmethod
    def play(self, state: GameState, targets: dict) -> None:
        ...
