"""Pruebas unitarias de MenuTienda (ui/menu.py).

Las preguntas al usuario (Prompt, IntPrompt, Confirm e input) se simulan con
monkeypatch, time.sleep se anula para que las pruebas sean rápidas y la
consola de Rich se reemplaza por una que graba lo impreso para revisarlo.
"""

from unittest.mock import Mock

import pytest
from rich.console import Console

import ui.menu as menu_mod
from models.composicion.comedor import Comedor
from models.concretos.mesa import Mesa
from models.concretos.silla import Silla
from services.tienda import TiendaMuebles
from ui.menu import MenuTienda


# ---------------------------------------------------------------- ayudas
def crear_silla(nombre="Silla A", material="Madera"):
    return Silla(nombre, material, "Café", 100.0)


def crear_mesa(nombre="Mesa A", material="Metal"):
    return Mesa(nombre, material, "Negro", 1000.0)


def mueble_roto(nombre="Roto"):
    """Mueble cuyo cálculo de precio siempre falla."""
    mueble = Mock()
    mueble.nombre = nombre
    mueble.material = "Madera"
    mueble.color = "Rojo"
    mueble.calcular_precio.side_effect = RuntimeError("sin precio")
    return mueble


def responder(monkeypatch, clase, *respuestas):
    """Hace que clase.ask devuelva las respuestas en orden.

    Si una respuesta es una excepción, se lanza en lugar de devolverse.
    """
    pendientes = iter(respuestas)
    llamadas = []

    def ask(*args, **kwargs):
        llamadas.append((args, kwargs))
        valor = next(pendientes)
        if isinstance(valor, BaseException):
            raise valor
        return valor

    monkeypatch.setattr(clase, "ask", ask)
    return llamadas


def salida(menu):
    return menu.console.export_text()


@pytest.fixture(autouse=True)
def sin_esperas(monkeypatch):
    monkeypatch.setattr(menu_mod.time, "sleep", lambda _segundos: None)


@pytest.fixture
def tienda():
    return TiendaMuebles("Tienda de Prueba")


@pytest.fixture
def menu(tienda):
    menu = MenuTienda(tienda)
    menu.console = Console(record=True, width=200, force_terminal=False)
    return menu


@pytest.fixture
def menu_con_muebles(menu):
    menu.tienda.agregar_mueble(crear_silla("Silla Roble", "Madera"))
    menu.tienda.agregar_mueble(crear_mesa("Mesa Industrial", "Metal"))
    return menu


# ---------------------------------------------------------------- constructor
class TestConstructor:
    def test_asigna_atributos(self, tienda):
        menu = MenuTienda(tienda)
        assert menu.tienda is tienda
        assert isinstance(menu.console, Console)
        assert menu.running is True


# ---------------------------------------------------------------- catálogo
class TestMostrarCatalogo:
    def test_inventario_vacio(self, menu):
        menu.mostrar_catalogo_completo()
        assert "No hay muebles en el inventario" in salida(menu)

    def test_muestra_cada_mueble(self, menu_con_muebles):
        menu_con_muebles.mostrar_catalogo_completo()
        texto = salida(menu_con_muebles)
        assert "Catálogo de Muebles" in texto
        assert "Silla Roble" in texto
        assert "Mesa Industrial" in texto
        assert "Silla" in texto and "Mesa" in texto
        assert "$1048.00" in texto

    def test_mueble_con_error_de_precio(self, menu):
        menu.tienda._inventario.append(mueble_roto("Mueble Roto"))
        menu.mostrar_catalogo_completo()
        texto = salida(menu)
        assert "Mueble Roto" in texto
        assert "Error" in texto


# ---------------------------------------------------------------- búsqueda
class TestBuscarMuebles:
    def test_termino_vacio(self, menu, monkeypatch):
        responder(monkeypatch, menu_mod.Prompt, "   ")
        menu.buscar_muebles_interactivo()
        assert "Término de búsqueda vacío" in salida(menu)

    def test_sin_resultados(self, menu_con_muebles, monkeypatch):
        responder(monkeypatch, menu_mod.Prompt, "sofá")
        menu_con_muebles.buscar_muebles_interactivo()
        assert "No se encontraron muebles que contengan 'sofá'" in salida(
            menu_con_muebles
        )

    def test_con_resultados(self, menu_con_muebles, monkeypatch):
        responder(monkeypatch, menu_mod.Prompt, "silla")
        menu_con_muebles.buscar_muebles_interactivo()
        texto = salida(menu_con_muebles)
        assert "Se encontraron 1 resultado(s)" in texto
        assert "Silla Roble" in texto
        assert "Mesa Industrial" not in texto


