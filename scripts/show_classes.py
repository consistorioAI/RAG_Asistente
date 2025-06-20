import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import weaviate
from src.config import settings

client = weaviate.Client(settings.WEAVIATE_URL)

classes = client.schema.get()["classes"]

print("\nClases encontradas en Weaviate:")
for c in classes:
    print(" -", c["class"])
