# src/rag_logic/retriever_module.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Weaviate
from src.config import settings
import weaviate
from weaviate.auth import AuthApiKey
from functools import lru_cache


@lru_cache(maxsize=1)
def _get_weaviate_client():
    auth = None
    if settings.WEAVIATE_API_KEY:
        auth = AuthApiKey(api_key=settings.WEAVIATE_API_KEY)
    return weaviate.Client(url=settings.WEAVIATE_URL, auth_client_secret=auth)


@lru_cache(maxsize=1)
def _get_embedder():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def get_retriever(k: int = 5, collection_name: str = "LegalDocs"):
    client = _get_weaviate_client()
    embedder = _get_embedder()

    vectorstore = Weaviate(
        client=client,
        index_name=collection_name,
        embedding=embedder,
        text_key="text",
        by_text=False,
    )

    return vectorstore.as_retriever(search_kwargs={"k": k})
