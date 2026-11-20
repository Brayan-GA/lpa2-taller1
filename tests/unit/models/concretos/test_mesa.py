"""Pruebas unitarias de la clase concreta Mesa."""

import pytest

from models.categorias.superficies import Superficie
from models.concretos.mesa import Mesa
from models.mueble import Mueble


@pytest.fixture
def mesa():
    """Mesa con todos los valores por defecto (120x80x75 cm, 4 personas)."""
    return Mesa("Mesa", "Madera", "Café", 1000.0)


class TestMesaHerencia:
    def test_es_clase_concreta(self):
        assert len(Mesa.__abstractmethods__) == 0

    def test_hereda_de_superficie_y_mueble(self, mesa):
        assert issubclass(Mesa, Superficie)
        assert issubclass(Mesa, Mueble)
        assert isinstance(mesa, Superficie)

    def test_str_heredado(self, mesa):
        assert str(mesa) == "Mesa de Madera en color Café"

    def test_validaciones_de_superficie_heredadas(self, mesa):
        with pytest.raises(ValueError, match="El largo debe ser mayor a 0"):
            mesa.largo = 0


class TestMesaConstructor:
    def test_valores_por_defecto(self, mesa):
        assert mesa.nombre == "Mesa"
        assert mesa.material == "Madera"
        assert mesa.color == "Café"
        assert mesa.precio_base == 1000.0
        assert mesa.forma == "rectangular"
        assert mesa.largo == 120.0
        assert mesa.ancho == 80.0
        assert mesa.altura == 75.0
        assert mesa.capacidad_personas == 4

    def test_valores_personalizados(self):
        mesa = Mesa("Mesa", "Vidrio", "Negro", 500.0, "redonda", 100.0, 100.0, 70.0, 6)

        assert mesa.forma == "redonda"
        assert mesa.largo == 100.0
        assert mesa.ancho == 100.0
        assert mesa.altura == 70.0
        assert mesa.capacidad_personas == 6


class TestMesaForma:
    @pytest.mark.parametrize("forma", ["rectangular", "redonda", "cuadrada", "ovalada"])
    def test_setter_acepta_formas_validas(self, mesa, forma):
        mesa.forma = forma
        assert mesa.forma == forma

    @pytest.mark.parametrize("forma", ["", "triangular", "Redonda", "OVALADA"])
    def test_setter_rechaza_formas_invalidas(self, mesa, forma):
        with pytest.raises(ValueError, match="Forma debe ser una de"):
            mesa.forma = forma

        assert mesa.forma == "rectangular"


class TestMesaCapacidad:
    @pytest.mark.parametrize("capacidad", [1, 4, 12])
    def test_setter_acepta_valores_positivos(self, mesa, capacidad):
        mesa.capacidad_personas = capacidad
        assert mesa.capacidad_personas == capacidad

    @pytest.mark.parametrize("capacidad", [0, -1, -8])
    def test_setter_rechaza_cero_y_negativos(self, mesa, capacidad):
        with pytest.raises(ValueError, match="La capacidad debe ser mayor a 0"):
            mesa.capacidad_personas = capacidad

        assert mesa.capacidad_personas == 4


class TestMesaPrecio:
    @pytest.mark.parametrize(
        "kwargs,esperado",
        [
            ({}, 1048.0),                                    # 1000 * 1.048
            ({"forma": "redonda"}, 1098.0),                  # +50 por forma
            ({"forma": "cuadrada"}, 1098.0),
            ({"forma": "ovalada"}, 1098.0),
            ({"capacidad_personas": 4}, 1048.0),             # límite: sin recargo
            ({"capacidad_personas": 5}, 1098.0),             # >4: +50
            ({"capacidad_personas": 6}, 1098.0),             # límite: sigue en +50
            ({"capacidad_personas": 7}, 1148.0),             # >6: +100
            ({"capacidad_personas": 12}, 1148.0),
            ({"largo": 100.0, "ancho": 100.0}, 1050.0),      # factor 1.05
            (
                {"forma": "redonda", "largo": 200.0, "ancho": 100.0, "capacidad_personas": 8},
                1250.0,                                      # 1100 + 50 + 100
            ),
        ],
    )
    def test_calcular_precio(self, kwargs, esperado):
        mesa = Mesa("Mesa", "Madera", "Café", 1000.0, **kwargs)

        assert mesa.calcular_precio() == pytest.approx(esperado)

    def test_precio_redondeado_a_dos_decimales(self):
        mesa = Mesa("Mesa", "Madera", "Café", 33.333)

        # 33.333 * 1.048 = 34.932984
        assert mesa.calcular_precio() == pytest.approx(34.93)

    def test_la_altura_no_afecta_el_precio(self):
        baja = Mesa("Mesa", "Madera", "Café", 1000.0, altura=40.0)
        alta = Mesa("Mesa", "Madera", "Café", 1000.0, altura=120.0)

        assert baja.calcular_precio() == alta.calcular_precio()


class TestMesaDescripcion:
    def test_descripcion_con_valores_por_defecto(self, mesa):
        esperado = (
            "Mesa: Mesa\n"
            "  Material: Madera\n"
            "  Color: Café\n"
            "  Forma: rectangular\n"
            "  Dimensiones: 120.0x80.0x75.0cm (Área: 9600.0cm²)\n"
            "  Capacidad: 4 personas\n"
            "  Precio final: $1048.0"
        )

        assert mesa.obtener_descripcion() == esperado

    def test_descripcion_personalizada(self):
        mesa = Mesa("Mesa Redonda", "Vidrio", "Negro", 1000.0, "redonda", 100.0, 100.0, 70.0, 6)

        esperado = (
            "Mesa: Mesa Redonda\n"
            "  Material: Vidrio\n"
            "  Color: Negro\n"
            "  Forma: redonda\n"
            "  Dimensiones: 100.0x100.0x70.0cm (Área: 10000.0cm²)\n"
            "  Capacidad: 6 personas\n"
            "  Precio final: $1150.0"
        )

        assert mesa.obtener_descripcion() == esperado