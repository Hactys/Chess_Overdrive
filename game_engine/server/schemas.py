from game_engine.core.state import GameState


def state_to_dict(state: GameState) -> dict:
    return state.to_dict()
