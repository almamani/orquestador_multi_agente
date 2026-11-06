from typing import Literal

from langgraph.graph import END, StateGraph

from agents.analyst_agent import analyst_node
from agents.research_agent import researcher_node
from agents.supervisor import supervisor_node
from agents.synthesis_agent import synthesis_node
from state import AgentState


def elegir_destino(
    state: AgentState,
) -> Literal["investigador", "analista", "sintesis", "FINALIZAR"]:
    return state["next_agent"]


workflow = StateGraph(AgentState)

# Registrar los nodos.
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("investigador", researcher_node)
workflow.add_node("analista", analyst_node)
workflow.add_node("sintesis", synthesis_node)

# El supervisor recibe el pedido inicial.
workflow.set_entry_point("supervisor")

# Cada especialista devuelve el control al supervisor.
workflow.add_edge("investigador", "supervisor")
workflow.add_edge("analista", "supervisor")
workflow.add_edge("sintesis", "supervisor")

# La decisión del supervisor determina el próximo destino.
workflow.add_conditional_edges(
    "supervisor",
    elegir_destino,
    {
        "investigador": "investigador",
        "analista": "analista",
        "sintesis": "sintesis",
        "FINALIZAR": END,
    },
)

app = workflow.compile()