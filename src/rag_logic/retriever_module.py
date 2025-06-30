# src/rag_logic/retriever_module.py


from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Weaviate
from langchain_weaviate import WeaviateVectorStore

from src.config import settings
from weaviate import WeaviateClient
from weaviate.auth import AuthApiKey
from functools import lru_cache


@lru_cache(maxsize=1)
def _get_weaviate_client():
    auth = None
    if settings.WEAVIATE_API_KEY:
        auth = AuthApiKey(api_key=settings.WEAVIATE_API_KEY)
    return WeaviateClient(url=settings.WEAVIATE_URL, auth_client_secret=auth)


@lru_cache(maxsize=1)
def _get_embedder():
    """Return a cached embedder instance."""
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        encode_kwargs={"batch_size": settings.BATCH_SIZE},
    )

def ensure_collection_exists(client, collection_name: str) -> None:
    """Verifies that the collection exists in Weaviate."""
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
        by_text=False,
    )

    return vectorstore.as_retriever(search_kwargs={"k": k})
