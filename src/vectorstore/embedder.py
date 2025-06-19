from pathlib import Path
import weaviate  # Cliente v3
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Weaviate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import settings


def get_local_embedder():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def get_weaviate_client():
    return weaviate.Client(
        url=settings.WEAVIATE_URL
    )


def load_documents_from_folder(folder_path: Path):
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


def chunk_documents(documents, chunk_size=500, chunk_overlap=50):
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


def index_chunks(chunks, index_name="LegalDocs"):
    client = get_weaviate_client()

    if not any(cls["class"] == index_name for cls in client.schema.get()["classes"]):

        class_obj = {
            "class": index_name,
            "vectorizer": "none"
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
