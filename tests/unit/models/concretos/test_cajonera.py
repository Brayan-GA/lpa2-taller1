"""Pruebas unitarias de la clase concreta Cajonera."""

import pytest

from models.concretos.cajonera import Cajonera
from models.mueble import Mueble


@pytest.fixture
def cajonera():
    """Cajonera con todos los valores por defecto."""
    return Cajonera("Cajonera", "Madera", "Blanco", 500)


class TestCajoneraHerencia:
    @pytest.mark.xfail(
        reason="cajonera.py tiene comentado el import de Mueble y no hereda de él"
    )
    def test_hereda_de_mueble(self):
        assert issubclass(Cajonera, Mueble)


class TestCajoneraConstructor:
    def test_valores_por_defecto(self, cajonera):
        assert cajonera.nombre == "Cajonera"
        assert cajonera.material == "Madera"
        assert cajonera.color == "Blanco"
        assert cajonera.precio_base == 500
        assert cajonera.num_cajones == 3
        assert cajonera.tiene_ruedas is False

    def test_valores_personalizados(self):
        cajonera = Cajonera("Mini", "Plástico", "Azul", 200, 5, True)

        assert cajonera.num_cajones == 5
        assert cajonera.tiene_ruedas is True

    def test_precio_base_decimal_se_convierte_a_entero(self):
        assert Cajonera("C", "M", "C", 99.9).precio_base == 99

    def test_precio_base_none_se_convierte_a_cero(self):
        assert Cajonera("C", "M", "C", None).precio_base == 0


class TestCajoneraPrecio:
    @pytest.mark.parametrize(
        "kwargs,esperado",
        [
            ({}, 560),                                   # 3 cajones por defecto: +60
            ({"num_cajones": 0}, 500),                   # sin extras
            ({"num_cajones": 5}, 600),                   # +20 por cajón
            ({"tiene_ruedas": True}, 590),               # +30
            ({"num_cajones": 4, "tiene_ruedas": True}, 610),
        ],
    )
    def test_calcular_precio(self, kwargs, esperado):
        cajonera = Cajonera("Cajonera", "Madera", "Blanco", 500, **kwargs)

        assert cajonera.calcular_precio() == esperado

    def test_calcular_precio_devuelve_entero(self, cajonera):
        assert isinstance(cajonera.calcular_precio(), int)


class TestCajoneraDescripcion:
    def test_descripcion_con_valores_por_defecto(self, cajonera):
        assert cajonera.obtener_descripcion() == (
            "Cajonera 'Cajonera': Material=Madera, Color=Blanco, "
            "Cajones=3, Ruedas=No, Precio base=$500"
        )

    def test_descripcion_con_ruedas(self):
        cajonera = Cajonera("Mini", "Plástico", "Azul", 200, 5, True)

        assert cajonera.obtener_descripcion() == (
            "Cajonera 'Mini': Material=Plástico, Color=Azul, "
            "Cajones=5, Ruedas=Sí, Precio base=$200"
        )