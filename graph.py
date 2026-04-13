from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, List
import operator
from agents import llm, tools

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# Create the four specialized agents
researcher = create_react_agent(llm, tools, name="Researcher")
analyst = create_react_agent(llm, tools, name="Analyst")
compliance = create_react_agent(llm, tools, name="Compliance")
reporter = create_react_agent(llm, tools, name="Reporter")

workflow = StateGraph(AgentState)

workflow.add_node("Researcher", researcher)
workflow.add_node("Analyst", analyst)
workflow.add_node("Compliance", compliance)
workflow.add_node("Reporter", reporter)

# STRICT linear flow (no loops, no repetition)
workflow.add_edge(START, "Researcher")
workflow.add_edge("Researcher", "Analyst")
workflow.add_edge("Analyst", "Compliance")
workflow.add_edge("Compliance", "Reporter")
workflow.add_edge("Reporter", END)

graph = workflow.compile()