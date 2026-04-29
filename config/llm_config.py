import os
import threading
import json
from dotenv import load_dotenv

load_dotenv()

# Attempt to load from Streamlit Secrets first
try:
    import streamlit as st
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

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
        from openai import AsyncOpenAI
        return AsyncOpenAI(
            api_key="ollama", # Ignored by Ollama
            base_url=OLLAMA_BASE_URL
        ), "ollama"
    
    # Default to Groq
    global _key_index
    if not API_KEYS:
        raise Exception("GROQ_API_KEY is missing! Please set it in Streamlit Secrets or your .env file.")
    
    with _lock:
        key = API_KEYS[_key_index]
        _key_index = (_key_index + 1) % len(API_KEYS)
    
    from groq import AsyncGroq
    return AsyncGroq(api_key=key), "groq"

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
            client, _ = get_async_client()
            response = await client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                temperature=0.2,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Local LLM failed. Ensure Ollama is running at {OLLAMA_BASE_URL}. Original error: {str(e)}")

    # Groq Key Failover Logic
    for _ in range(max(1, len(API_KEYS))):
        try:
            client, _ = get_async_client()
            response = await client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                temperature=0.2,
                max_tokens=8192
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            print(f"API Attempt failed: {error_msg}")
            if "invalid_api_key" in error_msg.lower() or "401" in error_msg or "organization_restricted" in error_msg.lower() or "rate_limit" in error_msg.lower() or "connection" in error_msg.lower():
                continue
            raise Exception(f"Groq API Error: {error_msg}")
            
    raise Exception("AI generation failed: All configured Groq API keys failed. Check Streamlit Secrets.")
