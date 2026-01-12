from typing import Dict, Type
from cards.base_card import BaseCard


CARD_REGISTRY: Dict[str, Type[BaseCard]] = {}


def register_card(card_cls: Type[BaseCard]) -> None: ...


def get_card(card_id: str) -> Type[BaseCard]: ...