# ---------------------------------------------------------------- filtro precio
class TestFiltrarPorPrecio:
    def test_minimo_mayor_que_maximo(self, menu, monkeypatch):
        responder(monkeypatch, menu_mod.IntPrompt, 500, 100)
        menu.filtrar_por_precio_interactivo()
        assert "El precio mínimo no puede ser mayor al máximo" in salida(menu)

    def test_maximo_cero_es_sin_limite(self, menu_con_muebles, monkeypatch):
        menu_con_muebles.tienda = Mock(wraps=menu_con_muebles.tienda)
        responder(monkeypatch, menu_mod.IntPrompt, 0, 0)
        menu_con_muebles.filtrar_por_precio_interactivo()
        menu_con_muebles.tienda.filtrar_por_precio.assert_called_once_with(
            0, float("inf")
        )
        assert "Se encontraron 2 mueble(s) en el rango" in salida(menu_con_muebles)

    def test_sin_resultados(self, menu_con_muebles, monkeypatch):
        responder(monkeypatch, menu_mod.IntPrompt, 5000, 9000)
        menu_con_muebles.filtrar_por_precio_interactivo()
        assert "No hay muebles en el rango $5000 - $9000" in salida(menu_con_muebles)

    def test_con_resultados(self, menu_con_muebles, monkeypatch):
        responder(monkeypatch, menu_mod.IntPrompt, 0, 500)
        menu_con_muebles.filtrar_por_precio_interactivo()
        texto = salida(menu_con_muebles)
        assert "Se encontraron 1 mueble(s) en el rango" in texto
        assert "Silla Roble" in texto
        assert "Mesa Industrial" not in texto


# ---------------------------------------------------------------- filtro material
class TestFiltrarPorMaterial:
    def test_material_vacio(self, menu, monkeypatch):
        responder(monkeypatch, menu_mod.Prompt, "")
        menu.filtrar_por_material_interactivo()
        assert "Material no puede estar vacío" in salida(menu)

    def test_sin_resultados(self, menu_con_muebles, monkeypatch):
        responder(monkeypatch, menu_mod.Prompt, "vidrio")
        menu_con_muebles.filtrar_por_material_interactivo()
        assert "No hay muebles de material 'vidrio'" in salida(menu_con_muebles)

    def test_con_resultados(self, menu_con_muebles, monkeypatch):
        responder(monkeypatch, menu_mod.Prompt, "metal")
        menu_con_muebles.filtrar_por_material_interactivo()
        texto = salida(menu_con_muebles)
        assert "Muebles de metal encontrados" in texto
        assert "Mesa Industrial" in texto
        assert "Silla Roble" not in texto


# ---------------------------------------------------------------- comedores
class TestMostrarComedores:
    def test_sin_comedores(self, menu):
        menu.mostrar_comedores()
        assert "No hay comedores disponibles" in salida(menu)

    def test_muestra_un_panel_por_comedor(self, menu):
        for nombre in ("Comedor Uno", "Comedor Dos"):
            comedor = Comedor(nombre, crear_mesa(), [crear_silla(), crear_silla()])
            menu.tienda.agregar_comedor(comedor)
        menu.mostrar_comedores()
        texto = salida(menu)
        assert "Comedor #1" in texto and "Comedor #2" in texto
        assert "COMEDOR COMEDOR UNO" in texto
        assert "COMEDOR COMEDOR DOS" in texto


