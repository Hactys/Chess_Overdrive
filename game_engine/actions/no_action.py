from game_engine.core.state import GameState
from game_engine.actions.base_action import BaseAction


class NoAction(BaseAction):
    """
    Tell the game to do nothing.
    """
    def __init__(self):
        return

    def validate(self, state: GameState) -> bool:
        return True

    def execute(self, state: GameState) -> None:
        return
