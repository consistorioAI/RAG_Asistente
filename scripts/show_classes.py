import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from weaviate import WeaviateClient
from src.config import settings

client = WeaviateClient(url=settings.WEAVIATE_URL)
classes = client.collections.list_all()

print("\nClases encontradas en Weaviate:")
for c in classes:
    print(" -", c)
