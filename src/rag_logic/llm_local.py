# src/rag_logic/llm_local.py

from langchain_community.llms import LlamaCpp  
from pathlib import Path

def get_local_llm():
    model_path = Path("C:/Users/ramon/ModelosLLM/mistral-7b-instruct-v0.1.Q4_K_M.gguf")

    llm = LlamaCpp(
        model_path=str(model_path),
        n_ctx=4096,  # Ajustable según el modelo
        n_threads=8,         # Ajustable según CPU
        n_gpu_layers=50,     # Solo si usas GPU
        temperature=0.0,
        verbose=False
    )
    return llm
