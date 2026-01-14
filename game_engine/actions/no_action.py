from game_engine.core.game import Game
from game_engine.actions.base_action import BaseAction


class NoAction(BaseAction):
    """
    Tell the game to do nothing.
    """

    def __init__(self, player_id: str):
        super().__init__(player_id)

    def validate(self, game: Game) -> bool:
        return True

    def execute(self, game: Game) -> None:
        return
