import json
from config.llm_config import generate_response

async def tester_agent(code_files: list) -> list:
    files_str = json.dumps(code_files, indent=2)
    system_prompt = f"""You are the Tester Agent.
Generate test cases and validation scripts for the provided code files.
You MUST output ONLY valid JSON in the following format. Do not include markdown blocks.
{{
    "files": [
        {{
            "path": "tests/test_main.py",
            "content": "pytest code..."
        }}
    ]
}}

Code Files: {files_str}
"""
    response = await generate_response(system_prompt)
    try:
        if response.startswith("```json"):
            response = response.strip("```json").strip("```")
        elif response.startswith("```"):
            response = response.strip("```")
        data = json.loads(response)
        return data.get("files", [])
    except Exception as e:
        print(f"Failed to parse tester output: {e}")
        return []
