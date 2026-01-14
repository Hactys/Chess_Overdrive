from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from game_engine.core.game import Game


class BaseAction(ABC):
    """
    Action abstraite du moteur.
    Toute interaction joueur → moteur passe par une Action.
    """

    def __init__(self, player_id: str):
        self.player_id = player_id

    @abstractmethod
    def validate(self, game: Game) -> bool:
        """
        Vérifie si l'action est autorisée dans l'état courant.
        Ne modifie PAS l'état.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, game: Game) -> None:
        """
        Applique l'action à l'état du jeu.
        Peut émettre des événements.
        """
        raise NotImplementedError
