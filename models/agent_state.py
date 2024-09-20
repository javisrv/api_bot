import operator
from typing import TypedDict, Annotated, Union
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    input: str
    input_translated: str
    agent_outcome: Union[AgentAction, AgentFinish, None]
    language: str
    tokens_used: dict