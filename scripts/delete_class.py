#!/usr/bin/env python3
"""
Elimina la colección 'LegalDocs' de Weaviate (API v4).
"""

import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from weaviate import connect_to_custom
from src.config import settings

# ── Construcción de conexión ──
parsed = urlparse(settings.WEAVIATE_URL)
host = parsed.hostname or "localhost"
http_secure = parsed.scheme == "https"
http_port = parsed.port or (443 if http_secure else 80)

grpc_host = host
grpc_port = 50051
grpc_secure = http_secure

client = connect_to_custom(
    host,
    http_port=http_port,
    http_secure=http_secure,
    grpc_host=grpc_host,
    grpc_port=grpc_port,
    grpc_secure=grpc_secure,
)
client.connect()

# ── Eliminar colección ──
CLASS_NAME = "LegalDocs"

if client.collections.exists(CLASS_NAME):
    client.collections.delete(CLASS_NAME)  # ← aquí corregido
    print(f"✅ Colección '{CLASS_NAME}' eliminada de Weaviate.")
else:
    print(f"ℹ️  La colección '{CLASS_NAME}' no existe.")

client.close()
