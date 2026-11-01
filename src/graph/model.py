"""Modelos de datos para Nodos, Aristas y el Grafo."""

from dataclasses import dataclass


@dataclass
class Node:
    """Representa un nodo en el mapa."""

    id: int
    tipo: str  # "ZS", "LS", "L"
    x: float = 0.0
    y: float = 0.0


@dataclass
class Edge:
    """Representa una arista ponderada entre dos nodos."""

    a: int
    b: int
    peso: int
    cluster: str  # "corto" o "largo"

    def contiene(self, nodo_id: int) -> bool:
        """Indica si la arista está conectada a un nodo dado."""
        return self.a == nodo_id or self.b == nodo_id

    def vecino(self, nodo_id: int) -> int:
        """Dado un extremo de la arista, retorna el otro extremo."""
        if self.a == nodo_id:
            return self.b
        if self.b == nodo_id:
            return self.a
        raise ValueError(f"El nodo {nodo_id} no pertenece a esta arista.")


class Graph:
    """Estructura de Grafo basada en lista de adyacencia."""

    def __init__(self) -> None:
        self.nodos: dict[int, Node] = {}
        self.aristas: list[Edge] = []
        self.adyacencia: dict[int, list[Edge]] = {}

    def agregar_nodo(
        self, nodo_id: int, tipo: str, x: float = 0.0, y: float = 0.0
    ) -> None:
        """Agrega un nodo al grafo."""
        if nodo_id not in self.nodos:
            self.nodos[nodo_id] = Node(id=nodo_id, tipo=tipo, x=x, y=y)
            self.adyacencia[nodo_id] = []

    def agregar_arista(self, a: int, b: int, peso: int, cluster: str) -> None:
        """Agrega una arista no dirigida entre dos nodos."""
        u, v = min(a, b), max(a, b)
        arista = Edge(a=u, b=v, peso=peso, cluster=cluster)
        self.aristas.append(arista)
        self.adyacencia[u].append(arista)
        self.adyacencia[v].append(arista)

    def grado(self, nodo_id: int) -> int:
        """Retorna el grado (cantidad de vecinos) de un nodo."""
        return len(self.adyacencia.get(nodo_id, []))

    def vecinos(self, nodo_id: int) -> list[int]:
        """Retorna la lista de IDs de los nodos vecinos."""
        return [e.vecino(nodo_id) for e in self.adyacencia.get(nodo_id, [])]
