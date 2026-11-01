"""Algoritmo de layout basado en fuerzas (Fruchterman-Reingold) para posicionar nodos"""

import math

from src.graph.model import Graph
from src.graph.validator import validar_mapa  # noqa: F401
from src.rng import RNG


def calcular_layout(
    grafo: Graph,
    rng: RNG,
    ancho: float = 1000.0,
    alto: float = 1000.0,
    iteraciones: int = 100,
) -> None:
    """Calcula y asigna posiciones (x, y) deterministas entre 0 y 1000."""
    n_nodos = len(grafo.nodos)
    if n_nodos == 0:
        return

    area = ancho * alto
    k = math.sqrt(area / n_nodos)

    # 1. Posiciones iniciales aleatorias con RNG con semilla
    pos: dict[int, list[float]] = {}
    for n_id in grafo.nodos:
        pos[n_id] = [
            rng.uniform(100.0, ancho - 100.0),
            rng.uniform(100.0, alto - 100.0),
        ]

    temp = ancho / 10.0
    enfriamiento = temp / iteraciones

    for _ in range(iteraciones):
        disp: dict[int, list[float]] = {n_id: [0.0, 0.0] for n_id in grafo.nodos}

        # Repulsión entre todos los pares de nodos
        for u_id in grafo.nodos:
            for v_id in grafo.nodos:
                if u_id == v_id:
                    continue
                dx = pos[u_id][0] - pos[v_id][0]
                dy = pos[u_id][1] - pos[v_id][1]
                dist = math.sqrt(dx * dx + dy * dy) or 0.01
                f_rep = (k * k) / dist
                disp[u_id][0] += (dx / dist) * f_rep
                disp[u_id][1] += (dy / dist) * f_rep

        # Atracción a lo largo de las aristas
        for arista in grafo.aristas:
            u_id, v_id = arista.a, arista.b
            dx = pos[u_id][0] - pos[v_id][0]
            dy = pos[u_id][1] - pos[v_id][1]
            dist = math.sqrt(dx * dx + dy * dy) or 0.01
            f_atr = (dist * dist) / k
            disp[u_id][0] -= (dx / dist) * f_atr
            disp[u_id][1] -= (dy / dist) * f_atr
            disp[v_id][0] += (dx / dist) * f_atr
            disp[v_id][1] += (dy / dist) * f_atr

        # Actualizar posiciones con límite de temperatura
        for n_id in grafo.nodos:
            d_x, d_y = disp[n_id]
            dist = math.sqrt(d_x * d_x + d_y * d_y) or 0.01
            limitado = min(dist, temp)
            pos[n_id][0] += (d_x / dist) * limitado
            pos[n_id][1] += (d_y / dist) * limitado

            # Limitar a los márgenes del canvas
            pos[n_id][0] = max(50.0, min(ancho - 50.0, pos[n_id][0]))
            pos[n_id][1] = max(50.0, min(alto - 50.0, pos[n_id][1]))

        temp = max(0.1, temp - enfriamiento)

    # Asignar coordenadas redondeadas a los nodos
    for n_id, n_obj in grafo.nodos.items():
        n_obj.x = round(pos[n_id][0], 2)
        n_obj.y = round(pos[n_id][1], 2)
