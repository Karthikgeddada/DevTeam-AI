from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

models = [
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

prompt = "Explain AI in one sentence"

for model in models:
    try:
        print(f"\nTesting model: {model}")

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        print("✅ WORKS")
        print("Response:", response.text)

    except Exception as e:
        print("❌ FAILED")
        print("Error:", e)