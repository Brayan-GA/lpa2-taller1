"""Pruebas unitarias de la clase concreta Sofa."""

import pytest

from models.categorias.asientos import Asiento
from models.concretos.sofa import Sofa
from models.mueble import Mueble


@pytest.fixture
def sofa():
    """Sofá con todos los valores por defecto."""
    return Sofa("Sofá", "Tela", "Gris", 1000.0)


class TestSofaHerencia:
    def test_es_clase_concreta(self):
        assert len(Sofa.__abstractmethods__) == 0

    def test_hereda_de_asiento_y_mueble(self, sofa):
        assert issubclass(Sofa, Asiento)
        assert issubclass(Sofa, Mueble)
        assert isinstance(sofa, Asiento)

    def test_str_heredado(self, sofa):
        assert str(sofa) == "Sofá de Tela en color Gris"

    def test_validacion_de_capacidad_heredada(self, sofa):
        with pytest.raises(ValueError, match="mayor a 0"):
            sofa.capacidad_personas = 0


class TestSofaConstructor:
    def test_valores_por_defecto(self, sofa):
        assert sofa.nombre == "Sofá"
        assert sofa.material == "Tela"
        assert sofa.color == "Gris"
        assert sofa.precio_base == 1000.0
        assert sofa.capacidad_personas == 3
        assert sofa.tiene_respaldo is True
        assert sofa.material_tapizado is None
        assert sofa.tiene_brazos is True
        assert sofa.es_modular is False
        assert sofa.incluye_cojines is False

    def test_valores_personalizados(self):
        sofa = Sofa("Sofá", "Cuero", "Negro", 1000.0, 4, False, "cuero", False, True, True)

        assert sofa.capacidad_personas == 4
        assert sofa.tiene_respaldo is False
        assert sofa.material_tapizado == "cuero"
        assert sofa.tiene_brazos is False
        assert sofa.es_modular is True
        assert sofa.incluye_cojines is True

    @pytest.mark.parametrize("atributo", ["tiene_brazos", "es_modular", "incluye_cojines"])
    def test_propiedades_propias_son_de_solo_lectura(self, sofa, atributo):
        with pytest.raises(AttributeError):
            setattr(sofa, atributo, True)


class TestSofaPrecio:
    @pytest.mark.parametrize(
        "kwargs,esperado",
        [
            ({}, 1350.0),                                  # 1000*1.2 + 150 de brazos
            ({"tiene_brazos": False}, 1200.0),
            ({"es_modular": True}, 1550.0),                # +200
            ({"incluye_cojines": True}, 1400.0),           # +50
            (
                {"es_modular": True, "incluye_cojines": True},
                1600.0,                                    # todos los extras
            ),
            ({"material_tapizado": "cuero"}, 1550.0),      # factor 1.4 + 150
            ({"material_tapizado": "tela"}, 1450.0),       # factor 1.3 + 150
            ({"tiene_respaldo": False, "tiene_brazos": False}, 1100.0),
            (
                {"capacidad_personas": 1, "tiene_respaldo": False, "tiene_brazos": False},
                1000.0,                                    # factor neutro
            ),
        ],
    )
    def test_calcular_precio(self, kwargs, esperado):
        sofa = Sofa("Sofá", "Tela", "Gris", 1000.0, **kwargs)

        assert sofa.calcular_precio() == pytest.approx(esperado)

    def test_precio_redondeado_a_dos_decimales(self):
        sofa = Sofa("Sofá", "Tela", "Gris", 33.333, tiene_brazos=False)

        # 33.333 * 1.2 = 39.9996, redondeado a 2 decimales
        assert sofa.calcular_precio() == pytest.approx(40.0)


class TestSofaDescripcion:
    def test_descripcion_con_valores_por_defecto(self, sofa):
        esperado = (
            "Sofá: Sofá\n"
            "  Material: Tela\n"
            "  Color: Gris\n"
            "  Capacidad: 3 personas, Respaldo: Sí\n"
            "  Brazos: Sí\n"
            "  Modular: No\n"
            "  Incluye cojines: No\n"
            "  Precio final: $1350.0"
        )

        assert sofa.obtener_descripcion() == esperado

    def test_descripcion_con_todas_las_caracteristicas(self):
        sofa = Sofa(
            "Sofá Modular", "Cuero", "Negro", 1000.0, 4, True, "cuero", False, True, True
        )

        esperado = (
            "Sofá: Sofá Modular\n"
            "  Material: Cuero\n"
            "  Color: Negro\n"
            "  Capacidad: 4 personas, Respaldo: Sí, Tapizado: cuero\n"
            "  Brazos: No\n"
            "  Modular: Sí\n"
            "  Incluye cojines: Sí\n"
            "  Precio final: $1700.0"
        )

        assert sofa.obtener_descripcion() == esperado