# ---------------------------------------------------------------- venta
class TestRealizarVenta:
    def test_sin_inventario(self, menu):
        menu.realizar_venta_interactiva()
        assert "No hay muebles disponibles para venta" in salida(menu)

    def test_venta_cancelada(self, menu_con_muebles, monkeypatch):
        responder(monkeypatch, menu_mod.IntPrompt, 1)
        responder(monkeypatch, menu_mod.Confirm, False)
        menu_con_muebles.realizar_venta_interactiva()
        assert "Venta cancelada" in salida(menu_con_muebles)
        assert len(menu_con_muebles.tienda._inventario) == 2

    def test_venta_exitosa(self, menu_con_muebles, monkeypatch):
        llamadas = responder(monkeypatch, menu_mod.IntPrompt, 2)
        responder(monkeypatch, menu_mod.Confirm, True)
        responder(monkeypatch, menu_mod.Prompt, "Ana")
        menu_con_muebles.realizar_venta_interactiva()
        texto = salida(menu_con_muebles)
        assert "Mueble seleccionado" in texto
        assert "Venta Exitosa" in texto
        assert "Cliente: Ana" in texto
        assert "Mesa Industrial" in texto
        assert llamadas[0][1]["choices"] == ["1", "2"]
        assert len(menu_con_muebles.tienda._inventario) == 1

    def test_error_de_la_tienda(self, menu_con_muebles, monkeypatch):
        monkeypatch.setattr(
            menu_con_muebles.tienda,
            "realizar_venta",
            lambda mueble, cliente: {"error": "sin stock"},
        )
        responder(monkeypatch, menu_mod.IntPrompt, 1)
        responder(monkeypatch, menu_mod.Confirm, True)
        responder(monkeypatch, menu_mod.Prompt, "Ana")
        menu_con_muebles.realizar_venta_interactiva()
        assert "Error: sin stock" in salida(menu_con_muebles)

    @pytest.mark.parametrize("excepcion", [ValueError("x"), IndexError("x")])
    def test_seleccion_invalida(self, menu_con_muebles, monkeypatch, excepcion):
        responder(monkeypatch, menu_mod.IntPrompt, excepcion)
        menu_con_muebles.realizar_venta_interactiva()
        assert "Selección inválida" in salida(menu_con_muebles)

    def test_lista_numerada_con_mueble_roto(self, menu, monkeypatch):
        menu.tienda._inventario.append(mueble_roto("Mueble Roto"))
        responder(monkeypatch, menu_mod.IntPrompt, 1)
        responder(monkeypatch, menu_mod.Confirm, False)
        menu.realizar_venta_interactiva()
        texto = salida(menu)
        assert "Mueble Roto" in texto
        assert "Error" in texto


# ---------------------------------------------------------------- estadísticas
class TestMostrarEstadisticas:
    def test_con_datos_reales(self, menu_con_muebles):
        menu_con_muebles.mostrar_estadisticas()
        texto = salida(menu_con_muebles)
        assert "Estadísticas de la Tienda" in texto
        assert "Total de muebles" in texto
        assert "Distribución por tipos" in texto
        assert "Silla: 1 unidades" in texto
        assert "Mesa: 1 unidades" in texto

    def test_estadisticas_que_no_son_dict(self, menu, monkeypatch):
        monkeypatch.setattr(menu.tienda, "obtener_estadisticas", lambda: None)
        menu.mostrar_estadisticas()
        texto = salida(menu)
        assert "Total de muebles" in texto
        assert "$0.00" in texto
        assert "Distribución por tipos" not in texto


# ---------------------------------------------------------------- reporte
class TestGenerarReporte:
    def test_no_guarda(self, menu_con_muebles, monkeypatch):
        responder(monkeypatch, menu_mod.Confirm, False)
        menu_con_muebles.generar_reporte_interactivo()
        assert "Reporte de Inventario" in salida(menu_con_muebles)
        assert "guardado" not in salida(menu_con_muebles)

    def test_guarda_en_archivo(self, menu_con_muebles, monkeypatch, tmp_path):
        archivo = tmp_path / "reporte.txt"
        responder(monkeypatch, menu_mod.Confirm, True)
        responder(monkeypatch, menu_mod.Prompt, str(archivo))
        menu_con_muebles.generar_reporte_interactivo()
        assert archivo.read_text(encoding="utf-8") == (
            menu_con_muebles.tienda.generar_reporte_inventario()
        )
        assert "Reporte guardado en" in salida(menu_con_muebles)

    def test_error_al_guardar(self, menu, monkeypatch, tmp_path):
        responder(monkeypatch, menu_mod.Confirm, True)
        # Una carpeta no se puede abrir como archivo para escribir.
        responder(monkeypatch, menu_mod.Prompt, str(tmp_path))
        menu.generar_reporte_interactivo()
        assert "Error al guardar" in salida(menu)


# ---------------------------------------------------------------- descuentos
class TestAplicarDescuentos:
    def test_aplica_descuento(self, menu, monkeypatch):
        menu.tienda = Mock()
        menu.tienda.aplicar_descuento.return_value = "Descuento aplicado"
        llamadas = responder(monkeypatch, menu_mod.IntPrompt, 2, 15)
        menu.aplicar_descuentos_interactivo()
        menu.tienda.aplicar_descuento.assert_called_once_with("mesa", 15)
        texto = salida(menu)
        assert "Categorías disponibles" in texto
        assert "1. Silla" in texto and "6. Escritorio" in texto
        assert "Descuento aplicado" in texto
        assert llamadas[1][1]["choices"] == [str(i) for i in range(1, 51)]

    @pytest.mark.parametrize("excepcion", [ValueError("x"), IndexError("x")])
    def test_seleccion_invalida(self, menu, monkeypatch, excepcion):
        responder(monkeypatch, menu_mod.IntPrompt, excepcion)
        menu.aplicar_descuentos_interactivo()
        assert "Selección inválida" in salida(menu)


