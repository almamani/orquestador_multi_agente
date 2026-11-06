import asyncio

from langchain_core.messages import HumanMessage

from graph import app
from state import AgentState


async def main():
    pedido = (
        "Compará las ventas de septiembre de 2026 "
        "como período base contra octubre de 2026 "
        "como período actual. Calculá la variación por producto "
        "y prepará un informe con conclusiones y fuentes."
    )

    estado_inicial: AgentState = {
        "messages": [HumanMessage(content=pedido)],
        "investigacion": None,
        "analisis": None,
        "next_agent": "investigador",
        "instrucciones": "",
        "errores_validacion": [],
        "pasos": 0,
        "informe_final": "",
    }

    informe_final = ""

    print(f"Pedido: {pedido}\n")

    async for actualizacion in app.astream(
        estado_inicial,
        config={"recursion_limit": 30},
        stream_mode="updates",
    ):
        for nodo, datos in actualizacion.items():
            print(f"Nodo '{nodo}' finalizado.")

            if nodo == "supervisor":
                print(f"  Próximo destino: {datos['next_agent']}")
                print(f"  Instrucciones: {datos['instrucciones']}")

            for error in datos.get("errores_validacion", []):
                print(f"  Revisión pendiente: {error}")

            if "informe_final" in datos:
                informe_final = datos["informe_final"]

                if nodo == "sintesis":
                    print("--- Borrador enviado al supervisor ---")
                    print(informe_final)

            print()

    print("--- Resultado final ---")
    print(informe_final or "El proceso terminó sin generar un informe.")

if __name__ == "__main__":
    asyncio.run(main())