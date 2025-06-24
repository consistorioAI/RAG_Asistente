import sys
from pathlib import Path
import json
import argparse

# Añadir el directorio raíz al path para imports absolutos
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.ingestion.ingestor import process_documents
from src.vectorstore.embedder import index_chunks, chunk_documents

# Ruta al archivo que lleva control de los documentos ya procesados
TRACKER_FILE = Path("data/.processed_files.json")

def load_tracker():
    """
    Carga el archivo de seguimiento que contiene los IDs de los documentos
    que ya han sido procesados e indexados.
    """
    if TRACKER_FILE.exists():
        return json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
    return {}

def save_tracker(tracker):
    """
    Guarda el diccionario actualizado de documentos procesados en disco.
    """
    TRACKER_FILE.write_text(json.dumps(tracker, indent=2), encoding="utf-8")

def sync_and_index(gpt_id: str):
    """
    Función principal de sincronización e indexación.

    - Detecta documentos nuevos en la ruta indicada por DOCS_INPUT_PATH.
    - Procesa su contenido y genera chunks en DOCS_OUTPUT_PATH.
    - Indexa solo los documentos nuevos en la clase de Weaviate asociada al `gpt_id`.
    """
    input_path = Path(settings.DOCS_INPUT_PATH)
    output_path = Path(settings.DOCS_OUTPUT_PATH)
    tracker = load_tracker()

    # Procesar todos los documentos disponibles
    all_docs = process_documents(input_path, output_path)

    # Filtrar aquellos que aún no se han indexado o fueron actualizados
    new_docs = []
    for doc in all_docs:
        source = doc["metadata"]["source"]
        doc_id = doc["metadata"]["doc_id"]
        if tracker.get(source) != doc_id:
            new_docs.append(doc)
            tracker[source] = doc_id

    if new_docs:
        print(f"\n🟢 Nuevos documentos detectados: {len(new_docs)}")
        chunks = chunk_documents(
            new_docs,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        index_chunks(chunks, gpt_id=gpt_id)
        print("✅ Reindexado completado.")
    else:
        print("No hay documentos nuevos para indexar.")

    # Guardar el nuevo estado del tracker
    save_tracker(tracker)

if __name__ == "__main__":
    # Permite especificar el GPT (colección Weaviate) como parámetro por CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpt_id", required=True, help="Identificador del GPT (colección en Weaviate)")
    args = parser.parse_args()

    print(f"\n[Ingesta manual] Procesando para GPT: {args.gpt_id}")
    sync_and_index(args.gpt_id)
