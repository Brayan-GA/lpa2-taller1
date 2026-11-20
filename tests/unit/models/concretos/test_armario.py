"""Pruebas unitarias de la clase concreta Armario."""

import pytest

from models.concretos.armario import Armario
from models.mueble import Mueble


@pytest.fixture
def armario():
    """Armario con todos los valores por defecto."""
    return Armario("Armario", "Madera", "Blanco", 1000)


class TestArmarioHerencia:
    @pytest.mark.xfail(
        reason="armario.py tiene comentado el import de Mueble y no hereda de él"
    )
    def test_hereda_de_mueble(self):
        assert issubclass(Armario, Mueble)


class TestArmarioConstructor:
    def test_valores_por_defecto(self, armario):
        assert armario.nombre == "Armario"
        assert armario.material == "Madera"
        assert armario.color == "Blanco"
        assert armario.precio_base == 1000
        assert armario.num_puertas == 2
        assert armario.num_cajones == 0
        assert armario.tiene_espejos is False

    def test_valores_personalizados(self):
        armario = Armario("Ropero", "Pino", "Café", 800, 4, 3, True)

        assert armario.num_puertas == 4
        assert armario.num_cajones == 3
        assert armario.tiene_espejos is True

    def test_precio_base_decimal_se_convierte_a_entero(self):
        assert Armario("A", "M", "C", 999.9).precio_base == 999

    def test_precio_base_none_se_convierte_a_cero(self):
        assert Armario("A", "M", "C", None).precio_base == 0

    def test_atributos_son_modificables(self, armario):
        armario.num_puertas = 6
        assert armario.num_puertas == 6


class TestArmarioPrecio:
    @pytest.mark.parametrize(
        "kwargs,esperado",
        [
            ({}, 1100),                                        # 2 puertas por defecto: +100
            ({"num_puertas": 0}, 1000),                        # sin extras
            ({"num_puertas": 4}, 1200),                        # +50 por puerta
            ({"num_cajones": 3}, 1190),                        # +30 por cajón
            ({"tiene_espejos": True}, 1200),                   # +100
            (
                {"num_puertas": 3, "num_cajones": 2, "tiene_espejos": True},
                1310,                                          # 150 + 60 + 100
            ),
        ],
    )
    def test_calcular_precio(self, kwargs, esperado):
        armario = Armario("Armario", "Madera", "Blanco", 1000, **kwargs)

        assert armario.calcular_precio() == esperado

    def test_calcular_precio_devuelve_entero(self, armario):
        assert isinstance(armario.calcular_precio(), int)


class TestArmarioDescripcion:
    def test_descripcion_con_valores_por_defecto(self):
        armario = Armario("Armario", "Madera", "Blanco", 1000)

        assert armario.obtener_descripcion() == (
            "Armario 'Armario': Material=Madera, Color=Blanco, Puertas=2, "
            "Cajones=0, Espejos=No, Precio base=$1000"
        )

    def test_descripcion_con_espejos_y_cajones(self):
        armario = Armario("Ropero", "Pino", "Café", 800, 4, 3, True)

        assert armario.obtener_descripcion() == (
            "Armario 'Ropero': Material=Pino, Color=Café, Puertas=4, "
            "Cajones=3, Espejos=Sí, Precio base=$800"
        )