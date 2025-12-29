from abc import ABC, abstractmethod
from game_engine.core.state import GameState


class BaseAction(ABC):
    """
    Action abstraite du moteur.
    Toute interaction joueur → moteur passe par une Action.
    """
    @abstractmethod
    def validate(self, state: GameState) -> bool:
        """
        Vérifie si l'action est autorisée dans l'état courant.
        Ne modifie PAS l'état.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, state: GameState) -> None:
        """
        Applique l'action à l'état du jeu.
        Peut émettre des événements.
        """
        raise NotImplementedError
