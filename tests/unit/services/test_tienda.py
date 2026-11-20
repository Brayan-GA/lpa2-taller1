"""Pruebas unitarias de TiendaMuebles (services/tienda.py).

Se usan muebles reales (Silla, Mesa, SofaCama) para las reglas de negocio y
Mock / patch para simular fallos, la fecha de la venta y las estadísticas.
"""

import re
from unittest.mock import Mock, patch

import pytest

from models.composicion.comedor import Comedor
from models.concretos.mesa import Mesa
from models.concretos.silla import Silla
from models.concretos.sofacama import SofaCama
from services.tienda import TiendaMuebles

METODOS_ESTADISTICAS = ["obtener_estadisticas", "estadisticas"]


# ---------------------------------------------------------------- ayudas
def crear_silla(nombre="Silla A", material="Madera", **kwargs):
    """Silla real de base 100: precio final 110.0 (con respaldo)."""
    return Silla(nombre, material, "Café", 100.0, **kwargs)


def crear_mesa(nombre="Mesa", material="Metal"):
    """Mesa real de base 1000: precio final 1048.0."""
    return Mesa(nombre, material, "Negro", 1000.0)


def mueble_falso(nombre="Falso", precio=100.0):
    mueble = Mock()
    mueble.nombre = nombre
    mueble.calcular_precio.return_value = precio
    return mueble


def mueble_roto():
    """Mueble cuyo cálculo de precio siempre falla."""
    mueble = Mock()
    mueble.calcular_precio.side_effect = RuntimeError("sin precio")
    return mueble


class SinNombre:
    """Mueble mínimo sin atributo nombre."""

    def calcular_precio(self):
        return 10.0

    def __str__(self):
        return "sin-nombre"


@pytest.fixture
def tienda():
    return TiendaMuebles()


@pytest.fixture
def muebles():
    """Silla Roja (110.0), Mesa Grande (1048.0) y Silla Azul (160.0)."""
    return (
        crear_silla("Silla Roja"),
        crear_mesa("Mesa Grande"),
        crear_silla("Silla Azul", altura_regulable=True, tiene_ruedas=True),
    )


@pytest.fixture
def tienda_llena(tienda, muebles):
    for mueble in muebles:
        tienda.agregar_mueble(mueble)
    return tienda


# ---------------------------------------------------------------- constructor
class TestConstructor:
    def test_nombre_por_defecto(self, tienda):
        assert tienda.nombre == "Mueblería OOP"

    def test_nombre_personalizado(self):
        assert TiendaMuebles("Mi Tienda").nombre == "Mi Tienda"

    def test_nombre_es_de_solo_lectura(self, tienda):
        with pytest.raises(AttributeError):
            tienda.nombre = "Otro"

    def test_tienda_nueva_esta_vacia(self, tienda):
        assert tienda.filtrar_por_precio() == []
        assert tienda.estadisticas() == {
            "total_muebles": 0,
            "total_comedores": 0,
            "valor_inventario": 0,
            "tipos_muebles": {},
            "descuentos_activos": {},
            "ventas_realizadas": 0,
            "total_muebles_vendidos": 0,
            "valor_total_ventas": 0.0,
        }


# ---------------------------------------------------------------- agregar mueble
class TestAgregarMueble:
    def test_agrega_mueble_valido(self, tienda):
        silla = crear_silla()

        mensaje = tienda.agregar_mueble(silla)

        assert mensaje == "Mueble Silla A agregado exitosamente al inventario"
        assert tienda.filtrar_por_precio() == [silla]

    def test_rechaza_none(self, tienda):
        assert tienda.agregar_mueble(None) == "Error: El mueble no puede ser None"
        assert tienda.filtrar_por_precio() == []

    @pytest.mark.parametrize("precio", [0, -5, -0.01])
    def test_rechaza_precio_no_positivo(self, tienda, precio):
        mueble = mueble_falso(precio=precio)

        mensaje = tienda.agregar_mueble(mueble)

        assert mensaje == "Error: El mueble debe tener un precio válido mayor a 0"
        assert tienda.estadisticas()["total_muebles"] == 0

    def test_error_al_calcular_el_precio(self, tienda):
        mueble = Mock()
        mueble.calcular_precio.side_effect = ValueError("falla")

        mensaje = tienda.agregar_mueble(mueble)

        assert mensaje == "Error al calcular precio del mueble: falla"
        assert tienda.estadisticas()["total_muebles"] == 0

    def test_mueble_sin_nombre_usa_su_representacion_en_texto(self, tienda):
        mensaje = tienda.agregar_mueble(SinNombre())

        assert mensaje == "Mueble sin-nombre agregado exitosamente al inventario"

    def test_consulta_el_precio_una_vez(self, tienda):
        mueble = mueble_falso()

        tienda.agregar_mueble(mueble)

        mueble.calcular_precio.assert_called_once_with()


