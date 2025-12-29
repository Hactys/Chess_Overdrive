from dash import html
import dash_bootstrap_components as dbc

def hands_component():
    return dbc.Card([
        html.H4("Main de cartes",className="text-center"),
        html.Div("Cartes du joueur [à venir]",style={"height":"80px"})
    ],className="mb-3")
