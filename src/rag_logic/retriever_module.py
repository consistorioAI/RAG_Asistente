from functools import lru_cache
from urllib.parse import urlparse

from langchain_huggingface import HuggingFaceEmbeddings          # ← nueva ruta
from langchain_weaviate import WeaviateVectorStore
from weaviate import connect_to_custom

from src.config import settings


# ──────────────────────────────────────────────────────────────
# 1) Cliente Weaviate (anónimo)
# ──────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _get_weaviate_client():
    """Devuelve un WeaviateClient ya conectado (cacheado)."""
    parsed = urlparse(settings.WEAVIATE_URL)
    host = parsed.hostname or "localhost"
    secure = parsed.scheme == "https"
    http_port = parsed.port or (443 if secure else 80)

    client = connect_to_custom(
        host,
        http_port=http_port,
        http_secure=secure,
        grpc_host=host,
        grpc_port=50051,   # ajusta si tu instancia usa otro
        grpc_secure=secure,
    )
    client.connect()
    return client


# ──────────────────────────────────────────────────────────────
# 2) Embedder HuggingFace
# ──────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _get_embedder():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        encode_kwargs={"batch_size": settings.BATCH_SIZE},
    )


# ──────────────────────────────────────────────────────────────
# 3) Utilidades
# ──────────────────────────────────────────────────────────────
def ensure_collection_exists(client, collection_name: str) -> None:
    if not client.collections.exists(collection_name):
        raise RuntimeError(
            f"Colección '{collection_name}' no encontrada en Weaviate. "
            "Ejecuta `scripts/sync_and_index.py --gpt_id <id>` antes de consultar."
        )


def get_retriever(k: int = settings.RETRIEVER_K, collection_name: str = "LegalDocs"):
    client = _get_weaviate_client()
    ensure_collection_exists(client, collection_name)
    embedder = _get_embedder()

    vectorstore = WeaviateVectorStore(
        client=client,
        index_name=collection_name,
        embedding=embedder,
        text_key="text",
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})
