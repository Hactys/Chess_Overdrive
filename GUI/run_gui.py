from dash import Dash
import dash_bootstrap_components as dbc

from state_manager import init_network
from layout import build_layout
from callbacks import register_callbacks


app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Chess Overdrive"

app.layout = build_layout()

register_callbacks(app)


if __name__ == "__main__":
    init_network(app)          # lance WebSocket client & auto create game
    app.run(port=8050, debug=True, use_reloader=False)
