import random
from typing import Any, Sequence, Tuple


class RNG:
    """
    Wrapper RNG déterministe.
    TOUT le hasard du moteur doit passer par cette classe.
    """

    def __init__(self, seed: int):
        self.seed = seed
        self._random = random.Random(seed)

    def random(self) -> float:
        """Retourne un float dans [0.0, 1.0)."""
        return self._random.random()

    def randint(self, a: int, b: int) -> int:
        """Retourne un entier N tel que a <= N <= b."""
        return self._random.randint(a, b)

    def choice(self, seq: Sequence[Any]) -> Any:
        """Retourne un élément aléatoire d'une séquence."""
        if not seq:
            raise ValueError("Cannot choose from an empty sequence")
        return self._random.choice(seq)

    def get_state(self) -> Tuple[Any | ...]:
        """Expose l'état interne pour replay/debug."""
        return self._random.getstate()

    def set_state(self, state: Tuple[Any | ...]) -> None:
        """Restaure l'état interne."""
        self._random.setstate(state)
