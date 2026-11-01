"""Pruebas unitarias para el generador aleatorio determinista."""

import pytest

from src.rng import RNG

pytestmark = pytest.mark.unit


def test_misma_semilla_produce_mismo_resultado():
    """Verifica que dos instancias con la misma semilla generen
    exactamente la misma secuencia.
    """
    rng1 = RNG(semilla=12345)
    rng2 = RNG(semilla=12345)

    enteros_1 = [rng1.randint(1, 100) for _ in range(10)]
    enteros_2 = [rng2.randint(1, 100) for _ in range(10)]

    assert enteros_1 == enteros_2


def test_diferente_semilla_produce_diferente_resultado():
    """Verifica que semillas distintas produzcan secuencias diferentes."""
    rng1 = RNG(semilla=12345)
    rng2 = RNG(semilla=54321)

    enteros_1 = [rng1.randint(1, 100) for _ in range(10)]
    enteros_2 = [rng2.randint(1, 100) for _ in range(10)]

    assert enteros_1 != enteros_2


def test_semilla_none_genera_semilla_valida():
    """Verifica que si no se proporciona semilla, se cree una
    semilla válida de 52 bits.
    """
    rng = RNG(semilla=None)
    assert rng.semilla is not None
    assert 0 <= rng.semilla < (2**53)


def test_metodos_de_seleccion():
    """Verifica el comportamiento de elección en listas y permutaciones."""
    rng = RNG(semilla=999)
    elementos = ["a", "b", "c", "d"]

    elegido = rng.choice(elementos)
    assert elegido in elementos

    copia = elementos.copy()
    rng.shuffle(copia)
    assert sorted(copia) == sorted(elementos)
