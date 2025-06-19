# scripts/ingest_local_docs.py

import sys
from pathlib import Path

# Añadir el directorio raíz del proyecto al sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.ingestion.ingestor import process_documents

if __name__ == "__main__":
    input_path = Path("data/raw")
    output_path = Path("data/chunks")

    docs = process_documents(input_path, output_path)

    print(f"\n{len(docs)} documentos procesados.")
