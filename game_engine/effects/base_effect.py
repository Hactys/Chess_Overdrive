from abc import ABC
from game_engine.core.events import GameEvent
from game_engine.core.state import GameState


class EffectInstance(ABC):
    effect_id: str
    target_id: str
    expires_at_turn: int

    def on_event(self, event: GameEvent, state: GameState) -> None:
        ...

    def is_expired(self, state: GameState) -> bool:
        ...
