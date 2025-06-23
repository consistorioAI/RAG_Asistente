# src/rag_logic/llm_local.py

from langchain_community.llms import LlamaCpp  
from pathlib import Path


def get_local_llm():
    # Ruta real al modelo que ya estás sirviendo por el servidor
    dummy_model_path = Path("C:/Users/ramon/ModelosLLM/mistral-7b-instruct-v0.1.Q4_K_M.gguf")

    return LlamaCpp(
        model_path=str(dummy_model_path),  # requerido por Pydantic
        model_url="http://localhost:8001",  # este prevalece
        n_ctx=4096,
        temperature=0.0,
        verbose=False
    )
