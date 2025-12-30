# server/api_actions.py

from game_engine.actions.move import MoveAction
from game_engine.actions.no_action import NoAction
# TODO : game_engine.from actions.play_card import PlayCardAction


def parse_action(data: dict):
    """
    Convertit une action JSON en instance d'action moteur.
    """
    if data["type"] == "no action":
        return NoAction()
    if data["type"] == "move":
        return MoveAction(data["from"], data["to"])

    # if data["type"] == "card":
    #     return PlayCardAction(data["card_id"], data.get("targets", {}))

    raise ValueError("Unknown action type")
