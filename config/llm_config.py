import os
import threading
from openai import AsyncOpenAI
import json
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# LLM Provider Configuration
# -----------------------------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant" if LLM_PROVIDER == "groq" else "llama3:8b")

# -----------------------------
# API Key Rotation (Groq only)
# -----------------------------
def _load_keys():
    raw_keys = os.getenv("GROQ_API_KEYS") or os.getenv("GROQ_API_KEY") or ""
    keys = [k.strip().strip('"').strip("'") for k in raw_keys.split(",") if k.strip()]
    return keys

API_KEYS = _load_keys()
_key_index = 0
_lock = threading.Lock()

def get_async_client():
    if LLM_PROVIDER == "ollama":
        return AsyncOpenAI(
            api_key="ollama", # Ignored by Ollama
            base_url=OLLAMA_BASE_URL
        )
    
    # Default to Groq key rotation
    global _key_index
    if not API_KEYS:
        # Fallback to local if no keys found but not explicitly set
        return AsyncOpenAI(api_key="ollama", base_url=OLLAMA_BASE_URL)
    
    with _lock:
        key = API_KEYS[_key_index]
        _key_index = (_key_index + 1) % len(API_KEYS)
    
    return AsyncOpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1"
    )

async def generate_response(prompt_or_messages) -> str:
    """
    Unified ASYNC LLM generation supporting Groq (Free Tier) and Ollama (Local).
    """
    if isinstance(prompt_or_messages, str):
        messages = [{"role": "user", "content": prompt_or_messages}]
    else:
        messages = prompt_or_messages

    # For Local Ollama, we don't need failover
    if LLM_PROVIDER == "ollama":
        try:
            client = get_async_client()
            response = await client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                temperature=0.2,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: Local LLM failed. Ensure Ollama is running at {OLLAMA_BASE_URL}. Original error: {str(e)}"

    # Groq Key Failover Logic
    for _ in range(max(1, len(API_KEYS))):
        try:
            client = get_async_client()
            response = await client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                temperature=0.2,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            print(f"API Attempt failed: {error_msg}")
            if "invalid_api_key" in error_msg.lower() or "401" in error_msg or "organization_restricted" in error_msg.lower():
                continue
            break
            
    return "Error: AI generation failed after multiple key attempts. Try switching to LLM_PROVIDER=ollama"
