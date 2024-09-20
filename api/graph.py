from langgraph.graph import END, StateGraph
from models.agent_state import AgentState
from utils.functions import CallChain

def load_graph():
    call_chain = CallChain()

    workflow = StateGraph(AgentState)

    workflow.add_node("get_language", call_chain.get_language)  

    workflow.add_node("rag", call_chain.rag)  
    
    workflow.set_entry_point("get_language")

    workflow.add_edge("get_language", "rag")

    workflow.add_edge("rag", END)

    return workflow.compile()