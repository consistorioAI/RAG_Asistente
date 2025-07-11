# scripts/query_retriever.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.rag_logic.retriever_module import get_retriever
from src.config import settings
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpt_id", default="default", help="Perfil de GPT")
    args = parser.parse_args()

    retriever = get_retriever(k=settings.RETRIEVER_K,
                              collection_name=f"LegalDocs_{args.gpt_id}")
    
    query = input("Introduce tu pregunta o búsqueda: ")

    results = retriever.get_relevant_documents(query)

    print("\nResultados relevantes:")
    for i, doc in enumerate(results):
        print(f"\n--- Documento {i+1} ---")
        print(doc.page_content[:500], "...")
        print("Metadatos:", doc.metadata)
