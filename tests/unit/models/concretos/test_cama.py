"""Pruebas unitarias de la clase concreta Cama."""

import pytest

from models.categorias.asientos import Asiento
from models.concretos.cama import Cama
from models.mueble import Mueble


@pytest.fixture
def cama():
    """Cama con todos los valores por defecto."""
    return Cama("Cama", "Madera", "Café", 1000.0)


class TestCamaHerencia:
    def test_es_clase_concreta(self):
        assert len(Cama.__abstractmethods__) == 0

    def test_hereda_de_mueble_y_no_de_asiento(self, cama):
        assert issubclass(Cama, Mueble)
        assert not issubclass(Cama, Asiento)

    def test_str_heredado(self, cama):
        assert str(cama) == "Cama de Madera en color Café"

    def test_validaciones_heredadas_de_mueble(self, cama):
        with pytest.raises(ValueError):
            cama.nombre = ""


class TestCamaConstructor:
    def test_valores_por_defecto(self, cama):
        assert cama.nombre == "Cama"
        assert cama.material == "Madera"
        assert cama.color == "Café"
        assert cama.precio_base == 1000.0
        assert cama.tamaño == "individual"
        assert cama.incluye_colchon is False
        assert cama.tiene_cabecera is False

    def test_valores_personalizados(self):
        cama = Cama("Cama", "Metal", "Negro", 500.0, "king", True, True)

        assert cama.tamaño == "king"
        assert cama.incluye_colchon is True
        assert cama.tiene_cabecera is True

    @pytest.mark.parametrize("atributo", ["incluye_colchon", "tiene_cabecera"])
    def test_propiedades_de_extras_son_de_solo_lectura(self, cama, atributo):
        with pytest.raises(AttributeError):
            setattr(cama, atributo, True)


class TestCamaTamaño:
    @pytest.mark.parametrize("tamaño", ["individual", "matrimonial", "queen", "king"])
    def test_setter_acepta_tamaños_validos(self, cama, tamaño):
        cama.tamaño = tamaño
        assert cama.tamaño == tamaño

    @pytest.mark.parametrize("tamaño", ["", "gigante", "KING", "Individual"])
    def test_setter_rechaza_tamaños_invalidos(self, cama, tamaño):
        with pytest.raises(ValueError, match="Tamaño debe ser uno de"):
            cama.tamaño = tamaño

        assert cama.tamaño == "individual"


class TestCamaPrecio:
    @pytest.mark.parametrize(
        "kwargs,esperado",
        [
            ({}, 1000.0),
            ({"tamaño": "matrimonial"}, 1200.0),          # +200
            ({"tamaño": "queen"}, 1400.0),                # +400
            ({"tamaño": "king"}, 1600.0),                 # +600
            ({"incluye_colchon": True}, 1300.0),          # +300
            ({"tiene_cabecera": True}, 1100.0),           # +100
            ({"tamaño": "matrimonial", "incluye_colchon": True}, 1500.0),
            (
                {"tamaño": "king", "incluye_colchon": True, "tiene_cabecera": True},
                2000.0,                                   # todos los extras
            ),
        ],
    )
    def test_calcular_precio(self, kwargs, esperado):
        cama = Cama("Cama", "Madera", "Café", 1000.0, **kwargs)

        assert cama.calcular_precio() == pytest.approx(esperado)

    def test_precio_redondeado_a_dos_decimales(self):
        cama = Cama("Cama", "Madera", "Café", 33.333)

        assert cama.calcular_precio() == pytest.approx(33.33)


class TestCamaDescripcion:
    def test_descripcion_con_valores_por_defecto(self, cama):
        esperado = (
            "Cama: Cama\n"
            "  Material: Madera\n"
            "  Color: Café\n"
            "  Tamaño: individual\n"
            "  Incluye colchón: No\n"
            "  Cabecera: No\n"
            "  Precio final: $1000.0"
        )

        assert cama.obtener_descripcion() == esperado

    def test_descripcion_con_todas_las_caracteristicas(self):
        cama = Cama("Cama Doble", "Madera", "Blanco", 1000.0, "king", True, True)

        esperado = (
            "Cama: Cama Doble\n"
            "  Material: Madera\n"
            "  Color: Blanco\n"
            "  Tamaño: king\n"
            "  Incluye colchón: Sí\n"
            "  Cabecera: Sí\n"
            "  Precio final: $2000.0"
        )

        assert cama.obtener_descripcion() == esperado