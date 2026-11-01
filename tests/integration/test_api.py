import pytest
from fastapi.testclient import TestClient

from src.api.app import crear_app

pytestmark = pytest.mark.integration


def test_health():
    cliente = TestClient(crear_app())
    respuesta = cliente.get("/api/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_sirve_el_frontend_compilado(tmp_path):
    (tmp_path / "index.html").write_text("<h1>hola</h1>")
    cliente = TestClient(crear_app(tmp_path))
    assert "hola" in cliente.get("/").text
