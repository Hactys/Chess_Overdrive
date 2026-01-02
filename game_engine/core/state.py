from dataclasses import dataclass, field
from typing import Dict, List

from game_engine.cards.base_card import CardInstance
from game_engine.effects.base_effect import EffectInstance
from game_engine.traps.base_trap import TrapInstance
from game_engine.rules.overload import overload_probability

from .board import Board
from .rng import RNG
from .events import GameEvent
from .event_bus import EventBus

PlayerID = str


@dataclass
class PlayerState:
    player_id: PlayerID
    overdrive: float = 0.0
    hand: List["CardInstance"] = field(default_factory=list)
    deck: List[str] = field(default_factory=list)
    graveyard: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "player_id": self.player_id,
            "overdrive": self.overdrive,
            "hand": [c.card_id for c in self.hand],
            "deck": list(self.deck),
            "graveyard": list(self.graveyard),
            "stats": dict(self.stats),
        }


@dataclass
class GameState:
    board: Board
    game_id: str
    players: Dict[PlayerID, PlayerState]
    current_player: PlayerID
    turn: int = 1

    active_effects: List["EffectInstance"] = field(default_factory=list)
    active_traps: Dict[str, "TrapInstance"] = field(default_factory=dict)

    rng: RNG = field(default_factory=lambda: RNG(0))
    event_log: List[GameEvent] = field(default_factory=list)
    event_bus: EventBus = field(default_factory=lambda: EventBus())

    def get_player(self, player_id: PlayerID) -> PlayerState:
        return self.players[player_id]

    def next_turn(self) -> None:
        self.turn += 1

    def log_event(self, event: GameEvent) -> None:
        self.event_log.append(event)

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "turn": self.turn,
            "current_player": self.current_player,
            "players": {pid: player.to_dict() for pid, player in self.players.items()},
            "board": self.board.to_dict(),
            "active_effects": [
                {
                    "effect_id": e.effect_id,
                    "expires_at_turn": e.expires_at_turn
                }
                for e in self.active_effects
            ],
            "active_traps": list(self.active_traps.keys()),
            "rng_seed": self.rng.seed,
            "overload_info": {
                pid: overload_probability(player.overdrive)
                for pid, player in self.players.items()
            }
        }
