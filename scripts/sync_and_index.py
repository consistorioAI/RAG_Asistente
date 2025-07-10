import sys
from pathlib import Path
import json
import argparse

# Añadir el directorio raíz al path para imports absolutos
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.ingestion.ingestor import process_documents
from src.vectorstore.embedder import index_chunks, chunk_documents


def get_tracker_file(gpt_id: str) -> Path:
    """Devuelve la ruta al archivo de seguimiento para cada GPT."""
    base = Path(settings.DATA_INDEX_PATH) / gpt_id
    base.mkdir(parents=True, exist_ok=True)
    return base / ".processed_files.json"


def load_tracker(tracker_file: Path) -> dict:
    """Carga el archivo de seguimiento.

    A partir de la versión actual se almacena un diccionario con el
    ``doc_id`` y un indicador ``chunked``. Para mantener compatibilidad con
    versiones anteriores, si el valor es una cadena se asume que el documento
    ya estaba procesado y troceado.
    """
    if not tracker_file.exists():
        return {}

    data = json.loads(tracker_file.read_text(encoding="utf-8"))

    for src, val in data.items():
        if isinstance(val, str):
            data[src] = {"doc_id": val, "chunked": True, "indexed": True}

    return data


def save_tracker(tracker_file: Path, tracker: dict) -> None:
    """Guarda el diccionario actualizado de documentos procesados."""
    tracker_file.write_text(json.dumps(tracker, indent=2), encoding="utf-8")

def sync_and_index(gpt_id: str):
    """
    Función principal de sincronización e indexación.

    - Detecta documentos nuevos en la ruta indicada por DOCS_INPUT_PATH.
    - Procesa su contenido y genera chunks en DOCS_OUTPUT_PATH.
    - Indexa solo los documentos nuevos en la clase de Weaviate asociada al `gpt_id`.
    """
    input_path = Path(settings.DOCS_INPUT_PATH) / gpt_id
    output_path = Path(settings.DOCS_OUTPUT_PATH) / gpt_id
    output_path.mkdir(parents=True, exist_ok=True)

    tracker_file = get_tracker_file(gpt_id)
    tracker = load_tracker(tracker_file)

    # Procesar todos los documentos disponibles
    all_docs = process_documents(
        input_path,
        output_path,
        save_to_disk=True,
        tracker=tracker,
    )

    # Filtrar aquellos que aún no han sido chunkificados o cuyo contenido cambió
    new_docs = []
    for doc in all_docs:
        source = doc["metadata"]["source"]
        doc_id = doc["metadata"]["doc_id"]

        entry = tracker.get(source)
        if entry and entry.get("doc_id") == doc_id and entry.get("chunked") and entry.get("indexed"):
            # Ya se procesó y se indexó este documento
            continue

        new_docs.append(doc)
        tracker[source] = {"doc_id": doc_id, "chunked": False, "indexed": False}

    # Guardar inmediatamente el estado para evitar reprocesar en caso de fallo
    save_tracker(tracker_file, tracker)

    if new_docs:
        print(f"\n🟢 Nuevos documentos detectados: {len(new_docs)}")
        chunks = chunk_documents(
            new_docs,
            size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP,
        )

        # Marcar como troceados para evitar reprocesos futuros
        for doc in new_docs:
            tracker[doc["metadata"]["source"]]["chunked"] = True
        save_tracker(tracker_file, tracker)

        index_chunks(chunks, gpt_id=gpt_id)

        # Marcar como indexados tras completarse sin errores
        for doc in new_docs:
            tracker[doc["metadata"]["source"]]["indexed"] = True
        print("✅ Reindexado completado.")
    else:
        print("No hay documentos nuevos para indexar.")

    # Guardar el nuevo estado del tracker
    save_tracker(tracker_file, tracker)

if __name__ == "__main__":
    # Permite especificar el GPT (colección Weaviate) como parámetro por CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpt_id", required=True, help="Identificador del GPT (colección en Weaviate)")
    args = parser.parse_args()

    print(f"\n[Ingesta manual] Procesando para GPT: {args.gpt_id}")
    sync_and_index(args.gpt_id)
