"""Servidor FastAPI: API del juego y archivos compilados de React."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def crear_app(dist: Path = DIST) -> FastAPI:
    app = FastAPI(title="Zombie Survival Engine")

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok"}

    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
    return app


app = crear_app()
