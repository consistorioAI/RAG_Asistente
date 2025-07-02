# scripts/start_api.py

from __future__ import annotations

import os
import sys
from pathlib import Path

# 1️⃣  AÑADIR LA RAÍZ **ANTES** DE CUALQUIER IMPORT DE `src`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.config import settings  # noqa: E402  ← ahora sí funciona

import uvicorn  # noqa: E402  (se importa después para mantener orden lógico)

if __name__ == "__main__":
    # No usar reload en Windows, rompe multiprocessing + imports
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "2"))
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=workers,
    )
