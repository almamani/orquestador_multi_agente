from decimal import Decimal
from typing import Literal

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field

class VentaPeriodo(BaseModel):
    """Ventas de un producto durante un mes."""

    producto: str = Field(min_length=1)
    periodo: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    unidades: int = Field(ge=0)
    importe: Decimal = Field(ge=0)
    fuente: str = Field(min_length=1)


class ResearchArtifact(BaseModel):
    """Datos recuperados por el investigador."""

    periodo_base: str = Field(
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    )
    periodo_actual: str = Field(
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    )
    ventas: list[VentaPeriodo] = Field(min_length=1)


class ComparacionProducto(BaseModel):
    """Comparación de importes entre dos períodos."""

    producto: str = Field(min_length=1)
    importe_base: Decimal = Field(ge=0)
    importe_actual: Decimal = Field(ge=0)
    diferencia: Decimal
    variacion_porcentual: float | None
    fuentes: list[str] = Field(min_length=1)


class AnalysisArtifact(BaseModel):
    """Resultado del análisis comercial."""

    comparaciones: list[ComparacionProducto] = Field(min_length=1)


class AgentState(MessagesState):
    """Información compartida por los nodos del grafo."""

    investigacion: ResearchArtifact | None
    analisis: AnalysisArtifact | None

    next_agent: Literal[
        "investigador",
        "analista",
        "sintesis",
        "FINALIZAR",
    ]

    instrucciones: str
    errores_validacion: list[str]
    pasos: int
    informe_final: str
