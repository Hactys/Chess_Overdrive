from dash import html, dcc
import dash_bootstrap_components as dbc

from components.board import board_component
from components.overdrive import overdrive_bars
from components.hands import hands_component
from components.captures import captures_component
from components.info_panel import info_panel


def build_layout():
    return dbc.Container([
        dcc.Interval(id="state_poll", interval=1/30, n_intervals=0),  # 30 Hz
        dcc.Store(id="game_id", data="test_game"),  # TODO : change this to get the real game_id
        dcc.Store(id="game_state_store"),
        dcc.Store(id="available_moves_store", data=[]),

        html.H1("Chess Overdrive", className="text-center mt-3 mb-4"),

        dbc.Row([
            dbc.Col(board_component(), width=6),     # Plateau cliquable
            dbc.Col([
                overdrive_bars(),
                hands_component(),
                captures_component(),
                info_panel()
            ], width=6),
        ]),
    ], fluid=True)
