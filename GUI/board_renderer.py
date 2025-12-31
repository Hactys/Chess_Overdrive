from dash import html


PIECE_IMAGE_MAP = {
    ("white", "pawn"):   "pawn-w.svg",
    ("white", "rook"):   "rook-w.svg",
    ("white", "knight"): "knight-w.svg",
    ("white", "bishop"): "bishop-w.svg",
    ("white", "queen"):  "queen-w.svg",
    ("white", "king"):   "king-w.svg",

    ("black", "pawn"):   "pawn-b.svg",
    ("black", "rook"):   "rook-b.svg",
    ("black", "knight"): "knight-b.svg",
    ("black", "bishop"): "bishop-b.svg",
    ("black", "queen"):  "queen-b.svg",
    ("black", "king"):   "king-b.svg",
}


def render_board(state):
    pieces = state["board"]["pieces"]
    children={}

    for pos,data in pieces.items():
        key = (data["owner"], data["type"])
        filename = PIECE_IMAGE_MAP.get(key)
        if not filename:
            continue

        children[f"square-{pos}"] = html.Img(
            src=f"/assets/pieces/{filename}",
            style={
                "width": "48px",
                "height": "48px",
                "pointerEvents": "none",
                "userSelect": "none",
                "hover": {
                    "transform": "scale(1.1)"
                }
            }
        )

    return list(children.items())
