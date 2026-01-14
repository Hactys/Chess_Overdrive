from game_engine.actions.move import MoveAction
from game_engine.actions.no_action import NoAction

# TODO : game_engine.from actions.play_card import PlayCardAction


def parse_action(data: dict):
    """
    Convertit une action JSON en instance d'action moteur.
    """
    if data["type"] == "no action":
        return NoAction(data["player_id"])
    if data["type"] == "move":
        return MoveAction(data["player_id"], data["from"], data["to"])

    # if data["type"] == "card":
    #     return PlayCardAction(data["player_id"], data["card_id"], data.get("targets", {}))

    raise ValueError("Unknown action type")
