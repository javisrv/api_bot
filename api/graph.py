from langgraph.graph import END, StateGraph
from models.agent_state import AgentState
from utils.functions import CallChain
from utils.auxiliar_functions import edge_has_name, edge_has_language

def load_graph() -> StateGraph:
    """
    Crea y configura el flujo de nodos.

    Esta función inicializa una instancia de `CallChain`, que contiene las funciones 
    necesarias para manejar las interacciones con el LLM. A continuación, se crea un 
    `StateGraph` que representa el flujo de estados y transiciones que ocurren durante
    cada interaccióin. Se añaden nodos que corresponden a diferentes etapas del flujo, 
    como solicitar el nombre, el idioma, interactuar con el RAG y añadir un nodo de 
    personalidad.

    Se configuran las transiciones condicionales entre los nodos en función de las 
    condiciones `edge_has_name` y `edge_has_language`, y se establecen los puntos de 
    entrada y salida del flujo de trabajo.

    Returns:
        El gráfico de estados compilado, que puede ser utilizado para manejar el 
        flujo de interacción del agente.
    """
    call_chain = CallChain()

    workflow = StateGraph(AgentState)

    workflow.add_node("request_name", call_chain.request_name)

    workflow.add_node("request_language", call_chain.request_language)  

    workflow.add_node("rag", call_chain.rag)  

    workflow.add_node("personality", call_chain.personality)  
    
    workflow.set_entry_point("request_name")

    workflow.add_conditional_edges(
        "request_name",  
        edge_has_name,
        {
            "request": "request_language",  
            "end": END  
        }
    )

    workflow.add_conditional_edges(
        "request_language",  
        edge_has_language,
        {
            "rag": "rag",  
            "end": END  
        }
    )

    workflow.add_edge("rag", "personality")

    workflow.add_edge("personality", END)

    return workflow.compile()