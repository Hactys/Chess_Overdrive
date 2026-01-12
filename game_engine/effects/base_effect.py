from abc import ABC
from typing import TYPE_CHECKING
from game_engine.core.events import GameEvent

if TYPE_CHECKING:
    from game_engine.core.state import GameState


class EffectInstance(ABC):
    effect_id: str
    target_id: str
    expires_at_turn: int

    def on_event(self, event: GameEvent, state: GameState) -> None: ...

    def is_expired(self, state: GameState) -> bool: ...
