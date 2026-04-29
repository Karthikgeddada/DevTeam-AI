import json
from config.llm_config import generate_response

async def documentation_agent(code_files: list, requirements: str) -> list:
    system_prompt = f"""You are the Documentation Agent.
Write the README.md, setup guide, and API docs based on the requirements and generated code.
You MUST output ONLY valid JSON in the following format. Do not include markdown blocks.
{{
    "files": [
        {{
            "path": "README.md",
            "content": "markdown content..."
        }}
    ]
}}

Requirements: {requirements}
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
        print(f"Failed to parse documentation output: {e}")
        return []
