import streamlit as st
import asyncio
import os
import zipfile
import uuid
from workflows.graph import workflow, DevState
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="DevTeam AI", page_icon="🚀", layout="wide")

st.title("🚀 DevTeam AI - Autonomous Software Studio")
st.markdown("Describe your project and our AI team will build it automatically.")

# Ensure generated projects directory exists
os.makedirs("generated_projects", exist_ok=True)

async def run_generation_workflow(prompt: str, run_id: str):
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
        "logs": ["Initializing DevTeam AI Agents..."]
    }

    progress_bar = st.progress(5)
    status_text = st.empty()
    log_container = st.empty()

    status_map = {
        'starting': 5,
        'analyzing_requirements': 15,
        'designing_architecture': 30,
        'generating_code': 50,
        'reviewing': 65,
        'debugging': 75,
        'testing': 85,
        'documenting': 95,
        'completed': 100
    }

    try:
        async for output in workflow.astream(state, stream_mode="updates"):
            for node_name, node_output in output.items():
                state.update(node_output)
                
                curr_status = state.get("status", "running")
                pct = status_map.get(curr_status, 5)
                
                progress_bar.progress(pct)
                status_text.markdown(f"**Current Phase:** {curr_status.replace('_', ' ').title()} ({pct}%)")
                
                # Render logs
                logs = state.get("logs", [])
                log_text = "\n".join([f"> {l}" for l in logs])
                log_container.code(log_text, language="bash")
                
    except Exception as e:
        st.error(f"Generation failed: {str(e)}")
        state["status"] = "failed"

    return state

prompt = st.text_area("What do you want to build?", height=100, placeholder="E.g., Build an ecommerce website with admin panel in Python FastAPI and React...")

if st.button("Generate Project ✨"):
    if not prompt:
        st.warning("Please enter a prompt to begin.")
    else:
        run_id = str(uuid.uuid4())
        
        with st.spinner("Firing up the AI Engineering Team..."):
            final_state = asyncio.run(run_generation_workflow(prompt, run_id))
            
        if final_state.get("status") == "completed":
            st.success("Project generated successfully!")
            
            # Aggregate files
            all_files = []
            all_files.extend(final_state.get("code_files", []))
            all_files.extend(final_state.get("tests_files", []))
            all_files.extend(final_state.get("docs_files", []))
            
            if all_files:
                st.subheader("📁 Generated Source Code")
                
                # File Explorer
                file_paths = [f.get("path") for f in all_files if f.get("path")]
                selected_file = st.selectbox("Select a file to preview:", file_paths)
                
                for f in all_files:
                    if f.get("path") == selected_file:
                        content = f.get("content", "")
                        # Guess language for syntax highlighting
                        lang = "python"
                        if selected_file.endswith(".js"): lang = "javascript"
                        elif selected_file.endswith(".html"): lang = "html"
                        elif selected_file.endswith(".css"): lang = "css"
                        elif selected_file.endswith(".md"): lang = "markdown"
                        elif selected_file.endswith(".json"): lang = "json"
                        
                        st.code(content, language=lang)
                        break
                        
                # Download ZIP
                zip_path = f"generated_projects/{run_id}.zip"
                if os.path.exists(zip_path):
                    with open(zip_path, "rb") as file:
                        btn = st.download_button(
                            label="Download Complete Project (ZIP) 📦",
                            data=file,
                            file_name=f"devteam_project_{run_id}.zip",
                            mime="application/zip"
                        )
