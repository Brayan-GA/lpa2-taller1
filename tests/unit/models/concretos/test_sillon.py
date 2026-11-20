"""Pruebas unitarias de la clase concreta Sillon."""

import pytest

from models.categorias.asientos import Asiento
from models.concretos.sillon import Sillon


@pytest.fixture
def sillon():
    """Sillón con todos los valores por defecto."""
    return Sillon("Sillón", "Madera", "Gris", 1000)


class TestSillonHerencia:
    @pytest.mark.xfail(
        reason="sillon.py tiene comentado el import de Asiento y no hereda de él"
    )
    def test_hereda_de_asiento(self):
        assert issubclass(Sillon, Asiento)


class TestSillonConstructor:
    def test_valores_por_defecto(self, sillon):
        assert sillon.nombre == "Sillón"
        assert sillon.material == "Madera"
        assert sillon.color == "Gris"
        assert sillon.precio_base == 1000
        assert sillon.capacidad_personas == 2
        assert sillon.tiene_respaldo is True
        assert sillon.material_tapizado is None
        assert sillon.tiene_brazos is True
        assert sillon.es_reclinable is False
        assert sillon.tiene_reposapiés is False

    def test_valores_personalizados(self):
        sillon = Sillon(
            "Relax", "Cuero", "Negro", 800, 1, False, "tela", False, True, True
        )

        assert sillon.capacidad_personas == 1
        assert sillon.tiene_respaldo is False
        assert sillon.material_tapizado == "tela"
        assert sillon.tiene_brazos is False
        assert sillon.es_reclinable is True
        assert sillon.tiene_reposapiés is True

    def test_precio_base_decimal_se_convierte_a_entero(self):
        assert Sillon("S", "M", "C", 999.9).precio_base == 999

    def test_precio_base_none_se_convierte_a_cero(self):
        assert Sillon("S", "M", "C", None).precio_base == 0

    def test_atributos_son_modificables(self, sillon):
        sillon.es_reclinable = True
        sillon.nombre = "Otro"

        assert sillon.es_reclinable is True
        assert sillon.nombre == "Otro"


class TestSillonPrecio:
    @pytest.mark.parametrize(
        "kwargs,esperado",
        [
            ({}, 1100),                                   # brazos por defecto: +100
            ({"tiene_brazos": False}, 1000),              # sin extras
            ({"material_tapizado": "cuero"}, 1300),       # +200 +100
            ({"es_reclinable": True}, 1350),              # +250 +100
            ({"tiene_reposapiés": True}, 1180),           # +80 +100
            (
                {
                    "material_tapizado": "tela",
                    "es_reclinable": True,
                    "tiene_reposapiés": True,
                },
                1630,                                     # todos los extras
            ),
            (
                {"tiene_brazos": False, "es_reclinable": True, "tiene_reposapiés": True},
                1330,
            ),
        ],
    )
    def test_calcular_precio(self, kwargs, esperado):
        sillon = Sillon("Sillón", "Madera", "Gris", 1000, **kwargs)

        assert sillon.calcular_precio() == esperado

    def test_calcular_precio_devuelve_entero(self, sillon):
        assert isinstance(sillon.calcular_precio(), int)


class TestSillonDescripcion:
    def test_descripcion_con_valores_por_defecto(self):
        sillon = Sillon("Sillón", "Madera", "Gris", 500)

        assert sillon.obtener_descripcion() == (
            "Sillón 'Sillón': Material=Madera, Color=Gris, Capacidad=2 personas, "
            "Tapizado=N/A, Brazos=Sí, Reclinable=No, Reposapiés=No, Precio base=$500"
        )

    def test_descripcion_con_todas_las_caracteristicas(self):
        sillon = Sillon(
            "Relax", "Cuero", "Negro", 1000, 1, True, "tela", False, True, True
        )

        assert sillon.obtener_descripcion() == (
            "Sillón 'Relax': Material=Cuero, Color=Negro, Capacidad=1 personas, "
            "Tapizado=tela, Brazos=No, Reclinable=Sí, Reposapiés=Sí, Precio base=$1000"
        )