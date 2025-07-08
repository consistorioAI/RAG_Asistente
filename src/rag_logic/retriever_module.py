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
def _create_weaviate_client():
    """Create and connect a new Weaviate client (cached)."""
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
        grpc_secure=False,
    )
    client.connect()
    return client


def get_weaviate_client():
    """Return a cached Weaviate client, recreating it if the connection is lost."""
    client = _create_weaviate_client()
    try:
        ready = client.is_ready()
    except Exception:
        ready = False

    if not ready:
        try:
            client.close()
        except Exception:
            pass
        _create_weaviate_client.cache_clear()
        client = _create_weaviate_client()

    return client


# ──────────────────────────────────────────────────────────────
# 2) Embedder HuggingFace
# ──────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _get_embedder():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
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
    client = get_weaviate_client()
    ensure_collection_exists(client, collection_name)
    embedder = _get_embedder()

    vectorstore = WeaviateVectorStore(
        client=client,
        index_name=collection_name,
        embedding=embedder,
        text_key="text",
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})
