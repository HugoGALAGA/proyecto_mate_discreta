"""Pruebas unitarias para el algoritmo de posicionamiento de nodos."""

import pytest

from src.config import cargar_config
from src.graph.generator import generar_mapa
from src.graph.layout import calcular_layout
from src.rng import RNG

pytestmark = pytest.mark.unit


def test_calcular_layout_asigna_coordenadas_validas():
    """Verifica que todos los nodos reciban coordenadas (x, y) entre 0 y 1000."""
    config = cargar_config()
    rng = RNG(semilla=42)
    grafo = generar_mapa(config, rng)

    calcular_layout(grafo, rng)

    for nodo in grafo.nodos.values():
        assert 0 <= nodo.x <= 1000
        assert 0 <= nodo.y <= 1000


def test_layout_es_determinista():
    """Verifica que la misma semilla produzca exactamente el mismo layout."""
    config = cargar_config()

    rng1 = RNG(semilla=999)
    g1 = generar_mapa(config, rng1)
    calcular_layout(g1, rng1)

    rng2 = RNG(semilla=999)
    g2 = generar_mapa(config, rng2)
    calcular_layout(g2, rng2)

    for id_nodo in g1.nodos:
        assert g1.nodos[id_nodo].x == g2.nodos[id_nodo].x
        assert g1.nodos[id_nodo].y == g2.nodos[id_nodo].y
