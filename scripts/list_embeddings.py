# scripts/list_embeddings.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import weaviate
from src.config import settings

if __name__ == "__main__":
    client = weaviate.Client(url=settings.WEAVIATE_URL)

    # Ejecuta una consulta para obtener objetos con sus vectores
    response = client.query.get("LegalDocs", ["text", "_additional { vector }"]).with_limit(5).do()

    print("\nPrimeros 5 vectores almacenados:\n")
    for i, item in enumerate(response["data"]["Get"]["LegalDocs"]):
        print(f"--- Embedding {i+1} ---")
        print("Texto:", item["text"][:100], "...")
        print("Vector (dimensión:", len(item["_additional"]["vector"]), ")")
        print(item["_additional"]["vector"][:5], "...")  # Mostramos solo los primeros 5 valores
        print()
