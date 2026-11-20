"""Pruebas unitarias de la clase concreta Silla."""

import pytest

from models.categorias.asientos import Asiento
from models.concretos.silla import Silla
from models.mueble import Mueble


@pytest.fixture
def silla():
    """Silla con todos los valores por defecto."""
    return Silla("Silla", "Madera", "Café", 100.0)


@pytest.fixture
def silla_oficina():
    """Silla con respaldo, tapizado de cuero, altura regulable y ruedas."""
    return Silla("Silla Oficina", "Metal", "Negro", 100.0, True, "cuero", True, True)


class TestSillaHerencia:
    def test_es_clase_concreta(self):
        assert len(Silla.__abstractmethods__) == 0

    def test_hereda_de_asiento_y_mueble(self, silla):
        assert issubclass(Silla, Asiento)
        assert issubclass(Silla, Mueble)
        assert isinstance(silla, Asiento)

    def test_capacidad_siempre_es_una_persona(self, silla):
        assert silla.capacidad_personas == 1

    def test_str_heredado(self, silla):
        assert str(silla) == "Silla de Madera en color Café"


class TestSillaConstructor:
    def test_valores_por_defecto(self, silla):
        assert silla.nombre == "Silla"
        assert silla.material == "Madera"
        assert silla.color == "Café"
        assert silla.precio_base == 100.0
        assert silla.tiene_respaldo is True
        assert silla.material_tapizado is None
        assert silla.altura_regulable is False
        assert silla.tiene_ruedas is False

    def test_valores_personalizados(self, silla_oficina):
        assert silla_oficina.tiene_respaldo is True
        assert silla_oficina.material_tapizado == "cuero"
        assert silla_oficina.altura_regulable is True
        assert silla_oficina.tiene_ruedas is True


class TestSillaSetters:
    def test_setter_altura_regulable(self, silla):
        silla.altura_regulable = True
        assert silla.altura_regulable is True

    def test_setter_tiene_ruedas(self, silla):
        silla.tiene_ruedas = True
        assert silla.tiene_ruedas is True


class TestSillaPrecio:
    @pytest.mark.parametrize(
        "kwargs,esperado",
        [
            ({}, 110.0),                                    # solo respaldo
            ({"tiene_respaldo": False}, 100.0),             # sin extras
            ({"material_tapizado": "cuero"}, 130.0),
            ({"material_tapizado": "tela"}, 120.0),
            ({"altura_regulable": True}, 140.0),            # +30
            ({"tiene_ruedas": True}, 130.0),                # +20
            ({"altura_regulable": True, "tiene_ruedas": True}, 160.0),
            (
                {"tiene_respaldo": False, "altura_regulable": True, "tiene_ruedas": True},
                150.0,
            ),
            (
                {"material_tapizado": "cuero", "altura_regulable": True, "tiene_ruedas": True},
                180.0,
            ),
        ],
    )
    def test_calcular_precio(self, kwargs, esperado):
        silla = Silla("Silla", "Madera", "Café", 100.0, **kwargs)

        assert silla.calcular_precio() == pytest.approx(esperado)

    def test_precio_redondeado_a_dos_decimales(self):
        silla = Silla("Silla", "Madera", "Café", 33.333)

        assert silla.calcular_precio() == pytest.approx(36.67)


class TestSillaDescripcion:
    def test_descripcion_completa(self, silla_oficina):
        esperado = (
            "Silla: Silla Oficina\n"
            "  Material: Metal\n"
            "  Color: Negro\n"
            "  Capacidad: 1 personas, Respaldo: Sí, Tapizado: cuero\n"
            "  Altura regulable: Sí\n"
            "  Ruedas: Sí\n"
            "  Precio final: $180.0"
        )

        assert silla_oficina.obtener_descripcion() == esperado

    def test_descripcion_silla_basica(self, silla):
        descripcion = silla.obtener_descripcion()

        assert "Silla: Silla" in descripcion
        assert "Altura regulable: No" in descripcion
        assert "Ruedas: No" in descripcion
        assert "Tapizado" not in descripcion
        assert "Precio final: $110.0" in descripcion


class TestRegularAltura:
    def test_silla_sin_altura_regulable(self, silla):
        assert silla.regular_altura(70) == "Esta silla no tiene altura regulable"

    def test_sin_altura_regulable_tiene_prioridad_sobre_el_rango(self, silla):
        assert silla.regular_altura(500) == "Esta silla no tiene altura regulable"

    @pytest.mark.parametrize("altura", [40, 70, 100])
    def test_altura_valida_incluye_los_limites(self, silla_oficina, altura):
        assert silla_oficina.regular_altura(altura) == f"Altura ajustada a {altura} cm"

    @pytest.mark.parametrize("altura", [0, 39, 101, 200])
    def test_altura_fuera_de_rango(self, silla_oficina, altura):
        assert silla_oficina.regular_altura(altura) == "La altura debe estar entre 40 y 100 cm"


class TestSillaOficina:
    @pytest.mark.parametrize(
        "altura,ruedas,esperado",
        [
            (True, True, True),
            (True, False, False),
            (False, True, False),
            (False, False, False),
        ],
    )
    def test_es_silla_oficina(self, altura, ruedas, esperado):
        silla = Silla("Silla", "Madera", "Café", 100.0, altura_regulable=altura, tiene_ruedas=ruedas)

        assert silla.es_silla_oficina() is esperado