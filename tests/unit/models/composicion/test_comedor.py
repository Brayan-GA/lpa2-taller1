"""Pruebas unitarias de Comedor (composición): una mesa y varias sillas.

Se usan objetos reales (Mesa, Silla) para las reglas de negocio y Mock para
aislar a Comedor de sus componentes en los cálculos y descripciones.
"""

from unittest.mock import Mock

import pytest

from models.composicion.comedor import Comedor
from models.concretos.mesa import Mesa
from models.concretos.silla import Silla


# ---------------------------------------------------------------- ayudas
def crear_mesa(capacidad=4):
    """Mesa real de 1000 base: precio final 1048.0 (120x80 cm)."""
    return Mesa("Mesa", "Madera", "Café", 1000.0, capacidad_personas=capacidad)


def crear_silla(nombre="A"):
    """Silla real de 100 base con respaldo: precio final 110.0."""
    return Silla(nombre, "Madera", "Café", 100.0)


def mesa_falsa(precio=1000.0, descripcion="DESC MESA", material="Madera"):
    """Mesa simulada SIN capacidad_personas (la capacidad máxima será 6)."""
    mesa = Mock(spec=["calcular_precio", "obtener_descripcion", "material"])
    mesa.calcular_precio.return_value = precio
    mesa.obtener_descripcion.return_value = descripcion
    mesa.material = material
    return mesa


def silla_falsa(precio=100.0, descripcion="DESC SILLA", material="Metal", tapizado=None):
    silla = Mock(
        spec=[
            "calcular_precio",
            "obtener_descripcion",
            "material",
            "material_tapizado",
            "nombre",
        ]
    )
    silla.calcular_precio.return_value = precio
    silla.obtener_descripcion.return_value = descripcion
    silla.material = material
    silla.material_tapizado = tapizado
    silla.nombre = "S"
    return silla


@pytest.fixture
def comedor():
    return Comedor("Set", crear_mesa())


# ---------------------------------------------------------------- constructor
class TestComedorConstructor:
    def test_sin_sillas_por_defecto(self, comedor):
        assert comedor.nombre == "Set"
        assert comedor.sillas == []

    def test_conserva_la_mesa_recibida(self):
        mesa = crear_mesa()

        assert Comedor("Set", mesa).mesa is mesa

    def test_acepta_sillas_iniciales(self):
        sillas = [crear_silla("A"), crear_silla("B")]

        assert Comedor("Set", crear_mesa(), sillas).sillas == sillas

    def test_dos_comedores_no_comparten_lista_de_sillas(self):
        c1 = Comedor("Uno", crear_mesa())
        c2 = Comedor("Dos", crear_mesa())

        c1.agregar_silla(crear_silla())

        assert len(c1.sillas) == 1
        assert c2.sillas == []

    @pytest.mark.parametrize("atributo", ["nombre", "mesa", "sillas"])
    def test_propiedades_son_de_solo_lectura(self, comedor, atributo):
        with pytest.raises(AttributeError):
            setattr(comedor, atributo, "otro")

    def test_sillas_devuelve_una_copia(self, comedor):
        comedor.agregar_silla(crear_silla())

        comedor.sillas.clear()

        assert len(comedor.sillas) == 1


# ---------------------------------------------------------------- agregar
class TestAgregarSilla:
    def test_agrega_silla_y_confirma(self, comedor):
        silla = crear_silla("A")

        mensaje = comedor.agregar_silla(silla)

        assert mensaje == "Silla A agregada exitosamente al comedor"
        assert comedor.sillas == [silla]

    def test_rechaza_objetos_de_otro_tipo(self, comedor):
        comedor.agregar_silla(crear_silla())

        mensaje = comedor.agregar_silla(crear_mesa())

        assert mensaje == "Error: Solo se pueden agregar objetos de tipo Silla"
        assert len(comedor.sillas) == 1

    def test_sin_sillas_previas_no_se_valida_el_tipo(self, comedor):
        # El tipo se deduce de la primera silla, así que en un comedor vacío
        # cualquier objeto pasa la validación (comportamiento actual).
        mensaje = comedor.agregar_silla("texto")

        assert mensaje == "Silla texto agregada exitosamente al comedor"

    def test_respeta_la_capacidad_maxima_de_la_mesa(self):
        comedor = Comedor("Set", crear_mesa(capacidad=2))
        comedor.agregar_silla(crear_silla("A"))
        comedor.agregar_silla(crear_silla("B"))

        mensaje = comedor.agregar_silla(crear_silla("C"))

        assert mensaje == "No se pueden agregar más sillas. Capacidad máxima: 2"
        assert len(comedor.sillas) == 2

    def test_mesa_sin_capacidad_usa_limite_de_seis(self):
        comedor = Comedor("Set", mesa_falsa())
        for i in range(6):
            comedor.agregar_silla(crear_silla(str(i)))

        mensaje = comedor.agregar_silla(crear_silla("extra"))

        assert mensaje == "No se pueden agregar más sillas. Capacidad máxima: 6"


