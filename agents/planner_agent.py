from config.llm_config import generate_response


def planner_agent(task: str):

    prompt = f"""
Break this task into clear development steps.

Task:
{task}

Return numbered steps.
"""

    plan = generate_response(prompt)

    return plan