import operator
from typing import Annotated, Literal, List

from pydantic import BaseModel
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from agents import llm, researcher, analyst, compliance, reporter


# ──────────────────────────────────────────────────────────────
# State
# ──────────────────────────────────────────────────────────────

class AgentState(BaseModel):
    messages: Annotated[List[BaseMessage], operator.add] = []
    next: str = ""
    completed: List[str] = []

    class Config:
        arbitrary_types_allowed = True


# ──────────────────────────────────────────────────────────────
# Supervisor structured output
# ──────────────────────────────────────────────────────────────

AGENTS = ["Researcher", "Analyst", "Compliance", "Reporter"]
RouteOptions = Literal["Researcher", "Analyst", "Compliance", "Reporter", "FINISH"]


class RouteDecision(BaseModel):
    """Routing decision from the supervisor."""
    next: RouteOptions
    reasoning: str


SUPERVISOR_PROMPT = """You are the Supervisor of a senior bank finance team.
Route work through the team IN THIS EXACT ORDER — no exceptions:
  1. Researcher
  2. Analyst
  3. Compliance
  4. Reporter
  5. FINISH

The agents already completed are listed below. NEVER route to a completed agent again.
Always pick the next uncompleted agent in the sequence above.
Once Reporter is done, respond with FINISH.

Completed agents: {completed}
"""


supervisor_llm = llm.with_structured_output(RouteDecision)


def supervisor_node(state: AgentState) -> dict:
    completed_str = ", ".join(state.completed) if state.completed else "none"
    prompt = SUPERVISOR_PROMPT.format(completed=completed_str)
    messages = [SystemMessage(content=prompt)] + list(state.messages)
    decision = supervisor_llm.invoke(messages)

    # Hard override: never re-route to a completed agent
    if decision.next in state.completed:
        remaining = [a for a in AGENTS if a not in state.completed]
        decision.next = remaining[0] if remaining else "FINISH"

    return {"next": decision.next}


# ──────────────────────────────────────────────────────────────
# Agent node wrappers
# ──────────────────────────────────────────────────────────────

def researcher_node(state: AgentState) -> dict:
    result = researcher.invoke({"messages": list(state.messages)})
    return {"messages": result["messages"], "completed": state.completed + ["Researcher"]}


def analyst_node(state: AgentState) -> dict:
    result = analyst.invoke({"messages": list(state.messages)})
    return {"messages": result["messages"], "completed": state.completed + ["Analyst"]}


def compliance_node(state: AgentState) -> dict:
    result = compliance.invoke({"messages": list(state.messages)})
    return {"messages": result["messages"], "completed": state.completed + ["Compliance"]}


def reporter_node(state: AgentState) -> dict:
    result = reporter.invoke({"messages": list(state.messages)})
    return {"messages": result["messages"], "completed": state.completed + ["Reporter"]}


# ──────────────────────────────────────────────────────────────
# Routing function
# ──────────────────────────────────────────────────────────────

def route_from_supervisor(state: AgentState) -> str:
    if state.next == "FINISH" or set(AGENTS).issubset(set(state.completed)):
        return END
    return state.next


# ──────────────────────────────────────────────────────────────
# Build graph
# ──────────────────────────────────────────────────────────────

workflow = StateGraph(AgentState)

workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Researcher", researcher_node)
workflow.add_node("Analyst", analyst_node)
workflow.add_node("Compliance", compliance_node)
workflow.add_node("Reporter", reporter_node)

workflow.add_edge(START, "Supervisor")

workflow.add_conditional_edges(
    "Supervisor",
    route_from_supervisor,
    {
        "Researcher": "Researcher",
        "Analyst": "Analyst",
        "Compliance": "Compliance",
        "Reporter": "Reporter",
        END: END,
    },
)

for agent_name in AGENTS:
    workflow.add_edge(agent_name, "Supervisor")

graph = workflow.compile(checkpointer=None)
