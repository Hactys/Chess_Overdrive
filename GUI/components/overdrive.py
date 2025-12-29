from dash import html
import dash_bootstrap_components as dbc

def overdrive_bars():
    return dbc.Card([
        html.H4("Overdrive",className="text-center"),
        html.Div("Jauge joueur blanc [à venir]",style={"height":"30px","background":"#555"}),
        html.Div("Jauge joueur noir [à venir]",style={"height":"30px","background":"#333","marginTop":"5px"}),
    ],className="mb-3")
