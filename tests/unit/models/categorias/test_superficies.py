"""Pruebas unitarias de la clase abstracta Superficie."""

import pytest

from models.categorias.superficies import Superficie
from models.mueble import Mueble


class SuperficieConcreta(Superficie):
    """Subclase mínima, solo para poder instanciar y probar Superficie."""

    def calcular_precio(self) -> float:
        return self.precio_base

    def obtener_descripcion(self) -> str:
        return self.nombre


def crear(largo=120, ancho=80, altura=75):
    return SuperficieConcreta("Mesa", "Madera", "Café", 100.0, largo, ancho, altura)


@pytest.fixture
def superficie():
    return crear()


class TestSuperficieAbstracta:
    def test_no_se_puede_instanciar(self):
        with pytest.raises(TypeError):
            Superficie("Mesa", "Madera", "Café", 100.0, 120, 80, 75)

    def test_metodos_abstractos_declarados(self):
        assert Superficie.__abstractmethods__ == {
            "calcular_precio",
            "obtener_descripcion",
        }

    def test_subclase_incompleta_no_se_puede_instanciar(self):
        class SoloPrecio(Superficie):
            def calcular_precio(self) -> float:
                return 0.0

        with pytest.raises(TypeError):
            SoloPrecio("Mesa", "Madera", "Café", 100.0, 120, 80, 75)


class TestSuperficieHerencia:
    def test_hereda_de_mueble(self, superficie):
        assert issubclass(Superficie, Mueble)
        assert isinstance(superficie, Mueble)

    def test_atributos_y_str_heredados(self, superficie):
        assert superficie.nombre == "Mesa"
        assert superficie.precio_base == 100.0
        assert str(superficie) == "Mesa de Madera en color Café"


class TestSuperficieDimensiones:
    def test_constructor_asigna_dimensiones(self, superficie):
        assert superficie.largo == 120
        assert superficie.ancho == 80
        assert superficie.altura == 75

    @pytest.mark.parametrize("atributo", ["largo", "ancho", "altura"])
    def test_setters_aceptan_valores_positivos(self, superficie, atributo):
        setattr(superficie, atributo, 50.5)
        assert getattr(superficie, atributo) == 50.5

    @pytest.mark.parametrize(
        "atributo,mensaje",
        [
            ("largo", "El largo debe ser mayor a 0"),
            ("ancho", "El ancho debe ser mayor a 0"),
            ("altura", "La altura debe ser mayor a 0"),
        ],
    )
    @pytest.mark.parametrize("valor", [0, -1, -50.5])
    def test_setters_rechazan_cero_y_negativos(self, superficie, atributo, mensaje, valor):
        original = getattr(superficie, atributo)

        with pytest.raises(ValueError, match=mensaje):
            setattr(superficie, atributo, valor)

        assert getattr(superficie, atributo) == original


class TestSuperficieArea:
    @pytest.mark.parametrize(
        "largo,ancho,esperado",
        [(120, 80, 9600), (100, 100, 10000), (50.5, 2, 101.0), (1, 1, 1)],
    )
    def test_calcular_area(self, largo, ancho, esperado):
        assert crear(largo, ancho).calcular_area() == pytest.approx(esperado)

    def test_el_area_no_depende_de_la_altura(self):
        assert crear(120, 80, 10).calcular_area() == crear(120, 80, 200).calcular_area()


class TestFactorTamaño:
    @pytest.mark.parametrize(
        "largo,ancho,esperado",
        [
            (120, 80, 1.048),      # 9600 cm²
            (100, 100, 1.05),      # 10000 cm²: +5%
            (200, 100, 1.10),      # 20000 cm²: +10%
            (1, 1, 1.000005),      # casi neutro
        ],
    )
    def test_calcular_factor_tamaño(self, largo, ancho, esperado):
        assert crear(largo, ancho).calcular_factor_tamaño() == pytest.approx(esperado)

    def test_factor_siempre_mayor_a_uno(self):
        assert crear(10, 10).calcular_factor_tamaño() > 1.0


class TestInfoSuperficie:
    def test_info(self, superficie):
        assert superficie.obtener_info_superficie() == (
            "Dimensiones: 120x80x75cm (Área: 9600cm²)"
        )

    def test_info_refleja_cambios(self, superficie):
        superficie.largo = 100
        superficie.ancho = 50

        assert superficie.obtener_info_superficie() == (
            "Dimensiones: 100x50x75cm (Área: 5000cm²)"
        )