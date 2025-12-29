from dash import html

import dash_bootstrap_components as dbc

def captures_component():
    return dbc.Card([
        html.H4("Pièces capturées",className="text-center"),
        html.Div("Zone captures [à venir]",style={"height":"60px"})
    ],className="mb-3")
