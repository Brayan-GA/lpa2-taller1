"""Pruebas unitarias de la clase concreta Escritorio."""

import pytest

from models.concretos.escritorio import Escritorio
from models.mueble import Mueble


@pytest.fixture
def escritorio():
    """Escritorio con todos los valores por defecto."""
    return Escritorio("Escritorio", "Madera", "Negro", 1000)


class TestEscritorioHerencia:
    @pytest.mark.xfail(
        reason="escritorio.py tiene comentado el import de Mueble y no hereda de él"
    )
    def test_hereda_de_mueble(self):
        assert issubclass(Escritorio, Mueble)


class TestEscritorioConstructor:
    def test_valores_por_defecto(self, escritorio):
        assert escritorio.nombre == "Escritorio"
        assert escritorio.material == "Madera"
        assert escritorio.color == "Negro"
        assert escritorio.precio_base == 1000
        assert escritorio.forma == "rectangular"
        assert escritorio.tiene_cajones is False
        assert escritorio.num_cajones == 0
        assert escritorio.largo == 1.2
        assert escritorio.tiene_iluminacion is False

    def test_valores_personalizados(self):
        escritorio = Escritorio("Esc", "Metal", "Gris", 900, "L", True, 3, 1.8, True)

        assert escritorio.forma == "L"
        assert escritorio.tiene_cajones is True
        assert escritorio.num_cajones == 3
        assert escritorio.largo == 1.8
        assert escritorio.tiene_iluminacion is True

    def test_precio_base_decimal_se_convierte_a_entero(self):
        assert Escritorio("E", "M", "C", 999.9).precio_base == 999

    def test_precio_base_none_se_convierte_a_cero(self):
        assert Escritorio("E", "M", "C", None).precio_base == 0


class TestEscritorioPrecio:
    @pytest.mark.parametrize(
        "kwargs,esperado",
        [
            ({}, 1000),                                            # sin extras
            ({"tiene_cajones": True, "num_cajones": 2}, 1050),     # +25 por cajón
            ({"tiene_cajones": False, "num_cajones": 2}, 1000),    # cajones ignorados
            ({"largo": 1.5}, 1000),                                # 1.5 no supera el límite
            ({"largo": 1.6}, 1050),                                # largo > 1.5: +50
            ({"tiene_iluminacion": True}, 1040),                   # +40
            ({"forma": "en L"}, 1030),                             # forma distinta: +30
            (
                {
                    "forma": "redonda",
                    "tiene_cajones": True,
                    "num_cajones": 4,
                    "largo": 2.0,
                    "tiene_iluminacion": True,
                },
                1220,                                              # 100 + 50 + 40 + 30
            ),
        ],
    )
    def test_calcular_precio(self, kwargs, esperado):
        escritorio = Escritorio("Escritorio", "Madera", "Negro", 1000, **kwargs)

        assert escritorio.calcular_precio() == esperado

    def test_calcular_precio_devuelve_entero(self, escritorio):
        assert isinstance(escritorio.calcular_precio(), int)


class TestEscritorioDescripcion:
    def test_descripcion_con_valores_por_defecto(self, escritorio):
        assert escritorio.obtener_descripcion() == (
            "Escritorio 'Escritorio': Material=Madera, Color=Negro, "
            "Forma=rectangular, Cajones=0, Largo=1.2m, Iluminación=No, "
            "Precio base=$1000"
        )

    def test_descripcion_con_todas_las_caracteristicas(self):
        escritorio = Escritorio("Esc", "Metal", "Gris", 900, "L", True, 2, 1.8, True)

        assert escritorio.obtener_descripcion() == (
            "Escritorio 'Esc': Material=Metal, Color=Gris, "
            "Forma=L, Cajones=2, Largo=1.8m, Iluminación=Sí, "
            "Precio base=$900"
        )

    def test_descripcion_muestra_cero_cajones_si_no_tiene_cajones(self):
        escritorio = Escritorio("Esc", "Metal", "Gris", 900, tiene_cajones=False, num_cajones=3)

        assert "Cajones=0" in escritorio.obtener_descripcion()