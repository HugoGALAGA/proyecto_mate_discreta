"""Validación de las 9 reglas topológicas obligatorias del mapa."""

from src.graph.algorithms import dijkstra
from src.graph.model import Graph


def validar_mapa(grafo: Graph, config: dict) -> tuple[bool, str]:
    """Evalúa las 9 reglas topológicas obligatorias sobre el grafo.

    Retorna (True, "") si es válido, o (False, "motivo") si falla alguna regla.
    """
    cfg_mapa = config["mapa"]
    n_nodos = len(grafo.nodos)

    # 1. Cantidad de nodos entre nodos_min y nodos_max
    if not (cfg_mapa["nodos_min"] <= n_nodos <= cfg_mapa["nodos_max"]):
        return False, f"Cantidad de nodos fuera de rango: {n_nodos}"

    # 2. Grafo conexo
    dist_total, _ = dijkstra(grafo, origen=0)
    if any(dist == float("inf") for dist in dist_total.values()):
        return False, "El grafo no es conexo"

    # 3. Exactamente 1 ZS con grado 2 o 3
    nodos_zs = [n for n in grafo.nodos.values() if n.tipo == "ZS"]
    if len(nodos_zs) != cfg_mapa["cantidad_zs"]:
        return False, f"Cantidad de ZS inválida: {len(nodos_zs)}"

    zs = nodos_zs[0]
    grado_zs = grafo.grado(zs.id)
    if not (cfg_mapa["grado_zs_min"] <= grado_zs <= cfg_mapa["grado_zs_max"]):
        return False, f"Grado de ZS inválido: {grado_zs}"

    # 4. Cada LS con grado 2 o 3, sin aristas LS-LS y peso ZS-LS entre 1 y 5
    vecinos_zs = set(grafo.vecinos(zs.id))
    nodos_ls = [n for n in grafo.nodos.values() if n.tipo == "LS"]

    if set(n.id for n in nodos_ls) != vecinos_zs:
        return False, "Los nodos LS no corresponden exactamente a los vecinos de la ZS"

    for ls in nodos_ls:
        grado_ls = grafo.grado(ls.id)
        if not (cfg_mapa["grado_ls_min"] <= grado_ls <= cfg_mapa["grado_ls_max"]):
            return False, f"Grado de LS {ls.id} inválido: {grado_ls}"

        # Comprobar aristas a otros LS y arista a la ZS
        for arista in grafo.adyacencia[ls.id]:
            v = arista.vecino(ls.id)
            if v in vecinos_zs:
                return False, f"Existe arista prohibida entre LS {ls.id} y {v}"
            if v == zs.id:
                if not (
                    cfg_mapa["peso_corto_min"]
                    <= arista.peso
                    <= cfg_mapa["peso_corto_max"]
                ):
                    return (
                        False,
                        f"Peso de arista ZS-LS {ls.id} fuera de rango: {arista.peso}",
                    )

    # 5. Todo L con grado entre 1 y 4 (grado max L)
    for n in grafo.nodos.values():
        if n.tipo == "L":
            g = grafo.grado(n.id)
            if not (1 <= g <= cfg_mapa["grado_max_l"]):
                return False, f"Grado de nodo L {n.id} inválido: {g}"

    # 6. Hojas totales <= 4 y ninguna es ZS ni LS
    hojas = [n for n in grafo.nodos.values() if grafo.grado(n.id) == 1]
    if len(hojas) > cfg_mapa["hojas_max"]:
        return False, f"Demasiadas hojas: {len(hojas)}"
    if any(h.tipo != "L" for h in hojas):
        return False, "Existe una hoja que no es tipo L"

    # 7. El grafo sin la ZS sigue conexo
    origen_sin_zs = nodos_ls[0].id
    dist_sin_zs, _ = dijkstra(grafo, origen=origen_sin_zs, nodos_excluidos={zs.id})
    for n_id, dist in dist_sin_zs.items():
        if n_id != zs.id and dist == float("inf"):
            return False, f"El grafo sin la ZS no es conexo (nodo {n_id} inalcanzable)"

    # 8. Nodos de spawn válidos >= 6 (nodos L a dist >= 15 de la ZS)
    nodos_spawn = [
        n_id
        for n_id, dist in dist_total.items()
        if grafo.nodos[n_id].tipo == "L" and dist >= cfg_mapa["spawn_distancia_min"]
    ]
    if len(nodos_spawn) < cfg_mapa["spawn_nodos_min"]:
        return False, f"Insuficientes nodos de spawn válidos: {len(nodos_spawn)}"

    # 9. Pesos enteros entre 1 y 10
    for e in grafo.aristas:
        if not (1 <= e.peso <= 10):
            return False, f"Peso de arista fuera de rango [1, 10]: {e.peso}"

    return True, ""
