"""Pruebas unitarias de SofaCama (herencia múltiple de Sofa y Cama)."""

import pytest

from models.categorias.asientos import Asiento
from models.concretos.cama import Cama
from models.concretos.sofa import Sofa
from models.concretos.sofacama import SofaCama
from models.mueble import Mueble


@pytest.fixture
def sofacama():
    """Sofá-cama con todos los valores por defecto."""
    return SofaCama("Sofá Cama", "Tela", "Gris", 1000)


class TestSofaCamaHerenciaMultiple:
    def test_es_clase_concreta(self):
        assert len(SofaCama.__abstractmethods__) == 0

    def test_es_instancia_de_todas_las_clases_padre(self, sofacama):
        assert isinstance(sofacama, Sofa)
        assert isinstance(sofacama, Cama)
        assert isinstance(sofacama, Asiento)
        assert isinstance(sofacama, Mueble)

    def test_orden_de_resolucion_de_metodos(self):
        # Sofa va primero porque es el primer padre declarado
        assert SofaCama.mro()[:5] == [SofaCama, Sofa, Asiento, Cama, Mueble]

    def test_constructor_inicializa_la_rama_de_cama_mediante_super(self, sofacama):
        # Cama.__init__ se ejecuta a través de la cadena super() de Asiento
        assert sofacama.tiene_cabecera is False

    def test_hereda_atributos_de_sofa(self, sofacama):
        assert sofacama.capacidad_personas == 3
        assert sofacama.tiene_respaldo is True
        assert sofacama.tiene_brazos is True
        assert sofacama.es_modular is False
        assert sofacama.incluye_cojines is False

    def test_calcular_precio_usa_sofa_y_no_cama(self, sofacama):
        # super().calcular_precio() resuelve a Sofa, no a Cama
        esperado = Sofa.calcular_precio(sofacama) + 300 + 250

        assert sofacama.calcular_precio() == pytest.approx(esperado)
        assert sofacama.calcular_precio() != pytest.approx(Cama.calcular_precio(sofacama))


class TestSofaCamaConstructor:
    def test_valores_por_defecto(self, sofacama):
        assert sofacama.nombre == "Sofá Cama"
        assert sofacama.material == "Tela"
        assert sofacama.color == "Gris"
        assert sofacama.precio_base == 1000
        assert sofacama.material_tapizado == "tela"
        assert sofacama.tamaño == "matrimonial"
        assert sofacama.tamaño_cama == "matrimonial"
        assert sofacama.incluye_colchon is True
        assert sofacama.mecanismo_conversion == "plegable"
        assert sofacama.modo_actual == "sofa"

    def test_valores_personalizados(self):
        sc = SofaCama("SC", "Cuero", "Negro", 800, 4, "cuero", "king", False, "electrico")

        assert sc.capacidad_personas == 4
        assert sc.material_tapizado == "cuero"
        assert sc.tamaño_cama == "king"
        assert sc.incluye_colchon is False
        assert sc.mecanismo_conversion == "electrico"

    @pytest.mark.parametrize(
        "atributo", ["tamaño", "tamaño_cama", "mecanismo_conversion", "modo_actual"]
    )
    def test_propiedades_son_de_solo_lectura(self, sofacama, atributo):
        with pytest.raises(AttributeError):
            setattr(sofacama, atributo, "king")


class TestSofaCamaPrecio:
    @pytest.mark.parametrize(
        "kwargs,esperado",
        [
            ({}, 2000.0),                                  # 1450 sofá + 300 + 250
            ({"tamaño_cama": "individual"}, 1700.0),       # sin recargo de tamaño
            ({"tamaño_cama": "queen"}, 2200.0),            # +500
            ({"tamaño_cama": "king"}, 2400.0),             # +700
            ({"incluye_colchon": False}, 1750.0),          # sin los +250
            ({"mecanismo_conversion": "plegable"}, 2000.0),
            ({"mecanismo_conversion": "hidraulico"}, 2150.0),   # +150
            ({"mecanismo_conversion": "electrico"}, 2300.0),    # +300
            ({"material_tapizado": "cuero"}, 2100.0),
            ({"capacidad_personas": 2}, 1950.0),
            (
                {"tamaño_cama": "king", "mecanismo_conversion": "electrico"},
                2700.0,                                    # recargos máximos
            ),
        ],
    )
    def test_calcular_precio(self, kwargs, esperado):
        sc = SofaCama("Sofá Cama", "Tela", "Gris", 1000, **kwargs)

        assert sc.calcular_precio() == pytest.approx(esperado)


class TestSofaCamaConversion:
    def test_convertir_a_cama(self, sofacama):
        resultado = sofacama.convertir_a_cama()

        assert resultado == "Sofá convertido a cama usando mecanismo plegable"
        assert sofacama.modo_actual == "cama"

    def test_convertir_a_cama_estando_en_modo_cama(self, sofacama):
        sofacama.convertir_a_cama()

        assert sofacama.convertir_a_cama() == "El sofá-cama ya está en modo cama"
        assert sofacama.modo_actual == "cama"

    def test_convertir_a_sofa_estando_en_modo_sofa(self, sofacama):
        assert sofacama.convertir_a_sofa() == "El sofá-cama ya está en modo sofá"
        assert sofacama.modo_actual == "sofa"

    def test_convertir_a_sofa_desde_modo_cama(self, sofacama):
        sofacama.convertir_a_cama()

        resultado = sofacama.convertir_a_sofa()

        assert resultado == "Cama convertida a sofá usando mecanismo plegable"
        assert sofacama.modo_actual == "sofa"

    def test_el_mensaje_incluye_el_mecanismo(self):
        sc = SofaCama("SC", "Tela", "Gris", 1000, mecanismo_conversion="electrico")

        assert "electrico" in sc.convertir_a_cama()


class TestSofaCamaCapacidadTotal:
    @pytest.mark.parametrize(
        "tamaño,como_cama",
        [("individual", 1), ("matrimonial", 2), ("queen", 2), ("king", 2)],
    )
    def test_capacidad_como_cama_segun_tamaño(self, tamaño, como_cama):
        sc = SofaCama("SC", "Tela", "Gris", 1000, tamaño_cama=tamaño)

        assert sc.obtener_capacidad_total()["como_cama"] == como_cama

    def test_capacidad_como_sofa(self):
        sc = SofaCama("SC", "Tela", "Gris", 1000, capacidad_personas=4)

        assert sc.obtener_capacidad_total() == {"como_sofa": 4, "como_cama": 2}


class TestSofaCamaTextos:
    def test_str(self, sofacama):
        assert str(sofacama) == "Sofá-cama Sofá Cama (modo: sofa)"

    def test_str_refleja_el_modo_actual(self, sofacama):
        sofacama.convertir_a_cama()

        assert str(sofacama) == "Sofá-cama Sofá Cama (modo: cama)"

    def test_descripcion(self, sofacama):
        esperado = (
            "Sofá-Cama: Sofá Cama\n"
            "  Material: Tela\n"
            "  Color: Gris\n"
            "  Capacidad: 3 personas, Respaldo: Sí, Tapizado: tela\n"
            "  Tamaño como cama: matrimonial\n"
            "  Incluye colchón: Sí\n"
            "  Mecanismo: plegable\n"
            "  Modo actual: sofa\n"
            "  Precio final: $2000.0"
        )

        assert sofacama.obtener_descripcion() == esperado