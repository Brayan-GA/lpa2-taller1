"""Pruebas unitarias de main.py (datos de ejemplo y punto de entrada).

Se usa una tienda real para comprobar los datos de ejemplo, capsys para
revisar lo que se imprime y monkeypatch para evitar abrir el menú interactivo.
"""

from unittest.mock import Mock

import pytest

import main
from models.composicion.comedor import Comedor
from models.concretos.sofacama import SofaCama
from services.tienda import TiendaMuebles


@pytest.fixture
def tienda():
    return TiendaMuebles("Tienda de Prueba")


class TestCrearCatalogoInicial:
    def test_agrega_todos_los_muebles(self, tienda, capsys):
        main.crear_catalogo_inicial(tienda)
        assert len(tienda._inventario) == 17
        texto = capsys.readouterr().out
        assert "Creando catálogo inicial" in texto
        assert texto.count("✓") == 17
        assert "Catálogo inicial creado con éxito" in texto

    def test_incluye_herencia_multiple(self, tienda, capsys):
        main.crear_catalogo_inicial(tienda)
        assert any(isinstance(m, SofaCama) for m in tienda._inventario)

    def test_todos_tienen_precio(self, tienda, capsys):
        main.crear_catalogo_inicial(tienda)
        for mueble in tienda._inventario:
            assert mueble.calcular_precio() > 0


class TestCrearComedoresEjemplo:
    def test_agrega_dos_comedores(self, tienda, capsys):
        main.crear_comedores_ejemplo(tienda)
        assert len(tienda._comedores) == 2
        assert all(isinstance(c, Comedor) for c in tienda._comedores)
        assert [c.nombre for c in tienda._comedores] == [
            "Comedor Familiar Completo",
            "Comedor Moderno Premium",
        ]
        assert "Comedores de ejemplo creados" in capsys.readouterr().out

    def test_cantidad_de_sillas(self, tienda, capsys):
        main.crear_comedores_ejemplo(tienda)
        familiar, moderno = tienda._comedores
        assert len(familiar.sillas) == 6
        assert len(moderno.sillas) == 4


class TestAplicarDescuentosEjemplo:
    def test_aplica_tres_descuentos(self, capsys):
        tienda = Mock()
        tienda.aplicar_descuento.return_value = "ok"
        main.aplicar_descuentos_ejemplo(tienda)
        assert [c.args for c in tienda.aplicar_descuento.call_args_list] == [
            ("silla", 10),
            ("mesa", 15),
            ("sofa", 20),
        ]
        texto = capsys.readouterr().out
        assert texto.count("✓ ok") == 3
        assert "Descuentos aplicados" in texto

    def test_con_tienda_real(self, tienda, capsys):
        main.aplicar_descuentos_ejemplo(tienda)
        assert "Descuentos aplicados" in capsys.readouterr().out


class TestMostrarEstadisticasIniciales:
    def test_imprime_estadisticas(self, capsys):
        tienda = Mock()
        tienda.obtener_estadisticas.return_value = {
            "total_muebles": 3,
            "total_comedores": 1,
            "valor_inventario": 1234.5,
            "descuentos_activos": {"silla": 10},
            "ventas_realizadas": 2,
            "total_muebles_vendidos": 4,
            "valor_total_ventas": 9999.0,
            "tipos_muebles": {"Silla": 2, "Mesa": 1},
        }
        main.mostrar_estadisticas_iniciales(tienda)
        texto = capsys.readouterr().out
        assert "Total de muebles: 3" in texto
        assert "Total de comedores: 1" in texto
        assert "Valor del inventario: $1,234.50" in texto
        assert "Descuentos activos: {'silla': 10}" in texto
        assert "Ventas realizadas: 2" in texto
        assert "Total muebles vendidos (acumulado): 4" in texto
        assert "Valor total de ventas (acumulado): $9,999.00" in texto
        assert "• Silla: 2 unidades" in texto
        assert "• Mesa: 1 unidades" in texto

    def test_valores_por_defecto(self, capsys):
        tienda = Mock()
        tienda.obtener_estadisticas.return_value = {"tipos_muebles": None}
        main.mostrar_estadisticas_iniciales(tienda)
        texto = capsys.readouterr().out
        assert "Total de muebles: 0" in texto
        assert "Valor del inventario: $0.00" in texto
        assert "unidades" not in texto


class TestMain:
    @pytest.fixture
    def menu_falso(self, monkeypatch):
        """Reemplaza MenuTienda para no abrir el menú interactivo."""
        clase = Mock()
        monkeypatch.setattr(main, "MenuTienda", clase)
        monkeypatch.setattr("builtins.input", lambda *_args: "")
        return clase

    def test_flujo_completo(self, menu_falso, capsys):
        main.main()
        menu_falso.assert_called_once()
        tienda = menu_falso.call_args.args[0]
        assert isinstance(tienda, TiendaMuebles)
        assert tienda.nombre == "Mueblería Moderna OOP"
        assert len(tienda._inventario) == 17
        assert len(tienda._comedores) == 2
        menu_falso.return_value.ejecutar.assert_called_once_with()
        texto = capsys.readouterr().out
        assert "Bienvenido a la Tienda de Muebles" in texto
        assert "Iniciando interfaz de usuario" in texto
        assert "Programa finalizado" in texto

    def test_keyboard_interrupt(self, menu_falso, capsys):
        menu_falso.return_value.ejecutar.side_effect = KeyboardInterrupt
        main.main()
        texto = capsys.readouterr().out
        assert "Programa interrumpido por el usuario" in texto
        assert "Programa finalizado" in texto

    def test_error_inesperado(self, menu_falso, capsys):
        menu_falso.return_value.ejecutar.side_effect = RuntimeError("falla")
        main.main()
        captura = capsys.readouterr()
        assert "Error inesperado: falla" in captura.out
        assert "RuntimeError: falla" in captura.err
        assert "Programa finalizado" in captura.out
