from dash import html
import dash_bootstrap_components as dbc

def info_panel():
    return dbc.Card([
        html.H4("Infos & Actions",className="text-center"),
        html.Button("Passer Tour",id="btn-end-turn")
    ],className="mt-3")
