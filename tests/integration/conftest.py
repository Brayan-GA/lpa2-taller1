"""Fixtures para las pruebas de integración.

A diferencia de las pruebas unitarias, aquí se usan objetos reales
(TiendaMuebles, muebles concretos y comedores) sin mocks, para comprobar
que los módulos funcionan bien juntos.
"""

import pytest

import main
from models.composicion.comedor import Comedor
from models.concretos.mesa import Mesa
from models.concretos.silla import Silla
from services.tienda import TiendaMuebles


@pytest.fixture
def tienda():
    return TiendaMuebles("Tienda Integración")


@pytest.fixture
def silla():
    """Silla de base 100: precio final 110.0 (recargo por respaldo)."""
    return Silla("Silla Roble", "Madera", "Café", 100.0)


@pytest.fixture
def mesa():
    """Mesa de base 1000: precio final 1048.0."""
    return Mesa("Mesa Industrial", "Metal", "Negro", 1000.0)


@pytest.fixture
def comedor():
    mesa = Mesa("Mesa Comedor", "Madera", "Roble", 1000.0)
    sillas = [Silla(f"Silla {i}", "Madera", "Roble", 100.0) for i in range(4)]
    return Comedor("Comedor Familiar", mesa, sillas)


@pytest.fixture
def tienda_con_catalogo(tienda, capsys):
    """Tienda con los mismos datos de ejemplo que usa main.py."""
    main.crear_catalogo_inicial(tienda)
    main.crear_comedores_ejemplo(tienda)
    capsys.readouterr()  # Descartar lo impreso al crear los datos
    return tienda
