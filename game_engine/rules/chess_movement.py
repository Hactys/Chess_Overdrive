from typing import List
from game_engine.core.state import GameState
from game_engine.core.board import Square, pos_to_coords


def is_legal_move(state: GameState, from_pos: Square, to_pos: Square) -> bool:
    """
    Vérifie si le mouvement est légal selon les règles d'échecs classiques
    (sans tenir compte des cartes / effets et du chemin parcouru).
    """
    board = state.board
    piece = board.get_piece(from_pos)

    if piece is None:
        return False

    if not board.is_inside(to_pos):
        return False

    target = board.get_piece(to_pos)
    if target is not None and target.owner == piece.owner:
        return False

    fx, fy = pos_to_coords(from_pos)
    tx, ty = pos_to_coords(to_pos)

    dx = tx - fx
    dy = ty - fy

    ptype = piece.piece_type.lower()

    if ptype == "pawn":  # TODO : rajouter l'implémentation pour la gravité inversée
        direction = 1 if piece.owner == "white" else -1
        # Avancée simple
        if dx == 0 and dy == direction and target is None:
            return True
        # Capture
        if abs(dx) == 1 and dy == direction and target is not None:
            return True
        return False
    if ptype == "rook":
        return dx == 0 or dy == 0
    if ptype == "bishop":
        return abs(dx) == abs(dy)
    if ptype == "queen":
        return dx == 0 or dy == 0 or abs(dx) == abs(dy)
    if ptype == "knight":
        return (abs(dx), abs(dy)) in [(1, 2), (2, 1)]
    if ptype == "king":
        return max(abs(dx), abs(dy)) == 1
    return False


def get_path(from_pos: Square, to_pos: Square) -> List[Square]:
    """
    Retourne la liste des cases traversées ENTRE from_pos et to_pos (excluant from_pos).
    Pour cavalier, retourne une liste vide.
    """
    fx, fy = pos_to_coords(from_pos)
    tx, ty = pos_to_coords(to_pos)

    dx = tx - fx
    dy = ty - fy

    path = []

    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

    # Cavalier : saute
    if (abs(dx), abs(dy)) in [(1, 2), (2, 1)]:
        return []

    cx, cy = fx + step_x, fy + step_y
    while (cx, cy) != (tx, ty):
        path.append(f"{chr(cx + ord('a'))}{cy + 1}")
        cx += step_x
        cy += step_y

    return path
