#!/usr/bin/env python3
"""
Elimina una colección de Weaviate (API v4).
Uso:
    python delete_class.py --gpt_id <perfil>
"""

import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from weaviate import connect_to_custom
from src.config import settings
import argparse

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

parser = argparse.ArgumentParser()
parser.add_argument("--gpt_id", default="default", help="Perfil de GPT")
args = parser.parse_args()

class_name = f"LegalDocs_{args.gpt_id}"

if client.collections.exists(class_name):
    client.collections.delete(class_name)
    print(f"✅ Colección '{class_name}' eliminada de Weaviate.")
else:
    print(f"ℹ️  La colección '{class_name}' no existe.")

client.close()
