import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from weaviate import WeaviateClient
from src.config import settings

client = WeaviateClient(settings.WEAVIATE_URL)

CLASS_NAME = "LegalDocs"

if client.collections.exists(CLASS_NAME):
    client.collections.delete(CLASS_NAME)
    print(f"Clase '{CLASS_NAME}' eliminada de Weaviate.")
else:
    print(f"La clase '{CLASS_NAME}' no existe.")
