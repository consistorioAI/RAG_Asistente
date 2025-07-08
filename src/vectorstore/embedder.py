# ── imports ───────────────────────
from pathlib import Path
from functools import lru_cache
from urllib.parse import urlparse

from weaviate import connect_to_custom, WeaviateClient
from weaviate.classes.config import (
    Configure, Property, DataType
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from src.config import settings

_GRPC_PORT = 50051

# ── embeddings ────────────────────
def get_local_embedder():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": settings.EMBEDDING_DEVICE},
        encode_kwargs={"batch_size": settings.BATCH_SIZE},
    )

# ── Weaviate client ───────────────
@lru_cache(maxsize=1)
def get_weaviate_client() -> WeaviateClient:
    parsed = urlparse(settings.WEAVIATE_URL)
    host, secure = parsed.hostname or "localhost", parsed.scheme == "https"
    http_port = parsed.port or (443 if secure else 80)

    client = connect_to_custom(
        host, http_port=http_port, http_secure=secure,
        grpc_host=host, grpc_port=_GRPC_PORT, grpc_secure=False,
    )
    client.connect()
    return client

# ── utils ─────────────────────────
def load_documents_from_folder(folder: Path):
    return [
        {"text": p.read_text(encoding="utf-8"),
         "metadata": {"filename": p.name, "path": str(p.resolve())}}
        for p in folder.glob("*.txt")
    ]

def chunk_documents(docs, size=500, overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    return [
        {"text": chunk, "metadata": doc["metadata"]}
        for doc in docs for chunk in splitter.split_text(doc["text"])
    ]

# ── indexing ──────────────────────
def index_chunks(chunks, gpt_id="default"):
    index_name = "LegalDocs" if gpt_id == "default" else f"LegalDocs_{gpt_id}"
    client = get_weaviate_client()

    if not client.collections.exists(index_name):
        client.collections.create(
            index_name,
            properties=[
                Property(name="text",     data_type=DataType.TEXT),
                Property(name="filename", data_type=DataType.TEXT),
                Property(name="path",     data_type=DataType.TEXT),
            ],
            vectorizer_config=Configure.Vectorizer.none(),  #  ✅ cambio clave
        )

    store = WeaviateVectorStore(
        client=client,
        index_name=index_name,
        embedding=get_local_embedder(),
        text_key="text",
    )
    store.add_texts(texts=[c["text"] for c in chunks],
                    metadatas=[c["metadata"] for c in chunks])

    client.close()
