"""Pruebas unitarias de la clase abstracta Mueble."""

import pytest

from src.models.mueble import Mueble


class MuebleConcreto(Mueble):
    """Subclase mínima, solo para poder instanciar y probar Mueble."""

    def calcular_precio(self) -> float:
        return self.precio_base

    def obtener_descripcion(self) -> str:
        return f"{self.nombre} ({self.material}, {self.color})"


@pytest.fixture
def mueble():
    return MuebleConcreto("Mesa", "Madera", "Café", 100.0)


class TestMuebleAbstracto:
    def test_no_se_puede_instanciar(self):
        with pytest.raises(TypeError):
            Mueble("Mesa", "Madera", "Café", 100.0)

    def test_metodos_abstractos_declarados(self):
        assert Mueble.__abstractmethods__ == {"calcular_precio", "obtener_descripcion"}

    def test_subclase_incompleta_no_se_puede_instanciar(self):
        class SoloPrecio(Mueble):
            def calcular_precio(self) -> float:
                return 0.0

        with pytest.raises(TypeError):
            SoloPrecio("Mesa", "Madera", "Café", 100.0)

    def test_subclase_completa_se_puede_instanciar(self, mueble):
        assert isinstance(mueble, Mueble)

    def test_metodos_abstractos_implementados_por_la_subclase(self, mueble):
        assert mueble.calcular_precio() == 100.0
        assert mueble.obtener_descripcion() == "Mesa (Madera, Café)"


class TestMuebleAtributos:
    def test_constructor_asigna_atributos(self, mueble):
        assert mueble.nombre == "Mesa"
        assert mueble.material == "Madera"
        assert mueble.color == "Café"
        assert mueble.precio_base == 100.0

    @pytest.mark.parametrize(
        "atributo,nuevo",
        [("nombre", "Silla"), ("material", "Metal"), ("color", "Negro")],
    )
    def test_setters_aceptan_valores_validos(self, mueble, atributo, nuevo):
        setattr(mueble, atributo, nuevo)
        assert getattr(mueble, atributo) == nuevo

    @pytest.mark.parametrize("atributo", ["nombre", "material", "color"])
    def test_setters_eliminan_espacios_extremos(self, mueble, atributo):
        setattr(mueble, atributo, "  Valor  ")
        assert getattr(mueble, atributo) == "Valor"

    @pytest.mark.parametrize("atributo", ["nombre", "material", "color"])
    @pytest.mark.parametrize("valor", ["", "   ", None])
    def test_setters_rechazan_valores_vacios(self, mueble, atributo, valor):
        original = getattr(mueble, atributo)

        with pytest.raises(ValueError, match="no puede estar vacío"):
            setattr(mueble, atributo, valor)

        assert getattr(mueble, atributo) == original


class TestMueblePrecioBase:
    @pytest.mark.parametrize("precio", [0, 0.0, 1, 250.5])
    def test_acepta_precios_validos(self, mueble, precio):
        mueble.precio_base = precio
        assert mueble.precio_base == precio

    @pytest.mark.parametrize("precio", [-1, -0.01, -1000.0])
    def test_rechaza_precios_negativos(self, mueble, precio):
        with pytest.raises(ValueError, match="no puede ser negativo"):
            mueble.precio_base = precio

        assert mueble.precio_base == 100.0


class TestMuebleRepresentaciones:
    def test_str(self, mueble):
        assert str(mueble) == "Mueble de Madera en color Café".replace("Mueble", "Mesa")

    def test_repr(self, mueble):
        esperado = (
            "Mueble(nombre='Mesa', material='Madera', "
            "color='Café', precio_base=100.0)"
        )
        assert repr(mueble) == esperado