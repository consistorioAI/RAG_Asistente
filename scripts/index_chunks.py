# scripts/index_chunks.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.vectorstore.embedder import (
    load_documents_from_folder,
    chunk_documents,
    index_chunks
)
from src.config import settings

if __name__ == "__main__":
    input_folder = settings.DATA_CHUNKS_PATH

    docs = load_documents_from_folder(input_folder)
    chunks = chunk_documents(
        docs,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )

    print(f"{len(docs)} documentos originales")
    print(f"{len(chunks)} chunks generados")

    index_chunks(chunks)
    print("Chunks indexados correctamente en Weaviate")
