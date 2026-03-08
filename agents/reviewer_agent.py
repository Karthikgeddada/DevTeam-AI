from config.llm_config import generate_response


def reviewer_agent(code: str):

    prompt = f"""
Review the following code and suggest improvements.

Code:
{code}
"""

    review = generate_response(prompt)

    return review