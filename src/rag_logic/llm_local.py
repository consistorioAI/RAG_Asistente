# src/rag_logic/llm_local.py

from langchain_community.llms import LlamaCpp
from pathlib import Path
from functools import lru_cache
from src.config import settings


@lru_cache(maxsize=1)
def get_local_llm():
    """Devuelve una instancia compartida del LLM local."""

    return LlamaCpp(
        model_path=str(settings.LLM_MODEL_PATH),  # requerido por Pydantic
        model_url=settings.LLM_MODEL_URL,
        n_ctx=4096,
        temperature=0.0,
        verbose=False,
    )
