"""Pruebas unitarias para el modelo de grafo, Dijkstra y Prim."""

import pytest

from src.graph.algorithms import dijkstra, prim
from src.graph.model import Graph

pytestmark = pytest.mark.unit


@pytest.fixture
def grafo_ejemplo() -> Graph:
    """Crea un grafo ponderado de prueba.

    0 (ZS) --3-- 1 (LS) --5-- 2 (L) --2-- 3 (L)
                  |           |
                  +----8------+
    """
    g = Graph()
    g.agregar_nodo(0, "ZS")
    g.agregar_nodo(1, "LS")
    g.agregar_nodo(2, "L")
    g.agregar_nodo(3, "L")

    g.agregar_arista(0, 1, 3, "corto")
    g.agregar_arista(1, 2, 5, "corto")
    g.agregar_arista(1, 2, 8, "largo")  # Arista repetida/paralela si aplicara
    g.agregar_arista(2, 3, 2, "corto")
    return g


def test_dijkstra_camino_minimo():
    """Verifica el cálculo de distancias y caminos mínimos."""
    g = Graph()
    g.agregar_nodo(0, "L")
    g.agregar_nodo(1, "L")
    g.agregar_nodo(2, "L")
    g.agregar_arista(0, 1, 4, "corto")
    g.agregar_arista(1, 2, 3, "corto")
    g.agregar_arista(0, 2, 10, "largo")

    distancias, prev = dijkstra(g, origen=0)

    assert distancias[2] == 7
    assert prev[2] == 1
    assert prev[1] == 0


def test_dijkstra_exclusion_de_nodos():
    """Verifica que Dijkstra ignore nodos excluidos (por ejemplo, ZS)."""
    g = Graph()
    g.agregar_nodo(0, "ZS")
    g.agregar_nodo(1, "L")
    g.agregar_nodo(2, "L")
    g.agregar_arista(0, 1, 2, "corto")
    g.agregar_arista(0, 2, 2, "corto")
    g.agregar_arista(1, 2, 10, "largo")

    # Al excluir el nodo 0 (ZS), el camino directo 1-2 debe ser por la arista (1,2)
    distancias, _ = dijkstra(g, origen=1, nodos_excluidos={0})

    assert distancias[2] == 10
    assert 0 not in distancias or distancias[0] == float("inf")


def test_prim_mst_calculo():
    """Verifica que el MST devuelva exactamente N-1 aristas y peso mínimo."""
    g = Graph()
    for i in range(4):
        g.agregar_nodo(i, "L")

    g.agregar_arista(0, 1, 1, "corto")
    g.agregar_arista(1, 2, 4, "corto")
    g.agregar_arista(2, 3, 2, "corto")
    g.agregar_arista(0, 3, 3, "corto")
    g.agregar_arista(0, 2, 5, "corto")

    aristas_mst, peso_total = prim(g)

    assert len(aristas_mst) == 3
    assert peso_total == 6  # Aristas: (0,1:1), (2,3:2), (0,3:3)
