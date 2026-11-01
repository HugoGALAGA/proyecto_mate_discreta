"""Generador de la topología del mapa con reintentos deterministas."""

from src.graph.model import Graph
from src.graph.validator import validar_mapa
from src.rng import RNG


def _intentar_generar_grafo(config: dict, rng: RNG) -> Graph:
    cfg = config["mapa"]
    n_nodos = rng.randint(cfg["nodos_min"], cfg["nodos_max"])

    g = Graph()
    # Crear nodos L por defecto
    for i in range(n_nodos):
        g.agregar_nodo(i, tipo="L")

    # 1. Construir estructura base en anillo (garantiza conexidad inicial)
    for i in range(n_nodos):
        sig = (i + 1) % n_nodos
        peso = rng.randint(cfg["peso_corto_min"], cfg["peso_largo_max"])
        cluster = "corto" if peso <= cfg["peso_corto_max"] else "largo"
        g.agregar_arista(i, sig, peso, cluster)

    # 2. Agregar atajos aleatorios respetando el grado máximo 4
    nodos_ids = list(range(n_nodos))
    rng.shuffle(nodos_ids)
    for u in nodos_ids:
        if g.grado(u) >= 3:
            continue
        candidatos = [
            v
            for v in nodos_ids
            if v != u
            and v not in g.vecinos(u)
            and abs(u - v) > 1
            and abs(u - v) != n_nodos - 1
            and g.grado(v) < 3
        ]
        if candidatos:
            v = rng.choice(candidatos)
            peso = rng.randint(cfg["peso_corto_min"], cfg["peso_largo_max"])
            cluster = "corto" if peso <= cfg["peso_corto_max"] else "largo"
            g.agregar_arista(u, v, peso, cluster)

    # 3. Elegir ZS y sus vecinos como LS
    candidatos_zs = [
        u
        for u in nodos_ids
        if g.grado(u) in (2, 3) and all(g.grado(v) in (2, 3) for v in g.vecinos(u))
    ]

    if not candidatos_zs:
        return g  # Fallará la validación y reintentará

    id_zs = rng.choice(candidatos_zs)
    g.nodos[id_zs].tipo = "ZS"

    for v in g.vecinos(id_zs):
        g.nodos[v].tipo = "LS"
        # Ajustar aristas ZS-LS a cluster corto (1-5)
        for e in g.adyacencia[id_zs]:
            if e.vecino(id_zs) == v:
                e.peso = rng.randint(cfg["peso_corto_min"], cfg["peso_corto_max"])
                e.cluster = "corto"

    return g


def generar_mapa(config: dict, rng: RNG) -> Graph:
    """Genera un mapa válido respetando la configuración y la semilla.

    Reintenta hasta 'intentos_max_generacion' veces si la validación falla.
    """
    max_intentos = config["mapa"]["intentos_max_generacion"]

    for _ in range(max_intentos):
        grafo = _intentar_generar_grafo(config, rng)
        es_valido, _ = validar_mapa(grafo, config)
        if es_valido:
            return grafo

    raise RuntimeError(
        f"No se logró generar un mapa válido tras {max_intentos} intentos."
    )
