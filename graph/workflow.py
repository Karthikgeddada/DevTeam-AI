from langgraph.graph import StateGraph
from typing import TypedDict

from agents.planner_agent import planner_agent
from agents.coder_agent import coder_agent
from agents.reviewer_agent import reviewer_agent


class DevState(TypedDict):
    task: str
    plan: str
    code: str
    review: str


def planner_node(state: DevState):
    plan = planner_agent(state["task"])
    return {"plan": plan}


def coder_node(state):

    result = coder_agent(state["plan"])

    return {
        "code": result["code"]
    }


def reviewer_node(state: DevState):
    review = reviewer_agent(state["code"])
    return {"review": review}


builder = StateGraph(DevState)

builder.add_node("planner", planner_node)
builder.add_node("coder", coder_node)
builder.add_node("reviewer", reviewer_node)

builder.set_entry_point("planner")

builder.add_edge("planner", "coder")
builder.add_edge("coder", "reviewer")

builder.set_finish_point("reviewer")

workflow = builder.compile()