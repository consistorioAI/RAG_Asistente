import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import weaviate
from src.config import settings

client = weaviate.Client(settings.WEAVIATE_URL)

CLASS_NAME = "LegalDocs"

if any(cls["class"] == CLASS_NAME for cls in client.schema.get()["classes"]):
    client.schema.delete_class(CLASS_NAME)
    print(f"Clase '{CLASS_NAME}' eliminada de Weaviate.")
else:
    print(f"La clase '{CLASS_NAME}' no existe.")
