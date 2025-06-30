#!/usr/bin/env python3
"""
scripts/index_chunks.py

Lee los documentos planos en `settings.DATA_CHUNKS_PATH`,
los trocea y los indexa en Weaviate.

Requisitos:
    - src.vectorstore.embedder actualizado a API v4
    - langchain-huggingface instalado
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Añadimos la carpeta raíz del proyecto al sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from src.vectorstore.embedder import (           # noqa: E402
    load_documents_from_folder,
    chunk_documents,
    index_chunks,
    get_weaviate_client,                         # para cerrar al final
)
from src.config import settings                  # noqa: E402

# ──────────────────────────────────────────────────────────────── #
if __name__ == "__main__":
    input_folder = Path(settings.DATA_CHUNKS_PATH)

    start = time.perf_counter()

    # 1) Leer documentos
    docs = load_documents_from_folder(input_folder)
    print(f"📄  {len(docs)} documentos originales")

    # 2) Chunking
    chunks = chunk_documents(
        docs,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    print(f"🔪 {len(chunks)} chunks generados")

    # 3) Indexar en Weaviate
    index_chunks(chunks)
    elapsed = time.perf_counter() - start
    print(f"✅ Chunks indexados correctamente en Weaviate ({elapsed:,.1f} s)")

    # 4) Cerrar conexión (buena práctica)
    get_weaviate_client().close()
