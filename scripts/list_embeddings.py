# scripts/list_embeddings.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from weaviate import WeaviateClient
from src.config import settings

if __name__ == "__main__":
    client = WeaviateClient(url=settings.WEAVIATE_URL)

    # Ejecuta una consulta para obtener objetos con sus vectores
    response = (
        client.collections.get("LegalDocs")
        .query.fetch_objects(return_properties=["text"], include_vector=True, limit=5)
    )

    print("\nPrimeros 5 vectores almacenados:\n")
    for i, item in enumerate(response.objects):
        print(f"--- Embedding {i+1} ---")
        print("Texto:", item.properties["text"][:100], "...")
        vector = item.vector
        print("Vector (dimensión:", len(vector), ")")
        print(vector[:5], "...")  # Mostramos solo los primeros 5 valores
        print()
