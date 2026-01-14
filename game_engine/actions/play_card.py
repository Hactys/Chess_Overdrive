from game_engine.core.game import Game
from .base_action import BaseAction


class PlayCardAction(BaseAction):
    def __init__(self, player_id: str, card_id: str, targets: dict): ...

    def validate(self, game: Game) -> bool: ...

    def execute(self, game: Game) -> None: ...
