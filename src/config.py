"""Carga de config.toml (por defecto, el de la raiz del proyecto)."""

import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_CONFIG = RAIZ / "config.toml"


def cargar_config(ruta: Path | None = None) -> dict:
    """Lee el archivo TOML y devuelve un diccionario."""
    with open(ruta or RUTA_CONFIG, "rb") as archivo:
        return tomllib.load(archivo)
