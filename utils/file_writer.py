import os
import re
import json
import ast

WORKSPACE = "workspace"


def extract_data(text):
    """
    Extract project files structure from LLM output.
    Supports JSON and Python-style dicts.
    """

    # remove markdown fences
    text = text.replace("```json", "").replace("```", "")

    match = re.search(r"\{[\s\S]*\}", text)

    if not match:
        print("No valid JSON found")
        return None

    data_text = match.group()

    # try JSON first
    try:
        return json.loads(data_text)
    except Exception:
        pass

    # fallback: python dict parser
    try:
        return ast.literal_eval(data_text)
    except Exception as e:
        print("Parse error:", e)
        return None


def write_project_files(response):

    os.makedirs(WORKSPACE, exist_ok=True)

    data = extract_data(response)

    if not data:
        return []

    created_files = []

    for file in data.get("files", []):

        filename = file.get("filename")
        content = file.get("content", "")

        path = os.path.join(WORKSPACE, filename)

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as f:
            f.write(content)

        created_files.append(filename)

    return created_files