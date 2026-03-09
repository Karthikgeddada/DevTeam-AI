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

Return ONLY VALID JSON.

STRICT RULES:
- Use double quotes only
- Never use single quotes
- Escape newlines using \\n
- No explanations
- No markdown
- Only JSON

Return JSON in this format:

{{
 "files":[
   {{
     "filename":"file1.py",
     "content":"code here"
   }},
   {{
     "filename":"file2.py",
     "content":"code here"
   }}
 ]
}}

Plan:
{plan}
"""

    response = llm.invoke(prompt)

    return {
        "code": response.content
    }
