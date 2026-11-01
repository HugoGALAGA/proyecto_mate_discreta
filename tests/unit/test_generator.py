"""Pruebas unitarias y de validación para la generación del mapa."""

import pytest

from src.config import cargar_config
from src.graph.generator import generar_mapa
from src.graph.validator import validar_mapa
from src.rng import RNG

pytestmark = pytest.mark.unit


def test_generar_mapa_valido_con_semilla():
    """Verifica que el generador cree un mapa que cumpla todas las reglas."""
    config = cargar_config()
    rng = RNG(semilla=42)

    grafo = generar_mapa(config, rng)
    es_valido, motivo = validar_mapa(grafo, config)

    assert es_valido, f"El mapa generado no es válido: {motivo}"


def test_determinismo_generacion_mapa():
    """Verifica que la misma semilla produzca exactamente el mismo mapa."""
    config = cargar_config()

    g1 = generar_mapa(config, RNG(semilla=12345))
    g2 = generar_mapa(config, RNG(semilla=12345))

    assert len(g1.nodos) == len(g2.nodos)
    assert len(g1.aristas) == len(g2.aristas)

    for id_nodo in g1.nodos:
        assert g1.nodos[id_nodo].tipo == g2.nodos[id_nodo].tipo

    for e1, e2 in zip(g1.aristas, g2.aristas):
        assert (e1.a, e1.b, e1.peso) == (e2.a, e2.b, e2.peso)
