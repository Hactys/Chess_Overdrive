import requests
from dash import Input, Output, State, html, ctx, no_update
from state_manager import pull_state, pull_moves, sio
from board_renderer import render_board


def register_callbacks(app):
    # Update store from server
    @app.callback(
        Output("game_state_store", "data"),
        Output("available_moves_store", "data"),
        Output("capture_probas_store", "data"),
        Input("state_poll", "n_intervals"),
    )
    def refresh_state(_):
        state = pull_state()
        moves, captures = pull_moves()
        return state, moves, captures

    # Update board when state changes
    @app.callback(
        [Output(f"square-{f}{r}","children") for r in range(8,0,-1) for f in "abcdefgh"],
        Input("game_state_store", "data"),
        Input("available_moves_store", "data"),
        State("capture_probas_store", "data")
    )
    def display_board(state, legal_moves, capture_probas):
        highlighted = set(legal_moves) if ctx.triggered[0]['prop_id'] == "available_moves_store.data" else set()
        capture_probas = capture_probas or {}
        if not state:
            sio.emit("action",{
                "game_id":"test_game",
                "action":{"type":"no action"}
            })
            return [""]*64
        mapping = dict(render_board(state))
        rendered = []
        for r in range(8,0,-1):
            for f in "abcdefgh":
                pos = f"{f}{r}"
                child = mapping.get(f"square-{pos}", "")
                title = None
                if pos in capture_probas:
                    title = f"Chance de capture : {int(capture_probas[pos]*100)}%"
                rendered.append(
                    html.Span(child, title=title,
                              style={
                                  "outline": "3px solid red" if pos in capture_probas else
                                  "3px solid yellow" if pos in highlighted else "none"
                                  }
                    )
                )

        return rendered

    # Clics sur plateau (MVP: premier clic=from, second clic=to)
    selected = {"from":None}

    @app.callback(
        Output("board","style"),
        [Input(f"square-{f}{r}", "n_clicks") for r in range(8,0,-1) for f in "abcdefgh"],
        State("game_state_store", "data"),
        State("available_moves_store", "data"),
        prevent_initial_call=True
    )
    def handle_click(*args):
        state = args[-2]
        clicks = args[:-2]
        available_moves = args[-1]

        squares=[f"{f}{r}" for r in range(8,0,-1) for f in "abcdefgh"]
        clicked=[squares[i] for i,c in enumerate(clicks) if c]

        if not clicked: return {"padding":"5px"}

        pos = ctx.triggered[0]['prop_id'].split('-')[1].split('.')[0]  # type: ignore

        current_player = state["current_player"] if state is not None else "white"

        if not selected["from"]:
            sio.emit("get_legal_moves", {
                "game_id":"test_game",
                "from": pos,
                "player": current_player
            })
            selected["from"]=pos
        elif pos not in available_moves:
            sio.emit("get_legal_moves", {
                "game_id":"test_game",
                "from": pos,
                "player": current_player
            })
            selected["from"]=pos
        else:
            sio.emit("action",{
                "game_id":"test_game",
                "action":{"type":"move","from":selected["from"],"to":pos}
            })
            selected["from"]=None

        return {"padding":"2vw"}
