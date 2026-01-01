from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class GameEvent:
    """
    Événement de base.
    Tous les événements du moteur en héritent.
    """
    name: str = field(init=False)
    payload: Dict[str, Any] = field(default_factory=dict)

    cancelled: bool = False  # Permet à un handler d'annuler la suite du traitement

    def cancel(self) -> None:
        self.cancelled = True

    def __post_init__(self):
        self.name = self.__class__.__name__.replace("Event", "")


# ÉVÉNEMENTS DE JEU

@dataclass
class MoveAttemptEvent(GameEvent):
    from_pos: str = ""
    to_pos: str = ""
    piece_id: str = ""


@dataclass
class PathCheckEvent(GameEvent):
    path: list = field(default_factory=list)


@dataclass
class PieceLandedEvent(GameEvent):
    position: str = ""
    piece_id: str = ""


@dataclass
class MovesGenerateEvent(GameEvent):
    """
    Étape 1 : génération brute des coups possibles
    """
    from_pos: str = ""
    piece_id: str = ""
    moves: list[str] = field(default_factory=list)


# COMBAT

@dataclass
class CombatCalculateEvent(GameEvent):
    attacker_id: str = ""
    defender_id: str = ""

    x: float = 0.0
    y: float = 0.0
    k: float = 0.0
    a: float = 0.0

    probability: Optional[float] = None


@dataclass
class CombatResolvedEvent(GameEvent):
    attacker_id: str = ""
    defender_id: str = ""
    success: bool = False
    probability: float = 0.0


# TOURS

@dataclass
class TurnStartEvent(GameEvent):
    player_id: str = ""


@dataclass
class TurnEndEvent(GameEvent):
    player_id: str = ""


@dataclass
class OverdriveChangedEvent(GameEvent):
    player_id: str = ""
    delta: float = 0.0
    new_value: float = 0.0


@dataclass
class TriggerOverloadEvent(GameEvent):
    player_id: str = ""
    probability: float = 0.0
    triggered: bool = False    # définit si l'entrée en overload a eu lieu


@dataclass
class OverloadExplosionEvent(GameEvent):
    player_id: str = ""
    piece_id: str = ""          # pièce détruite par l’explosion
    destroyed: list[str] = field(default_factory=list)  # list des pièces adjacentes détruites incluses


@dataclass
class EndOverloadEvent(GameEvent):
    player_id: str = ""
    reason: str = "stabilized"  # ex: retour sous 100, carte, événement etc.
