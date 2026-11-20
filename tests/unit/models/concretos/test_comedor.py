"""Pruebas unitarias de Comedor (versión simple de models/concretos)."""

from unittest.mock import Mock

import pytest

from models.concretos.comedor import Comedor
from models.concretos.mesa import Mesa
from models.concretos.silla import Silla


def crear_mesa():
    """Mesa real: precio final 1048.0."""
    return Mesa("Mesa", "Madera", "Café", 1000.0)


def crear_silla(nombre="A"):
    """Silla real: precio final 110.0."""
    return Silla(nombre, "Madera", "Café", 100.0)


@pytest.fixture
def comedor():
    return Comedor(crear_mesa())


class TestComedorConstructor:
    def test_sin_sillas_por_defecto(self, comedor):
        assert comedor.sillas == []
        assert comedor.cantidad_sillas() == 0

    def test_conserva_mesa_y_sillas(self):
        mesa = crear_mesa()
        sillas = [crear_silla("A"), crear_silla("B")]

        comedor = Comedor(mesa, sillas)

        assert comedor.mesa is mesa
        assert comedor.sillas == sillas
        assert comedor.cantidad_sillas() == 2

    def test_dos_comedores_no_comparten_lista_de_sillas(self):
        c1 = Comedor(crear_mesa())
        c2 = Comedor(crear_mesa())

        c1.agregar_silla(crear_silla())

        assert c2.sillas == []


class TestAgregarYQuitar:
    def test_agregar_silla(self, comedor):
        silla = crear_silla()

        resultado = comedor.agregar_silla(silla)

        assert resultado is None
        assert comedor.sillas == [silla]
        assert comedor.cantidad_sillas() == 1

    def test_agregar_no_tiene_limite(self, comedor):
        for _ in range(10):
            comedor.agregar_silla(crear_silla())

        assert comedor.cantidad_sillas() == 10

    def test_quitar_silla_existente(self, comedor):
        a, b = crear_silla("A"), crear_silla("B")
        comedor.agregar_silla(a)
        comedor.agregar_silla(b)

        comedor.quitar_silla(a)

        assert comedor.sillas == [b]

    def test_quitar_silla_inexistente_no_hace_nada(self, comedor):
        comedor.agregar_silla(crear_silla("A"))

        comedor.quitar_silla(crear_silla("B"))

        assert comedor.cantidad_sillas() == 1

    def test_quitar_en_comedor_vacio_no_falla(self, comedor):
        comedor.quitar_silla(crear_silla())

        assert comedor.cantidad_sillas() == 0

    def test_quitar_solo_elimina_una_aparicion(self, comedor):
        silla = crear_silla()
        comedor.agregar_silla(silla)
        comedor.agregar_silla(silla)

        comedor.quitar_silla(silla)

        assert comedor.cantidad_sillas() == 1


class TestPrecioTotal:
    def test_solo_mesa(self, comedor):
        assert comedor.calcular_precio_total() == pytest.approx(1048.0)

    def test_suma_mesa_y_sillas(self, comedor):
        comedor.agregar_silla(crear_silla("A"))
        comedor.agregar_silla(crear_silla("B"))

        assert comedor.calcular_precio_total() == pytest.approx(1268.0)  # 1048 + 2*110

    def test_no_aplica_descuento_con_cuatro_sillas(self, comedor):
        for nombre in "ABCD":
            comedor.agregar_silla(crear_silla(nombre))

        assert comedor.calcular_precio_total() == pytest.approx(1488.0)

    def test_delegacion_en_los_componentes(self):
        mesa = Mock()
        mesa.calcular_precio.return_value = 1000.0
        sillas = [Mock(), Mock()]
        for silla in sillas:
            silla.calcular_precio.return_value = 100.0

        total = Comedor(mesa, sillas).calcular_precio_total()

        assert total == 1200.0
        mesa.calcular_precio.assert_called_once_with()
        for silla in sillas:
            silla.calcular_precio.assert_called_once_with()


class TestDescripcion:
    def test_sin_sillas(self):
        mesa = Mock()
        mesa.obtener_descripcion.return_value = "DESC MESA"

        assert Comedor(mesa).descripcion() == "Comedor con mesa: DESC MESA\ny 0 sillas:\n"

    def test_con_sillas_numeradas(self):
        mesa = Mock()
        mesa.obtener_descripcion.return_value = "DESC MESA"
        s1, s2 = Mock(), Mock()
        s1.obtener_descripcion.return_value = "DESC 1"
        s2.obtener_descripcion.return_value = "DESC 2"

        assert Comedor(mesa, [s1, s2]).descripcion() == (
            "Comedor con mesa: DESC MESA\n"
            "y 2 sillas:\n"
            "  1. DESC 1\n"
            "  2. DESC 2\n"
        )

    def test_con_objetos_reales(self, comedor):
        comedor.agregar_silla(crear_silla("A"))

        descripcion = comedor.descripcion()

        assert descripcion.startswith("Comedor con mesa: Mesa: Mesa\n")
        assert "y 1 sillas:" in descripcion
        assert "  1. Silla: A" in descripcion