# ---------------------------------------------------------------- comprobante
class TestComprobanteVenta:
    def test_formato(self, menu):
        menu._mostrar_comprobante_venta(
            {
                "cliente": "Luis",
                "mueble": "Silla X",
                "precio_original": 100,
                "descuento": 10,
                "precio_final": 90,
            }
        )
        texto = salida(menu)
        assert "Cliente: Luis" in texto
        assert "Producto: Silla X" in texto
        assert "Precio original: $100.00" in texto
        assert "Descuento aplicado: 10.0%" in texto
        assert "PRECIO FINAL: $90.00" in texto


# ---------------------------------------------------------------- banner y menú
class TestBannerYMenuPrincipal:
    def test_banner_muestra_nombre_de_tienda(self, menu):
        menu.mostrar_banner()
        texto = salida(menu)
        assert "Tienda de Prueba" in texto
        assert "Bienvenido" in texto

    def test_menu_principal_devuelve_opcion(self, menu, monkeypatch):
        llamadas = responder(monkeypatch, menu_mod.IntPrompt, 7)
        assert menu.mostrar_menu_principal() == 7
        assert llamadas[0][1]["choices"] == [str(i) for i in range(10)]
        texto = salida(menu)
        assert "MENÚ PRINCIPAL" in texto
        assert "0. Salir" in texto

    def test_menu_principal_reintenta_si_valor_invalido(self, menu, monkeypatch):
        responder(monkeypatch, menu_mod.IntPrompt, ValueError("x"), 3)
        assert menu.mostrar_menu_principal() == 3
        assert "Opción inválida" in salida(menu)


# ---------------------------------------------------------------- bucle principal
ACCIONES = {
    1: "mostrar_catalogo_completo",
    2: "buscar_muebles_interactivo",
    3: "filtrar_por_precio_interactivo",
    4: "filtrar_por_material_interactivo",
    5: "mostrar_comedores",
    6: "realizar_venta_interactiva",
    7: "mostrar_estadisticas",
    8: "generar_reporte_interactivo",
    9: "aplicar_descuentos_interactivo",
}


class TestEjecutar:
    @pytest.fixture
    def menu_falso(self, menu, monkeypatch):
        """Menú con las acciones reemplazadas por Mocks e input anulado."""
        for nombre in ACCIONES.values():
            monkeypatch.setattr(menu, nombre, Mock())
        monkeypatch.setattr(menu, "mostrar_banner", Mock())
        monkeypatch.setattr("builtins.input", lambda *_args: "")
        return menu

    def elegir(self, menu, monkeypatch, *opciones):
        monkeypatch.setattr(menu, "mostrar_menu_principal", Mock(side_effect=opciones))

    def test_salir_inmediatamente(self, menu_falso, monkeypatch):
        self.elegir(menu_falso, monkeypatch, 0)
        menu_falso.ejecutar()
        assert menu_falso.running is False
        menu_falso.mostrar_banner.assert_called_once()
        assert "Hasta luego" in salida(menu_falso)
        for nombre in ACCIONES.values():
            getattr(menu_falso, nombre).assert_not_called()

    @pytest.mark.parametrize("opcion, accion", ACCIONES.items())
    def test_cada_opcion_llama_su_accion(self, menu_falso, monkeypatch, opcion, accion):
        self.elegir(menu_falso, monkeypatch, opcion, 0)
        menu_falso.ejecutar()
        getattr(menu_falso, accion).assert_called_once_with()
        for otra in ACCIONES.values():
            if otra != accion:
                getattr(menu_falso, otra).assert_not_called()

    def test_pausa_despues_de_cada_opcion(self, menu_falso, monkeypatch):
        pausas = []
        monkeypatch.setattr("builtins.input", lambda *args: pausas.append(args))
        self.elegir(menu_falso, monkeypatch, 1, 1, 0)
        menu_falso.ejecutar()
        assert len(pausas) == 2

    def test_keyboard_interrupt_termina(self, menu_falso, monkeypatch):
        self.elegir(menu_falso, monkeypatch, KeyboardInterrupt())
        menu_falso.ejecutar()
        assert menu_falso.running is False
        assert "Operación cancelada por el usuario" in salida(menu_falso)

    def test_error_inesperado_continua(self, menu_falso, monkeypatch):
        menu_falso.mostrar_catalogo_completo.side_effect = RuntimeError("falla")
        self.elegir(menu_falso, monkeypatch, 1, 0)
        menu_falso.ejecutar()
        assert "Error inesperado: falla" in salida(menu_falso)
        assert menu_falso.running is False
