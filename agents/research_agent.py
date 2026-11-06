import sqlite3

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from settings import llm
from state import AgentState, ResearchArtifact
from tools import ConsultaVentasInput, consultar_ventas


RESEARCH_PROMPT = """
Sos un especialista en recuperación de datos comerciales.

Identificá los dos períodos mensuales indicados en la tarea.
El período base es la referencia y el período actual es el que
se compara con esa referencia.

Devolvé ambos períodos usando el esquema solicitado,
con formato YYYY-MM.
"""

selector_periodos = llm.with_structured_output(ConsultaVentasInput)


async def researcher_node(state: AgentState) -> dict:
    print("--- Investigador: consultando ventas ---")

    try:
        instrucciones = state["instrucciones"]

        if not instrucciones.strip():
            raise ValueError(
                "El investigador necesita instrucciones con los dos períodos."
            )

        consulta = await selector_periodos.ainvoke(
            [
                SystemMessage(content=RESEARCH_PROMPT),
                HumanMessage(content=instrucciones),
            ]
        )

        resultado = await consultar_ventas.ainvoke(
            consulta.model_dump()
        )

        investigacion = ResearchArtifact.model_validate(resultado)

        mensaje = (
            f"Ventas recuperadas para {investigacion.periodo_base} "
            f"y {investigacion.periodo_actual}. "
            f"Registros encontrados: {len(investigacion.ventas)}."
        )

        return {
            "investigacion": investigacion,
            "analisis": None,
            "errores_validacion": [],
            "messages": [
                AIMessage(content=mensaje, name="investigador")
            ],
        }

    except (ValueError, sqlite3.Error, OSError) as error:
        detalle = f"Investigador: {error}"

        return {
            "investigacion": None,
            "analisis": None,
            "errores_validacion": [detalle],
            "messages": [
                AIMessage(content=detalle, name="investigador")
            ],
        }