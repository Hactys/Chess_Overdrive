from game_engine.core.events import PathCheckEvent
from game_engine.core.state import GameState


def handle_blocking(event: PathCheckEvent, state: GameState) -> None:
    """
    Empêche les déplacements où une pièce bloque le chemin.
    Ne s'applique pas aux cavaliers (path list vide).
    """

    board = state.board

    # Si path est vide → cavalier → rien à bloquer
    for pos in event.path:
        piece = board.get_piece(pos)
        if piece is not None:
            # On bloque le mouvement
            event.cancel()
            return
