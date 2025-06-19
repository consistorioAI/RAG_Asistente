# scripts/ingest_local_docs.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.ingestion.ingestor import process_documents
from src.config import settings

if __name__ == "__main__":
    input_path = settings.DATA_RAW_PATH
    output_path = settings.DATA_CHUNKS_PATH

    docs = process_documents(input_path, output_path)

    print(f"\n{len(docs)} documentos procesados.")
