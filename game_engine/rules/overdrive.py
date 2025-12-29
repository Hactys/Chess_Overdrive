from game_engine.core.state import GameState


def gain_overdrive(state: GameState, player_id: str, amount: float) -> None:
    ...

def spend_overdrive(state: GameState, player_id: str, amount: float) -> bool:
    ...
