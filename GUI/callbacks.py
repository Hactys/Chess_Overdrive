from dash import Input, Output, State, html, ctx
from state_manager import pull_state, sio
from board_renderer import render_board


def register_callbacks(app):
    # Update store from server
    @app.callback(
        Output("game_state_store","data"),
        Input("state_poll","n_intervals")
    )
    def refresh_state(_):
        return pull_state()

    # Update board when state changes
    @app.callback(
        [Output(f"square-{f}{r}","children")
         for r in range(8,0,-1) for f in "abcdefgh"],
        Input("game_state_store","data")
    )
    def display_board(state):
        if not state:
            return [""]*64
        mapping = dict(render_board(state))
        return [mapping.get(f"square-{f}{r}","") for r in range(8,0,-1) for f in "abcdefgh"]

    # Clics sur plateau (MVP: premier clic=from, second clic=to)
    selected = {"from":None}

    @app.callback(
        Output("board","style"),
        [Input(f"square-{f}{r}","n_clicks") for r in range(8,0,-1) for f in "abcdefgh"],
        State("game_state_store","data"),
        prevent_initial_call=True
    )
    def handle_click(*args):
        state = args[-1]
        clicks=args[:-1]

        squares=[f"{f}{r}" for r in range(8,0,-1) for f in "abcdefgh"]
        clicked=[squares[i] for i,c in enumerate(clicks) if c]

        if not clicked: return {"padding":"5px"}

        pos= ctx.triggered[0]['prop_id'].split('-')[1].split('.')[0]  # type: ignore

        if not selected["from"]:
            selected["from"]=pos
            print("Selected from",pos)
        else:
            sio.emit("action",{
                "game_id":"test_game",
                "action":{"type":"move","from":selected["from"],"to":pos}
            })
            print(f"Move {selected['from']}->{pos}")
            selected["from"]=None

        return {"padding":"5px"}
