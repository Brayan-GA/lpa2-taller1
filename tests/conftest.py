"""Configuración compartida de pytest para todo el proyecto."""

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: pruebas lentas (se omiten con -m \"not slow\")"
    )
    config.addinivalue_line(
        "markers", "integration: pruebas de integración entre módulos"
    )


def pytest_collection_modifyitems(items):
    """Marca automáticamente como 'integration' todo lo que está en tests/integration."""
    for item in items:
        if "integration" in item.path.parts:
            item.add_marker(pytest.mark.integration)
