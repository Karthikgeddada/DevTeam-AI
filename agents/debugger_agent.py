from config.llm_config import generate_response


def debugger_agent(code: str):

    prompt = f"""
    You are an expert Python debugger.

    Analyze the following code and fix any potential bugs.

    Code:
    {code}
    """

    fixed_code = generate_response(prompt)

    return {
        "fixed_code": fixed_code
    }