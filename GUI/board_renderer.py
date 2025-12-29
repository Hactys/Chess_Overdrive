from dash import html

def render_board(state):
    pieces = state["board"]["pieces"]

    children={}
    for pos,data in pieces.items():
        piece_char = data["type"][0].upper() if data["owner"]=="white" else data["type"][0]
        children[f"square-{pos}"] = piece_char

    rendered=[]
    for sq,content in children.items():
        rendered.append((sq,content))
    return rendered
