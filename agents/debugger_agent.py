import json
from config.llm_config import generate_response

async def debugger_agent(code_files: list, review_comments: str) -> list:
    if "LGTM" in review_comments.upper() and len(review_comments) < 50:
        return code_files

    files_str = json.dumps(code_files, indent=2)
    system_prompt = f"""You are the Debugger Agent.
Based on the code files and the reviewer's comments, apply fixes and generate the corrected source code files.
You MUST output ONLY valid JSON in the following format. Do not include markdown blocks or any other text.
{{
    "files": [
        {{
            "path": "backend/main.py",
            "content": "fixed full source code..."
        }}
    ]
}}

Code Files: {files_str}
Review Comments: {review_comments}
"""
    response = await generate_response(system_prompt)
    try:
        if response.startswith("```json"):
            response = response.strip("```json").strip("```")
        elif response.startswith("```"):
            response = response.strip("```")
        data = json.loads(response)
        return data.get("files", code_files)
    except Exception as e:
        print(f"Failed to parse debugger output: {e}")
        return code_files
