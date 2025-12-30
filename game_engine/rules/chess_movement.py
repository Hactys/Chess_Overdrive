from typing import List, Protocol
from game_engine.core.state import GameState
from game_engine.core.board import Square, pos_to_coords, coords_to_pos
from game_engine.core.board import Piece
from game_engine.core.events import MovesGenerateEvent


class MoveRule(Protocol):
    """Interface pour TOUTES les règles de déplacement.
      Chaque règle peut ajouter, filtrer ou modifier des déplacements.
    """
    def generate(self, state: GameState, from_pos: Square, piece: Piece) -> List[Square]:
        return []
    
    def on_generate(self, event: MovesGenerateEvent, state: GameState):
        return



class ChessMovementRule(MoveRule):  # mouvements classiques d'échecs
    def generate(self, state, from_pos, piece):
        moves = []
        board = state.board
        fx, fy = pos_to_coords(from_pos)

        def add(dx,dy,repeat=False):
            cx, cy = fx+dx, fy+dy
            while board.is_inside(pos:=coords_to_pos(cx,cy)):
                target = board.get_piece(pos)
                if target:
                    if target.owner != piece.owner:
                        moves.append(pos)
                    break
                moves.append(pos)
                if not repeat: 
                    break
                cx += dx
                cy += dy

        p=piece.piece_type.lower()
        if p == "pawn":
            direction = 1 if piece.owner=="white" else -1
            forward = coords_to_pos(fx, fy+direction)
            if board.is_inside(forward) and not board.get_piece(forward):
                moves.append(forward)
            for dx in (-1,1):
                cap = coords_to_pos(fx+dx, fy+direction)
                if board.is_inside(cap):
                    t = board.get_piece(cap)
                    if t and t.owner!=piece.owner:
                        moves.append(cap)

        if p=="rook":   
            add(1,0,True)
            add(-1,0,True)
            add(0,1,True)
            add(0,-1,True)
        if p=="bishop": 
            add(1,1,True)
            add(1,-1,True)
            add(-1,1,True)
            add(-1,-1,True)
        if p=="queen":
            add(1,0,True)
            add(-1,0,True)
            add(0,1,True)
            add(0,-1,True)
            add(1,1,True)
            add(1,-1,True)
            add(-1,1,True)
            add(-1,-1,True)
        if p=="king":
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx or dy:
                        add(dx,dy)
        if p=="knight":
            for dx,dy in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                add(dx,dy)

        return moves
    
    def on_generate(self, event: MovesGenerateEvent, state: GameState):
        piece = state.board.get_piece(event.from_pos)
        if not piece or piece.piece_id != event.piece_id:
            return

        moves = self.generate(state, event.from_pos, piece)
        event.moves.extend(moves)


class SpectralRule(MoveRule):
    """une pièce Spectrale ignore les collisions MAIS ne capture pas."""
    def on_generate(self, event: MovesGenerateEvent, state: GameState):
        piece = state.board.get_piece(event.from_pos)
        if not piece or piece.piece_id != event.piece_id:
            return

        if not any(e.effect_id == "spectral" and e.target_id == piece.piece_id 
                   for e in state.active_effects):
            return

        moves = []
        board = state.board
        fx, fy = pos_to_coords(event.from_pos)

        def add(dx,dy):
            cx, cy = fx+dx, fy+dy
            while board.is_inside(pos:=coords_to_pos(cx,cy)):
                target = board.get_piece(pos)
                if target is None :
                    moves.append(pos)
                cx += dx
                cy += dy

        p = piece.piece_type.lower()
        if p=="rook":   
            add(1,0)
            add(-1,0)
            add(0,1)
            add(0,-1)
        elif p=="bishop": 
            add(1,1)
            add(1,-1)
            add(-1,1)
            add(-1,-1)
        elif p=="queen":
            add(1,0); add(-1,0)
            add(0,1); add(0,-1)
            add(1,1); add(1,-1)
            add(-1,1); add(-1,-1)
        else:
            return
        event.moves[:] = moves



# Garder ça après les class de règles.
MOVE_RULES: List[MoveRule] = [
    ChessMovementRule(),
    SpectralRule(),      # autres règles se plug ici
]


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
