#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Sequence

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from weaviate import connect_to_custom
from src.config import settings

# ---------- Conexión ----------
parsed = urlparse(settings.WEAVIATE_URL)
host, secure = parsed.hostname or "localhost", parsed.scheme == "https"
port = parsed.port or (443 if secure else 80)

client = connect_to_custom(
    host,
    http_port=port, http_secure=secure,
    grpc_host=host, grpc_port=50051, grpc_secure=secure,
)
client.connect()

COL_NAME = "LegalDocs"

try:
    if not client.collections.exists(COL_NAME):
        print(f"❌ La colección '{COL_NAME}' no existe.")
        sys.exit(1)

    col = client.collections.get(COL_NAME)

    # --------- Averiguar configuración de vectores ---------
    cfg = col.config.get()               # CollectionConfig
    vec_cfg = getattr(cfg, "vector_config", None)

    # Caso 1: sin vector_config → vector por defecto
    if vec_cfg is None:
        named_vecs: Sequence[str] = []
        include_param: List[str] | bool = True

    # Caso 2: vector_config sin named_vectors → vector por defecto
    elif getattr(vec_cfg, "named_vectors", None) in (None, []):
        named_vecs = []
        include_param = True

    # Caso 3: vector_config con named_vectors
    else:
        named_vecs = [nv.name for nv in vec_cfg.named_vectors]
        include_param = list(named_vecs)  # p.e. ["vector"]

    print(f"\n🧬 Primeros 5 vectores en '{COL_NAME}' "
          f"(include_vector={include_param}):\n")

    # ---------- Iterar y mostrar ----------
# --- función auxiliar segura ---------------------------------
    def fmt(v):
        """
        Devuelve un string con el tamaño del embedding y los cinco
        primeros valores, soportando tanto lista como dict.
        """
        # Si viene como dict ⇒ coger el primer vector que contenga
        if isinstance(v, dict):
            v = next(iter(v.values()))  # primer embedding de ese dict

        # Si al final no es secuencia numérica, indicarlo
        if not isinstance(v, (list, tuple)):
            return "vector en formato inesperado"

        return f"dim={len(v)} → {v[:5]} …"

    # --- en el bucle principal -----------------------------------
    for i, obj in enumerate(col.iterator(include_vector=True,
                                        return_properties=["text"])):
        preview = obj.properties.get("text", "").replace("\n", " ")[:100]

        # Compatibilidad: dict → primer valor
        vec = getattr(obj, "vector", None)
        if vec is None and getattr(obj, "vectors", None):
            vec = next(iter(obj.vectors.values()))

        print(f"--- Embedding {i+1} ---")
        print("Texto:", preview + ("…" if len(preview) == 100 else ""))

        if vec:
            print("Vector", fmt(vec), "\n")
        else:
            print("⚠️  Vector no disponible.\n")

        if i >= 4:
            break

finally:
    client.close()
