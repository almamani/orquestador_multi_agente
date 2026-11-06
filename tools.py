import sqlite3
from decimal import Decimal

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from setup_db import DB_PATH
from state import (
    AnalysisArtifact,
    ComparacionProducto,
    ResearchArtifact,
    VentaPeriodo,
)


class ConsultaVentasInput(BaseModel):
    periodo_base: str = Field(
        description="Mes de referencia, con formato YYYY-MM.",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    )
    periodo_actual: str = Field(
        description="Mes que se comparará con el de referencia.",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    )


@tool(args_schema=ConsultaVentasInput)
def consultar_ventas(
    periodo_base: str,
    periodo_actual: str,
) -> dict:
    """Consulta ventas mensuales de todos los productos para dos meses.

    Devuelve los períodos solicitados y los registros disponibles,
    incluyendo producto, unidades, importe monetario y fuente.
    No calcula diferencias ni porcentajes.
    """
    if periodo_base == periodo_actual:
        raise ValueError("Elegí dos períodos diferentes para comparar.")

    if not DB_PATH.is_file():
        raise FileNotFoundError(
            "No existe la base de ventas. Ejecutá python setup_db.py."
        )

    # Abrimos la base en modo de solo lectura.
    uri = DB_PATH.as_uri() + "?mode=ro"

    with sqlite3.connect(uri, uri=True) as conexion:
        conexion.row_factory = sqlite3.Row

        filas = conexion.execute(
            """
            SELECT producto, periodo, unidades, importe_centavos
            FROM ventas_mensuales
            WHERE periodo IN (?, ?)
            ORDER BY producto, periodo
            """,
            (periodo_base, periodo_actual),
        ).fetchall()

    periodos_encontrados = {fila["periodo"] for fila in filas}

    if periodos_encontrados != {periodo_base, periodo_actual}:
        raise ValueError(
            "Se necesitan datos para ambos períodos. "
            f"Períodos encontrados: {sorted(periodos_encontrados)}."
        )

    ventas = [
        VentaPeriodo(
            producto=fila["producto"],
            periodo=fila["periodo"],
            unidades=fila["unidades"],
            importe=Decimal(fila["importe_centavos"]) / Decimal("100"),
            fuente=(
                f"ventas_mensuales|{fila['producto']}|{fila['periodo']}"
            ),
        )
        for fila in filas
    ]

    investigacion = ResearchArtifact(
        periodo_base=periodo_base,
        periodo_actual=periodo_actual,
        ventas=ventas,
    )

    return investigacion.model_dump(mode="json")


class AnalisisVentasInput(BaseModel):
    investigacion: ResearchArtifact = Field(
        description="Ventas recuperadas para los dos períodos a comparar."
    )


@tool(args_schema=AnalisisVentasInput)
def analizar_ventas(investigacion: ResearchArtifact) -> dict:
    """Compara los importes de ventas por producto entre dos meses.

    Calcula diferencia monetaria y variación porcentual.
    Requiere un registro por producto para cada período.
    Si el importe base es cero, devuelve variacion_porcentual=None.
    Conserva las fuentes de los registros utilizados.
    """
    investigacion = ResearchArtifact.model_validate(investigacion)

    periodo_base = investigacion.periodo_base
    periodo_actual = investigacion.periodo_actual

    if periodo_base == periodo_actual:
        raise ValueError("Los períodos de comparación deben ser diferentes.")

    periodos_esperados = {periodo_base, periodo_actual}
    ventas_por_producto: dict[str, dict[str, VentaPeriodo]] = {}

    for venta in investigacion.ventas:
        if venta.periodo not in periodos_esperados:
            raise ValueError(
                f"Período inesperado para {venta.producto}: "
                f"{venta.periodo}."
            )

        registros = ventas_por_producto.setdefault(venta.producto, {})

        if venta.periodo in registros:
            raise ValueError(
                f"Registro duplicado: {venta.producto}, {venta.periodo}."
            )

        registros[venta.periodo] = venta

    comparaciones = []

    for producto, registros in sorted(ventas_por_producto.items()):
        if set(registros) != periodos_esperados:
            raise ValueError(
                f"Faltan datos de alguno de los períodos para {producto}."
            )

        venta_base = registros[periodo_base]
        venta_actual = registros[periodo_actual]

        diferencia = venta_actual.importe - venta_base.importe

        variacion = None
        if venta_base.importe != 0:
            porcentaje = (
                diferencia / venta_base.importe
            ) * Decimal("100")
            variacion = round(float(porcentaje), 2)

        comparaciones.append(
            ComparacionProducto(
                producto=producto,
                importe_base=venta_base.importe,
                importe_actual=venta_actual.importe,
                diferencia=diferencia,
                variacion_porcentual=variacion,
                fuentes=[venta_base.fuente, venta_actual.fuente],
            )
        )

    analisis = AnalysisArtifact(comparaciones=comparaciones)

    return analisis.model_dump(mode="json")