# ---------------------------------------------------------------- agregar comedor
class TestAgregarComedor:
    def test_agrega_comedor_valido(self, tienda):
        comedor = Comedor("Set", crear_mesa())

        mensaje = tienda.agregar_comedor(comedor)

        assert mensaje == "Comedor Set agregado exitosamente"
        assert tienda.estadisticas()["total_comedores"] == 1

    def test_rechaza_none(self, tienda):
        assert tienda.agregar_comedor(None) == "Error: El comedor no puede ser None"
        assert tienda.estadisticas()["total_comedores"] == 0

    def test_comedor_sin_nombre_usa_su_representacion_en_texto(self, tienda):
        class Raro:
            def __str__(self):
                return "raro"

        assert tienda.agregar_comedor(Raro()) == "Comedor raro agregado exitosamente"


# ---------------------------------------------------------------- buscar por nombre
class TestBuscarPorNombre:
    @pytest.mark.parametrize(
        "busqueda,esperados",
        [
            ("silla", ["Silla Roja", "Silla Azul"]),
            ("SILLA", ["Silla Roja", "Silla Azul"]),    # sin distinguir mayúsculas
            ("  silla  ", ["Silla Roja", "Silla Azul"]),  # ignora espacios extremos
            ("roj", ["Silla Roja"]),                      # coincidencia parcial
            ("mesa", ["Mesa Grande"]),
            ("sofá", []),
        ],
    )
    def test_busqueda(self, tienda_llena, busqueda, esperados):
        nombres = [m.nombre for m in tienda_llena.buscar_muebles_por_nombre(busqueda)]

        assert nombres == esperados

    @pytest.mark.parametrize("busqueda", ["", "   ", None])
    def test_busqueda_vacia_no_devuelve_nada(self, tienda_llena, busqueda):
        assert tienda_llena.buscar_muebles_por_nombre(busqueda) == []

    def test_en_tienda_vacia(self, tienda):
        assert tienda.buscar_muebles_por_nombre("silla") == []


# ---------------------------------------------------------------- filtrar por precio
class TestFiltrarPorPrecio:
    @pytest.mark.parametrize(
        "kwargs,esperados",
        [
            ({}, ["Silla Roja", "Mesa Grande", "Silla Azul"]),
            ({"precio_min": 150}, ["Mesa Grande", "Silla Azul"]),
            ({"precio_max": 200}, ["Silla Roja", "Silla Azul"]),
            ({"precio_min": 110, "precio_max": 160}, ["Silla Roja", "Silla Azul"]),  # inclusivo
            ({"precio_min": -50, "precio_max": 200}, ["Silla Roja", "Silla Azul"]),  # min negativo = 0
            ({"precio_min": 500, "precio_max": 100}, []),
            ({"precio_min": 2000}, []),
        ],
    )
    def test_filtro(self, tienda_llena, kwargs, esperados):
        nombres = [m.nombre for m in tienda_llena.filtrar_por_precio(**kwargs)]

        assert nombres == esperados

    def test_omite_muebles_con_error_de_precio(self, tienda_llena):
        tienda_llena._inventario.append(mueble_roto())

        assert len(tienda_llena.filtrar_por_precio()) == 3


