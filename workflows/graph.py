from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from agents.requirement_agent import requirement_agent
from agents.architect_agent import architect_agent
from agents.coder_agent import coder_agent
from agents.reviewer_agent import reviewer_agent
from agents.debugger_agent import debugger_agent
from agents.tester_agent import tester_agent
from agents.documentation_agent import documentation_agent
from agents.packager_agent import packager_agent

class DevState(TypedDict):
    run_id: str
    prompt: str
    requirements: str
    architecture: str
    code_files: List[Dict[str, str]]  # [{"path": "...", "content": "..."}]
    review_comments: str
    tests_files: List[Dict[str, str]]
    docs_files: List[Dict[str, str]]
    status: str
    logs: List[str]

# Graph Nodes
async def node_requirements(state: DevState):
    state["logs"].append("Analyzing requirements...")
    reqs = await requirement_agent(state["prompt"])
    return {"requirements": reqs, "status": "analyzing_requirements"}

async def node_architecture(state: DevState):
    state["logs"].append("Designing architecture...")
    arch = await architect_agent(state["prompt"], state["requirements"])
    return {"architecture": arch, "status": "designing_architecture"}

async def node_coder(state: DevState):
    state["logs"].append("Generating code files...")
    files = await coder_agent(state["prompt"], state["architecture"])
    return {"code_files": files, "status": "generating_code"}

async def node_reviewer(state: DevState):
    state["logs"].append("Reviewing code...")
    review = await reviewer_agent(state["code_files"])
    return {"review_comments": review, "status": "reviewing"}

async def node_debugger(state: DevState):
    state["logs"].append("Debugging and fixing code...")
    fixed_files = await debugger_agent(state["code_files"], state["review_comments"])
    return {"code_files": fixed_files, "status": "debugging"}

async def node_tester(state: DevState):
    state["logs"].append("Generating tests...")
    tests = await tester_agent(state["code_files"])
    return {"tests_files": tests, "status": "testing"}

async def node_documentation(state: DevState):
    state["logs"].append("Writing documentation...")
    docs = await documentation_agent(state["code_files"], state["requirements"])
    return {"docs_files": docs, "status": "documenting"}

async def node_packager(state: DevState):
    state["logs"].append("Packaging project...")
    # Packager writes files to disk and zips them
    await packager_agent(state)
    return {"status": "completed"}

def build_graph():
    builder = StateGraph(DevState)
    builder.add_node("requirements", node_requirements)
    builder.add_node("architecture", node_architecture)
    builder.add_node("coder", node_coder)
    builder.add_node("reviewer", node_reviewer)
    builder.add_node("debugger", node_debugger)
    builder.add_node("tester", node_tester)
    builder.add_node("documentation", node_documentation)
    builder.add_node("packager", node_packager)

    builder.set_entry_point("requirements")
    builder.add_edge("requirements", "architecture")
    builder.add_edge("architecture", "coder")
    builder.add_edge("coder", "reviewer")
    builder.add_edge("reviewer", "debugger")
    builder.add_edge("debugger", "tester")
    builder.add_edge("tester", "documentation")
    builder.add_edge("documentation", "packager")
    builder.add_edge("packager", END)

    return builder.compile()

workflow = build_graph()
