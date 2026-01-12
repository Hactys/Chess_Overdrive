from game_engine.core.state import GameState
from .base_action import BaseAction


class PlayCardAction(BaseAction):
    def __init__(self, card_id: str, targets: dict): ...

    def validate(self, state: GameState) -> bool: ...

    def execute(self, state: GameState) -> None: ...
