from langchain_core.messages import AIMessage

from state import AgentState, AnalysisArtifact, ResearchArtifact
from tools import analizar_ventas


async def analyst_node(state: AgentState) -> dict:
    print("--- Analista: comparando ventas ---")

    try:
        investigacion = state.get("investigacion")

        if investigacion is None:
            raise ValueError(
                "Se necesita una investigación válida para analizar."
            )

        investigacion = ResearchArtifact.model_validate(investigacion)

        resultado = await analizar_ventas.ainvoke(
            {
                "investigacion": investigacion.model_dump(mode="json")
            }
        )

        analisis = AnalysisArtifact.model_validate(resultado)

        mensaje = (
            f"Análisis completado. "
            f"Productos comparados: {len(analisis.comparaciones)}. "
            "Cada comparación conserva las fuentes utilizadas."
        )

        return {
            "analisis": analisis,
            "errores_validacion": [],
            "messages": [
                AIMessage(content=mensaje, name="analista")
            ],
        }

    except ValueError as error:
        detalle = f"Analista: {error}"

        return {
            "analisis": None,
            "errores_validacion": [detalle],
            "messages": [
                AIMessage(content=detalle, name="analista")
            ],
        }