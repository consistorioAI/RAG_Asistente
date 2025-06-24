# src/rag_logic/llm_openai.py
from langchain_openai import ChatOpenAI
from src.config import settings

def get_openai_llm():
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL_NAME,
        temperature=0.0,
        max_tokens=settings.MAX_COMPLETION_TOKENS
    )