# ---------------------------------------------------------------- filtrar por material
class TestFiltrarPorMaterial:
    @pytest.mark.parametrize(
        "material,esperados",
        [
            ("madera", ["Silla Roja", "Silla Azul"]),
            ("  MADERA  ", ["Silla Roja", "Silla Azul"]),
            ("metal", ["Mesa Grande"]),
            ("vidrio", []),
        ],
    )
    def test_filtro(self, tienda_llena, material, esperados):
        nombres = [m.nombre for m in tienda_llena.filtrar_por_material(material)]

        assert nombres == esperados

    @pytest.mark.parametrize("material", ["", "   ", None])
    def test_material_vacio_no_devuelve_nada(self, tienda_llena, material):
        assert tienda_llena.filtrar_por_material(material) == []

    def test_ignora_muebles_con_material_anomalo(self, tienda_llena):
        sin_atributo = Mock(spec=["calcular_precio", "nombre"])
        material_vacio = crear_silla("Sin material", material="")
        material_no_texto = Mock()
        material_no_texto.material = 5  # .lower() fallaría
        tienda_llena._inventario.extend([sin_atributo, material_vacio, material_no_texto])

        nombres = [m.nombre for m in tienda_llena.filtrar_por_material("madera")]

        assert nombres == ["Silla Roja", "Silla Azul"]


# ---------------------------------------------------------------- descuentos
class TestAplicarDescuento:
    @pytest.mark.parametrize(
        "categoria,porcentaje,clave,fraccion",
        [
            ("sillas", 10, "Silla", 0.10),
            ("Mesas", 25, "Mesa", 0.25),
            ("silla", 15, "Silla", 0.15),          # sin 's' final
            ("  SILLAS  ", 20, "Silla", 0.20),     # espacios y mayúsculas
            ("cajoneras", 5, "Cajonera", 0.05),
            ("Sofa", 100, "Sofa", 1.0),            # 100% es válido
        ],
    )
    def test_aplica_y_normaliza_la_categoria(
        self, tienda, categoria, porcentaje, clave, fraccion
    ):
        mensaje = tienda.aplicar_descuento(categoria, porcentaje)

        assert mensaje == f"Descuento del {porcentaje}% aplicado a la categoría '{clave}'"
        descuentos = tienda.estadisticas()["descuentos_activos"]
        assert list(descuentos) == [clave]
        assert descuentos[clave] == pytest.approx(fraccion)

    @pytest.mark.parametrize("porcentaje", [0, -5, 101, 150])
    def test_rechaza_porcentajes_fuera_de_rango(self, tienda, porcentaje):
        mensaje = tienda.aplicar_descuento("sillas", porcentaje)

        assert mensaje == "Error: El porcentaje debe estar entre 1 y 100"
        assert tienda.estadisticas()["descuentos_activos"] == {}

    def test_acepta_porcentajes_menores_a_uno(self, tienda):
        # El mensaje de error habla de "entre 1 y 100", pero 0.5 sí se acepta.
        mensaje = tienda.aplicar_descuento("sillas", 0.5)

        assert mensaje == "Descuento del 0.5% aplicado a la categoría 'Silla'"

    def test_reaplicar_reemplaza_el_descuento_anterior(self, tienda):
        tienda.aplicar_descuento("sillas", 10)
        tienda.aplicar_descuento("sillas", 20)

        descuentos = tienda.estadisticas()["descuentos_activos"]

        assert descuentos["Silla"] == pytest.approx(0.20)

    def test_varias_categorias_conviven(self, tienda):
        tienda.aplicar_descuento("sillas", 10)
        tienda.aplicar_descuento("mesas", 25)

        assert set(tienda.estadisticas()["descuentos_activos"]) == {"Silla", "Mesa"}

    def test_sofacama_se_normaliza_como_sofacama(self, tienda):
        # El nombre de la clase es "SofaCama", pero capitalize() produce "Sofacama".
        tienda.aplicar_descuento("SofaCama", 10)

        assert list(tienda.estadisticas()["descuentos_activos"]) == ["Sofacama"]


