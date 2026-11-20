"""Pruebas de integración: MenuTienda + TiendaMuebles reales.

Se simula una sesión completa de un usuario en el menú (solo se reemplazan
las preguntas por teclado y las pausas); la tienda y los muebles son reales.
"""

import pytest
from rich.console import Console

import ui.menu as menu_mod
from ui.menu import MenuTienda


def responder(monkeypatch, clase, *respuestas):
    pendientes = iter(respuestas)
    monkeypatch.setattr(clase, "ask", lambda *args, **kwargs: next(pendientes))


@pytest.fixture
def menu(tienda_con_catalogo, monkeypatch):
    monkeypatch.setattr(menu_mod.time, "sleep", lambda _segundos: None)
    monkeypatch.setattr("builtins.input", lambda *_args: "")
    menu = MenuTienda(tienda_con_catalogo)
    menu.console = Console(record=True, width=200, force_terminal=False)
    return menu


class TestSesionCompleta:
    def test_vender_y_ver_estadisticas(self, menu, monkeypatch):
        tienda = menu.tienda
        primer_mueble = tienda._inventario[0]
        # Menú: 6 (vender) -> mueble 1 -> 7 (estadísticas) -> 0 (salir)
        responder(monkeypatch, menu_mod.IntPrompt, 6, 1, 7, 0)
        responder(monkeypatch, menu_mod.Confirm, True)
        responder(monkeypatch, menu_mod.Prompt, "Ana")

        menu.ejecutar()

        texto = menu.console.export_text()
        assert "Venta Exitosa" in texto
        assert "Cliente: Ana" in texto
        assert "Hasta luego" in texto
        assert primer_mueble not in tienda._inventario
        stats = tienda.obtener_estadisticas()
        assert stats["total_muebles"] == 16
        assert stats["ventas_realizadas"] == 1

    def test_descuento_desde_menu_se_aplica_en_la_venta(self, menu, monkeypatch):
        tienda = menu.tienda
        silla = tienda.buscar_muebles_por_nombre("Silla Clásica")[0]
        indice = tienda._inventario.index(silla) + 1
        # Menú: 9 (descuentos) -> categoría 1 (silla) -> 20% -> 6 (vender) -> silla -> 0
        responder(monkeypatch, menu_mod.IntPrompt, 9, 1, 20, 6, indice, 0)
        responder(monkeypatch, menu_mod.Confirm, True)
        responder(monkeypatch, menu_mod.Prompt, "Luis")

        menu.ejecutar()

        venta = tienda._ventas_realizadas[-1]
        assert venta["mueble"] == "Silla Clásica"
        assert venta["descuento"] == 20.0
        assert venta["precio_final"] == pytest.approx(
            venta["precio_original"] * 0.8, abs=0.01
        )
        assert "Descuento aplicado: 20.0%" in menu.console.export_text()

    def test_buscar_filtrar_y_guardar_reporte(self, menu, monkeypatch, tmp_path):
        archivo = tmp_path / "reporte.txt"
        # Menú: 2 (buscar) -> 4 (material) -> 8 (reporte) -> 0
        responder(monkeypatch, menu_mod.IntPrompt, 2, 4, 8, 0)
        responder(monkeypatch, menu_mod.Prompt, "cama", "vidrio", str(archivo))
        responder(monkeypatch, menu_mod.Confirm, True)

        menu.ejecutar()

        texto = menu.console.export_text()
        assert "Cama King Size de Lujo" in texto
        assert "Mesa de Centro Redonda" in texto
        assert archivo.read_text(encoding="utf-8").startswith(
            "=== REPORTE DE INVENTARIO"
        )
