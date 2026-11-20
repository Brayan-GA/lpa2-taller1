"""Pruebas unitarias de la clase abstracta Almacenamiento."""

import pytest

from models.categorias.almacenamiento import Almacenamiento
from models.mueble import Mueble


class AlmacenamientoConcreto(Almacenamiento):
    """Subclase mínima, solo para poder instanciar y probar Almacenamiento."""

    def calcular_precio(self) -> float:
        return self.precio_base

    def obtener_descripcion(self) -> str:
        return self.nombre


def crear(compartimentos=3, litros=200.0):
    return AlmacenamientoConcreto("Armario", "Madera", "Blanco", 100.0, compartimentos, litros)


@pytest.fixture
def almacen():
    return crear()


class TestAlmacenamientoAbstracto:
    def test_no_se_puede_instanciar(self):
        with pytest.raises(TypeError):
            Almacenamiento("Armario", "Madera", "Blanco", 100.0, 3, 200.0)

    def test_metodos_abstractos_declarados(self):
        assert Almacenamiento.__abstractmethods__ == {
            "calcular_precio",
            "obtener_descripcion",
        }

    def test_subclase_incompleta_no_se_puede_instanciar(self):
        class SoloPrecio(Almacenamiento):
            def calcular_precio(self) -> float:
                return 0.0

        with pytest.raises(TypeError):
            SoloPrecio("Armario", "Madera", "Blanco", 100.0, 3, 200.0)


class TestAlmacenamientoHerencia:
    def test_hereda_de_mueble(self, almacen):
        assert issubclass(Almacenamiento, Mueble)
        assert isinstance(almacen, Mueble)

    def test_atributos_y_str_heredados(self, almacen):
        assert almacen.nombre == "Armario"
        assert almacen.precio_base == 100.0
        assert str(almacen) == "Armario de Madera en color Blanco"

    def test_validaciones_heredadas_de_mueble(self, almacen):
        with pytest.raises(ValueError):
            almacen.nombre = ""


class TestAlmacenamientoAtributos:
    def test_constructor_asigna_atributos_propios(self, almacen):
        assert almacen.num_compartimentos == 3
        assert almacen.capacidad_litros == 200.0

    @pytest.mark.parametrize("valor", [1, 5, 20])
    def test_compartimentos_acepta_positivos(self, almacen, valor):
        almacen.num_compartimentos = valor
        assert almacen.num_compartimentos == valor

    @pytest.mark.parametrize("valor", [0, -1, -10])
    def test_compartimentos_rechaza_cero_y_negativos(self, almacen, valor):
        with pytest.raises(ValueError, match="mayor a 0"):
            almacen.num_compartimentos = valor

        assert almacen.num_compartimentos == 3

    @pytest.mark.parametrize("valor", [0.5, 100.0, 500])
    def test_capacidad_acepta_positivos(self, almacen, valor):
        almacen.capacidad_litros = valor
        assert almacen.capacidad_litros == valor

    @pytest.mark.parametrize("valor", [0, -0.1, -100.0])
    def test_capacidad_rechaza_cero_y_negativos(self, almacen, valor):
        with pytest.raises(ValueError, match="mayor a 0"):
            almacen.capacidad_litros = valor

        assert almacen.capacidad_litros == 200.0


class TestFactorAlmacenamiento:
    @pytest.mark.parametrize(
        "compartimentos,litros,esperado",
        [
            (1, 0.0, 1.0),       # sin extras (el constructor no valida)
            (1, 100.0, 1.02),    # solo capacidad
            (3, 200.0, 1.14),    # 1 + 0.10 + 0.04
            (5, 50.0, 1.21),     # 1 + 0.20 + 0.01
            (11, 500.0, 1.6),    # 1 + 0.50 + 0.10
        ],
    )
    def test_calcular_factor_almacenamiento(self, compartimentos, litros, esperado):
        almacen = crear(compartimentos, litros)

        assert almacen.calcular_factor_almacenamiento() == pytest.approx(esperado)


class TestInfoAlmacenamiento:
    def test_info(self, almacen):
        assert almacen.obtener_info_almacenamiento() == "Compartimentos: 3, Capacidad: 200.0L"

    def test_info_refleja_cambios(self, almacen):
        almacen.num_compartimentos = 5
        almacen.capacidad_litros = 80.5

        assert almacen.obtener_info_almacenamiento() == "Compartimentos: 5, Capacidad: 80.5L"