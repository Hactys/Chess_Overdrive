from typing import Dict, Optional, List, Tuple

Square = str  # ex: "e4"


def pos_to_coords(square: Square) -> Tuple[int, int]:
    """Convertit 'e4' → (4, 3)"""
    col = ord(square[0].lower()) - ord("a")
    row = int(square[1:]) - 1
    return col, row


def coords_to_pos(col: int, row: int) -> Square:
    """Convertit (4, 3) → 'e4'"""
    return f"{chr(col + ord('a'))}{row + 1}"


class Piece:
    def __init__(self, piece_id: str, color: str, owner: str, piece_type: str, force: int):
        self.piece_id = piece_id
        self.color = color
        self.owner = owner
        self.piece_type = piece_type
        self.force = force

    def to_dict(self) -> dict:
        return {
            "id": self.piece_id,
            "color": self.color,
            "owner": self.owner,
            "type": self.piece_type,
            "force": self.force,
        }


class Board:
    """
    Plateau extensible (jusqu'à 12x12).
    Ne contient AUCUNE règle de déplacement.
    """

    # TODO : à voir si avec l'ajout de cases ça ne casse pas tout

    def __init__(self, width: int = 8, height: int = 8):
        if width > 12 or height > 12:
            raise ValueError("Board size exceeds maximum (12x12)")
        self.width = width
        self.height = height
        self._grid: Dict[Square, Optional[Piece]] = {}

        # Initialisation des cases vides
        for col in range(width):
            for row in range(height):
                self._grid[coords_to_pos(col, row)] = None

    def is_inside(self, square: Square) -> bool:
        try:
            col, row = pos_to_coords(square)
        except Exception:
            return False
        return 0 <= col < self.width and 0 <= row < self.height

    def get_piece(self, square: Square) -> Optional[Piece]:
        if not self.is_inside(square):
            return None
        return self._grid.get(square)

    def get_square(self, piece_id: str) -> Square:
        for square, piece in self._grid.items():
            if piece is not None and piece.piece_id == piece_id:
                return square
        raise ValueError(f"'{piece_id}' not on the board")

    def set_piece(self, square: Square, piece: Optional[Piece]) -> None:
        if not self.is_inside(square):
            raise ValueError(f"Square hors plateau: {square}")
        self._grid[square] = piece

    def move_piece(self, from_pos: Square, to_pos: Square) -> None:
        if not self.is_inside(from_pos) or not self.is_inside(to_pos):
            raise ValueError("Move outside board")

        piece = self.get_piece(from_pos)
        if piece is None:
            raise ValueError("No piece at source square")

        self.set_piece(to_pos, piece)
        self.set_piece(from_pos, None)

    def remove_piece(self, square: Square) -> None:
        if self.is_inside(square):
            self._grid[square] = None

    def get_adjacent_squares(self, square: Square) -> List[Square]:
        if not self.is_inside(square):
            return []

        col, row = pos_to_coords(square)
        adj = []

        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                if dc == 0 and dr == 0:
                    continue
                nc, nr = col + dc, row + dr
                if 0 <= nc < self.width and 0 <= nr < self.height:
                    adj.append(coords_to_pos(nc, nr))

        return adj

    def expand(self, squares: List[Square]) -> None:
        """
        Ajoute de nouvelles cases au plateau (extension).
        Les squares doivent être adjacentes au plateau existant.
        """
        for pos in squares:
            if pos in self._grid:
                continue

            col, row = pos_to_coords(pos)

            if col >= 12 or row >= 12:
                raise ValueError("Expansion exceeds board limits")

            self._grid[pos] = None
            self.width = max(self.width, col + 1)
            self.height = max(self.height, row + 1)

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "pieces": {
                pos: piece.to_dict() for pos, piece in self._grid.items() if piece is not None
            },
        }