# ---------------------------------------------------------------- ventas
class TestRealizarVenta:
    def test_mueble_fuera_de_inventario(self, tienda):
        resultado = tienda.realizar_venta(crear_silla())

        assert resultado == {"error": "El mueble no está disponible en inventario"}

    def test_venta_sin_descuento(self, tienda):
        silla = crear_silla()
        tienda.agregar_mueble(silla)

        venta = tienda.realizar_venta(silla)

        assert venta["mueble"] == "Silla A"
        assert venta["cliente"] == "Cliente Anónimo"
        assert venta["precio_original"] == pytest.approx(110.0)
        assert venta["descuento"] == 0
        assert venta["precio_final"] == pytest.approx(110.0)
        assert tienda.filtrar_por_precio() == []

    def test_venta_con_cliente_personalizado(self, tienda):
        silla = crear_silla()
        tienda.agregar_mueble(silla)

        assert tienda.realizar_venta(silla, "Ana")["cliente"] == "Ana"

    def test_venta_con_descuento_de_su_categoria(self, tienda):
        silla = crear_silla()
        tienda.agregar_mueble(silla)
        tienda.aplicar_descuento("sillas", 10)

        venta = tienda.realizar_venta(silla)

        assert venta["descuento"] == pytest.approx(10.0)
        assert venta["precio_final"] == pytest.approx(99.0)  # 110 * 0.90

    def test_el_descuento_de_otra_categoria_no_aplica(self, tienda):
        silla = crear_silla()
        tienda.agregar_mueble(silla)
        tienda.aplicar_descuento("mesas", 50)

        venta = tienda.realizar_venta(silla)

        assert venta["descuento"] == 0
        assert venta["precio_final"] == pytest.approx(110.0)

    def test_mueble_sin_nombre_usa_el_nombre_de_su_clase(self, tienda):
        silla = crear_silla(nombre="")
        tienda.agregar_mueble(silla)

        assert tienda.realizar_venta(silla)["mueble"] == "Silla"

    def test_fecha_tiene_formato_valido(self, tienda):
        silla = crear_silla()
        tienda.agregar_mueble(silla)

        fecha = tienda.realizar_venta(silla)["fecha"]

        assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", fecha)

    def test_fecha_simulada_con_patch(self, tienda):
        silla = crear_silla()
        tienda.agregar_mueble(silla)

        with patch("datetime.datetime") as dt:
            dt.now.return_value.strftime.return_value = "2026-11-20 13:57:00"
            venta = tienda.realizar_venta(silla)

        assert venta["fecha"] == "2026-11-20 13:57:00"
        dt.now.return_value.strftime.assert_called_once_with("%Y-%m-%d %H:%M:%S")

    def test_no_se_puede_vender_dos_veces_el_mismo_mueble(self, tienda):
        silla = crear_silla()
        tienda.agregar_mueble(silla)
        tienda.realizar_venta(silla)

        assert tienda.realizar_venta(silla) == {
            "error": "El mueble no está disponible en inventario"
        }

    def test_acumula_ventas_y_valor(self, tienda_llena, muebles):
        silla_roja, _, silla_azul = muebles

        tienda_llena.realizar_venta(silla_roja)
        tienda_llena.realizar_venta(silla_azul)
        stats = tienda_llena.estadisticas()

        assert stats["ventas_realizadas"] == 2
        assert stats["total_muebles_vendidos"] == 2
        assert stats["valor_total_ventas"] == pytest.approx(270.0)  # 110 + 160
        assert stats["total_muebles"] == 1

    def test_error_durante_la_venta_no_altera_el_inventario(self, tienda):
        mueble = Mock()
        mueble.nombre = "Frágil"
        # La primera consulta (al agregar) funciona y la segunda (al vender) falla.
        mueble.calcular_precio.side_effect = [100.0, RuntimeError("boom")]
        tienda.agregar_mueble(mueble)

        resultado = tienda.realizar_venta(mueble)
        stats = tienda.estadisticas()

        assert resultado == {"error": "Error al procesar la venta: boom"}
        assert stats["total_muebles"] == 1
        assert stats["ventas_realizadas"] == 0
        assert stats["total_muebles_vendidos"] == 0

    @pytest.mark.xfail(
        reason="aplicar_descuento normaliza 'sofacama' como 'Sofacama' y no "
        "coincide con el nombre de la clase 'SofaCama'"
    )
    def test_descuento_se_aplica_a_sofacama(self, tienda):
        sofacama = SofaCama("SC", "Tela", "Gris", 1000)  # precio final 2000.0
        tienda.agregar_mueble(sofacama)
        tienda.aplicar_descuento("sofacama", 10)

        venta = tienda.realizar_venta(sofacama)

        assert venta["precio_final"] == pytest.approx(1800.0)


