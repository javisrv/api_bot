from langgraph.graph import END, StateGraph
from models.agent_state import AgentState
from utils.functions import CallChain
from utils.auxiliar_functions import edge_has_name, edge_has_language

def load_graph():
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