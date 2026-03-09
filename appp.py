import streamlit as st
import os
import json
import zipfile
import re
import shutil

from graph.workflow import workflow

WORKSPACE = "workspace"


# -----------------------------
# Reset workspace
# -----------------------------
def reset_workspace():

    if os.path.exists(WORKSPACE):
        shutil.rmtree(WORKSPACE)

    os.makedirs(WORKSPACE)


# -----------------------------
# Make safe project name
# -----------------------------
def make_project_name(task):

    name = task.lower()

    name = re.sub(r'[^a-z0-9 ]', '', name)

    name = name.replace(" ", "-")

    return name[:40]


# -----------------------------
# Extract files safely
# -----------------------------
def extract_files(result):

    if "code" not in result:
        return []

    code = result["code"]

    # remove markdown
    code = code.replace("```json", "")
    code = code.replace("```", "")

    # extract json block
    match = re.search(r'\{[\s\S]*\}', code)

    if not match:
        return []

    json_text = match.group(0)

    try:

        data = json.loads(json_text)

        if "files" in data:

            files = data["files"]

            # remove duplicates
            unique = {}

            for f in files:
                unique[f["filename"]] = f

            return list(unique.values())

    except Exception as e:

        st.error(f"JSON parsing error: {e}")

    return []


# -----------------------------
# Clean code formatting
# -----------------------------
def clean_code(content):

    if isinstance(content, dict):
        content = content.get("body", "")

    content = content.replace("\\n", "\n")
    content = content.replace('\\"', '"')

    return content


# -----------------------------
# Run AI agents
# -----------------------------
def run_agents(task):

    reset_workspace()

    result = workflow.invoke({"task": task})

    files = extract_files(result)

    for f in files:

        filename = f["filename"]
        content = clean_code(f["content"])

        path = os.path.join(WORKSPACE, filename)

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as file:
            file.write(content)

    return result, files


# -----------------------------
# Build ZIP file
# -----------------------------
def build_zip(project_name):

    zip_name = f"{project_name}.zip"

    with zipfile.ZipFile(zip_name, "w") as zipf:

        for root, dirs, files in os.walk(WORKSPACE):

            for file in files:

                full = os.path.join(root, file)

                zipf.write(full, os.path.relpath(full, WORKSPACE))

    return zip_name


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="DevTeam AI", layout="wide")

st.title("🤖 DevTeam AI")
st.write("Generate full software projects using AI agents")

task = st.text_input(
    "Enter your project request",
    placeholder="Create a REST API for a blog platform using Express.js"
)

if st.button("Generate Project"):

    if not task:
        st.warning("Please enter a prompt")
        st.stop()

    with st.spinner("AI agents working..."):

        result, files = run_agents(task)

    # Debug output
    with st.expander("Debug Output"):
        st.json(result)

    if not files:

        st.error("No files generated")

    else:

        st.success("Project generated successfully")

        # Task
        with st.expander("Task", expanded=True):
            st.write(result.get("task"))

        # Plan
        with st.expander("Plan"):
            st.write(result.get("plan"))

        # Code files
        with st.expander("Generated Code Files"):

            for f in files:

                filename = f["filename"]
                content = clean_code(f["content"])

                with st.expander(filename):
                    st.code(content)

        # Download project
        project_name = make_project_name(task)

        zip_file = build_zip(project_name)

        with open(zip_file, "rb") as f:

            st.download_button(
                "Download Project",
                f,
                file_name=f"{project_name}.zip"
            )
