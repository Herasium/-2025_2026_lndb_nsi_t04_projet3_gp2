"""Fournit des capacités de suivi de la souris avec alignement sur la grille et analyse directionnelle."""

from typing import List, Tuple
from arcade import Vec2
from modules.data import data


class _Mouse:
    """Gère l'état de la souris, incluant la position brute, les coordonnées alignées sur la grille et les vecteurs de mouvement."""

    def __init__(self) -> None:
        """Initialise le traqueur de souris avec un état par défaut."""
        self._x: float = 0.0
        self._y: float = 0.0
        self._position: Tuple[float, float] = (0.0, 0.0)

        self.history: List[Vec2] = []
        self.direction: str = "RIGHT"
        self.previous_direction: str = "RIGHT"

        self.direction_bias: int = 0


    @property
    def position(self) -> Tuple[float, float]:
        return self._position

    @position.setter
    def position(self, value: Tuple[float, float]) -> Tuple[float, float]:
        self._position = value
        self._x = self._position[0]
        self._y = self._position[1]
        return self._position

    @property
    def x(self) -> float:
        """Retourne la coordonnée x actuelle."""
        return self._x

    @property
    def y(self) -> float:
        """Retourne la coordonnée y actuelle."""
        return self._y


mouse: _Mouse = _Mouse()