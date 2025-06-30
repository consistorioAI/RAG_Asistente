#!/usr/bin/env python3
"""
Lista todas las colecciones (clases) existentes en Weaviate   –   API v4
"""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

# añadir raíz del proyecto al PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from weaviate import connect_to_custom                         # v4 helper
from src.config import settings                                 # noqa: E402

# ───────────── Construir la conexión ───────────── #
parsed = urlparse(settings.WEAVIATE_URL)

host = parsed.hostname or "localhost"
http_secure = parsed.scheme == "https"
http_port = parsed.port or (443 if http_secure else 80)

grpc_host = host
grpc_secure = http_secure
grpc_port = 50051  # puerto gRPC por defecto en el contenedor

client = connect_to_custom(
    host,
    http_port=http_port,
    http_secure=http_secure,
    grpc_host=grpc_host,
    grpc_port=grpc_port,
    grpc_secure=grpc_secure,
)
client.connect()      # obligatorio en v4

# ───────────── Listar colecciones ───────────── #
print("\n🧠  Clases (colecciones) en Weaviate:")
for col in client.collections.list_all():
    print(" -", col)


client.close()        # buena práctica
