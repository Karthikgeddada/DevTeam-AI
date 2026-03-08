from config.llm_config import generate_response


def tester_agent(code: str):

    prompt = f"""
    You are a QA engineer.

    Write unit tests for the following Python code.

    Code:
    {code}
    """

    tests = generate_response(prompt)

    return {
        "tests": tests
    }