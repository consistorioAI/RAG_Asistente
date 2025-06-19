# scripts/index_chunks.py

import sys
from pathlib import Path

# Añadir el directorio raíz del proyecto al sys.path para permitir imports absolutos
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Importa las funciones desde el módulo correcto
from src.vectorstore.embedder import (
    load_documents_from_folder,
    chunk_documents,
    index_chunks
)

if __name__ == "__main__":
    input_folder = Path("data/chunks")

    # Carga y fragmenta los documentos
    docs = load_documents_from_folder(input_folder)
    chunks = chunk_documents(docs)

    print(f"{len(docs)} documentos originales")
    print(f"{len(chunks)} chunks generados")

    # Indexa los chunks en la base vectorial (Weaviate)
    index_chunks(chunks)
    print("Chunks indexados correctamente en Weaviate")
