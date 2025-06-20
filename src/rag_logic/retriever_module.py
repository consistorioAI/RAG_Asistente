# src/rag_logic/retriever_module.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Weaviate
from src.config import settings
import weaviate


def get_retriever(k: int = 5, collection_name: str = "LegalDocs"):
    client = weaviate.Client(url=settings.WEAVIATE_URL)

    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Weaviate(
        client=client,
        index_name=collection_name,
        embedding=embedder,
        text_key="text",
        by_text=False
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever
