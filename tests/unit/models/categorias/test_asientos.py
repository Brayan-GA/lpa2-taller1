"""Pruebas unitarias de la clase abstracta Asiento."""

import pytest

from models.categorias.asientos import Asiento
from models.mueble import Mueble


class AsientoConcreto(Asiento):
    """Subclase mínima, solo para poder instanciar y probar Asiento."""

    def calcular_precio(self) -> float:
        return self.precio_base

    def obtener_descripcion(self) -> str:
        return self.nombre


def crear_asiento(capacidad=1, respaldo=False, tapizado=None):
    return AsientoConcreto("Silla", "Madera", "Café", 100.0, capacidad, respaldo, tapizado)


@pytest.fixture
def asiento():
    return crear_asiento(capacidad=2, respaldo=True, tapizado="Cuero")


class TestAsientoAbstracto:
    def test_no_se_puede_instanciar(self):
        with pytest.raises(TypeError):
            Asiento("Silla", "Madera", "Café", 100.0, 1, True)

    def test_metodos_abstractos_declarados(self):
        assert Asiento.__abstractmethods__ == {"calcular_precio", "obtener_descripcion"}

    def test_subclase_incompleta_no_se_puede_instanciar(self):
        class SoloPrecio(Asiento):
            def calcular_precio(self) -> float:
                return 0.0

        with pytest.raises(TypeError):
            SoloPrecio("Silla", "Madera", "Café", 100.0, 1, True)


class TestAsientoHerencia:
    def test_asiento_hereda_de_mueble(self, asiento):
        assert issubclass(Asiento, Mueble)
        assert isinstance(asiento, Mueble)

    def test_atributos_heredados(self, asiento):
        assert asiento.nombre == "Silla"
        assert asiento.material == "Madera"
        assert asiento.color == "Café"
        assert asiento.precio_base == 100.0

    def test_validaciones_heredadas_de_mueble(self, asiento):
        with pytest.raises(ValueError):
            asiento.nombre = ""

    def test_str_heredado(self, asiento):
        assert str(asiento) == "Silla de Madera en color Café"


class TestAsientoAtributos:
    def test_constructor_asigna_atributos_propios(self, asiento):
        assert asiento.capacidad_personas == 2
        assert asiento.tiene_respaldo is True
        assert asiento.material_tapizado == "Cuero"

    def test_material_tapizado_es_opcional(self):
        asiento = AsientoConcreto("Silla", "Madera", "Café", 100.0, 1, False)
        assert asiento.material_tapizado is None

    @pytest.mark.parametrize("capacidad", [1, 2, 10])
    def test_capacidad_acepta_valores_positivos(self, asiento, capacidad):
        asiento.capacidad_personas = capacidad
        assert asiento.capacidad_personas == capacidad

    @pytest.mark.parametrize("capacidad", [0, -1, -5])
    def test_capacidad_rechaza_cero_y_negativos(self, asiento, capacidad):
        with pytest.raises(ValueError, match="mayor a 0"):
            asiento.capacidad_personas = capacidad

        assert asiento.capacidad_personas == 2

    def test_setter_tiene_respaldo(self, asiento):
        asiento.tiene_respaldo = False
        assert asiento.tiene_respaldo is False

    def test_setter_material_tapizado(self, asiento):
        asiento.material_tapizado = "Tela"
        assert asiento.material_tapizado == "Tela"


class TestFactorComodidad:
    @pytest.mark.parametrize(
        "capacidad,respaldo,tapizado,esperado",
        [
            (1, False, None, 1.0),    # sin extras
            (1, True, None, 1.1),     # respaldo
            (1, False, "cuero", 1.2),
            (1, False, "CUERO", 1.2),  # no distingue mayúsculas
            (1, False, "Tela", 1.1),
            (1, False, "lino", 1.0),   # tapizado desconocido
            (1, False, "", 1.0),       # tapizado vacío
            (3, False, None, 1.1),     # capacidad adicional
            (2, True, "tela", 1.25),
            (3, True, "cuero", 1.4),   # todos los extras
        ],
    )
    def test_calcular_factor_comodidad(self, capacidad, respaldo, tapizado, esperado):
        asiento = crear_asiento(capacidad, respaldo, tapizado)

        assert asiento.calcular_factor_comodidad() == pytest.approx(esperado)


class TestInfoAsiento:
    def test_info_completa(self, asiento):
        assert asiento.obtener_info_asiento() == (
            "Capacidad: 2 personas, Respaldo: Sí, Tapizado: Cuero"
        )

    def test_info_sin_tapizado_ni_respaldo(self):
        asiento = crear_asiento(capacidad=1, respaldo=False, tapizado=None)

        assert asiento.obtener_info_asiento() == "Capacidad: 1 personas, Respaldo: No"