# ---------------------------------------------------------------- quitar
class TestQuitarSilla:
    def test_sin_sillas(self, comedor):
        assert comedor.quitar_silla() == "No hay sillas para quitar"

    def test_quita_la_ultima_por_defecto(self, comedor):
        a, b = crear_silla("A"), crear_silla("B")
        comedor.agregar_silla(a)
        comedor.agregar_silla(b)

        mensaje = comedor.quitar_silla()

        assert mensaje == "Silla B removida del comedor"
        assert comedor.sillas == [a]

    def test_quita_por_indice(self, comedor):
        a, b = crear_silla("A"), crear_silla("B")
        comedor.agregar_silla(a)
        comedor.agregar_silla(b)

        mensaje = comedor.quitar_silla(0)

        assert mensaje == "Silla A removida del comedor"
        assert comedor.sillas == [b]

    @pytest.mark.parametrize("indice", [5, -5])
    def test_indice_invalido(self, comedor, indice):
        comedor.agregar_silla(crear_silla())

        assert comedor.quitar_silla(indice) == "Índice de silla inválido"
        assert len(comedor.sillas) == 1


# ---------------------------------------------------------------- precio
class TestPrecioTotal:
    def test_solo_mesa(self, comedor):
        assert comedor.calcular_precio_total() == pytest.approx(1048.0)

    def test_mesa_y_sillas_reales(self, comedor):
        comedor.agregar_silla(crear_silla("A"))

        assert comedor.calcular_precio_total() == pytest.approx(1158.0)  # 1048 + 110

    def test_tres_sillas_no_tienen_descuento(self):
        comedor = Comedor("Set", mesa_falsa(), [silla_falsa() for _ in range(3)])

        assert comedor.calcular_precio_total() == pytest.approx(1300.0)

    def test_cuatro_sillas_tienen_cinco_por_ciento_de_descuento(self):
        comedor = Comedor("Set", mesa_falsa(), [silla_falsa() for _ in range(4)])

        assert comedor.calcular_precio_total() == pytest.approx(1330.0)  # 1400 * 0.95

    def test_cuatro_sillas_reales(self, comedor):
        for nombre in "ABCD":
            comedor.agregar_silla(crear_silla(nombre))

        assert comedor.calcular_precio_total() == pytest.approx(1413.6)  # 1488 * 0.95

    def test_delegacion_en_los_componentes(self):
        mesa = mesa_falsa()
        sillas = [silla_falsa(), silla_falsa()]
        comedor = Comedor("Set", mesa, sillas)

        comedor.calcular_precio_total()

        mesa.calcular_precio.assert_called_once_with()
        for silla in sillas:
            silla.calcular_precio.assert_called_once_with()

    def test_resultado_redondeado_a_dos_decimales(self):
        comedor = Comedor("Set", mesa_falsa(precio=100.0), [silla_falsa(precio=33.333)])

        assert comedor.calcular_precio_total() == 133.33


