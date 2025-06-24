# src/rag_logic/llm_openai.py
from langchain_openai import ChatOpenAI
from src.config import settings
from functools import lru_cache

@lru_cache(maxsize=1)
def get_openai_llm():
    """Instancia compartida del modelo de OpenAI."""
    print("🧠 MODELO USADO:", settings.OPENAI_MODEL_NAME)  # ← DEBUG
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model_name=settings.OPENAI_MODEL_NAME,
        temperature=0.0,
        max_tokens=settings.MAX_COMPLETION_TOKENS,
    )

