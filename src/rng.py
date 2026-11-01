"""Generador de números aleatorios con semilla inyectable para el motor de juego."""

import random
from typing import Sequence, TypeVar

T = TypeVar("T")


class RNG:
    """Wrapper determinista sobre random.Random."""

    def __init__(self, semilla: int | None = None) -> None:
        if semilla is None:
            # Genera una semilla de hasta 52 bits (límite seguro para JSON / JavaScript)
            semilla = random.SystemRandom().randint(0, (2**53) - 1)

        self._semilla = semilla
        self._rng = random.Random(self._semilla)

    @property
    def semilla(self) -> int:
        """Devuelve la semilla asignada a esta instancia."""
        return self._semilla

    def randint(self, a: int, b: int) -> int:
        """Retorna un entero aleatorio N tal que a <= N <= b."""
        return self._rng.randint(a, b)

    def uniform(self, a: float, b: float) -> float:
        """Retorna un número flotante aleatorio N tal que a <= N <= b."""
        return self._rng.uniform(a, b)

    def choice(self, seq: Sequence[T]) -> T:
        """Selecciona un elemento aleatorio de una secuencia no vacía."""
        return self._rng.choice(seq)

    def shuffle(self, x: list[T]) -> None:
        """Mezcla la lista in-place."""
        self._rng.shuffle(x)
