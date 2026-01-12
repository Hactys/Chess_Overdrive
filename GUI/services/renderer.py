from GUI.core.templates import templates


PIECE_IMAGE_MAP = {
    ("white", "pawn"): "pawn-w.svg",
    ("white", "rook"): "rook-w.svg",
    ("white", "knight"): "knight-w.svg",
    ("white", "bishop"): "bishop-w.svg",
    ("white", "queen"): "queen-w.svg",
    ("white", "king"): "king-w.svg",
    ("black", "pawn"): "pawn-b.svg",
    ("black", "rook"): "rook-b.svg",
    ("black", "knight"): "knight-b.svg",
    ("black", "bishop"): "bishop-b.svg",
    ("black", "queen"): "queen-b.svg",
    ("black", "king"): "king-b.svg",
}


def render_board(request, game_id, state, selected=None, legal_moves=None, capture_probas=None):
    """
    selected      = case source cliquée
    legal_moves   = liste positions jouables pour cette pièce
    capture_probas = {pos: float} map cases → probabilité
    """
    return templates.TemplateResponse(
        "board.html",
        {
            "request": request,
            "game_id": game_id,
            "board": state["board"]["pieces"] if state else {},
            "selected": selected,
            "legal": legal_moves or [],
            "probas": capture_probas or {},
            "PIECE_IMAGE_MAP": PIECE_IMAGE_MAP,
        },
    )
