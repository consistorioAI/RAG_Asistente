from pathlib import Path
import weaviate  # Cliente v3
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Weaviate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import settings
from weaviate.auth import AuthApiKey
from functools import lru_cache
import os


def get_local_embedder():
    """Devuelve un modelo de embedding local (BAAI/bge-small-en-v1.5)."""
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={"device": settings.EMBEDDING_DEVICE}
    )

@lru_cache(maxsize=1)
def get_weaviate_client():
    """Devuelve un cliente Weaviate sin autenticación (modo anónimo)."""
    return weaviate.Client(url=settings.WEAVIATE_URL)



def load_documents_from_folder(folder_path: Path):
    """Carga archivos .txt de una carpeta en una lista de diccionarios."""
    documents = []
    for file in folder_path.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        documents.append({
            "text": content,
            "metadata": {
                "filename": file.name,
                "path": str(file.resolve())
            }
        })
    return documents


def chunk_documents(documents, chunk_size=500, chunk_overlap=100):
    """Divide los documentos en chunks usando un splitter recursivo."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = []
    for doc in documents:
        texts = splitter.split_text(doc["text"])
        for t in texts:
            chunks.append({"text": t, "metadata": doc["metadata"]})
    return chunks


def index_chunks(chunks, gpt_id="default"):
    """
    Indexa los chunks en la base vectorial Weaviate.

    El nombre de la clase de Weaviate será:
    - "LegalDocs" si gpt_id == "default"
    - "LegalDocs_<gpt_id>" en cualquier otro caso
    """
    index_name = "LegalDocs" if gpt_id == "default" else f"LegalDocs_{gpt_id}"
    client = get_weaviate_client()

    # Crear clase si no existe
    if not any(cls["class"] == index_name for cls in client.schema.get()["classes"]):
        class_obj = {
            "class": index_name,
            "vectorizer": "none",
            "properties": [
                {"name": "text", "dataType": ["text"]},
                {"name": "doc_id", "dataType": ["text"]},
                {"name": "filename", "dataType": ["text"]},
                {"name": "created", "dataType": ["text"]},
                {"name": "source", "dataType": ["text"]}
            ]
        }
        client.schema.create_class(class_obj)

    embedder = get_local_embedder()
    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    vectorstore = Weaviate(
        client=client,
        index_name=index_name,
        embedding=embedder,
        text_key="text",
        by_text=False
    )

    vectorstore.add_texts(
        texts=texts,
        metadatas=metadatas
    )