# ---------------------------------------------------------------- estadísticas
@pytest.mark.parametrize("metodo", METODOS_ESTADISTICAS)
class TestEstadisticas:
    def test_resumen_del_inventario(self, tienda_llena, metodo):
        stats = getattr(tienda_llena, metodo)()

        assert stats["total_muebles"] == 3
        assert stats["valor_inventario"] == pytest.approx(1318.0)  # 110 + 1048 + 160
        assert stats["tipos_muebles"] == {"Silla": 2, "Mesa": 1}

    def test_cuenta_comedores_sin_sumarlos_al_valor(self, tienda_llena, metodo):
        tienda_llena.agregar_comedor(Comedor("Uno", crear_mesa()))
        tienda_llena.agregar_comedor(Comedor("Dos", crear_mesa()))

        stats = getattr(tienda_llena, metodo)()

        assert stats["total_comedores"] == 2
        assert stats["valor_inventario"] == pytest.approx(1318.0)

    def test_mueble_con_error_cuenta_pero_no_suma_valor(self, tienda_llena, metodo):
        tienda_llena._inventario.append(mueble_roto())

        stats = getattr(tienda_llena, metodo)()

        assert stats["total_muebles"] == 4
        assert stats["valor_inventario"] == pytest.approx(1318.0)
        assert stats["tipos_muebles"]["Mock"] == 1

    def test_descuentos_activos_es_una_copia(self, tienda, metodo):
        tienda.aplicar_descuento("sillas", 10)

        getattr(tienda, metodo)()["descuentos_activos"].clear()

        assert list(getattr(tienda, metodo)()["descuentos_activos"]) == ["Silla"]

    def test_sin_atributos_acumulativos_usa_valores_por_defecto(self, tienda, metodo):
        del tienda._ventas_realizadas
        del tienda._total_muebles_vendidos
        del tienda._valor_total_ventas

        stats = getattr(tienda, metodo)()

        assert stats["ventas_realizadas"] == 0
        assert stats["total_muebles_vendidos"] == 0
        assert stats["valor_total_ventas"] == 0.0

    def test_ante_un_error_devuelve_estadisticas_en_cero(self, tienda, metodo):
        tienda._ventas_realizadas = [{"venta": 1}]
        tienda._inventario = None  # hace fallar len() y activa el except

        assert getattr(tienda, metodo)() == {
            "total_muebles": 0,
            "total_comedores": 0,
            "valor_inventario": 0.0,
            "tipos_muebles": {},
            "descuentos_activos": {},
            "ventas_realizadas": 0,
            "total_muebles_vendidos": 0,
            "valor_total_ventas": 0.0,
        }


def test_ambos_metodos_de_estadisticas_devuelven_lo_mismo(tienda_llena):
    tienda_llena.aplicar_descuento("sillas", 10)

    assert tienda_llena.obtener_estadisticas() == tienda_llena.estadisticas()


