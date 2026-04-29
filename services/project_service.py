import uuid
import asyncio
from typing import Dict
from workflows.graph import workflow, DevState

active_runs: Dict[str, DevState] = {}

async def start_generation(prompt: str) -> str:
    run_id = str(uuid.uuid4())
    state: DevState = {
        "run_id": run_id,
        "prompt": prompt,
        "requirements": "",
        "architecture": "",
        "code_files": [],
        "review_comments": "",
        "tests_files": [],
        "docs_files": [],
        "status": "starting",
        "logs": []
    }
    active_runs[run_id] = state
    
    # Run graph in background
    asyncio.create_task(run_graph(run_id, state))
    return run_id

async def run_graph(run_id: str, state: DevState):
    try:
        async for output in workflow.astream(state, stream_mode="updates"):
            for node_name, node_output in output.items():
                active_runs[run_id].update(node_output)
    except Exception as e:
        active_runs[run_id]["status"] = "failed"
        active_runs[run_id]["logs"].append(f"Error: {e}")

def get_status(run_id: str):
    return active_runs.get(run_id)

def get_files(run_id: str):
    state = active_runs.get(run_id)
    if not state: return []
    all_files = []
    all_files.extend(state.get("code_files", []))
    all_files.extend(state.get("tests_files", []))
    all_files.extend(state.get("docs_files", []))
    return all_files
