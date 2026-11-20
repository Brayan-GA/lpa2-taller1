# LPA2 Taller1: Pruebas Unitarias Tienda de Muebles

![commits](https://badgen.net/github/commits/UR-CC/lpa2-taller1?icon=github) 
![last_commit](https://img.shields.io/github/last-commit/UR-CC/lpa2-taller1)

> **Entrega del estudiante:** las instrucciones para ejecutar las pruebas y los
> resultados obtenidos están en la sección
> [Ejecución de las Pruebas de esta Entrega](#ejecución-de-las-pruebas-de-esta-entrega).

## Objetivos

- Aplicar **pruebas unitarias** con `pytest`
- Implementar **mocks y fixtures** para aislar dependencias
- Medir y analizar **cobertura de código** con `pytest-cov`
- Aplicar **Test-Driven Development (TDD)** en nuevas funcionalidades
- Diseñar pruebas para **clases abstractas y herencia**
- Crear pruebas para **composición y herencia múltiple**
- Implementar **pruebas de integración** básicas

## Prerrequisitos

- Conocimientos de OOP con Python
- Familiaridad con los conceptos de abstracción, herencia, polimorfismo

## Estructura del Proyecto

```
lpa2-taller1/
├─ src/                   # Código del proyecto
├─ tests/
│  ├─ fixtures/          # Datos de prueba
│  ├─ unit/              # Pruebas unitarias
│  │  ├─ conftest.py     # Configuración compartida
│  │  └─ models/
│  │     ├─ test_mueble.py
│  │     ├─ categorias/
│  │     │  ├─ test_almacenamiento.py
│  │     │  ├─ test_asientos.py
│  │     │  └─ test_superficies.py
│  │     ├─ concretos/
│  │     │  ├─ test_armario.py
│  │     │  ├─ test_cajonera.py
│  │     │  ├─ test_cama.py
│  │     │  ├─ test_comedor.py
│  │     │  ├─ test_escritorio.py
│  │     │  ├─ test_mesa.py
│  │     │  ├─ test_silla.py
│  │     │  ├─ test_sillon.py
│  │     │  ├─ test_sofa.py
│  │     │  └─ test_sofacama.py
│  │     └─ composicion/
│  │        └─ test_comedor.py
│  └─ integration/       # Pruebas de integración
├─ .coveragerc           # Configuración de cobertura
└─ pytest.ini            # Configuración de pytest
```

## Configuración del Entorno

### Preparación del Proyecto

- Crear un **fork** del repo `https://github.com/UR-CC/lpa2-taller1` en la cuenta GitHub del estudiante.

- Abrir una terminal de comandos.

- Crear un directorio para los **proyectos**:

    ```bash
    mkdir proyectos
    cd proyectos
    ```

- Clonar el repo del estudiante:

    ```bash
    git clone https://github.com/usuario/lpa2-taller1.git
    cd lpa2-taller1
    ```

- Crear entorno virtual - en Ubuntu utiliza `python3`:

    ```bash
    python -m venv venv
    source venv/bin/activate # Mac/Linux/WSL
    pip install -r requirements.txt
    ```

### Configurar Pytest

Archivo `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --color=yes
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-branch
pythonpath = . src tests
filterwarnings =
    ignore::DeprecationWarning
```

### Configurar Cobertura

Archivo `.coveragerc`:

```ini
[run]
source = src
omit = 
    */__pycache__/*
    */tests/*
    */venv/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    pass

fail_under = 80
```

## Diseño de Pruebas Unitarias

### Filosofía de las Pruebas

**Principios AAA (Arrange-Act-Assert):**

```python
def test_nombre_del_test():
    # Arrange: Preparar el escenario
    objeto = Clase(parametro=valor)
    
    # Act: Ejecutar la acción a probar
    resultado = objeto.metodo()
    
    # Assert: Verificar el resultado
    assert resultado == valor_esperado
```

**Patrones Comunes:**

- Una prueba por escenario
- Nombres descriptivos para tests
- Tests independientes y aislados
- Mockear dependencias externas

### Pruebas para Clases Abstractas

**tests/unit/models/test_mueble.py:**

```python
import pytest
from abc import ABC
from src.models.mueble import Mueble

class TestMueble:
    def test_es_clase_abstracta(self):
        # Verificar que Mueble es abstracta
        with pytest.raises(TypeError):
            mueble = Mueble("Mesa", "Madera", 100.0)
    
    def test_tiene_metodos_abstractos(self):
        # Verificar que tiene métodos abstractos
        assert hasattr(Mueble, 'calcular_precio')
        assert hasattr(Mueble, 'obtener_descripcion')
        
        # Verificar que son abstractos
        assert Mueble.calcular_precio.__isabstractmethod__
        assert Mueble.obtener_descripcion.__isabstractmethod__
```

### Pruebas para Herencia

**tests/unit/models/concretos/test_silla.py:**

```python
import pytest
from src.models.concretos.silla import Silla

class TestSilla:
    @pytest.fixture
    def silla_basica(self):
        return Silla("Silla Básica", "Madera", 50.0, 4, "Madera")
    
    def test_instanciacion_correcta(self, silla_basica):
        # Verificar herencia de atributos
        assert silla_basica.nombre == "Silla Básica"
        assert silla_basica.material == "Madera"
        assert silla_basica.precio_base == 50.0
        
        # Verificar atributos específicos
        assert silla_basica.numero_patas == 4
        assert silla_basica.tipo_madera == "Madera"
    
    def test_calcular_precio(self, silla_basica):
        # Probar polimorfismo
        precio = silla_basica.calcular_precio()
        assert precio == 50.0  # Precio base sin modificaciones
    
    def test_obtener_descripcion(self, silla_basica):
        descripcion = silla_basica.obtener_descripcion()
        assert "Silla Básica" in descripcion
        assert "Madera" in descripcion
```

### Pruebas para Herencia Múltiple

**tests/unit/models/concretos/test_sofacama.py:**

```python
import pytest
from src.models.concretos.sofacama import SofaCama

class TestSofaCama:
    def test_herencia_multiple(self):
        sofa_cama = SofaCama("Sofá Cama Moderno", "Tela", 500.0, 3, "Queen")
        
        # Verificar atributos de Sofa
        assert sofa_cama.capacidad_personas == 3
        
        # Verificar atributos de Cama
        assert sofa_cama.tamaño_colchon == "Queen"
        
        # Verificar método específico
        assert hasattr(sofa_cama, 'transformar')
    
    def test_resolucion_metodos(self):
        sofa_cama = SofaCama("Sofá Cama", "Cuero", 600.0, 2, "Full")
        
        # Verificar que usa el método correcto (MRO)
        precio = sofa_cama.calcular_precio()
        assert precio > 600.0  # Debe incluir recargos de ambas clases
```

### Pruebas para Composición

**tests/unit/models/composicion/test_comedor.py:**

```python
import pytest
from src.models.composicion.comedor import Comedor
from src.models.concretos.mesa import Mesa
from src.models.concretos.silla import Silla

class TestComedor:
    @pytest.fixture
    def comedor_basico(self):
        mesa = Mesa("Mesa Comedor", "Roble", 200.0, "Rectangular", 6)
        sillas = [Silla("Silla Comedor", "Roble", 50.0, 4, "Roble") for _ in range(6)]
        return Comedor("Comedor Familiar", mesa, sillas)
    
    def test_composicion_correcta(self, comedor_basico):
        assert comedor_basico.mesa is not None
        assert len(comedor_basico.sillas) == 6
        assert isinstance(comedor_basico.mesa, Mesa)
        assert all(isinstance(silla, Silla) for silla in comedor_basico.sillas)
    
    def test_calcular_precio_total(self, comedor_basico):
        precio_total = comedor_basico.calcular_precio()
        precio_esperado = 200.0 + (6 * 50.0)  # Mesa + 6 sillas
        assert precio_total == precio_esperado
```

### Pruebas con Mocks

**tests/unit/services/test_tienda.py:**

```python
import pytest
from unittest.mock import Mock, patch
from src.services.tienda import Tienda
from src.models.concretos.silla import Silla

class TestTienda:
    @pytest.fixture
    def tienda_vacia(self):
        return Tienda()
    
    @pytest.fixture
    def silla_mock(self):
        mock_silla = Mock(spec=Silla)
        mock_silla.nombre = "Silla Mock"
        mock_silla.calcular_precio.return_value = 75.0
        return mock_silla
    
    def test_agregar_producto(self, tienda_vacia, silla_mock):
        tienda_vacia.agregar_producto(silla_mock)
        assert len(tienda_vacia.inventario) == 1
        assert tienda_vacia.inventario[0] == silla_mock
    
    def test_vender_producto_existente(self, tienda_vacia, silla_mock):
        tienda_vacia.agregar_producto(silla_mock)
        
        with patch('builtins.print') as mock_print:
            resultado = tienda_vacia.vender_producto("Silla Mock")
            
            assert resultado is True
            assert len(tienda_vacia.inventario) == 0
            mock_print.assert_called_once()
    
    def test_vender_producto_inexistente(self, tienda_vacia):
        resultado = tienda_vacia.vender_producto("Producto Inexistente")
        assert resultado is False
```

## Ejecución de Pruebas

### Comandos Básicos

- Configurar la variable de entorno `PYTHONPATH`:

    ```bash
    export PYTHONPATH=.
    ```

- Ejecutar todas las pruebas, `-v` en modo *verbose*:

    ```bash
    pytest -v
    ```

- Ejecutar pruebas con cobertura detallada

    ```bash
    pytest --cov=src --cov-report=html
    ```

- Ejecutar pruebas específicas

    ```bash
    pytest tests/unit/models/ -v
    ```

- Ejecutar pruebas y mostrar cobertura en terminal

    ```bash
    pytest --cov=src --cov-report=term-missing
    ```

- Ejecutar pruebas marcadas como rápidas

    ```bash
    pytest -m "not slow"
    ```

### Marcadores de Pruebas

**tests/conftest.py:**

```python
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
```

**Uso en pruebas:**

```python
@pytest.mark.slow
def test_proceso_lento():
    # Esta prueba se puede saltar con pytest -m "not slow"
    pass

@pytest.mark.integration
def test_integracion_completa():
    # Prueba de integración
    pass
```

## Estrategias de Pruebas

### 1. Test-Driven Development (TDD)

**Ciclo Red-Green-Refactor:**

1. **RED**: Escribir prueba que falle
2. **GREEN**: Implementar mínimo código para pasar
3. **REFACTOR**: Mejorar el código manteniendo pruebas

**Ejemplo - Nueva funcionalidad de descuentos:**

```python
# tests/unit/services/test_descuentos.py
def test_aplicar_descuento_por_material():
    # RED: Escribir prueba primero
    tienda = Tienda()
    silla = Silla("Silla", "Roble", 100.0, 4, "Roble")
    
    tienda.agregar_producto(silla)
    tienda.aplicar_descuento_material("Roble", 0.1)  # 10% descuento
    
    assert silla.precio_base == 90.0  # Esta prueba fallará inicialmente
```

### 2. Categorías de Pruebas

| Tipo | Objetivo | Ejemplo |
|------|----------|---------|
| **Unitarias** | Probar unidades individuales | `test_silla_calcular_precio()` |
| **Integración** | Probar interacción entre módulos | `test_tienda_con_catalogo()` |
| **Fixtures** | Datos de prueba reutilizables | `@pytest.fixture def silla_basica()` |
| **Mocks** | Simular dependencias externas | `@patch('services.tienda.print')` |

### 3. Patrones de Diseño para Pruebas

**Fixture para datos complejos:**

```python
@pytest.fixture
def comedor_completo():
    mesa = Mesa("Mesa Roble", "Roble", 300.0, "Rectangular", 8)
    sillas = [Silla("Silla Roble", "Roble", 80.0, 4, "Roble") for _ in range(8)]
    return Comedor("Comedor Grande", mesa, sillas)

def test_comedor_precio(comedor_completo):
    precio = comedor_completo.calcular_precio()
    assert precio == 300.0 + (8 * 80.0)
```

**Parámetros para múltiples escenarios:**

```python
@pytest.mark.parametrize("material,precio_base,esperado", [
    ("Madera", 100.0, 100.0),
    ("Roble", 150.0, 150.0),
    ("Metal", 120.0, 120.0),
])
def test_silla_precios_diferentes_materiales(material, precio_base, esperado):
    silla = Silla(f"Silla {material}", material, precio_base, 4, material)
    assert silla.calcular_precio() == esperado
```

## Análisis de Cobertura

### Interpretar Reportes de Cobertura

```bash
# Generar reporte HTML
pytest --cov=src --cov-report=html

# Abrir reporte
open htmlcov/index.html
```

**Métricas importantes:**

- **Cobertura total**: Porcentaje general de código cubierto
- **Líneas cubiertas**: Líneas ejecutadas durante pruebas
- **Líneas missing**: Líneas que necesitan pruebas
- **Branch coverage**: Cobertura de ramas condicionales

### Mejorar Cobertura

**Identificar gaps:**

```bash
pytest --cov=src --cov-report=term-missing
```

**Ejemplo de salida:**

```
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/models/mueble.py       15      3    80%   22-24
src/services/tienda.py     45     10    78%   15-18, 33-39
```

## Ejecución de las Pruebas de esta Entrega

### 1. Preparar el entorno

Requiere Python 3.10 o superior (probado con Python 3.13).

**Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Si PowerShell bloquea la activación, ejecutar una vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**Mac / Linux / WSL:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

No es necesario configurar `PYTHONPATH`: `pytest.ini` ya agrega `.`, `src` y
`tests` con la opción `pythonpath`.

### 2. Ejecutar las pruebas

Todos los comandos se ejecutan desde la raíz del proyecto, con el entorno
virtual activado.

| Comando | Qué hace |
|---|---|
| `pytest` | Ejecuta todas las pruebas con cobertura (terminal + HTML) |
| `pytest tests/unit` | Solo pruebas unitarias |
| `pytest tests/integration` | Solo pruebas de integración |
| `pytest -m integration` | Pruebas con el marcador `integration` |
| `pytest -m "not integration"` | Todo excepto integración |
| `pytest tests/unit/ui/test_menu.py -v` | Un archivo específico |
| `pytest --no-cov` | Pruebas sin medir cobertura (más rápido) |
| `pytest --durations=10` | Muestra las 10 pruebas más lentas |

El reporte HTML de cobertura se genera en `htmlcov/`. Para abrirlo:

```powershell
start htmlcov\index.html      # Windows
```

```bash
open htmlcov/index.html       # Mac
xdg-open htmlcov/index.html   # Linux
```

### 3. Resultados

```
543 passed, 8 xfailed
Required test coverage of 80.0% reached. Total coverage: 99.78%
```

| Módulo | Cobertura |
|---|---|
| `src/models/` (mueble, categorías, concretos) | 100% |
| `src/models/composicion/comedor.py` | 99% |
| `src/services/tienda.py` | 100% |
| `src/ui/menu.py` | 99% |
| `src/main.py` | 100% |
| **Total** | **99.78%** |

Las 8 pruebas `xfailed` son **fallos esperados** marcados con
`@pytest.mark.xfail`: documentan defectos conocidos del código fuente (por
ejemplo, `armario.py`, `cajonera.py`, `escritorio.py` y `sillon.py` tienen
comentado el import de su clase base y no heredan de ella). No cuentan como
pruebas fallidas.

### 4. Organización de las pruebas

```
tests/
├─ conftest.py                    # Marcadores slow / integration
├─ unit/                          # 528 pruebas unitarias
│  ├─ models/
│  │  ├─ test_mueble.py           # Clase abstracta base
│  │  ├─ categorias/              # Asiento, Superficie, Almacenamiento (abstractas)
│  │  ├─ concretos/               # Silla, Mesa, Sofa, Cama, SofaCama, ...
│  │  └─ composicion/             # Comedor (mesa + sillas)
│  ├─ services/test_tienda.py     # Lógica de negocio con Mock / patch
│  ├─ ui/test_menu.py             # Menú Rich simulando la entrada del usuario
│  └─ test_main.py                # Datos de ejemplo y punto de entrada
└─ integration/                   # 15 pruebas de integración
   ├─ conftest.py                 # Fixtures con objetos reales (sin mocks)
   ├─ test_tienda_integracion.py  # Agregar -> descontar -> vender -> reportar
   └─ test_menu_integracion.py    # Sesiones completas del menú con tienda real
```

### 5. Técnicas aplicadas

- **Patrón AAA** (Arrange-Act-Assert) en cada prueba.
- **Fixtures** (`@pytest.fixture`) para crear muebles, comedores y tiendas reutilizables.
- **Parametrización** (`@pytest.mark.parametrize`) para probar muchos valores con una sola prueba.
- **Mocks** (`Mock`, `patch`) para aislar la tienda de los muebles y simular fallos.
- **`monkeypatch`** para simular `Prompt`, `IntPrompt`, `Confirm`, `input` y anular `time.sleep`.
- **`capsys`** para revisar lo que se imprime en `main.py`, y una consola Rich con `record=True` para el menú.
- **`tmp_path`** para probar el guardado del reporte sin dejar archivos en el proyecto.
- **Clases abstractas:** se verifica que no se pueden instanciar y que declaran sus métodos abstractos.
- **Herencia múltiple:** `SofaCama` combina el comportamiento de `Sofa` y `Cama` y se verifica su MRO.
- **Composición:** `Comedor` se prueba con mesa y sillas reales, incluido el 5% de descuento con 4 o más sillas.
- **Casos límite y errores:** valores cero, negativos e inválidos, muebles sin precio, ventas repetidas, archivos que no se pueden escribir y `Ctrl+C`.

## Entregables

El estudiante debe actualizar su repositorio personal con:

1. **Estructura de pruebas completa** organizada por módulos
2. **Cobertura mínima del 80%** en todos los módulos principales
3. **Pruebas para casos edge** y condiciones de error
4. **Fixtures y mocks** para pruebas aisladas
5. **Reporte de cobertura** HTML generado
6. **README actualizado** con instrucciones de ejecución

## Recursos Adicionales

### Documentación Oficial

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Coverage](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### Mejores Prácticas

- Escribir pruebas independientes y rápidas
- Usar nombres descriptivos para tests
- Probar tanto el éxito como los casos de error
- Mantener las pruebas actualizadas con el código
- Usar fixtures para datos de prueba complejos

### Comandos Útiles

- Ejecutar pruebas y generar badge de cobertura

    ```bash
    pytest --cov=src --cov-report=term-missing --cov-badge
    ```

- Ejecutar pruebas en paralelo

    ```bash
    pytest -n auto
    ```

- Ver tiempo de ejecución de pruebas

    ```bash
    pytest --durations=10
    ```

**Nota**: repo [solución al proyecto Muebles](https://github.com/axlcraft/lpa1-taller-poo).

