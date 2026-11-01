"""Algoritmos de caminos mínimos (Dijkstra) y árbol de cobertura mínima (Prim)."""

import heapq
from typing import Set

from src.graph.model import Edge, Graph


def dijkstra(
    grafo: Graph, origen: int, nodos_excluidos: Set[int] | None = None
) -> tuple[dict[int, float], dict[int, int | None]]:
    """Calcula distancias mínimas y predecesores usando Dijkstra con heapq.

    Soporta la exclusión opcional de nodos (por ejemplo, omitir la ZS).
    """
    if nodos_excluidos is None:
        nodos_excluidos = set()

    distancias: dict[int, float] = {n: float("inf") for n in grafo.nodos}
    predecesores: dict[int, int | None] = {n: None for n in grafo.nodos}

    if origen in nodos_excluidos or origen not in grafo.nodos:
        return distancias, predecesores

    distancias[origen] = 0.0
    # Cola de prioridad contiene tuplas: (distancia, nodo_id)
    cola: list[tuple[float, int]] = [(0.0, origen)]

    while cola:
        dist_actual, u = heapq.heappop(cola)

        if dist_actual > distancias[u]:
            continue

        for arista in grafo.adyacencia.get(u, []):
            v = arista.vecino(u)

            if v in nodos_excluidos:
                continue

            nueva_dist = dist_actual + arista.peso
            if nueva_dist < distancias[v]:
                distancias[v] = nueva_dist
                predecesores[v] = u
                heapq.heappush(cola, (nueva_dist, v))

    return distancias, predecesores


def prim(grafo: Graph) -> tuple[list[Edge], int]:
    """Calcula el Árbol de Cobertura Mínima (MST) usando el algoritmo de Prim.

    Desempata deterministamente por (peso, min(a, b), max(a, b)).
    """
    if not grafo.nodos:
        return [], 0

    inicio = min(grafo.nodos.keys())
    visitados: set[int] = {inicio}

    # Elementos en la cola: (peso, u_min, v_max, objeto_arista)
    cola: list[tuple[int, int, int, Edge]] = []

    def agregar_aristas(u: int) -> None:
        for e in grafo.adyacencia.get(u, []):
            v = e.vecino(u)
            if v not in visitados:
                heapq.heappush(cola, (e.peso, e.a, e.b, e))

    agregar_aristas(inicio)

    aristas_mst: list[Edge] = []
    peso_total = 0

    while cola and len(visitados) < len(grafo.nodos):
        peso, u, v, arista = heapq.heappop(cola)

        siguiente_nodo = v if u in visitados else u
        if siguiente_nodo in visitados:
            continue

        visitados.add(siguiente_nodo)
        aristas_mst.append(arista)
        peso_total += peso
        agregar_aristas(siguiente_nodo)

    return aristas_mst, peso_total
