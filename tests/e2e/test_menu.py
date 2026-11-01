import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e


def test_menu_principal(page: Page, base_url: str):
    page.goto(base_url)
    titulo = page.get_by_role("heading", name="Zombie Survival Engine")
    expect(titulo).to_be_visible()
    for nombre in ("Iniciar juego", "Opciones", "Sources"):
        expect(page.get_by_role("button", name=nombre)).to_be_visible()
