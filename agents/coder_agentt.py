from langchain_groq import ChatGroq
import os

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

def coder_agent(plan):

    prompt = f"""
You are a senior software engineer.

Based on this development plan generate a FULL PROJECT.

Return ONLY valid JSON in this format:

{{
 "files":[
   {{"filename":"file1","content":"code"}},
   {{"filename":"file2","content":"code"}}
 ]
}}

Rules:
- No explanations
- No markdown
- Only JSON
- Escape newlines with \\n

Plan:
{plan}
"""

    response = llm.invoke(prompt)

    return {
        "code": response.content
    }
