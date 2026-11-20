"""Pruebas de integración: TiendaMuebles con modelos reales.

Comprueban flujos completos (agregar -> descontar -> vender -> reportar)
en los que participan varios módulos a la vez.
"""

import pytest

from models.concretos.sofacama import SofaCama


class TestCatalogoDeEjemplo:
    def test_catalogo_y_comedores_cargados(self, tienda_con_catalogo):
        stats = tienda_con_catalogo.obtener_estadisticas()
        assert stats["total_muebles"] == 17
        assert stats["total_comedores"] == 2
        assert stats["valor_inventario"] > 0

    def test_distribucion_por_tipos(self, tienda_con_catalogo):
        tipos = tienda_con_catalogo.obtener_estadisticas()["tipos_muebles"]
        assert tipos["Silla"] == 3
        assert tipos["Mesa"] == 3
        assert tipos["Cama"] == 2
        assert tipos["SofaCama"] == 1
        assert sum(tipos.values()) == 17

    def test_busqueda_y_filtros_sobre_catalogo_real(self, tienda_con_catalogo):
        sillas = tienda_con_catalogo.buscar_muebles_por_nombre("silla")
        assert len(sillas) == 3

        de_metal = tienda_con_catalogo.filtrar_por_material("metal")
        assert de_metal and all(m.material == "Metal" for m in de_metal)

        baratos = tienda_con_catalogo.filtrar_por_precio(0, 300)
        assert baratos and all(m.calcular_precio() <= 300 for m in baratos)

    def test_sofacama_combina_comportamientos(self, tienda_con_catalogo):
        (sofacama,) = [
            m for m in tienda_con_catalogo._inventario if isinstance(m, SofaCama)
        ]
        assert "SofaCama" in tienda_con_catalogo.obtener_estadisticas()[
            "tipos_muebles"
        ]
        assert sofacama.calcular_precio() > sofacama.precio_base


class TestFlujoDeVenta:
    def test_venta_con_descuento(self, tienda, silla, mesa):
        tienda.agregar_mueble(silla)
        tienda.agregar_mueble(mesa)
        tienda.aplicar_descuento("sillas", 10)

        venta = tienda.realizar_venta(silla, "Ana")

        assert venta["cliente"] == "Ana"
        assert venta["precio_original"] == 110.0
        assert venta["descuento"] == 10.0
        assert venta["precio_final"] == 99.0
        assert silla not in tienda._inventario
        assert mesa in tienda._inventario

    def test_descuento_no_afecta_otra_categoria(self, tienda, silla, mesa):
        tienda.agregar_mueble(silla)
        tienda.agregar_mueble(mesa)
        tienda.aplicar_descuento("silla", 50)

        venta = tienda.realizar_venta(mesa)

        assert venta["descuento"] == 0
        assert venta["precio_final"] == venta["precio_original"] == 1048.0

    def test_estadisticas_acumuladas_tras_varias_ventas(self, tienda, silla, mesa):
        tienda.agregar_mueble(silla)
        tienda.agregar_mueble(mesa)

        tienda.realizar_venta(silla)
        tienda.realizar_venta(mesa)

        stats = tienda.obtener_estadisticas()
        assert stats["total_muebles"] == 0
        assert stats["ventas_realizadas"] == 2
        assert stats["total_muebles_vendidos"] == 2
        assert stats["valor_total_ventas"] == pytest.approx(110.0 + 1048.0)
        assert stats["valor_inventario"] == 0

    def test_no_se_puede_vender_dos_veces(self, tienda, silla):
        tienda.agregar_mueble(silla)
        tienda.realizar_venta(silla)

        segunda = tienda.realizar_venta(silla)

        assert "error" in segunda
        assert tienda.obtener_estadisticas()["ventas_realizadas"] == 1


class TestComedorEnTienda:
    def test_comedor_y_muebles_sueltos_son_independientes(
        self, tienda, comedor, silla
    ):
        tienda.agregar_comedor(comedor)
        tienda.agregar_mueble(silla)

        stats = tienda.obtener_estadisticas()
        assert stats["total_comedores"] == 1
        assert stats["total_muebles"] == 1
        # Las sillas del comedor no se cuentan como muebles sueltos.
        assert stats["tipos_muebles"] == {"Silla": 1}

    def test_precio_comedor_suma_sus_partes_con_descuento(self, comedor):
        suma_partes = comedor.mesa.calcular_precio() + sum(
            s.calcular_precio() for s in comedor.sillas
        )
        # Con 4 o más sillas el comedor tiene 5% de descuento.
        assert comedor.calcular_precio_total() == pytest.approx(
            suma_partes * 0.95, abs=0.01
        )


class TestReporte:
    def test_reporte_refleja_estado_actual(self, tienda, silla, mesa, comedor):
        tienda.agregar_mueble(silla)
        tienda.agregar_mueble(mesa)
        tienda.agregar_comedor(comedor)
        tienda.aplicar_descuento("mesa", 15)

        reporte = tienda.generar_reporte_inventario()

        assert "REPORTE DE INVENTARIO - Tienda Integración" in reporte
        assert "Total de muebles: 2" in reporte
        assert "Total de comedores: 1" in reporte
        assert "Valor total del inventario: $1158.00" in reporte
        assert "- Silla: 1 unidades" in reporte
        assert "- Mesa: 15.0%" in reporte

    def test_reporte_cambia_despues_de_vender(self, tienda, silla, mesa):
        tienda.agregar_mueble(silla)
        tienda.agregar_mueble(mesa)
        tienda.realizar_venta(mesa)

        reporte = tienda.generar_reporte_inventario()

        assert "Total de muebles: 1" in reporte
        assert "Mesa" not in reporte
