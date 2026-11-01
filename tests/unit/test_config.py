import pytest

from src.config import cargar_config

pytestmark = pytest.mark.unit


def test_hay_una_sola_zona_segura():
    assert cargar_config()["mapa"]["cantidad_zs"] == 1


def test_limites_de_tiempo():
    tiempos = cargar_config()["tiempos"]
    assert tiempos["limite_partida"] == 120
    assert tiempos["limite_pruebas"] == 60


def test_tiempos_son_ticks_enteros():
    tiempos = cargar_config()["tiempos"]
    tick = tiempos["tick_segundos"]
    for clave in ("cooldown_zombie", "cooldown_superviviente"):
        assert (tiempos[clave] / tick).is_integer()
