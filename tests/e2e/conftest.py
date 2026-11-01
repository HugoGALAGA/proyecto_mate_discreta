"""Levanta el servidor real (FastAPI + React compilado) para Playwright."""

import socket
import subprocess
import sys
import time
import urllib.request

import pytest

from src.api.app import DIST
from src.config import RAIZ


def _puerto_libre() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def servidor():
    if not DIST.is_dir():
        pytest.skip("Falta compilar el frontend: cd frontend && npm run build")
    puerto = _puerto_libre()
    url = f"http://127.0.0.1:{puerto}"
    proceso = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api.app:app", "--port", str(puerto)],
        cwd=RAIZ,
    )
    try:
        for _ in range(600):
            try:
                urllib.request.urlopen(f"{url}/api/health", timeout=1)
                break
            except OSError:
                time.sleep(0.2)
        else:
            raise RuntimeError("El servidor no arranco a tiempo")
        yield url
    finally:
        proceso.terminate()
        proceso.wait(timeout=10)


@pytest.fixture(scope="session")
def base_url(servidor):
    return servidor
