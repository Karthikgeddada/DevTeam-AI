import streamlit as st
import os
import json
import zipfile
import re
import shutil

from graph.workflow import workflow

WORKSPACE = "workspace"

# reset workspace each run
if os.path.exists(WORKSPACE):
    shutil.rmtree(WORKSPACE)

os.makedirs(WORKSPACE, exist_ok=True)


# -----------------------------
# Extract JSON safely (robust)
# -----------------------------
def extract_json(text):

    if not text:
        return None

    # try direct parse
    try:
        return json.loads(text)
    except:
        pass

    # try extracting JSON block
    match = re.search(r"\{[\s\S]*\}", text)

    if not match:
        return None

    json_str = match.group()

    # repair common LLM mistakes
    json_str = json_str.replace("'", '"')
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)

    try:
        return json.loads(json_str)
    except Exception as e:
        st.error(f"JSON repair failed: {e}")
        return None


# -----------------------------
# Clean LLM content
# -----------------------------
def clean_content(content):

    if not content:
        return content

    content = content.replace("\\n", "\n")
    content = content.replace('\\"', '"')

    return content


# -----------------------------
# Run AI Agents
# -----------------------------
def run_devteam(task):

    result = workflow.invoke({"task": task})

    st.expander("Debug Output").write(result)

    files = []

    if isinstance(result, dict):

        if "files" in result:
            files = result["files"]

        elif "code" in result:

            data = extract_json(result["code"])

            if data and "files" in data:
                files = data["files"]

    # retry if JSON broken
    if not files:

        st.warning("AI returned invalid JSON. Attempting repair...")

        fix_prompt = f"""
Fix this response and return ONLY valid JSON.

Format:

{{
 "files":[
   {{
     "filename":"example.py",
     "content":"print('hello')"
   }}
 ]
}}

Response:
{result}
"""

        retry = workflow.invoke({"task": fix_prompt})

        data = extract_json(str(retry))

        if data and "files" in data:
            files = data["files"]

    # write files
    for f in files:

        path = os.path.join(WORKSPACE, f["filename"])

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as file:
            file.write(clean_content(f["content"]))

    return files, result


# -----------------------------
# ZIP generator
# -----------------------------
def create_zip():

    zip_path = "project.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:

        for root, dirs, files in os.walk(WORKSPACE):

            for file in files:

                full = os.path.join(root, file)

                zipf.write(full, os.path.relpath(full, WORKSPACE))

    return zip_path


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="DevTeam AI", layout="wide")

st.title("🤖 DevTeam AI")
st.caption("Multi-Agent AI Software Development System")

st.write("Generate full software projects using AI agents")

task = st.text_input(
    "Enter your project request",
    placeholder="Build a full Twitter clone with backend and frontend"
)

if st.button("Generate Project"):

    if not task:
        st.warning("Please enter a request")
        st.stop()

    with st.spinner("AI agents working..."):

        files, raw = run_devteam(task)

    if not files:

        st.error("No files generated")

        st.subheader("Raw LLM Output")

        st.code(str(raw))

    else:

        st.success("Project generated successfully")

        st.subheader("Task")
        st.write(task)

        st.subheader("Generated Code Files")

        for f in files:

            st.markdown(f"### {f['filename']}")

            st.code(clean_content(f["content"]))

        zip_file = create_zip()

        with open(zip_file, "rb") as f:

            st.download_button(
                "Download Project",
                f,
                file_name="ai_project.zip"
            )