# ---------------------------------------------------------------- descripcion
class TestDescripcionCompleta:
    def test_sin_sillas(self):
        comedor = Comedor("Set", mesa_falsa())

        assert comedor.obtener_descripcion_completa() == (
            "=== COMEDOR SET ===\n\n"
            "MESA:\nDESC MESA\n\n"
            "SILLAS: Ninguna incluida\n"
            "\n--- PRECIO TOTAL: $1000.00 ---"
        )

    def test_con_una_silla(self):
        comedor = Comedor("Set", mesa_falsa(), [silla_falsa()])

        assert comedor.obtener_descripcion_completa() == (
            "=== COMEDOR SET ===\n\n"
            "MESA:\nDESC MESA\n\n"
            "SILLAS (1 unidades):\n1. DESC SILLA\n"
            "\n--- PRECIO TOTAL: $1100.00 ---"
        )

    def test_nombre_en_mayusculas(self):
        comedor = Comedor("mi set", mesa_falsa())

        assert comedor.obtener_descripcion_completa().startswith("=== COMEDOR MI SET ===")

    def test_con_cuatro_sillas_menciona_el_descuento(self):
        comedor = Comedor("Set", mesa_falsa(), [silla_falsa() for _ in range(4)])

        descripcion = comedor.obtener_descripcion_completa()

        assert "SILLAS (4 unidades):" in descripcion
        assert "$1330.00" in descripcion
        assert descripcion.endswith("\n(Incluye 5% de descuento por set completo)")

    def test_con_menos_de_cuatro_sillas_no_menciona_descuento(self):
        comedor = Comedor("Set", mesa_falsa(), [silla_falsa() for _ in range(3)])

        assert "descuento" not in comedor.obtener_descripcion_completa()

    def test_numera_las_sillas(self):
        sillas = [silla_falsa(descripcion="PRIMERA"), silla_falsa(descripcion="SEGUNDA")]
        comedor = Comedor("Set", mesa_falsa(), sillas)

        descripcion = comedor.obtener_descripcion_completa()

        assert "1. PRIMERA\n" in descripcion
        assert "2. SEGUNDA\n" in descripcion


# ---------------------------------------------------------------- resumen
class TestResumen:
    def test_resumen_completo(self):
        sillas = [
            silla_falsa(precio=100.0, material="Metal", tapizado="Tela"),
            silla_falsa(precio=150.0, material="Metal", tapizado=None),
        ]
        comedor = Comedor("Set", mesa_falsa(), sillas)

        resumen = comedor.obtener_resumen()
        materiales = resumen.pop("materiales_utilizados")

        assert resumen == {
            "nombre": "Set",
            "total_muebles": 3,
            "precio_mesa": 1000.0,
            "precio_sillas": 250.0,
            "precio_total": 1250.0,
            "capacidad_personas": 2,
        }
        assert sorted(materiales) == ["Madera", "Metal", "Tela"]

    def test_resumen_sin_sillas(self):
        resumen = Comedor("Set", mesa_falsa()).obtener_resumen()

        assert resumen["total_muebles"] == 1
        assert resumen["precio_sillas"] == 0
        assert resumen["capacidad_personas"] == 0
        assert resumen["materiales_utilizados"] == ["Madera"]

    def test_materiales_sin_duplicados(self):
        sillas = [silla_falsa(material="Madera"), silla_falsa(material="Madera")]
        comedor = Comedor("Set", mesa_falsa(material="Madera"), sillas)

        assert comedor.obtener_resumen()["materiales_utilizados"] == ["Madera"]

    def test_mesa_sin_atributo_material_se_ignora(self):
        mesa = Mock(spec=["calcular_precio"])
        mesa.calcular_precio.return_value = 500.0
        comedor = Comedor("Set", mesa, [silla_falsa(material="Metal")])

        assert comedor._obtener_materiales_unicos() == ["Metal"]


# ---------------------------------------------------------------- capacidad
class TestCapacidadMaxima:
    @pytest.mark.parametrize("capacidad", [2, 4, 8])
    def test_usa_la_capacidad_de_la_mesa(self, capacidad):
        comedor = Comedor("Set", crear_mesa(capacidad=capacidad))

        assert comedor._calcular_capacidad_maxima() == capacidad

    def test_valor_por_defecto_si_la_mesa_no_tiene_capacidad(self):
        assert Comedor("Set", mesa_falsa())._calcular_capacidad_maxima() == 6


# ---------------------------------------------------------------- dunder
class TestRepresentaciones:
    def test_str(self, comedor):
        comedor.agregar_silla(crear_silla("A"))
        comedor.agregar_silla(crear_silla("B"))

        assert str(comedor) == "Comedor Set: Mesa + 2 sillas"

    def test_len_cuenta_mesa_y_sillas(self, comedor):
        assert len(comedor) == 1

        comedor.agregar_silla(crear_silla())

        assert len(comedor) == 2