# ---------------------------------------------------------------- reporte
class TestReporteInventario:
    def test_reporte_de_tienda_vacia(self, tienda):
        assert tienda.generar_reporte_inventario() == (
            "=== REPORTE DE INVENTARIO - Mueblería OOP ===\n\n"
            "Total de muebles: 0\n"
            "Total de comedores: 0\n"
            "Valor total del inventario: $0.00\n\n"
            "DISTRIBUCIÓN POR TIPOS:\n"
        )

    def test_reporte_completo(self, tienda_llena):
        tienda_llena.aplicar_descuento("sillas", 10)

        assert tienda_llena.generar_reporte_inventario() == (
            "=== REPORTE DE INVENTARIO - Mueblería OOP ===\n\n"
            "Total de muebles: 3\n"
            "Total de comedores: 0\n"
            "Valor total del inventario: $1318.00\n\n"
            "DISTRIBUCIÓN POR TIPOS:\n"
            "- Silla: 2 unidades\n"
            "- Mesa: 1 unidades\n"
            "\nDESCUENTOS ACTIVOS:\n"
            "- Silla: 10.0%\n"
        )

    def test_usa_el_nombre_de_la_tienda(self):
        reporte = TiendaMuebles("Mi Tienda").generar_reporte_inventario()

        assert reporte.startswith("=== REPORTE DE INVENTARIO - Mi Tienda ===")

    def test_reporte_con_estadisticas_simuladas(self, tienda):
        falsas = {
            "total_muebles": 3,
            "total_comedores": 1,
            "valor_inventario": 1234.5,
            "tipos_muebles": {"Silla": 2, "Mesa": 1},
            "descuentos_activos": {"Silla": 0.1, "Mesa": 0.25},
        }

        with patch.object(tienda, "obtener_estadisticas", return_value=falsas) as mock:
            reporte = tienda.generar_reporte_inventario()

        mock.assert_called_once_with()
        assert reporte == (
            "=== REPORTE DE INVENTARIO - Mueblería OOP ===\n\n"
            "Total de muebles: 3\n"
            "Total de comedores: 1\n"
            "Valor total del inventario: $1234.50\n\n"
            "DISTRIBUCIÓN POR TIPOS:\n"
            "- Silla: 2 unidades\n"
            "- Mesa: 1 unidades\n"
            "\nDESCUENTOS ACTIVOS:\n"
            "- Silla: 10.0%\n"
            "- Mesa: 25.0%\n"
        )

    @pytest.mark.parametrize("devuelto", [None, [], ["no es un diccionario"]])
    def test_estadisticas_invalidas_se_tratan_como_vacias(self, tienda, devuelto):
        with patch.object(tienda, "obtener_estadisticas", return_value=devuelto):
            reporte = tienda.generar_reporte_inventario()

        assert "Total de muebles: 0\n" in reporte
        assert "Valor total del inventario: $0.00" in reporte
        assert "DESCUENTOS" not in reporte

    def test_tipos_y_descuentos_nulos_se_ignoran(self, tienda):
        falsas = {"tipos_muebles": None, "descuentos_activos": None}

        with patch.object(tienda, "obtener_estadisticas", return_value=falsas):
            reporte = tienda.generar_reporte_inventario()

        assert reporte.endswith("DISTRIBUCIÓN POR TIPOS:\n")


# ---------------------------------------------------------------- pendientes (TODO)
class TestFuncionalidadPendiente:
    """Métodos que en tienda.py siguen como TODO (solo tienen `pass`).

    Describen el comportamiento esperado según el código comentado de cada
    método. Hoy salen como XFAIL; al implementarlos pasarán a XPASS.
    """

    @pytest.mark.xfail(reason="obtener_muebles_por_tipo aún no está implementado")
    def test_obtener_muebles_por_tipo(self, tienda_llena, muebles):
        silla_roja, _, silla_azul = muebles

        assert tienda_llena.obtener_muebles_por_tipo(Silla) == [silla_roja, silla_azul]

    @pytest.mark.xfail(reason="calcular_valor_inventario aún no está implementado")
    def test_calcular_valor_inventario_incluye_comedores(self, tienda_llena):
        tienda_llena.agregar_comedor(Comedor("Set", crear_mesa()))

        # 110 + 1048 + 160 de muebles, más 1048 del comedor (solo mesa)
        assert tienda_llena.calcular_valor_inventario() == pytest.approx(2366.0)

    @pytest.mark.xfail(reason="_contar_tipos_muebles aún no está implementado")
    def test_contar_tipos_muebles(self, tienda_llena):
        assert tienda_llena._contar_tipos_muebles() == {"Silla": 2, "Mesa": 1}